import copy
import json
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate import validate,digest
from replay import run,route,compare

class ContextTests(unittest.TestCase):
    def setUp(self):
        import shutil
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'corpus'
        shutil.copytree(ROOT/'examples/worked-corpus',self.root)
        self.registry=json.loads((self.root/'registry.json').read_text())
        self.case=json.loads((self.root/'suite.json').read_text())['cases'][0]
    def tearDown(self):self.temp.cleanup()
    def codes(self):return {x['code'] for x in validate(self.root,self.registry)['issues']}
    def artifact(self,id):return next(a for a in self.registry['artifacts'] if a['id']==id)
    def test_worked_before_after_correctness_before_cost(self):
        before=run(self.root,self.root/'registry-before.json',self.root/'suite.json')
        after=run(self.root,self.root/'registry.json',self.root/'suite.json')
        self.assertEqual((before['passed'],after['passed']),(1,3))
        delta=compare(before,after);self.assertEqual(delta['recovered'],2);self.assertEqual(delta['regressions'],0)
        self.assertEqual(delta['changes'][0]['readDelta'],1)
        self.assertFalse(delta['changes'][0]['efficiencyComparable'])
        self.assertTrue(delta['changes'][2]['efficiencyComparable'])
        for c in after['cases']:
            for x in c['ledger']:self.assertEqual(x['submitted'],'unknown');self.assertEqual(x['retention'],'unknown')
    def test_declared_file_drift(self):
        (self.root/'menu.md').write_text('Changed')
        self.assertIn('stale-hash',self.codes());self.assertEqual(route(self.root,self.registry,self.case)['ledger'],[])
    def test_duplicate_ids_and_aliases(self):
        self.registry['artifacts'].append(copy.deepcopy(self.artifact('menu')))
        self.assertTrue({'duplicate-id','duplicate-alias'}<=self.codes())
    def test_alias_shadows_identity(self):
        self.artifact('menu')['aliases']=['policy'];self.assertIn('alias-collision',self.codes())
    def test_missing_dependency(self):
        self.artifact('menu')['relationships']['depends_on']=['absent'];self.assertIn('missing-reference',self.codes())
    def test_unavailable_file(self):
        (self.root/'policy.md').unlink();self.assertIn('unavailable-path',self.codes())
    def test_cycle_terminates(self):
        self.artifact('policy')['relationships']={'depends_on':['menu']}
        self.assertIn('cycle',self.codes());self.assertEqual(route(self.root,self.registry,self.case)['status'],'blocked')
    def test_conflicting_governing_directives(self):
        self.artifact('policy')['directives']={'keyboard':'required'}
        self.artifact('menu')['directives']={'keyboard':'forbidden'}
        r=route(self.root,self.registry,self.case)
        self.assertEqual(r['status'],'blocked');self.assertIn('Conflicting directive',r['reason'])
    def test_budget_blocks_instead_of_short_success(self):
        for budget in [{'reads':1,'bytes':1024},{'reads':8,'bytes':1}]:
            c=dict(self.case,budget=budget);r=route(self.root,self.registry,c)
            self.assertEqual(r['status'],'blocked');self.assertIn('budget exhausted',r['reason'])
    def test_ambiguous_or_unknown_route(self):
        r=route(self.root,self.registry,{'intent':'unknown'});self.assertEqual(r['status'],'blocked')
        self.registry['routes'].append({'intent':'edit-menu','target':'billing'})
        self.assertIn('ambiguous-route',self.codes())
    def test_direct_alias_and_optional_reference(self):
        self.artifact('menu')['relationships']['references']=['billing']
        r=route(self.root,self.registry,{'target':'legacy-menu'})
        self.assertEqual([x['id'] for x in r['ledger']],['policy','menu'])
    def test_misleading_summary_does_not_satisfy_acceptance(self):
        self.artifact('billing')['summary']='Use the custom menu. Keep keyboard navigation.'
        self.registry['routes'][0]['target']='billing'
        p=self.root/'misleading.json';p.write_text(json.dumps(self.registry))
        r=run(self.root,p,self.root/'suite.json')
        self.assertFalse(r['cases'][0]['passed']);self.assertTrue(any('Required source' in x for x in r['cases'][0]['acceptanceFailures']))
    def test_required_content_checked_even_when_hash_current(self):
        (self.root/'policy.md').write_text('Policy no longer contains required guidance')
        self.artifact('policy')['sha256']=digest((self.root/'policy.md').read_bytes())
        p=self.root/'updated.json';p.write_text(json.dumps(self.registry))
        self.assertTrue(validate(self.root,self.registry)['valid'])
        self.assertFalse(run(self.root,p,self.root/'suite.json')['cases'][0]['passed'])
    def test_generated_source_drift(self):
        self.artifact('menu')['sourceDigests']={'policy.md':digest((self.root/'policy.md').read_bytes())}
        (self.root/'policy.md').write_text('new source')
        self.artifact('policy')['sha256']=digest((self.root/'policy.md').read_bytes())
        self.assertIn('stale-hash',self.codes())
    def test_no_root_escape_or_external_symlink(self):
        outside=Path(self.temp.name)/'outside';outside.write_text('private')
        for location in ['../outside',str(outside),'link']:
            if location=='link':(self.root/'link').symlink_to(outside)
            self.artifact('menu')['location']=location
            self.assertIn('unavailable-path',self.codes())
    def test_comparison_rejects_changed_acceptance(self):
        a=run(self.root,self.root/'registry.json',self.root/'suite.json');b=copy.deepcopy(a);b['suiteSha256']='changed'
        with self.assertRaisesRegex(ValueError,'Acceptance suite changed'):compare(a,b)
    def test_profile_malformed_fields(self):
        for key,value in [('artifacts',{}),('routes',[None]),('schemaVersion',True)]:
            r=copy.deepcopy(self.registry);r[key]=value;self.assertFalse(validate(self.root,r)['valid'])
        self.artifact('menu')['relationships']={'depends_on':None};self.assertIn('relationship-shape',self.codes())
    def test_offline_and_no_corpus_execution(self):
        with patch.object(socket,'socket',side_effect=AssertionError('network')),patch.object(subprocess,'run',side_effect=AssertionError('execution')):
            self.assertEqual(run(self.root,self.root/'registry.json',self.root/'suite.json')['passed'],3)
    def test_cli_and_no_overwrite(self):
        output=Path(self.temp.name)/'result.json'
        cmd=[sys.executable,str(ROOT/'scripts/replay.py'),'--root',str(self.root),'--registry',str(self.root/'registry.json'),'--suite',str(self.root/'suite.json'),'--out',str(output)]
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        saved=output.read_bytes();self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2);self.assertEqual(output.read_bytes(),saved)
        self.assertEqual(subprocess.run([sys.executable,str(ROOT/'scripts/validate.py'),'--root',str(self.root),'--registry',str(self.root/'registry.json')],capture_output=True).returncode,0)
    def test_descriptor_without_registry_discloses_limit(self):
        r=validate(self.root,self.artifact('menu'),descriptor=True)
        self.assertTrue(r['valid']);self.assertTrue(any('Standalone' in s for s in r['limits']))

if __name__=='__main__':unittest.main()
