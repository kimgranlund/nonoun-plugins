#!/usr/bin/env python3
import contextlib, hashlib, io, json, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.dont_write_bytecode = True
from scan import scan, SKILL
from report import render

class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='reportcard-fixture-',dir='/private/tmp');self.root=Path(self.tmp.name);self.out=self.root/'output';self.marker='PRIVATE_INJECTION_7391';self.allowed=self.root/'base-ui';self.allowed.mkdir()
    def tearDown(self):self.tmp.cleanup()
    def put(self,path,data):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data));return p
    def collect(self,**kwargs):return scan([self.root],self.out,['base-ui'],**kwargs)
    def test_candidate_privacy_and_duplicates(self):
        a=self.put('base-ui/report.json',{'status':'pass','prose':self.marker});self.put('base-ui/copy/report.json',json.loads(a.read_text()));d=self.collect();self.assertEqual(len(d['candidates']),1);self.assertEqual(len(d['candidates'][0]['paths']),2);self.assertEqual(d['coverage']['counts']['exactDuplicates'],1);self.assertNotIn(self.marker,json.dumps(d));self.assertEqual(d['candidates'][0]['qualification'],'unqualified')
    def test_excluded_explicit_roots_and_symlinks(self):
        for folder in ['secrets','sessions','holdout-sealed','.claude']:
            self.put(folder+'/report.json',{'skill':'base-ui','text':self.marker})
            d=scan([self.root/folder],self.out,['base-ui']);self.assertEqual(d['roots'][0]['status'],'excluded')
        external=self.put('secrets/report.json',{'skill':'base-ui'});(self.allowed/'report.json').symlink_to(external)
        self.assertEqual(len(self.collect()['candidates']),0)
    def test_malformed_oversized_unattributed(self):
        (self.allowed/'report.json').write_text('{broken');(self.allowed/'results.json').write_text(' '*1000);self.put('unrelated/report.json',{'text':'base-ui is mentioned but not attributed'})
        d=self.collect(max_bytes=100);self.assertEqual(d['coverage']['counts']['malformed'],1);self.assertEqual(d['coverage']['counts']['oversized'],1);self.assertEqual(d['coverage']['counts']['unattributed'],1);self.assertEqual(len(d['candidates']),0)
    def test_budgets_and_depth_visible(self):
        for n in range(5):self.put(f'base-ui/{n}/report.json',{'n':n})
        d=self.collect(max_entries=1);self.assertEqual(d['coverage']['stopReason'],'entry-budget');d=self.collect(depth=0);self.assertGreater(d['coverage']['counts']['depthLimitedDirectories'],0);self.assertFalse(d['coverage']['completeSystemCoverage'])
    def test_missing_and_overlapping_roots(self):
        self.put('base-ui/report.json',{'skill':'base-ui'});d=scan([self.allowed,self.root,self.root/'missing'],self.out,['base-ui']);self.assertEqual(len(d['candidates']),1);self.assertEqual(len(d['candidates'][0]['paths']),1);self.assertEqual(d['roots'][-1]['status'],'missing')
    def test_cli_compact_output_preserves_source_and_prior_output(self):
        p=self.put('base-ui/report.json',{'skill':'base-ui','text':self.marker});before=p.read_bytes();args=[sys.executable,str(SKILL/'scripts/scan.py'),'--root',str(self.root),'--output',str(self.out)]
        result=subprocess.run(args,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr);self.assertLess(len(result.stdout.encode()),4096);self.assertNotIn(self.marker,result.stdout);self.assertNotIn(self.marker,(self.out/'index.html').read_text());self.assertEqual(p.read_bytes(),before)
        card=json.loads((self.out/'report-card.json').read_text());self.assertTrue(all(m['value'] is None for s in card['skills'] for m in s['metrics']));self.assertEqual(sum(len(s['metrics']) for s in card['skills']),17)
        html=(self.out/'index.html').read_bytes();again=subprocess.run(args,capture_output=True,text=True);self.assertNotEqual(again.returncode,0);self.assertEqual((self.out/'index.html').read_bytes(),html)
    def test_renderer_script_escape_and_plain_fallback(self):
        self.out.mkdir();r={'coverage':{},'skills':[],'probe':'</script><script>globalThis.injected=true</script>'};render(r,self.out,self.root/'missing-kit');s=(self.out/'index.html').read_text();self.assertNotIn('</script><script>globalThis.injected',s);self.assertIn('\\u003c/script',s);self.assertEqual(r['styling']['state'],'plain-html')
    def test_contract_shape(self):
        c=json.loads((SKILL/'references/kpis.json').read_text());self.assertEqual(len(c['skills']),3)
        for s in c['skills']:
            self.assertTrue(s['primaryGoal']);self.assertTrue(3<=len(s['kpis'])<=8);self.assertEqual(len({k['id'] for k in s['kpis']}),len(s['kpis']));self.assertTrue(all(k['target'] is None and k['boundary'] for k in s['kpis']))

if __name__=='__main__':unittest.main(verbosity=2)
