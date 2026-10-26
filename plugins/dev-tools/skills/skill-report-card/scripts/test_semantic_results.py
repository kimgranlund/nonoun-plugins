import unittest,copy,json,tempfile,subprocess,sys
from pathlib import Path
from semantic_results import aggregate,integrate,validate_packet,evidence_items,SKILL

def case(**kw):
    c=dict(skillId='component-variants',metricId='decision-usefulness',attemptId='attempt-a',criterionId='response',outcome='pass',origin='explicit-human',confidence='high',cohort={'task':'fixture','model':None},retrospectiveRubric=False,provenance=[{'path':'fixture','sha256':'a'*64}],rationale='Explicit supported choice')
    c.update(kw);return c

class SemanticTests(unittest.TestCase):
    def test_duplicates_and_reanalysis(self):
        a=case();b=case(rationale='Reanalysis');r=aggregate([a,b])[0];self.assertEqual((r['numerator'],r['denominator']),(1,1))
    def test_failure_bites(self):
        r=aggregate([case(),case(attemptId='b',outcome='fail')])[0];self.assertEqual(r['value'],.5)
    def test_missing_not_failure(self):
        r=aggregate([case(outcome='unverified')])[0];self.assertIsNone(r['value']);self.assertEqual(r['missingCases'],1)
    def test_conflict_not_best_result(self):
        r=aggregate([case(),case(outcome='fail')])[0];self.assertIsNone(r['value']);self.assertEqual(r['conflictingCases'],1)
    def test_test_population_and_failure_phase_not_pooled(self):
        rows=aggregate([case(cohort={'population':'controlled-test','phase':'initial'},outcome='fail'),case(cohort={'population':'controlled-test','phase':'repaired'}),case(cohort={'population':'real-use','phase':'repaired'})])
        self.assertEqual(len(rows),3)
        self.assertEqual(sorted(r['value'] for r in rows),[0,1,1])
    def test_mixed_populations_cannot_be_mislabelled(self):
        registry=json.loads((SKILL/'references/kpis.json').read_text())
        base={'skills':registry['skills']}
        packet={'schemaVersion':1,'skillId':'component-variants','cases':[case(cohort={'population':'real-use'}),case(cohort={'population':'controlled-test'})]}
        with self.assertRaisesRegex(ValueError,'populations separately'):integrate(base,[packet])
    def test_telemetry_not_boolean_proportion(self):
        with self.assertRaisesRegex(ValueError,'unit-specific'):aggregate([case(skillId='base-ui',metricId='context-burden')])
    def test_cohorts_not_pooled(self):
        r=aggregate([case(),case(cohort={'task':'other'},outcome='fail')]);self.assertEqual(len(r),2);self.assertEqual(sorted(x['value'] for x in r),[0,1])
    def test_inference_and_retrospective_distinct(self):
        r=aggregate([case(origin='inferred',confidence='medium'),case(retrospectiveRubric=True)]);self.assertEqual(len(r),2);self.assertEqual(sum(x['inferredCases'] for x in r),1)
    def test_identity_required(self):
        with self.assertRaises(ValueError):aggregate([case(provenance=[])])
        with self.assertRaises(ValueError):aggregate([case(provenance=[{'sha256':'wrong'}])])
    def test_evidence_sentence_not_characters(self):
        sentence='No eligible consumer export was found.'
        self.assertEqual(evidence_items(sentence),[sentence])
        self.assertEqual(' '.join(dict.fromkeys(evidence_items(sentence))),sentence)
        registry=json.loads((SKILL/'references/kpis.json').read_text())
        base={'skills':[dict(s,metrics=[{'id':k['id'],'value':None,'reason':'Missing'} for k in s['kpis']]) for s in registry['skills']],'coverage':{'limitations':[]}}
        report,_=integrate(base,[{'schemaVersion':1,'skillId':'component-variants','cases':[case(outcome='unverified',missingEvidence=sentence)]}])
        metric=next(m for s in report['skills'] if s['id']=='component-variants' for m in s['metrics'] if m['id']=='decision-usefulness')
        self.assertEqual(metric['reason'],sentence)
    def test_raw_field_rejected(self):
        with self.assertRaisesRegex(ValueError,'Raw evidence'):validate_packet({'rawLog':'PRIVATE_MARKER'})
    def test_actual_cli_no_target_and_existing_output(self):
        with tempfile.TemporaryDirectory(prefix='semantic-test-',dir='/private/tmp') as tmp:
            p=Path(tmp);registry=json.loads((SKILL/'references/kpis.json').read_text())
            base={'skills':[dict(s,metrics=[{'id':k['id'],'value':None,'reason':'Missing','evidenceState':'insufficient'} for k in s['kpis']],candidateDocuments=0) for s in registry['skills']],'coverage':{'uniqueCandidateDocuments':1,'limitations':[],'stopReason':None}}
            (p/'base.json').write_text(json.dumps(base));(p/'review.json').write_text(json.dumps({'schemaVersion':1,'skillId':'component-variants','cases':[case()],'findings':[]}))
            cmd=[sys.executable,str(SKILL/'scripts/semantic_results.py'),'--base',str(p/'base.json'),'--review',str(p/'review.json'),'--output',str(p/'out')]
            result=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stdout);self.assertEqual(json.loads(result.stdout)['measuredKpis'],1)
            report=json.loads((p/'out/report-card.json').read_text());m=next(s for s in report['skills'] if s['id']=='component-variants')['metrics'][4]
            self.assertEqual(m['status'],'no-target');self.assertEqual(m['value'],'1/1 (100%)')
            again=subprocess.run(cmd,capture_output=True,text=True);self.assertNotEqual(again.returncode,0)
if __name__=='__main__':unittest.main()
