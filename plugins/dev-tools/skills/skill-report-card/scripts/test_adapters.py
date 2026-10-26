#!/usr/bin/env python3
"""Synthetic contracts and CLI controls; fixtures live only in disposable temp dirs."""
import copy, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.dont_write_bytecode=True
from adapters import qualify, validate_observation, PRODUCER, STATIC, STAGES, LINT_SOURCES
from scan import SKILL

def h(x):return hashlib.sha256(x).hexdigest()
class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='adapter-fixture-',dir='/private/tmp');self.root=Path(self.tmp.name);self.packet=self.root/'packet';self.packet.mkdir();self.marker='RAW_PRIVATE_'+'q'*100000
        self.blobs={'artifact.html':b'<html>synthetic artifact</html>','manifest.json':json.dumps({'units':[{'id':'task','kind':'component','variants':[{'id':'one'}]}]}).encode(),'source.manifest.json':b'{}'}
        v={'schemaVersion':1,'generatedBy':'verify-artifact/1','inputs':{'artifact':{'sha256':h(self.blobs['artifact.html'])},'manifest':{'sha256':h(self.blobs['manifest.json'])}},'checks':[{'id':c,'status':'pass'} for c in STATIC],'limitations':[self.marker]}
        self.blobs['verification.json']=json.dumps(v).encode()
        self.blobs['runtime.json']=json.dumps({'status':'pass','errors':[],'inputs':{'artifact':h(self.blobs['artifact.html']),'manifest':h(self.blobs['manifest.json'])},'cases':[{'unit':'task','variant':'one','viewport':w} for w in ('desktop','mobile')]}).encode()
        self.blobs['lint.json']=json.dumps({'input':{'sha256':h(self.blobs['artifact.html'])},'inspectedHtmlSHA256':h(self.blobs['artifact.html']),'sources':LINT_SOURCES,'policy':None,'temporaryBuild':None,'documents':['root'],'findings':[]}).encode()
        self.data={'pipelineSHA256':PRODUCER,'mode':'draft','status':'passed','source':{'sha256':h(b'{}')},'artifactSHA256':h(self.blobs['artifact.html']),'uiKit':{'packageId':'local.base-ui','contentSHA256':'a'*64},'stages':[{'name':c,'exit':0,'signal':None,'stdout':self.marker} for c in STAGES],'reports':{n:h(self.blobs[n]) for n in ('verification.json','runtime.json','lint.json')},'delivery':{'status':'delivery-incomplete'},'notes':self.marker}
    def tearDown(self):self.tmp.cleanup()
    def q(self,d=None):
        raw=json.dumps(d or self.data).encode();return qualify(d or self.data,h(raw),self.blobs.get)
    def rewrite_verifier(self,fn):
        v=json.loads(self.blobs['verification.json']);fn(v);self.blobs['verification.json']=json.dumps(v).encode();self.data['reports']['verification.json']=h(self.blobs['verification.json'])
    def test_positive_reported_only(self):
        r=self.q();self.assertEqual(r['state'],'qualified-reported');self.assertEqual(len(r['observations']),15);self.assertFalse(r['performanceEligible']);self.assertNotIn(self.marker,json.dumps(r))
        for o in r['observations']:validate_observation(o);self.assertIsNone(o['attemptId'])
        self.assertEqual(r['observations'][-1]['outcome'],'unverified')
    def test_unknown_schema_completion_only(self):
        r=self.q({'skill':'wireframe-review','pass':True,'status':'passed'})
        self.assertEqual(r['state'],'unsupported');self.assertEqual(r['observations'],[])
    def test_identity_mismatches(self):
        for field in ('pipelineSHA256','artifactSHA256'):
            d=copy.deepcopy(self.data);d[field]='0'*64;self.assertNotEqual(self.q(d)['state'],'qualified-reported')
        self.blobs['artifact.html']+=b'changed';self.assertEqual(self.q()['reason'],'artifact-identity-mismatch')
    def test_report_and_source_mismatch(self):
        self.blobs['verification.json']+=b' ';self.assertEqual(self.q()['reason'],'report-identity-mismatch')
        self.blobs['source.manifest.json']=b'changed';self.assertEqual(self.q()['reason'],'source-identity-mismatch')
    def test_omitted_duplicate_and_wrong_input(self):
        original=self.blobs['verification.json']
        for mutate,reason in [(lambda v:v['checks'].pop(),'missing-or-duplicate-criterion'),(lambda v:v['checks'].append(v['checks'][0]),'missing-or-duplicate-criterion'),(lambda v:v['inputs']['artifact'].update(sha256='0'*64),'verifier-input-mismatch')]:
            self.blobs['verification.json']=original;self.rewrite_verifier(mutate);self.assertEqual(self.q()['reason'],reason)
    def test_malformed_criterion_identifier(self):
        self.rewrite_verifier(lambda v:v['checks'][0].update(id=['invalid']))
        self.assertEqual(self.q()['reason'],'invalid-criterion-shape')
    def test_forged_completion_and_conflict(self):
        self.data['status']='passed';self.data['pass']=True;self.data['delivery']={'status':'delivery-verified'}
        self.rewrite_verifier(lambda v:v['checks'][0].update(status='fail'))
        r=self.q();self.assertEqual(r['state'],'conflicting');self.assertEqual(r['observations'][5]['outcome'],'fail');self.assertEqual(r['observations'][-1]['outcome'],'unverified')
    def test_missing_gate_and_failed_gate(self):
        d=copy.deepcopy(self.data);d['stages'].pop();self.assertEqual(self.q(d)['reason'],'missing-or-duplicate-gate')
        self.data['stages'][0]['exit']=1;r=self.q();self.assertEqual(r['observations'][1]['outcome'],'fail');self.assertFalse(r['performanceEligible'])
    def test_missing_dependency_and_companion(self):
        d=copy.deepcopy(self.data);d.pop('uiKit');self.assertEqual(self.q(d)['reason'],'missing-dependency-identity')
        del self.blobs['artifact.html'];self.assertEqual(self.q()['reason'],'missing-or-unsafe-companion')
    def change_report(self,name,fn):
        d=json.loads(self.blobs[name]);fn(d);self.blobs[name]=json.dumps(d).encode();self.data['reports'][name]=h(self.blobs[name])
    def test_runtime_identity_and_route_controls(self):
        original=self.blobs['runtime.json']
        for mutate,reason in [(lambda r:r['inputs'].update(artifact='0'*64),'runtime-input-identity-mismatch'),(lambda r:r['inputs'].update(manifest='0'*64),'runtime-input-identity-mismatch'),(lambda r:r['cases'].pop(),'runtime-route-coverage-mismatch'),(lambda r:r['cases'].append(r['cases'][0]),'runtime-route-coverage-mismatch'),(lambda r:r['cases'][0].update(unit=[]),'invalid-runtime-cases')]:
            self.blobs['runtime.json']=original;self.change_report('runtime.json',mutate);self.assertEqual(self.q()['reason'],reason)
    def test_runtime_stale_missing_and_conflict(self):
        self.blobs['runtime.json']+=b' ';self.assertEqual(self.q()['reason'],'runtime-report-identity-mismatch')
        self.change_report('runtime.json',lambda r:r['errors'].append(self.marker));r=self.q();self.assertEqual(r['state'],'conflicting');self.assertEqual(r['observations'][-3]['outcome'],'fail');self.assertNotIn(self.marker,json.dumps(r))
        del self.blobs['runtime.json'];self.assertEqual(self.q()['reason'],'missing-or-unsafe-companion')
    def test_lint_identity_controls(self):
        original=self.blobs['lint.json']
        for mutate,reason in [(lambda r:r['input'].update(sha256='0'*64),'lint-input-identity-mismatch'),(lambda r:r.update(inspectedHtmlSHA256='0'*64),'lint-input-identity-mismatch'),(lambda r:r['sources'].pop(next(iter(r['sources']))),'lint-source-identity-mismatch'),(lambda r:r['sources'].update({'scripts/lint-artifact.mjs':'0'*64}),'lint-source-identity-mismatch'),(lambda r:r.update(temporaryBuild='untrusted-path'),'unsupported-lint-temporary-build'),(lambda r:r.update(findings=[{'severity':[]}]),'invalid-lint-findings'),(lambda r:r.update(documents=[[]]),'invalid-lint-documents')]:
            self.blobs['lint.json']=original;self.change_report('lint.json',mutate);self.assertEqual(self.q()['reason'],reason)
    def test_lint_stale_and_conflict(self):
        self.blobs['lint.json']+=b' ';self.assertEqual(self.q()['reason'],'lint-report-identity-mismatch')
        self.change_report('lint.json',lambda r:r['findings'].append({'rule':'test','severity':'error','document':'root','selector':'','detail':self.marker}));r=self.q();self.assertEqual(r['state'],'conflicting');self.assertEqual(r['observations'][-2]['outcome'],'fail');self.assertNotIn(self.marker,json.dumps(r))
    def test_lint_warning_unverified_and_policy(self):
        self.change_report('lint.json',lambda r:r['findings'].extend([{'rule':'test','severity':s,'document':'root','selector':'','detail':self.marker} for s in ('warning','unverified')]))
        r=self.q();self.assertEqual(r['state'],'qualified-reported');self.assertEqual(r['identityAudits']['lint']['findingCounts'],{'error':0,'warning':1,'unverified':1});self.assertNotIn(self.marker,json.dumps(r))
        self.blobs['lint-policy.json']=b'{"deferredReferences":[]}'
        self.data['policy']={'sha256':h(self.blobs['lint-policy.json'])}
        self.assertEqual(self.q()['reason'],'lint-policy-identity-mismatch')
        self.change_report('lint.json',lambda r:r.update(policy={'sha256':self.data['policy']['sha256']}))
        self.assertEqual(self.q()['state'],'qualified-reported')
        self.blobs['lint-policy.json']+=b' ';self.assertEqual(self.q()['reason'],'lint-policy-identity-mismatch')
    def test_schema_negative_control(self):
        o=self.q()['observations'][0];o['artifactId']='bad'
        with self.assertRaises(ValueError):validate_observation(o)
    def write_packet(self):
        for n,b in self.blobs.items():(self.packet/n).write_bytes(b)
        (self.packet/'generation.json').write_text(json.dumps(self.data))
    def cli(self):
        out=self.root/'output';r=subprocess.run([sys.executable,str(SKILL/'scripts/scan.py'),'--root',str(self.root),'--output',str(out),'--skill','wireframe-review'],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);self.assertLess(len(r.stdout.encode()),4096);return r,out
    def test_cli_duplicate_reanalysis_and_privacy(self):
        self.write_packet();(self.packet/'copy-report.json').write_bytes((self.packet/'generation.json').read_bytes())
        d=copy.deepcopy(self.data);d['reanalysis']='different interpretation, no new author attempt';(self.packet/'reanalysis-report.json').write_text(json.dumps(d))
        before={p.name:h(p.read_bytes()) for p in self.packet.iterdir()};r,out=self.cli();self.assertNotIn(self.marker,r.stdout+r.stderr)
        for n in ('observations.json','index.html','report-card.json','evidence-index.json'):self.assertNotIn(self.marker,(out/n).read_text())
        index=json.loads((out/'evidence-index.json').read_text());self.assertEqual(index['coverage']['counts']['exactDuplicates'],1)
        obs=json.loads((out/'observations.json').read_text());self.assertEqual(len(obs['observations']),30);self.assertTrue(all(o['attemptId'] is None for o in obs['observations']))
        self.assertFalse(obs['performanceEligible']);self.assertEqual(json.loads(r.stdout)['measuredKpis'],0)
        self.assertEqual(before,{p.name:h(p.read_bytes()) for p in self.packet.iterdir()})
    def test_cli_runtime_lint_companion_exclusion(self):
        self.write_packet();hidden=self.root/'secrets';hidden.mkdir();(hidden/'raw.json').write_text(self.marker)
        for name in ('runtime.json','lint.json'):
            p=self.packet/name;original=p.read_bytes();p.unlink();p.symlink_to(hidden/'raw.json')
            out=self.root/('output-'+name)
            result=subprocess.run([sys.executable,str(SKILL/'scripts/scan.py'),'--root',str(self.packet),'--output',str(out),'--skill','wireframe-review'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0);self.assertNotIn(self.marker,result.stdout+result.stderr)
            index=json.loads((out/'evidence-index.json').read_text());self.assertEqual(index['candidates'][0]['adapterResult']['reason'],'missing-or-unsafe-companion')
            p.unlink();p.write_bytes(original)
    def test_cli_symlink_companion_exclusion(self):
        self.write_packet();artifact=self.packet/'artifact.html';artifact.unlink();hidden=self.root/'secrets';hidden.mkdir();(hidden/'raw.html').write_text(self.marker);artifact.symlink_to(hidden/'raw.html');r,out=self.cli()
        index=json.loads((out/'evidence-index.json').read_text());self.assertEqual(index['candidates'][0]['adapterResult']['reason'],'missing-or-unsafe-companion');self.assertNotIn(self.marker,r.stdout)
if __name__=='__main__':unittest.main(verbosity=2)
