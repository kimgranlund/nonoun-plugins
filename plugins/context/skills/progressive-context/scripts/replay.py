#!/usr/bin/env python3
"""Offline authored route replay, not model execution or proof of submission."""
import argparse
import json
from pathlib import Path
from validate import validate, local, digest


def route(root, registry, case):
    check=validate(root,registry)
    result=dict(status='blocked',reason='',ledger=[],batches=[],stages=[],contextReads=0,contextBytes=0,
                coverage={},verificationBytes=0,validationBytes=check['validationBytes'],validationIssues=check['issues'])
    if not check['valid']:
        result['reason']='Invalid corpus contract';return result
    artifacts={a['id']:a for a in registry['artifacts']}
    aliases={alias:a['id'] for a in artifacts.values() for alias in a.get('aliases',[])}
    budget=case.get('budget',{})
    if not isinstance(budget,dict) or set(budget)-{'reads','bytes','itemBytes','batchBytes'}:raise ValueError('Unknown budget field')
    limits={'reads':8,'bytes':16384,'itemBytes':budget.get('bytes',16384),'batchBytes':budget.get('bytes',16384)}
    limits.update(budget)
    if any(type(v) is not int or v<0 for v in limits.values()):
        raise ValueError('Budget must contain nonnegative integers')
    stages=case.get('stages',[{k:case[k] for k in ('target','intent') if k in case}])
    if not isinstance(stages,list) or not stages or any(not isinstance(x,dict) for x in stages):
        raise ValueError('Expected nonempty stages array')
    deliveries=case.get('deliveries',{})
    if not isinstance(deliveries,dict):raise ValueError('Expected deliveries object')
    bodies={};directives={};visited=set()
    def resolve(stage):
        target=stage.get('target')
        if target is None:target=next((r['target'] for r in registry.get('routes',[]) if r['intent']==stage.get('intent')),None)
        return aliases.get(target,target)
    def load(identity, target, batch, stage):
        a=artifacts[identity]
        # Revisit relationships at every scope change, even if this source is reusable.
        for kind in ('governed_by','depends_on'):
            for parent in a.get('relationships',{}).get(kind,[]):
                if not load(parent,target,batch,stage):return False
        raw=local(root,a['location']).read_bytes()
        result['verificationBytes']+=len(raw)
        if digest(raw)!=a['sha256']:
            result['reason']='Source changed during replay: '+identity;return False
        if identity in visited:
            if identity not in stage['reused']:stage['reused'].append(identity)
            return True
        delivery=deliveries.get(identity,{})
        if not isinstance(delivery,dict):raise ValueError('Expected delivery object')
        mode=delivery.get('mode','full')
        if mode not in ('full','summary','pages','projection'):raise ValueError('Unknown delivery mode')
        payload=a['summary'].encode('utf-8') if mode=='summary' else raw
        if mode=='projection':
            value=json.loads(raw)
            fields=delivery.get('fields')
            records=delivery.get('records')
            if (fields is None)==(records is None):raise ValueError('Projection needs exactly one of fields or records')
            if fields is not None:
                if not isinstance(value,dict) or not isinstance(fields,list) or any(not isinstance(k,str) or k not in value for k in fields):raise ValueError('Invalid field projection')
                value={k:value[k] for k in fields}
            else:
                if not isinstance(value,list) or not isinstance(records,list) or any(type(k) is not int or k<0 or k>=len(value) for k in records):raise ValueError('Invalid record projection')
                value=[value[k] for k in records]
            payload=json.dumps(value,ensure_ascii=False).encode('utf-8')
        page_bytes=delivery.get('pageBytes',len(payload) or 1)
        max_pages=delivery.get('maxPages',1)
        if type(page_bytes) is not int or page_bytes<=0 or type(max_pages) is not int or max_pages<=0:
            raise ValueError('pageBytes and maxPages must be positive integers')
        if mode!='pages':page_bytes=len(payload) or 1;max_pages=1
        offset=0;collected=b''
        for page in range(max_pages):
            if result['contextReads']>=limits['reads']:
                result['reason']='Read budget exhausted; next required item: '+identity;break
            requested=payload[offset:offset+page_bytes]
            available=min(limits['itemBytes'],limits['batchBytes']-batch['bytes'],limits['bytes']-result['contextBytes'])
            returned=requested[:available]
            # Byte receipts are exact, including fragments of multibyte characters.
            result['contextReads']+=1;result['contextBytes']+=len(returned);batch['bytes']+=len(returned)
            end=offset+len(returned);complete=end==len(payload) and mode not in ('summary','projection')
            reasons=[]
            if len(returned)<len(requested):
                for key,left in [('itemBytes',limits['itemBytes']),('batchBytes',limits['batchBytes']-(batch['bytes']-len(returned))),('bytes',limits['bytes']-(result['contextBytes']-len(returned)))]:
                    if left<len(requested):reasons.append(key)
            result['ledger'].append(dict(id=identity,location=a['location'],revision=a['revision'],sha256=a['sha256'],
                available=True,requested=True,returned=bool(returned),submitted='unknown',retention='unknown',
                bytes=len(returned),requestedBytes=len(requested),sourceBytes=len(raw),returnedSha256=digest(returned),
                fields=delivery.get('fields'),records=delivery.get('records'),mode=mode,coverage='complete' if complete else mode if mode in ('summary','projection') else 'partial',
                byteRange=[offset,end],page=page+1,batch=batch['index'],stage=stage['index'],
                continuation=end if end<len(payload) else None,truncated=bool(reasons),budgetLimits=reasons,
                reason='target' if identity==target else 'required relationship'))
            collected+=returned;offset=end
            if reasons:
                result['reason']='Byte budget exhausted ('+', '.join(reasons)+'); next required item: '+identity;break
            if offset==len(payload):break
        coverage=mode if mode in ('summary','projection') else 'complete' if offset==len(payload) else 'partial'
        result['coverage'][identity]=coverage
        if mode not in ('summary','projection'):bodies[identity]=collected.decode('utf-8',errors='replace')
        if coverage!='complete':
            if not result['reason']:result['reason']='Incomplete required contract: '+identity+' ('+coverage+')'
            return False
        for key,value in a.get('directives',{}).items():
            if key in directives and directives[key][0]!=value:
                result['reason']='Conflicting directive '+key+' between '+directives[key][1]+' and '+identity;return False
            directives[key]=(value,identity)
        visited.add(identity);return True
    try:
        for index,spec in enumerate(stages):
            target=resolve(spec)
            stage=dict(index=index+1,target=target,reused=[]);result['stages'].append(stage)
            batch=dict(index=index+1,bytes=0);result['batches'].append(batch)
            if target not in artifacts:
                result['reason']='Target unresolved; provide an ID or a scoped entry';break
            if not load(target,target,batch,stage):break
        else:result.update(status='complete',reason='Declared required routes loaded')
    except (OSError,UnicodeError,ValueError) as e:result['reason']='Unavailable required source: '+str(e)
    result['returnedBodies']=bodies
    return result


