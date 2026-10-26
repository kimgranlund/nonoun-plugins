"""Bounded reported acceptance identity audit; no evaluation or KPI calculation."""
import json,hashlib,re
from pathlib import Path
PINS=json.loads((Path(__file__).resolve().parents[1]/'references/acceptance-sources-v1.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def audit(data,artifact,read):
    def reject(reason):return {'reason':reason}
    supplied='acceptance' in data
    if not supplied:
        if data.get('mode')=='delivery' or 'acceptance-report.json' in data.get('reports',{}):return reject('missing-acceptance-declaration')
        return {'state':'not-supplied','conflict':False}
    spec_raw=read('acceptance.json');report_raw=read('acceptance-report.json')
    if spec_raw is None or report_raw is None:return reject('missing-or-unsafe-acceptance-companion')
    identity=data['acceptance']
    if not isinstance(identity,dict) or identity.get('sha256')!=sha(spec_raw):return reject('acceptance-spec-identity-mismatch')
    if data['reports'].get('acceptance-report.json')!=sha(report_raw):return reject('acceptance-report-identity-mismatch')
    try:spec=json.loads(spec_raw);r=json.loads(report_raw)
    except (ValueError,UnicodeError,RecursionError):return reject('invalid-acceptance-json')
    if not isinstance(spec,dict) or type(spec.get('version')) is not int or spec['version']!=2 or spec.get('surface') not in ('review','document'):return reject('unsupported-acceptance-spec')
    if not isinstance(r,dict) or type(r.get('version')) is not int or r['version']!=1 or r.get('specVersion')!=2:return reject('unsupported-acceptance-report')
    inputs=r.get('inputs')
    if not isinstance(inputs,dict) or any(not isinstance(inputs.get(k),dict) or inputs[k].get('sha256')!=v for k,v in [('html',artifact),('acceptance',sha(spec_raw))]):return reject('acceptance-input-identity-mismatch')
    if any(inputs.get(k)!=v for k,v in PINS.items()):return reject('acceptance-runner-identity-mismatch')
    reqs=spec.get('requirements');cases=spec.get('cases')
    def unique_ids(rows):return isinstance(rows,list) and bool(rows) and all(isinstance(x,dict) and isinstance(x.get('id'),str) and re.fullmatch('[a-z][a-z0-9-]*',x['id']) for x in rows) and len({x['id'] for x in rows})==len(rows)
    if not unique_ids(reqs) or not unique_ids(cases):return reject('invalid-acceptance-contract-identities')
    ids={x['id'] for x in reqs};case_ids={c['id'] for c in cases};prior=set()
    for req in reqs:
        if req.get('type') not in ('scenario','contrast','gap','width','menu','disabled','inventory') or not isinstance(req.get('description'),str) or not req['description']:return reject('invalid-acceptance-requirement')
        if 'required' in req and type(req['required']) is not bool:return reject('invalid-acceptance-required-flag')
        for key,valid in [('caseIds',case_ids),('dependsOn',prior)]:
            if key in req and (not isinstance(req[key],list) or (key=='caseIds' and not req[key]) or any(not isinstance(x,str) or x not in valid for x in req[key]) or len(set(req[key]))!=len(req[key])):return reject('invalid-acceptance-applicability')
        if req.get('execution') not in (None,'unexecuted') or (req.get('execution')=='unexecuted' and (not isinstance(req.get('reason'),str) or not req['reason'])):return reject('invalid-acceptance-execution')
        prior.add(req['id'])
    rows=r.get('cases')
    if not unique_ids(rows) or {c['id'] for c in rows}!=case_ids:return reject('acceptance-case-coverage-mismatch')
    required=[x for x in reqs if x.get('required',True)];statuses=[];conflict=False;missing=[]
    allowed=('pass','not-applicable','unexecuted','blocked','fail','assertion-failure','setup-error','unsupported','harness-error','application-exception')
    for row in rows:
        errors=row.get('errors');results=row.get('results');coverage=row.get('coverage');case=next(c for c in cases if c['id']==row['id'])
        if not isinstance(errors,list) or any(not isinstance(e,str) for e in errors):return reject('invalid-acceptance-case-errors')
        if not isinstance(coverage,dict) or {k:v for k,v in coverage.items() if k!='actualSchemes'}!=case:return reject('acceptance-case-identity-mismatch')
        if not unique_ids(results) or {x['id'] for x in results}!=ids or any(x.get('status') not in allowed for x in results):return reject('acceptance-result-coverage-mismatch')
        by_id={x['id']:x for x in results}
        for req in reqs:
            status=by_id[req['id']]['status'];applies='caseIds' not in req or case['id'] in req['caseIds']
            if (status=='not-applicable')!= (not applies):return reject('acceptance-result-applicability-mismatch')
            if applies and req.get('execution')=='unexecuted' and status!='unexecuted':conflict=True
            if applies and status=='pass' and any(by_id[x]['status']!='pass' for x in req.get('dependsOn',[])):conflict=True
            if req in required and applies:statuses.append('unexecuted' if req.get('execution')=='unexecuted' else 'blocked' if status=='pass' and any(by_id[x]['status']!='pass' for x in req.get('dependsOn',[])) else status)
        if errors or any(x['status']=='application-exception' for x in results):statuses.append('application-exception')
    for req in required:
        if not any(x['id']==req['id'] and x['status']!='not-applicable' for row in rows for x in row['results']):missing.append(req['id'])
    if r.get('unexecutedRequirements')!=missing:return reject('acceptance-missing-requirement-mismatch')
    reported_pass=not missing and all(not row['errors'] and not any(x['status']=='application-exception' for x in row['results']) and all(next(x['status'] for x in row['results'] if x['id']==q['id']) in ('pass','not-applicable') for q in required) for row in rows)
    if type(r.get('pass')) is not bool or r.get('deliveryStatus') not in ('delivery-verified','delivery-incomplete'):return reject('invalid-acceptance-summary')
    stage=next(x for x in data['stages'] if x['name']=='task-acceptance')
    conflict=conflict or r['pass']!=reported_pass or (r['deliveryStatus']=='delivery-verified')!=reported_pass or (stage['exit']==0)!=reported_pass
    delivery=data.get('delivery')
    if not isinstance(delivery,dict) or delivery.get('status') not in ('delivery-verified','delivery-incomplete'):return reject('invalid-generation-acceptance-summary')
    conflict=conflict or (delivery['status']=='delivery-verified')!=reported_pass
    outcome='fail' if any(s in ('fail','assertion-failure','application-exception') for s in statuses) else 'pass' if statuses and all(s=='pass' for s in statuses) and not missing else 'unverified'
    return {'state':'subjects-and-pinned-runner-matched','conflict':conflict,'outcome':outcome,'reportSHA256':sha(report_raw),'specSHA256':sha(spec_raw),'caseCount':len(rows),'requiredResultCount':len(statuses),'independence':'unverified','taskCompleteness':'unverified','executionReproduced':False}
