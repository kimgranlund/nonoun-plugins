"""Reported observations only. No discovered code execution or KPI aggregation."""
import hashlib, json, re
from pathlib import Path
from acceptance import audit as audit_acceptance
LINT_SOURCES=json.loads((Path(__file__).resolve().parents[1]/'references/lint-sources-v1.json').read_text())

PRODUCER = 'b319038a6e92f11ed8c81d0a3260c0daaf3cbbedae5b4cdafefc6642186c0bcb'
LINT_SOURCES_V2=json.loads((Path(__file__).resolve().parents[1]/'references/lint-sources-v2.json').read_text())
ADAPTER = 'wireframe-generation/1.2.0'
STATIC = ('executable-syntax','manifest','artifact-binding','foundation-binding',
          'token-index-freshness','kit-binding','token-references')
STAGES = ('compile','artifact-verification','runtime-startup','preventive-lint')
def digest(raw): return hashlib.sha256(raw).hexdigest()
def is_hash(x): return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) is not None

def qualify(data, evidence_hash, read):
    """read accepts fixed sibling names only, with collector privacy/read budgets."""
    if not isinstance(data,dict) or data.get('pipelineSHA256') != PRODUCER:
        return {'adapter':None,'state':'unsupported','observations':[]}
    def reject(code): return {'adapter':ADAPTER,'state':'rejected','reason':code,'observations':[]}
    if data.get('mode') not in ('draft','delivery') or not isinstance(data.get('stages'),list):
        return reject('invalid-generation-shape')
    stages=data['stages']; expected=STAGES+(('task-acceptance',) if 'acceptance' in data else ())
    if len(stages)!=len(expected) or [s.get('name') for s in stages if isinstance(s,dict)]!=list(expected):
        return reject('missing-or-duplicate-gate')
    if any(type(s.get('exit')) is not int or s.get('signal') is not None for s in stages):
        return reject('invalid-gate-result')
    if not is_hash(data.get('artifactSHA256')) or not isinstance(data.get('reports'),dict):
        return reject('missing-artifact-or-report-identity')
    names=['artifact.html','manifest.json','source.manifest.json','verification.json','runtime.json','lint.json']
    blobs={n:read(n) for n in names}
    if any(v is None for v in blobs.values()):return reject('missing-or-unsafe-companion')
    ah=digest(blobs['artifact.html']); mh=digest(blobs['manifest.json'])
    if ah!=data['artifactSHA256']:return reject('artifact-identity-mismatch')
    source=data.get('source');kit=data.get('uiKit')
    if not isinstance(source,dict) or source.get('sha256')!=digest(blobs['source.manifest.json']):
        return reject('source-identity-mismatch')
    if not isinstance(kit,dict) or kit.get('packageId')!='local.base-ui' or not is_hash(kit.get('contentSHA256')):
        return reject('missing-dependency-identity')
    if data['reports'].get('verification.json')!=digest(blobs['verification.json']):
        return reject('report-identity-mismatch')
    try: v=json.loads(blobs['verification.json'])
    except (ValueError,UnicodeError,RecursionError):return reject('invalid-verification')
    if not isinstance(v,dict) or v.get('schemaVersion')!=1 or v.get('generatedBy')!='verify-artifact/1':return reject('unsupported-verifier')
    inputs=v.get('inputs',{})
    if not isinstance(inputs,dict) or any(not isinstance(inputs.get(k),dict) or inputs[k].get('sha256')!=h for k,h in [('artifact',ah),('manifest',mh)]):
        return reject('verifier-input-mismatch')
    checks=v.get('checks')
    if isinstance(checks,list) and any(not isinstance(c,dict) or not isinstance(c.get('id'),str) for c in checks):
        return reject('invalid-criterion-shape')
    if not isinstance(checks,list) or len(checks)!=len(STATIC) or {c['id'] for c in checks}!=set(STATIC):
        return reject('missing-or-duplicate-criterion')
    if any(c.get('status') not in ('pass','fail') for c in checks):return reject('invalid-criterion-outcome')
    # Audit fixed report bytes and their declared subjects, not filesystem paths in reports.
    for name in ('runtime.json','lint.json'):
        if data['reports'].get(name)!=digest(blobs[name]):return reject(name[:-5]+'-report-identity-mismatch')
    try:
        runtime=json.loads(blobs['runtime.json']);lint=json.loads(blobs['lint.json']);manifest=json.loads(blobs['manifest.json'])
    except (ValueError,UnicodeError,RecursionError):return reject('invalid-runtime-or-lint-json')
    if not isinstance(runtime,dict) or runtime.get('status') not in ('pass','fail') or not isinstance(runtime.get('errors'),list) or any(not isinstance(e,str) for e in runtime['errors']):return reject('invalid-runtime-shape')
    if runtime.get('inputs')!={'artifact':ah,'manifest':mh}:return reject('runtime-input-identity-mismatch')
    cases=runtime.get('cases')
    if not isinstance(cases,list) or not cases or any(not isinstance(c,dict) or set(c)!={'unit','variant','viewport'} or any(not isinstance(c[k],str) for k in c) for c in cases):return reject('invalid-runtime-cases')
    if not isinstance(manifest,dict) or not isinstance(manifest.get('units'),list) or not manifest['units']:return reject('invalid-runtime-manifest')
    units=manifest['units']
    if any(not isinstance(u,dict) or not isinstance(u.get('id'),str) or not isinstance(u.get('variants'),list) or not u['variants'] or any(not isinstance(v,dict) or not isinstance(v.get('id'),str) for v in u['variants']) for u in units):return reject('invalid-runtime-manifest')
    pages=[u for u in units if u.get('kind')=='page']
    expected_routes=[(u['id'],v['id'],w) for u in (pages or units) for v in u['variants'] for w in ('desktop','mobile')]
    routes=[(c['unit'],c['variant'],c['viewport']) for c in cases]
    if len(set(expected_routes))!=len(expected_routes) or len(set(routes))!=len(routes) or set(routes)!=set(expected_routes):return reject('runtime-route-coverage-mismatch')
    if not isinstance(lint,dict) or not isinstance(lint.get('input'),dict) or lint['input'].get('sha256')!=ah or lint.get('inspectedHtmlSHA256')!=ah:return reject('lint-input-identity-mismatch')
    lint_profile=next((name for name,profile in [('v1',LINT_SOURCES),('v2',LINT_SOURCES_V2)] if lint.get('sources')==profile),None)
    if lint_profile is None:return reject('lint-source-identity-mismatch')
    if lint.get('temporaryBuild') is not None:return reject('unsupported-lint-temporary-build')
    if 'policy' in data:
        policy=data['policy'];reported=lint.get('policy');policy_raw=read('lint-policy.json')
        if not isinstance(policy,dict) or not isinstance(reported,dict) or policy_raw is None or not is_hash(policy.get('sha256')) or digest(policy_raw)!=policy['sha256'] or reported.get('sha256')!=policy['sha256']:return reject('lint-policy-identity-mismatch')
    elif lint.get('policy') is not None:return reject('lint-policy-identity-mismatch')
    findings=lint.get('findings');documents=lint.get('documents')
    if not isinstance(documents,list) or not documents or any(not isinstance(d,str) for d in documents) or len(set(documents))!=len(documents):return reject('invalid-lint-documents')
    if not isinstance(findings,list) or any(not isinstance(f,dict) or f.get('severity') not in ('error','warning','unverified') or any(not isinstance(f.get(k),str) for k in ('rule','document','selector','detail')) for f in findings):return reject('invalid-lint-findings')
    runtime_pass=not runtime['errors'];lint_pass=not any(f['severity']=='error' for f in findings)
    # No pass inferred from completion flags. Gate/criterion contradictions survive as conflicts.
    conflict=(stages[1]['exit']==0)!=all(c['status']=='pass' for c in checks)
    conflict=conflict or ((runtime['status']=='pass')!=runtime_pass) or ((stages[2]['exit']==0)!=runtime_pass) or ((stages[3]['exit']==0)!=lint_pass)
    acceptance=audit_acceptance(data,ah,read)
    if 'reason' in acceptance:return reject(acceptance['reason'])
    conflict=conflict or acceptance['conflict']
    observations=[]
    def add(criterion,outcome,pointer,h=evidence_hash):
        o={'schemaVersion':1,'skillId':'wireframe-review','metricContractVersion':1,
           'adapterVersion':ADAPTER,'producerSHA256':PRODUCER,'skillSourceIdentity':None,
           'dependencyIdentity':{'packageId':'local.base-ui','contentSHA256':kit['contentSHA256'],'origin':'reported'},
           'attemptId':None,'artifactId':ah,'phase':'generation','predecessor':None,
           'criterionId':criterion,'outcome':outcome,'evidence':{'sha256':h,'pointer':pointer},
           'origin':'reported','taskCohort':None,'model':None,'effort':None,'environment':None,
           'observationTime':None,'applicability':'current-source-transfer-unverified',
           'acceptedLimitations':'retained-in-source-not-promoted-to-pass',
           'missingData':['author-attempt-identity','full-skill-source-identity','task-cohort','environment','observation-time'],
           'telemetry':None}
        validate_observation(o);observations.append(o)
    add('reported-delivery-mode','not-applicable' if data['mode']=='draft' else 'unverified','/mode')
    for i,s in enumerate(stages):add('reported-gate:'+s['name'],'pass' if s['exit']==0 else 'fail',f'/stages/{i}/exit')
    for i,c in enumerate(checks):add('reported-static:'+c['id'],c['status'],f'/checks/{i}/status',digest(blobs['verification.json']))
    add('reported-runtime:startup','pass' if runtime_pass else 'fail','/errors',digest(blobs['runtime.json']))
    add('reported-lint:error-gate','pass' if lint_pass else 'fail','/findings',digest(blobs['lint.json']))
    if acceptance['state']!='not-supplied':add('reported-acceptance:required-cases',acceptance['outcome'],'/cases',acceptance['reportSHA256'])
    add('delivery-integrity','unverified','/artifactSHA256')
    return {'adapter':ADAPTER,'state':'conflicting' if conflict else 'qualified-reported',
            'reason':'no-author-attempt-or-full-delivery-audit','observations':observations,
            'performanceEligible':False,'reportedMode':data['mode'],
            'identityAudits':{'acceptance':{k:v for k,v in acceptance.items() if k not in ('conflict','outcome')},'runtime':{'state':'artifact-and-manifest-matched','caseCount':len(cases),'errorCount':len(runtime['errors']),'runnerIdentity':'unavailable-in-report'},
            'lint':{'state':'artifact-and-pinned-sources-matched','sourceCount':len(LINT_SOURCES),'sourceProfile':lint_profile,'documentCount':len(documents),'policyIdentity':'matched' if 'policy' in data else 'no-supplied-policy','findingCounts':{severity:sum(f['severity']==severity for f in findings) for severity in ('error','warning','unverified')}},'origin':'reported','executionReproduced':False}}