def run(root, registry_path, suite_path):
    registry_bytes=Path(registry_path).read_bytes();suite_bytes=Path(suite_path).read_bytes()
    registry=json.loads(registry_bytes);suite=json.loads(suite_bytes)
    if not isinstance(suite,dict) or suite.get('version')!=1 or not isinstance(suite.get('cases'),list):raise ValueError('Invalid suite')
    ids=set();cases=[]
    for case in suite['cases']:
        if not isinstance(case,dict) or not isinstance(case.get('id'),str) or case['id'] in ids:raise ValueError('Missing or duplicate case ID')
        ids.add(case['id']);expected=case.get('acceptance')
        if not isinstance(expected,dict) or not isinstance(expected.get('required'),dict) or not expected['required']:raise ValueError('Acceptance requires independent source IDs and content clauses')
        for identity,clauses in expected['required'].items():
            if not isinstance(clauses,list) or not clauses or any(not isinstance(x,str) or not x for x in clauses):raise ValueError('Expected nonempty acceptance clause arrays')
        if 'forbidden' in expected and (not isinstance(expected['forbidden'],list) or any(not isinstance(x,str) for x in expected['forbidden'])):raise ValueError('Invalid forbidden IDs')
        if 'acceptablePaths' in expected and (not isinstance(expected['acceptablePaths'],list) or not expected['acceptablePaths'] or any(not isinstance(p,list) or any(not isinstance(x,str) for x in p) for p in expected['acceptablePaths'])):raise ValueError('Invalid acceptable paths')
        result=route(root,registry,case);bodies=result.pop('returnedBodies',{})
        path=list(dict.fromkeys(x['id'] for x in result['ledger']));failures=[]
        if result['status']!='complete':failures.append(result['reason'])
        for identity,clauses in expected['required'].items():
            if identity not in bodies:failures.append('Required source not returned: '+identity)
            else:
                for clause in clauses:
                    if clause not in bodies[identity]:failures.append('Missing acceptance clause in '+identity+': '+clause)
        for identity in expected.get('forbidden',[]):
            if identity in path:failures.append('Unrelated source returned: '+identity)
        if expected.get('acceptablePaths') and path not in expected['acceptablePaths']:failures.append('Route is not an accepted alternative')
        result.update(id=case['id'],passed=not failures,acceptanceFailures=failures)
        cases.append(result)
    return dict(version=2,kind='authored-route-replay',suiteSha256=digest(suite_bytes),registrySha256=digest(registry_bytes),
                cases=cases,passed=sum(c['passed'] for c in cases),total=len(cases),
                limits=['No model was run. This tests routing mechanics and literal acceptance clauses, not semantic correctness.',
                        'Returned bytes are not evidence of actual model submission, understanding, influence or retention.',
                        'Validation scans declared files and is accounted separately from context reads.'])


