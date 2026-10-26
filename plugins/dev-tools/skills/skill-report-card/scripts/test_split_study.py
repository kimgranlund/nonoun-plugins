#!/usr/bin/env python3
import copy,json,sys,unittest
sys.dont_write_bytecode=True
from split_study import interpret,validate,sha,KEYS

def fixture():
    return {'protocol':{'schemaVersion':1,'revisionContaminated':True},'metrics':[{'readCommandReturnBytes':v,'readMetricDefinition':'mixed command heuristic','evaluatorAccess':['evaluator check'] if i==2 else []} for i,v in enumerate((72320,295410,1387892))], 'revision':[{'width':w,'scheme':s,'variants':[{'variant':v,'checks':{f'criterion-{i}':{'pass':True} for i in range(5)}} for v in ('A','B')]} for w in (390,1280) for s in ('light','dark')], 'qualification':{k:True for k in ('capFaultDetected','swappedErrorFaultDetectedByStrongPredicate','positiveStrongPredicatePasses','qualifierCopiesAreNotAuthorRepairs')},'generation':{'mode':'draft','delivery':{'status':'delivery-incomplete'},'artifactSHA256':'a'*64,'findings':{'unverified':[{'rule':'unknown-style-owner','severity':'unverified','detail':'PRIVATE_MARKER'} for _ in range(5)]}},'preservation':{k:True for k in ('03-revisionFrozen','03-revisionPredecessor','03-revisionSeal')}}
def run(packet):return interpret(packet,{k:sha(json.dumps(v).encode()) for k,v in packet.items()},'a'*64)
class SplitStudyTests(unittest.TestCase):
    def setUp(self):self.packet=fixture()
    def test_positive_scopes_and_privacy(self):
        n=run(self.packet);self.assertEqual(len(n['observations']),53);self.assertEqual(n['cleanContextEligibility'],'ineligible');self.assertFalse(n['performanceEligible']);self.assertEqual(n['telemetry']['values'],[72320,295410,1387892]);self.assertIsNone(n['confirmedDefectCount']);self.assertNotIn('PRIVATE_MARKER',json.dumps(n));validate(n)
    def test_contamination_conflict_keeps_behavior(self):
        self.packet['protocol']['revisionContaminated']=False;n=run(self.packet);self.assertEqual(n['cleanContextEligibility'],'ineligible');self.assertTrue(n['contaminationConflict']);self.assertEqual(sum(x['outcome']=='pass' for x in n['observations'] if x['dimension']=='scoped-behavior'),40)
    def test_missing_access_is_not_clean_success(self):
        self.packet['metrics'][2]['evaluatorAccess']=[];self.packet['protocol']['revisionContaminated']=False;n=run(self.packet);self.assertEqual(n['cleanContextEligibility'],'unverified');self.assertFalse(n['performanceEligible'])
    def test_behavior_failure_and_preservation_separate(self):
        self.packet['revision'][0]['variants'][0]['checks']['criterion-0']['pass']=False;n=run(self.packet);self.assertEqual(sum(o['outcome']=='fail' for o in n['observations'] if o['dimension']=='scoped-behavior'),1);self.assertTrue(all(o['outcome']=='pass' for o in n['observations'] if o['dimension']=='preservation'))
        self.packet['preservation']['03-revisionSeal']=False;n=run(self.packet);self.assertEqual(sum(o['outcome']=='fail' for o in n['observations'] if o['dimension']=='preservation'),1)
    def test_claim_promotions_rejected(self):
        for key,value in [('fullSystemAcceptance',True),('cleanContextEligibility','eligible'),('deliveryAcceptance','complete'),('confirmedDefectCount',5),('preservationSubstitutesForBehavior',True),('attemptDenominator',1),('performanceEligible',True)]:
            n=run(self.packet);n[key]=value
            with self.assertRaises(ValueError):validate(n)
    def test_telemetry_relabelling_rejected(self):
        for key,value in [('unit','tokens'),('mixedCommands',False),('modelTokens',1387892),('crossTaskEfficiencyRanking',[0,1,2])]:
            n=run(self.packet);n['telemetry'][key]=value
            with self.assertRaises(ValueError):validate(n)
    def test_preservation_cannot_be_behavior_evidence(self):
        n=run(self.packet);n['observations'][0]['evidence'][0]['sourceId']='preservation'
        with self.assertRaises(ValueError):validate(n)
    def test_duplicate_case_and_weak_predicate_rejected(self):
        self.packet['revision'][1]=copy.deepcopy(self.packet['revision'][0])
        with self.assertRaises(ValueError):run(self.packet)
        self.packet=fixture();self.packet['qualification']['swappedErrorFaultDetectedByStrongPredicate']=False
        with self.assertRaises(ValueError):run(self.packet)
    def test_draft_and_subject_substitution_rejected(self):
        self.packet['generation']['delivery']['status']='delivery-verified'
        with self.assertRaises(ValueError):run(self.packet)
        self.packet=fixture();self.packet['generation']['artifactSHA256']='b'*64
        with self.assertRaises(ValueError):run(self.packet)
if __name__=='__main__':unittest.main(verbosity=2)