def validate_observation(o):
    required={'schemaVersion','skillId','metricContractVersion','adapterVersion','producerSHA256','skillSourceIdentity','dependencyIdentity','attemptId','artifactId','phase','predecessor','criterionId','outcome','evidence','origin','taskCohort','model','effort','environment','observationTime','applicability','acceptedLimitations','missingData','telemetry'}
    if set(o)!=required or o['schemaVersion']!=1 or o['skillId']!='wireframe-review' or o['origin']!='reported' or o['phase']!='generation':raise ValueError('invalid-observation-schema')
    if o['outcome'] not in ('pass','fail','unverified','not-applicable') or not is_hash(o['artifactId']) or not is_hash(o['evidence']['sha256']) or not o['evidence']['pointer'].startswith('/'):raise ValueError('invalid-observation-provenance')
    if o['attemptId'] is not None or o['skillSourceIdentity'] is not None:raise ValueError('unsupported-attempt-attribution')

    allowed={'reported-delivery-mode','delivery-integrity','reported-runtime:startup','reported-lint:error-gate','reported-acceptance:required-cases'}|{'reported-gate:'+c for c in STAGES+('task-acceptance',)}|{'reported-static:'+c for c in STATIC}
    if o['criterionId'] not in allowed or o['adapterVersion']!=ADAPTER or o['producerSHA256']!=PRODUCER or o['metricContractVersion']!=1:raise ValueError('unsupported-observation-contract')
    if set(o['evidence'])!={'sha256','pointer'} or not re.fullmatch(r'/(mode|artifactSHA256|errors|findings|cases|stages/[0-4]/exit|checks/[0-6]/status)',o['evidence']['pointer']):raise ValueError('invalid-selection')
    dep=o['dependencyIdentity']
    if set(dep)!={'packageId','contentSHA256','origin'} or dep['packageId']!='local.base-ui' or dep['origin']!='reported' or not is_hash(dep['contentSHA256']):raise ValueError('invalid-dependency')
    if any(o[k] is not None for k in ('attemptId','skillSourceIdentity','predecessor','taskCohort','model','effort','environment','observationTime','telemetry')):raise ValueError('unsupported-attribution')
    if o['applicability']!='current-source-transfer-unverified' or o['acceptedLimitations']!='retained-in-source-not-promoted-to-pass' or o['missingData']!=['author-attempt-identity','full-skill-source-identity','task-cohort','environment','observation-time']:raise ValueError('invalid-coverage-state')
    if o['criterionId']=='delivery-integrity' and o['outcome']!='unverified':raise ValueError('unsupported-performance-claim')
