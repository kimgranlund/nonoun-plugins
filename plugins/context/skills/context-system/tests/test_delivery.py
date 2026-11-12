"""Delivery regressions: acceptance remains independent of retrieval settings."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from replay import route,run,compare
from validate import digest

class DeliveryTests(unittest.TestCase):
    def setUp(self):
        import shutil
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'corpus'
        shutil.copytree(ROOT/'examples/worked-corpus',self.root)
        self.registry=json.loads((self.root/'registry.json').read_text())
    def tearDown(self):self.temp.cleanup()
    def replay(self,**kwargs):return route(self.root,self.registry,dict(target='menu',**kwargs))
    def test_combined_batch_truncates_even_when_items_fit(self):
        r=self.replay(budget={'itemBytes':100,'batchBytes':50,'bytes':200})
        self.assertEqual(r['status'],'blocked');self.assertEqual(r['contextBytes'],50)
        self.assertEqual(r['ledger'][-1]['budgetLimits'],['batchBytes'])
        self.assertEqual(r['coverage']['menu'],'partial')
        self.assertEqual(sum(x['bytes'] for x in r['ledger']),50)
    def test_item_limit_is_independent(self):
        r=self.replay(budget={'itemBytes':10,'batchBytes':200,'bytes':200})
        self.assertEqual(r['contextBytes'],10);self.assertEqual(r['ledger'][0]['budgetLimits'],['itemBytes'])
    def test_incomplete_pagination_has_exact_continuation(self):
        r=self.replay(deliveries={'policy':{'mode':'pages','pageBytes':10,'maxPages':2}})
        self.assertEqual(r['status'],'blocked');self.assertEqual(r['contextBytes'],20)
        self.assertEqual(r['ledger'][-1]['byteRange'],[10,20]);self.assertEqual(r['ledger'][-1]['continuation'],20)
        self.assertFalse(r['ledger'][-1]['truncated'])
        self.assertEqual(r['returnedBodies']['policy'],(self.root/'policy.md').read_text()[:20])
    def test_complete_pages_satisfy_same_acceptance(self):
        suite=json.loads((self.root/'suite.json').read_text())
        suite['cases'][0]['deliveries']={'policy':{'mode':'pages','pageBytes':15,'maxPages':3}}
        suite['cases'][0]['budget']['reads']=5
        (self.root/'pages.json').write_text(json.dumps(suite))
        r=run(self.root,self.root/'registry.json',self.root/'pages.json')
        self.assertEqual(r['passed'],3)
        c=r['cases'][0];self.assertEqual(c['coverage']['policy'],'complete');self.assertEqual(c['contextReads'],4)
    def test_summary_cannot_impersonate_contract(self):
        for a in self.registry['artifacts']:
            if a['id']=='policy':a['summary']='Keep keyboard navigation.'
        r=self.replay(deliveries={'policy':{'mode':'summary'}})
        self.assertEqual(r['status'],'blocked');self.assertEqual(r['coverage']['policy'],'summary')
        self.assertNotIn('policy',r['returnedBodies'])
    def test_new_scope_loads_dependency_and_reuses_old_contract(self):
        for a in self.registry['artifacts']:
            if a['id']=='status':a['relationships']={'depends_on':['menu'],'governed_by':['billing']}
        r=route(self.root,self.registry,{'stages':[{'target':'menu'},{'target':'status'}]})
        self.assertEqual(r['status'],'complete')
        self.assertEqual([x['id'] for x in r['ledger']],['policy','menu','billing','status'])
        self.assertEqual(r['stages'][1]['reused'],['policy','menu'])
        self.assertEqual([x['stage'] for x in r['ledger']],[1,1,2,2])
    def test_total_budget_does_not_reset_between_scope_changes(self):
        r=route(self.root,self.registry,{'stages':[{'target':'policy'},{'target':'menu'}],
            'budget':{'batchBytes':100,'itemBytes':100,'bytes':50}})
        self.assertEqual(r['status'],'blocked');self.assertEqual(r['contextBytes'],50)
        self.assertEqual(r['ledger'][-1]['budgetLimits'],['bytes'])
        self.assertEqual(r['stages'][1]['reused'],['policy'])
    def test_read_budget_counts_pages(self):
        r=self.replay(budget={'reads':2},deliveries={'policy':{'mode':'pages','pageBytes':10,'maxPages':10}})
        self.assertEqual(r['contextReads'],2);self.assertIn('Read budget exhausted',r['reason'])
    def test_utf8_partial_receipt_counts_bytes_not_characters(self):
        raw='éé'.encode();(self.root/'policy.md').write_bytes(raw)
        for a in self.registry['artifacts']:
            if a['id']=='policy':a['sha256']=digest(raw)
        r=self.replay(budget={'itemBytes':3})
        self.assertEqual(r['contextBytes'],3);self.assertEqual(r['ledger'][0]['returnedSha256'],digest(raw[:3]))
        self.assertEqual(r['status'],'blocked')
    def test_projection_accounts_fields_and_records_without_full_coverage(self):
        for value,selection in [({'anatomy':'menu','dependencies':['policy']},{'fields':['anatomy']}),
                                (['first','second'],{'records':[0]})]:
            raw=json.dumps(value).encode();(self.root/'policy.md').write_bytes(raw)
            for a in self.registry['artifacts']:
                if a['id']=='policy':a['sha256']=digest(raw)
            r=self.replay(deliveries={'policy':dict(mode='projection',**selection)})
            self.assertEqual(r['coverage']['policy'],'projection');self.assertEqual(r['status'],'blocked')
            key=next(iter(selection));self.assertEqual(r['ledger'][0][key],selection[key])
    def test_invalid_delivery_and_budget_fail_closed(self):
        for delivery in [{'mode':'unknown'},{'mode':'pages','pageBytes':0},{'mode':'pages','maxPages':True}]:
            self.assertEqual(self.replay(deliveries={'policy':delivery})['status'],'blocked')
        with self.assertRaises(ValueError):self.replay(budget={'batchBytes':-1})
    def test_comparison_rejects_old_accounting_version(self):
        r=run(self.root,self.root/'registry.json',self.root/'suite.json');old=copy.deepcopy(r);old['version']=1
        with self.assertRaisesRegex(ValueError,'accounting version'):compare(old,r)

if __name__=='__main__':unittest.main()
