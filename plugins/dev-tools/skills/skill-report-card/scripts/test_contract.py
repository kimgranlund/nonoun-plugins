#!/usr/bin/env python3
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
from validate_contract import validate,SCHEMA,validate_schema
ROOT=Path(__file__).resolve().parents[1]
class ContractTests(unittest.TestCase):
    def setUp(self):self.c=json.loads((ROOT/'assets/performance-contract.example.json').read_text())
    def test_example(self):self.assertEqual(validate(self.c)['kpis'],5)
    def test_bounds(self):
        for n in [2,9]:
            c=copy.deepcopy(self.c);c['kpis']=(c['kpis']*2)[:n]
            with self.assertRaises(ValueError):validate(c)
    def test_missing_goal_duplicate_ids_and_unknown_reference(self):
        for mutation in [lambda c:c['goals'].pop('primary'),lambda c:c['kpis'][1].update(id=c['kpis'][0]['id']),lambda c:c['kpis'][0].update(goalIds=['unknown']),lambda c:c['goals']['secondary'].append(c['goals']['primary'])]:
            c=copy.deepcopy(self.c);mutation(c)
            with self.assertRaises(ValueError):validate(c)
    def test_unknown_fields_and_bad_measure(self):
        for mutation in [lambda c:c.update(score=100),lambda c:c['kpis'][0]['measurement'].pop('denominator'),lambda c:c['kpis'][0].update(missingData='pass'),lambda c:c.update(schemaVersion=True)]:
            c=copy.deepcopy(self.c);mutation(c)
            with self.assertRaises(ValueError):validate(c)
    def test_target_and_alternative_measurements(self):
        k=self.c['kpis'][0];k['measurement']={'kind':'rubric','rubric':'Explicit anchored rubric','scale':['insufficient','adequate']};validate(self.c)
        k['defaultTarget']={'value':2,'operator':'>=','rationale':'Example','scope':'Test'}
        with self.assertRaises(ValueError):validate(self.c)
        k['unit']='bytes';k['defaultTarget']['value']=float('inf')
        with self.assertRaises(ValueError):validate(self.c)
    def test_no_primary_coverage(self):
        for k in self.c['kpis']:k['goalIds']=k['goalIds'][1:]
        with self.assertRaises(ValueError):validate(self.c)
    def test_unknown_schema_keyword(self):
        s=json.loads(SCHEMA.read_text());s['unevaluatedProperties']=False
        with self.assertRaises(ValueError):validate_schema(s)
    def test_real_cli_readonly(self):
        p=ROOT/'assets/performance-contract.example.json';before=p.read_bytes();run=subprocess.run([sys.executable,str(ROOT/'scripts/validate_contract.py'),str(p)],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(p.read_bytes(),before);self.assertEqual(len(json.loads(run.stdout)['sha256']),64)
        with tempfile.TemporaryDirectory(dir='/private/tmp',prefix='contract-check-') as d:
            f=Path(d)/'bad.json';f.write_text('{"schemaVersion": 1}')
            self.assertNotEqual(subprocess.run([sys.executable,str(ROOT/'scripts/validate_contract.py'),str(f)],capture_output=True).returncode,0)
if __name__=='__main__':unittest.main(verbosity=2)
