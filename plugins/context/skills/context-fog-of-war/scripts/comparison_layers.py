"""Independent extraction, diagnosis and execution comparison layers."""
import json

TYPES=('context-engineering','product-repair','instrumentation','unspecified')

def contract(value, kind):
    if kind not in TYPES: raise ValueError('Invalid experiment type')
    value=value or {}
    if kind=='context-engineering':
        for key in ('contextIntervention','expectedBehavior','acceptanceCheck'):
            if not isinstance(value.get(key),str) or not value[key].strip():
                raise ValueError('Context experiment requires contract.'+key)
    return value

def identity(run):
    s=run.get('session',{})
    return s.get('traceSha256') or run.get('snapshot',{}).get('bundle',{}).get('inputHash')

def evidence(run):
    data=run.get('snapshot',{});paths={s['id']:s['path'] for s in data.get('sources',[])}
    returned={paths[x['sourceId']] for e in data.get('events',[]) for x in e.get('exposures',[]) if x.get('state') in ('read','partial') and x.get('sourceId') in paths}
    return {'returnedPaths':sorted(returned),'assessed':{c['detector']:c['assessed'] for c in run.get('coverage',[])},'warnings':run.get('adapter',{}).get('coverage',[]),'available':bool(data)}

def normalized_finding(f,run):
    if not f:return None
    lines={e['id']:e.get('evidence',{}).get('traceLine',e['id']) for e in run.get('snapshot',{}).get('events',[])}
    value=dict(f);value.pop('id',None)
    refs=[]
    for r in f.get('evidence',[]):
        r=dict(r)
        if 'eventId' in r:r['traceLine']=lines.get(r['eventId'],r['eventId']);r.pop('eventId')
        refs.append(r)
    value['evidence']=refs
    return value

def layers(before,after,result,experiment=None,mode='auto',experiment_type=None,experiment_contract=None,reassessments=None):
    from engineer import verify_refs
    left,right=identity(before),identity(after)
    same=bool(left and right and left==right)
    if mode=='extraction' and not same:raise ValueError('Extraction comparison requires identical recorded trace hashes')
    if mode=='execution' and same:raise ValueError('Identical frozen trace cannot be an execution improvement')
    mode='extraction' if same else ('execution' if left and right else 'unclassified') if mode=='auto' else mode
    kind=(experiment or {}).get('experimentType','unspecified')
    if experiment_type:
        if not experiment:raise ValueError('Experiment classification requires a registered experiment')
        if kind!='unspecified' and kind!=experiment_type:raise ValueError('Cannot override a typed experiment')
        kind=experiment_type
    if (experiment or {}).get('experimentType','unspecified')!='unspecified' and experiment_contract is not None and experiment_contract!=(experiment or {}).get('contract',{}):
        raise ValueError('Cannot override a registered experiment contract')
    chain=contract(experiment_contract or (experiment or {}).get('contract'),kind)
    a,b=evidence(before),evidence(after)
    evidence_change={'sameTrace':same,'baselineIdentity':left,'runIdentity':right,'before':a,'after':b,
        'addedReturnedPaths':sorted(set(b['returnedPaths'])-set(a['returnedPaths'])),
        'removedReturnedPaths':sorted(set(a['returnedPaths'])-set(b['returnedPaths'])),
        'assessmentDelta':{k:b['assessed'].get(k,0)-a['assessed'].get(k,0) for k in sorted(a['assessed'].keys()|b['assessed'].keys())},
        'interpretation':'Extraction coverage only; no new execution.' if same else 'Different executions or unknown provenance; count differences are not extraction improvements.'}
    old={f['id']:f for f in before['findings']};new={f['id']:f for f in after['findings']}
    reviews={}
    for review in reassessments or []:
        key=review.get('finding')
        if key not in old.keys()|new.keys() or key in reviews:raise ValueError('Unknown or duplicate reassessed finding')
        if review.get('status') not in ('strengthened','weakened','contradicted','unchanged','unassessable'):raise ValueError('Invalid reassessment status')
        if not review.get('reason','').strip() or not review.get('evidence'):raise ValueError('Reassessment requires rationale and exact evidence')
        verify_refs(after.get('snapshot',{'events':[]}),review['evidence'])
        reviews[key]=review
    changes=[]
    for key in sorted(old.keys()|new.keys()):
        x,y=old.get(key),new.get(key)
        if x and y:
            status='unchanged' if normalized_finding(x,before)==normalized_finding(y,after) else 'changed; interpretation needs review'
        elif y:status='newly observed'
        else:status='no longer observed; not automatically resolved'
        if y and y.get('state')=='unknown':status='unassessable'
        review=reviews.get(key)
        changes.append({'finding':key,'status':review['status'] if review else status,'basis':'cited reassessment' if review else 'record comparison',
            'before':x,'after':y,'actionBefore':(x or {}).get('action'),
            'actionAfter':review.get('recommendedAction',(y or x or {}).get('action')) if review else (y or x or {}).get('action'),
            'reassessment':review})
    reasons=list(result['limitations'][:-1])
    if mode=='execution' and not (left and right):reasons.append('Execution identity unavailable')
    if mode!='execution':reasons.append('Same-trace re-extraction, not a new execution' if same else 'Execution identity unavailable')
    outcome=dict(comparable=not reasons,limitations=reasons,experimentType=kind,contract=chain,
        classificationSource='comparison annotation for legacy experiment' if experiment_type and (experiment or {}).get('experimentType','unspecified')=='unspecified' else 'experiment record' if experiment else 'no experiment',
        measuredTransitions={k:{'before':before.get('assessment',{}).get(k,{'state':'unknown'}),'after':after.get('assessment',{}).get(k,{'state':'unknown'})} for k in ('mechanism','behavior','outcome')},
        workflowBefore=before.get('workflows',{}),workflowAfter=after.get('workflows',{}))
    if mode!='execution' or not (left and right):
        result.update(comparable=False,verdict='Outcome improvement not established.',costDelta={})
        for t in result['transitions']:t['state']='not assessable'
    outcome['verdict']=result['verdict']
    improved='Improvement observed' in result['verdict'] and not reasons
    outcome['contextEngineeringImprovement']=bool(improved and kind=='context-engineering' and chain)
    outcome['scope']='Context mechanism and scoped acceptance' if kind=='context-engineering' else 'Product acceptance only; no context-engineering claim' if kind=='product-repair' else 'Instrumentation only; no product or context-engineering claim' if kind=='instrumentation' else 'Unclassified legacy experiment; no context-engineering claim'
    result.update(comparisonMode=mode,evidenceChanges=evidence_change,diagnosisChanges=changes,outcomeChanges=outcome)
    result['limitations']=reasons+['One comparison does not establish general reliability or causal attribution.']
    if mode!='execution':result['nextAction']='Review changed evidence and interpretations; run a separate controlled execution to measure improvement.'
    return result
