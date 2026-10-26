#!/usr/bin/env python3
import json,sys,unittest,subprocess
sys.dont_write_bytecode=True
import test_adapters as fixtures
h=fixtures.h
from acceptance import PINS
from scan import SKILL
class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.seed=fixtures.AdapterTests();self.seed.setUp();s=self.seed
        spec={'version':2,'surface':'document','requirements':[{'id':'presence','type':'scenario','description':'Controlled presence check','steps':[{'selector':'body','assert':'visible','value':True}]}],'cases':[{'id':'desktop'}]}
        s.blobs['acceptance.json']=json.dumps(spec).encode();s.data['acceptance']={'sha256':h(s.blobs['acceptance.json'])};s.data['mode']='delivery';s.data['delivery']={'status':'delivery-verified'};s.data['stages'].append({'name':'task-acceptance','exit':0,'signal':None})
        report={'version':1,'specVersion':2,'inputs':{'html':{'sha256':s.data['artifactSHA256']},'acceptance':{'sha256':s.data['acceptance']['sha256']},**PINS},'cases':[{'id':'desktop','coverage':{'id':'desktop'},'errors':[],'results':[{'id':'presence','status':'pass'}]}],'unexecutedRequirements':[],'pass':True,'deliveryStatus':'delivery-verified'}
        s.blobs['acceptance-report.json']=json.dumps(report).encode();s.data['reports']['acceptance-report.json']=h(s.blobs['acceptance-report.json'])
    def tearDown(self):self.seed.tearDown()
    def change(self,fn):self.seed.change_report('acceptance-report.json',fn)
    def test_positive_is_reported_not_complete(self):
        r=self.seed.q();self.assertEqual(r['state'],'qualified-reported');self.assertEqual(len(r['observations']),17);self.assertEqual(r['observations'][-2]['outcome'],'pass');self.assertEqual(r['observations'][-1]['outcome'],'unverified');self.assertFalse(r['performanceEligible']);self.assertEqual(r['identityAudits']['acceptance']['independence'],'unverified')
    def test_case_result_and_subject_controls(self):
        s=self.seed;original=s.blobs['acceptance-report.json']
        for fn,reason in [(lambda r:r['inputs']['html'].update(sha256='0'*64),'acceptance-input-identity-mismatch'),(lambda r:r['inputs'].update(runner='0'*64),'acceptance-runner-identity-mismatch'),(lambda r:r['cases'].clear(),'acceptance-case-coverage-mismatch'),(lambda r:r['cases'][0]['results'].clear(),'acceptance-result-coverage-mismatch'),(lambda r:r['cases'][0]['results'][0].update(status='not-applicable'),'acceptance-result-applicability-mismatch'),(lambda r:r['cases'][0]['results'][0].update(id=[]),'acceptance-result-coverage-mismatch')]:
            s.blobs['acceptance-report.json']=original;self.change(fn);self.assertEqual(s.q()['reason'],reason)
    def test_stale_spec_and_missing_companion(self):
        s=self.seed;s.blobs['acceptance.json']+=b' ';self.assertEqual(s.q()['reason'],'acceptance-spec-identity-mismatch');del s.blobs['acceptance.json'];self.assertEqual(s.q()['reason'],'missing-or-unsafe-acceptance-companion')
    def test_false_pass_is_conflict_and_failure_stays_failure(self):
        self.change(lambda r:r['cases'][0]['results'][0].update(status='assertion-failure',detail=self.seed.marker));r=self.seed.q();self.assertEqual(r['state'],'conflicting');self.assertEqual(r['observations'][-2]['outcome'],'fail');self.assertNotIn(self.seed.marker,json.dumps(r))
    def test_harness_error_is_unverified(self):
        self.change(lambda r:r['cases'][0]['results'][0].update(status='harness-error'));r=self.seed.q();self.assertEqual(r['state'],'conflicting');self.assertEqual(r['observations'][-2]['outcome'],'unverified')
    def test_generation_summary_conflict(self):
        self.seed.data['delivery']['status']='delivery-incomplete';self.assertEqual(self.seed.q()['state'],'conflicting')
    def test_unsupported_spec_and_required_type(self):
        s=self.seed;spec=json.loads(s.blobs['acceptance.json']);spec['version']=1;s.blobs['acceptance.json']=json.dumps(spec).encode();s.data['acceptance']['sha256']=h(s.blobs['acceptance.json']);self.assertEqual(s.q()['reason'],'unsupported-acceptance-spec')
    def test_required_flag_type(self):
        s=self.seed;spec=json.loads(s.blobs['acceptance.json']);spec['requirements'][0]['required']=0;s.blobs['acceptance.json']=json.dumps(spec).encode();s.data['acceptance']['sha256']=h(s.blobs['acceptance.json']);self.change(lambda r:r['inputs']['acceptance'].update(sha256=s.data['acceptance']['sha256']));self.assertEqual(s.q()['reason'],'invalid-acceptance-required-flag')
    def test_forged_pass_for_unexecuted_requirement(self):
        s=self.seed;spec=json.loads(s.blobs['acceptance.json']);spec['requirements'][0].update(execution='unexecuted',reason='deliberately not run');s.blobs['acceptance.json']=json.dumps(spec).encode();s.data['acceptance']['sha256']=h(s.blobs['acceptance.json']);self.change(lambda r:r['inputs']['acceptance'].update(sha256=s.data['acceptance']['sha256']));r=s.q();self.assertEqual(r['state'],'conflicting');self.assertEqual(r['observations'][-2]['outcome'],'unverified')
    def test_zero_required_results_remain_unverified(self):
        s=self.seed;spec=json.loads(s.blobs['acceptance.json']);spec['requirements'][0]['required']=False;s.blobs['acceptance.json']=json.dumps(spec).encode();s.data['acceptance']['sha256']=h(s.blobs['acceptance.json']);self.change(lambda r:r['inputs']['acceptance'].update(sha256=s.data['acceptance']['sha256']));r=s.q();self.assertEqual(r['observations'][-2]['outcome'],'unverified');self.assertFalse(r['performanceEligible'])
    def test_cli_privacy_and_symlink_companions(self):
        s=self.seed;self.change(lambda r:r.update(limitations=[s.marker]));s.write_packet();r,out=s.cli();self.assertNotIn(s.marker,r.stdout+r.stderr)
        for n in ('observations.json','index.html','evidence-index.json'):self.assertNotIn(s.marker,(out/n).read_text())
        secret=s.root/'secrets';secret.mkdir();(secret/'raw.json').write_text(s.marker)
        for name in ('acceptance.json','acceptance-report.json'):
            p=s.packet/name;original=p.read_bytes();p.unlink();p.symlink_to(secret/'raw.json');out=s.root/('unsafe-'+name)
            cli=subprocess.run([sys.executable,str(SKILL/'scripts/scan.py'),'--root',str(s.packet),'--output',str(out),'--skill','wireframe-review'],capture_output=True,text=True);self.assertEqual(cli.returncode,0);self.assertNotIn(s.marker,cli.stdout+cli.stderr);index=json.loads((out/'evidence-index.json').read_text());self.assertEqual(index['candidates'][0]['adapterResult']['reason'],'missing-or-unsafe-acceptance-companion');p.unlink();p.write_bytes(original)
if __name__=='__main__':unittest.main(verbosity=2)