def compare(before,after):
    if before.get('kind')!='authored-route-replay' or after.get('kind')!='authored-route-replay':raise ValueError('Expected authored replay records')
    if before.get('version')!=after.get('version'):raise ValueError('Replay accounting version changed; rerun both inputs')
    if before['suiteSha256']!=after['suiteSha256']:raise ValueError('Acceptance suite changed; results are not comparable')
    a={c['id']:c for c in before['cases']};b={c['id']:c for c in after['cases']}
    if a.keys()!=b.keys():raise ValueError('Case IDs changed')
    changes=[]
    for identity,x in a.items():
        y=b[identity];changes.append(dict(id=identity,beforePassed=x['passed'],afterPassed=y['passed'],
            readDelta=y['contextReads']-x['contextReads'],byteDelta=y['contextBytes']-x['contextBytes'],
            efficiencyComparable=x['passed'] and y['passed']))
    return dict(changes=changes,regressions=sum(x['beforePassed'] and not x['afterPassed'] for x in changes),
                recovered=sum(not x['beforePassed'] and x['afterPassed'] for x in changes),
                limit='Authored replay changes only; no measured runtime or product improvement.')


def main():
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='compare':
        p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);a=p.parse_args(sys.argv[2:])
        result=compare(json.loads(a.before.read_text()),json.loads(a.after.read_text()));print(json.dumps(result,indent=2));return int(result['regressions']>0)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--registry',type=Path,required=True);p.add_argument('--suite',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=run(a.root,a.registry,a.suite);a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(passed=result['passed'],total=result['total'],out=str(a.out)),indent=2));return int(result['passed']!=result['total'])

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,TypeError,KeyError) as e:print('Error: '+str(e));raise SystemExit(2)
