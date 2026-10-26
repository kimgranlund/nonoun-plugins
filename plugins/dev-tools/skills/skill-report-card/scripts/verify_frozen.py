#!/usr/bin/env python3
"""Verify a locally frozen minimal producer draft; keep raw packets in fresh output."""
import argparse, copy, json, os, stat, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
from adapters import qualify, digest, PRODUCER, ADAPTER
from scan import excluded

FILES=('generation.json','artifact.html','manifest.json','source.manifest.json',
       'verification.json','runtime.json','lint.json','producer.mjs')
MAX_BYTES=2097152

def read_local(root,name):
    p=root/name
    if excluded(p) or p.resolve()!=p:raise ValueError('unsafe-frozen-path')
    fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as f:
        a=os.fstat(f.fileno())
        if not stat.S_ISREG(a.st_mode) or a.st_size>MAX_BYTES:raise ValueError('invalid-frozen-file')
        b=f.read(MAX_BYTES+1);z=os.fstat(f.fileno())
    if len(b)>MAX_BYTES or (a.st_size,a.st_mtime_ns)!=(z.st_size,z.st_mtime_ns):raise ValueError('changed-frozen-file')
    return b

def verify(root,out):
    receipt=json.loads(read_local(root,'freeze-receipt.json'))
    bearing='acceptance.json' in receipt.get('files',{})
    names=FILES+(('acceptance.json','acceptance-report.json','acceptance-runner.mjs','acceptance-checks.mjs','acceptance-scheme.mjs') if bearing else ())
    blobs={n:read_local(root,n) for n in names}
    if receipt.get('schemaVersion')!=1 or receipt.get('producerSHA256')!=PRODUCER or receipt.get('files')!={n:digest(b) for n,b in blobs.items()}:raise ValueError('freeze-identity-mismatch')
    if digest(blobs['producer.mjs'])!=PRODUCER:raise ValueError('producer-snapshot-mismatch')
    execution=receipt.get('execution',{})
    if execution.get('exit')!=0 or execution.get('execution')!='actual-pinned-cli' or execution.get('inputSHA256')!=digest(blobs['source.manifest.json']):raise ValueError('execution-receipt-mismatch')
    raw=blobs['generation.json'];data=json.loads(raw)
    if data.get('mode')!=('delivery' if bearing else 'draft'):raise ValueError('unexpected-pilot-mode')
    if bearing:
        from acceptance import PINS
        if any(digest(blobs['acceptance-'+k+'.mjs'])!=v for k,v in PINS.items()):raise ValueError('acceptance-source-snapshot-mismatch')
        if execution.get('acceptanceSHA256')!=digest(blobs['acceptance.json']):raise ValueError('acceptance-execution-receipt-mismatch')
    expected_observations=17 if bearing else 15
    r=qualify(data,digest(raw),blobs.get)
    assert r['state']=='qualified-reported' and len(r['observations'])==expected_observations and not r['performanceEligible']
    assert sum(o['outcome']=='pass' for o in r['observations'])==(15 if bearing else 13)
    assert r['observations'][-1]['outcome']=='unverified'
    results=[];marker='PRIVATE_FROZEN_CONTROL_'+'z'*100000
    def control(name,mutate,expected,reason=None):
        b=copy.copy(blobs);d=copy.deepcopy(data);mutate(d,b)
        raw=json.dumps(d).encode();b['generation.json']=raw
        packet=out/'controls'/name;packet.mkdir(parents=True,mode=0o700)
        for n,content in b.items():(packet/n).write_bytes(content)
        observed=qualify(d,digest(raw),b.get)
        assert observed['state']==expected
        if reason:assert observed['reason']==reason
        assert marker not in json.dumps(observed)
        if observed['observations']:assert not observed['performanceEligible'] and all(o['attemptId'] is None for o in observed['observations'])
        results.append({'control':name,'passed':True,'adapterState':observed['state'],'reason':observed.get('reason')})
    def verifier_change(fn):
        def mutate(d,b):
            v=json.loads(b['verification.json']);fn(v);b['verification.json']=json.dumps(v).encode();d['reports']['verification.json']=digest(b['verification.json'])
        return mutate
    control('stale-artifact',lambda d,b:b.update({'artifact.html':b['artifact.html']+b'changed'}),'rejected','artifact-identity-mismatch')
    control('stale-report',lambda d,b:b.update({'verification.json':b['verification.json']+b' '}),'rejected','report-identity-mismatch')
    control('omitted-criterion',verifier_change(lambda v:v['checks'].pop()),'rejected','missing-or-duplicate-criterion')
    control('duplicate-criterion',verifier_change(lambda v:v['checks'].append(v['checks'][0])),'rejected','missing-or-duplicate-criterion')
    control('malformed-criterion',verifier_change(lambda v:v['checks'][0].update(id=['invalid'])),'rejected','invalid-criterion-shape')
    def forged(d,b):
        d.update(passFlag=True,status='passed');d['delivery']={'status':'delivery-verified'};verifier_change(lambda v:v['checks'][0].update(status='fail'))(d,b)
    control('forged-completion',forged,'conflicting')
    control('wrong-verifier-input',verifier_change(lambda v:v['inputs']['artifact'].update(sha256='0'*64)),'rejected','verifier-input-mismatch')
    control('missing-gate',lambda d,b:d['stages'].pop(),'rejected','missing-or-duplicate-gate')
    control('unsupported-producer',lambda d,b:d.update(pipelineSHA256='0'*64),'unsupported')
    def private(d,b):
        d['stages'][0]['stdout']=marker;d['limitations']=[marker];verifier_change(lambda v:v.update(limitations=[marker]))(d,b)
    control('private-prose',private,'qualified-reported')
    control('reanalysis',lambda d,b:d.update(reanalysis='second-interpretation'),'qualified-reported')
    def report_change(name,fn):
        def mutate(d,b):
            v=json.loads(b[name]);fn(v);b[name]=json.dumps(v).encode();d['reports'][name]=digest(b[name])
        return mutate
    control('runtime-stale',lambda d,b:b.update({'runtime.json':b['runtime.json']+b' '}),'rejected','runtime-report-identity-mismatch')
    control('runtime-artifact-mismatch',report_change('runtime.json',lambda r:r['inputs'].update(artifact='0'*64)),'rejected','runtime-input-identity-mismatch')
    control('runtime-manifest-mismatch',report_change('runtime.json',lambda r:r['inputs'].update(manifest='0'*64)),'rejected','runtime-input-identity-mismatch')
    control('runtime-omitted-route',report_change('runtime.json',lambda r:r['cases'].pop()),'rejected','runtime-route-coverage-mismatch')
    control('runtime-duplicate-route',report_change('runtime.json',lambda r:r['cases'].append(r['cases'][0])),'rejected','runtime-route-coverage-mismatch')
    control('runtime-errors-forged-pass',report_change('runtime.json',lambda r:r['errors'].append(marker)),'conflicting')
    control('lint-stale',lambda d,b:b.update({'lint.json':b['lint.json']+b' '}),'rejected','lint-report-identity-mismatch')
    control('lint-artifact-mismatch',report_change('lint.json',lambda r:r['input'].update(sha256='0'*64)),'rejected','lint-input-identity-mismatch')
    control('lint-inspected-mismatch',report_change('lint.json',lambda r:r.update(inspectedHtmlSHA256='0'*64)),'rejected','lint-input-identity-mismatch')
    control('lint-missing-source',report_change('lint.json',lambda r:r['sources'].pop('scripts/lint-artifact.mjs')),'rejected','lint-source-identity-mismatch')
    control('lint-stale-source',report_change('lint.json',lambda r:r['sources'].update({'scripts/lint-artifact.mjs':'0'*64})),'rejected','lint-source-identity-mismatch')
    control('lint-unsupplied-policy',report_change('lint.json',lambda r:r.update(policy={'sha256':'0'*64})),'rejected','lint-policy-identity-mismatch')
    control('lint-error-forged-pass',report_change('lint.json',lambda r:r['findings'].append({'rule':'test','severity':'error','document':'root','selector':'','detail':marker})),'conflicting')
    control('lint-invalid-severity',report_change('lint.json',lambda r:r['findings'].append({'severity':[]})),'rejected','invalid-lint-findings')
    def new_private(d,b):
        private(d,b)
        report_change('runtime.json',lambda r:r.update(notes=marker))(d,b)
        report_change('lint.json',lambda r:r['findings'].append({'rule':'test','severity':'unverified','document':'root','selector':'','detail':marker}))(d,b)
        if bearing:report_change('acceptance-report.json',lambda r:r.update(limitations=[marker]))(d,b)
    control('runtime-lint-private-prose',new_private,'qualified-reported')
    if bearing:
        control('acceptance-spec-stale',lambda d,b:b.update({'acceptance.json':b['acceptance.json']+b' '}),'rejected','acceptance-spec-identity-mismatch')
        control('acceptance-report-stale',lambda d,b:b.update({'acceptance-report.json':b['acceptance-report.json']+b' '}),'rejected','acceptance-report-identity-mismatch')
        control('acceptance-missing-companion',lambda d,b:b.pop('acceptance.json'),'rejected','missing-or-unsafe-acceptance-companion')
        for key in ('html','acceptance'):
            control('acceptance-wrong-'+key,report_change('acceptance-report.json',lambda r,key=key:r['inputs'][key].update(sha256='0'*64)),'rejected','acceptance-input-identity-mismatch')
        for key in ('runner','checks','scheme'):
            control('acceptance-wrong-'+key,report_change('acceptance-report.json',lambda r,key=key:r['inputs'].update({key:'0'*64})),'rejected','acceptance-runner-identity-mismatch')
        control('acceptance-omitted-case',report_change('acceptance-report.json',lambda r:r['cases'].pop()),'rejected','acceptance-case-coverage-mismatch')
        control('acceptance-duplicate-case',report_change('acceptance-report.json',lambda r:r['cases'].append(r['cases'][0])),'rejected','acceptance-case-coverage-mismatch')
        control('acceptance-substituted-case',report_change('acceptance-report.json',lambda r:r['cases'][0]['coverage'].update(viewport='mobile' if r['cases'][0]['coverage']['viewport']=='desktop' else 'desktop')),'rejected','acceptance-case-identity-mismatch')
        control('acceptance-omitted-result',report_change('acceptance-report.json',lambda r:r['cases'][0]['results'].pop()),'rejected','acceptance-result-coverage-mismatch')
        control('acceptance-duplicate-result',report_change('acceptance-report.json',lambda r:r['cases'][0]['results'].append(r['cases'][0]['results'][0])),'rejected','acceptance-result-coverage-mismatch')
        control('acceptance-forged-failure-pass',report_change('acceptance-report.json',lambda r:r['cases'][0]['results'][0].update(status='assertion-failure',detail=marker)),'conflicting')
        control('acceptance-forged-not-applicable',report_change('acceptance-report.json',lambda r:r['cases'][0]['results'][0].update(status='not-applicable')),'rejected','acceptance-result-applicability-mismatch')
        control('acceptance-malformed-result',report_change('acceptance-report.json',lambda r:r['cases'][0]['results'][0].update(id=[])),'rejected','acceptance-result-coverage-mismatch')
        control('acceptance-generation-summary-conflict',lambda d,b:d['delivery'].update(status='delivery-incomplete'),'conflicting')
        control('acceptance-private-prose',report_change('acceptance-report.json',lambda r:r.update(limitations=[marker])),'qualified-reported')
    # Real scanner entry against the untouched freeze, not the mutated controls.
    dashboard=out/'dashboard';cli=subprocess.run([sys.executable,str(Path(__file__).with_name('scan.py')),'--root',str(root),'--skill','wireframe-review','--output',str(dashboard)],capture_output=True,timeout=30)
    (out/'scanner.stdout').write_bytes(cli.stdout);(out/'scanner.stderr').write_bytes(cli.stderr)
    assert cli.returncode==0 and len(cli.stdout)<4096
    summary=json.loads(cli.stdout);assert summary['measuredKpis']==0
    obs=json.loads((dashboard/'observations.json').read_bytes());assert len(obs['observations'])==expected_observations and not obs['performanceEligible']
    cards=json.loads((dashboard/'report-card.json').read_bytes());assert all(m['value'] is None for s in cards['skills'] for m in s['metrics'])
    # Private mutated packet also travels through the actual entry/renderer boundary.
    private_out=out/'private-dashboard';private_cli=subprocess.run([sys.executable,str(Path(__file__).with_name('scan.py')),'--root',str(out/'controls/runtime-lint-private-prose'),'--skill','wireframe-review','--output',str(private_out)],capture_output=True,timeout=30)
    assert private_cli.returncode==0 and marker.encode() not in private_cli.stdout+private_cli.stderr
    for n in ('observations.json','evidence-index.json','report-card.json','index.html'):assert marker not in (private_out/n).read_text()
    assert len(json.loads((private_out/'observations.json').read_bytes())['observations'])==expected_observations
    assert all(digest(read_local(root,n))==receipt['files'][n] for n in names)
    result={'schemaVersion':1,'scope':'actual-cli-presence-acceptance-compatibility' if bearing else 'actual-cli-minimal-draft-compatibility','adapterVersion':ADAPTER,'producerSHA256':PRODUCER,'freezeReceiptSHA256':digest(read_local(root,'freeze-receipt.json')),'baselineState':r['state'],'identityAudits':r['identityAudits'],'reportedObservations':expected_observations,'controls':results,'originalFrozenFilesUnchanged':True,'performanceEligible':False,'measuredKpis':0,'dashboard':str(dashboard/'index.html'),'limits':['One controlled official minimal draft; no task-efficacy or representative cohort claim.','Execution receipt records local provenance; hashes do not authenticate report truth.','No full dependency, acceptance, author-attempt or environment qualification.']}
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return {'status':'verified-presence-acceptance' if bearing else 'verified-minimal-draft','controlsPassed':len(results),'reportedObservations':expected_observations,'measuredKpis':0,'report':str(out/'verification.json'),'dashboard':str(dashboard/'index.html')}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frozen',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    root=Path(a.frozen).absolute();out=Path(a.output).absolute();skill_parent=Path(__file__).resolve().parents[2]
    if out.exists() or out.resolve()!=out or out==skill_parent or skill_parent in out.parents or out==root or root in out.parents:p.error('Use a fresh local output outside frozen evidence and installed skills')
    out.mkdir(parents=True,mode=0o700)
    try:summary=verify(root,out)
    except (OSError,ValueError,AssertionError,KeyError,TypeError,subprocess.SubprocessError):
        print(json.dumps({'status':'verification-failed','output':str(out),'rawEvidenceKeptLocal':True}));return 1
    print(json.dumps(summary));return 0
if __name__=='__main__':sys.exit(main())
