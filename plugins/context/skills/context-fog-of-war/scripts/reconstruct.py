"""Reconstruct explicit request relationships; no temporal causal guesses."""
import json
from collections import defaultdict
from bundle import hash_value,VERSION

CATALOG=[
 dict(id='retrieved-not-submitted',name='Retrieved content omitted',requires='Explicit target request, complete included-chunk identity list and successful retrieval',rule='Returned chunk identity absent from complete target assembly',alternatives=['Intentional relevance filtering','Incorrect mapping semantics'],guidance='Inspect the request assembler and relevance policy; preserve required retrieved chunks through assembly.',verification='Repeat the same task; verify required chunks reach the request and unchanged acceptance checks pass.'),
 dict(id='tool-result-not-propagated',name='Tool result omitted',requires='Successful tool result, explicit target request and complete tool-result identity list',rule='Result identity absent from complete target assembly',alternatives=['Intentional suppression','Incorrect target-request mapping'],guidance='Inspect tool-result serialization and next-request assembly; propagate required results with their IDs.',verification='Verify the result reaches the specified request and the task outcome passes unchanged checks.'),
 dict(id='stop-at-cap',name='Stopped at the output token cap',requires='One model_request record with outputTokens and maxTokens and no recorded stop reason',rule='Output tokens reached the request max_tokens; the reply was likely cut at the cap',alternatives=['The reply ended exactly at the cap by chance','The recorded usage counts a different response than this request'],guidance='Record the provider stop reason; raise max_tokens or shorten the expected output if the reply needs more room.',verification='Rerun the request with the stop reason recorded; confirm it is not max_tokens and the acceptance checks pass.'),
 dict(id='evaluation-artifact-mismatch',name='Evaluation artifact mismatch',requires='Explicit delivery identity and comparable SHA256 hashes',rule='Evaluation hash differs from delivered hash',alternatives=['Intended evaluation of an intermediate artifact','Incorrect delivery correlation'],guidance='Evaluate the final delivered bytes; bind the acceptance receipt to that artifact hash.',verification='Confirm evaluation and delivered SHA256 match, then run the acceptance checks on those bytes.')]

def reconstruct(bundle,repo=None):
    from fog import inventory,validate
    from diagnostics import diagnose
    paths,mode,revision=inventory(repo) if repo else ([], 'No repository inventory supplied','unknown')
    data=dict(schemaVersion=2,session=dict(title='Web-chat session bundle',trace='bundle',traceSha256=bundle['fingerprint'],repo=repo.name if repo else 'bundle',revision=revision,host='bundle',adapterVersion=VERSION),coverage=dict(inventory=mode,warnings=['Bundle events are ordered by file/record position; only explicit identities establish relationships.','Mapping semantics are supplied interpretations, not automatically verified.']+bundle['issues']),sources=[],events=[],links=[],decisions=[],guidanceEdges=[],findings=[],contextRecords=[])
    ids={};dedup={};records=[];conflicts=set()
    def source(path):
        if path not in ids:ids[path]='s'+str(len(ids)+1);data['sources'].append(dict(id=ids[path],path=path,inventoried=path in paths))
        return ids[path]
    for path in paths:source(path)
    for record in bundle['records']:
        n=record['normalized'];identity=(n['conversationId'],n.get('eventId')) if isinstance(n.get('eventId'),str) else None
        if identity and identity in dedup:
            old=dedup[identity]
            if old['normalized']==n:
                old['provenance'].append(record['provenance']);continue
            conflicts.add(identity)
        e=dict(id='e'+str(len(data['events'])+1),seq=len(data['events']),kind='context' if n['eventType']=='model_request' else 'result',label=n['eventType']+' · '+str(n.get('requestId',n.get('targetRequestId',''))),actor='web-harness',timestamp=n.get('timestamp','') if isinstance(n.get('timestamp',''),str) else '',evidence=dict(traceLine=record['provenance']['line'],text=json.dumps(dict(normalized=n,original=record['original'],provenance=record['provenance']),ensure_ascii=False,indent=2)),exposures=[])
        data['events'].append(e)
        item=dict(eventId=e['id'],normalized=n,provenance=[record['provenance']]);records.append(item)
        if identity:dedup[identity]=item
        for key,state in [('chunkIds','discovered'),('includedChunkIds','discovered')]:
            for chunk in n.get(key,[]) if isinstance(n.get(key),list) else []:
                if not isinstance(chunk,str):continue
                sid=source('chunk://'+n['conversationId']+'/'+chunk)
                e['exposures'].append(dict(sourceId=sid,state=state,basis='Recorded chunk identity; content bytes not established'))
                if key=='includedChunkIds' and n['eventType']=='model_request':data['contextRecords'].append(dict(sourceId=sid,eventId=e['id'],status='included',evidence=dict(eventId=e['id'],excerpt=e['evidence']['text'])))
    for item in records:
        n=item['normalized'];item['ambiguous']=(n['conversationId'],n.get('eventId')) in conflicts
    if conflicts:data['coverage']['warnings'].append('Conflicting duplicate event identities; affected evidence excluded from joins.')
    data['bundle']=dict(version=VERSION,mappingHash=bundle['mappingHash'],fingerprint=bundle['fingerprint'],records=records,inventory=bundle['inventory'],manifest=bundle['manifest'])
    requests=defaultdict(list);deliveries=defaultdict(list);streams=defaultdict(list);operations=defaultdict(list)
    for r in records:
        n=r['normalized'];conv=n['conversationId']
        if n['eventType']=='model_request' and isinstance(n.get('requestId'),str):requests[(conv,n['requestId'])].append(r)
        if n['eventType']=='delivery' and isinstance(n.get('deliveryId'),str):deliveries[(conv,n['deliveryId'])].append(r)
        if n['eventType']=='stream_chunk' and all(isinstance(n.get(k),str) for k in ('requestId','streamId')):streams[(conv,n['requestId'],n['streamId'])].append(r)
        if n['eventType']=='model_request' and isinstance(n.get('operationId'),str):operations[(conv,n['operationId'])].append(r['eventId'])
    for r in records:
        n=r['normalized'];target=requests.get((n['conversationId'],n.get('targetRequestId'))) if isinstance(n.get('targetRequestId'),str) else None
        if n['eventType']=='evaluation' and isinstance(n.get('targetDeliveryId'),str):target=deliveries.get((n['conversationId'],n['targetDeliveryId']))
        if target and len(target)==1 and not r['ambiguous'] and not target[0]['ambiguous']:
            data['links'].append({'from':r['eventId'],'to':target[0]['eventId'],'kind':'recorded','reason':'Explicit target identity; not temporal ordering or proof of influence'})
    assembled=[]
    for key,parts in streams.items():
        counts={p['normalized'].get('totalChunks') for p in parts if isinstance(p['normalized'].get('totalChunks'),int)}
        total=next(iter(counts)) if len(counts)==1 else None
        sequence={p['normalized'].get('sequence'):p['normalized'].get('text') for p in parts if isinstance(p['normalized'].get('sequence'),int)}
        complete=isinstance(total,int) and 0<total<=10000 and len(sequence)==len(parts)==total and set(sequence)==set(range(total)) and all(isinstance(v,str) for v in sequence.values()) and all(p['normalized'].get('totalChunks')==total for p in parts) and not any(p['ambiguous'] for p in parts)
        assembled.append(dict(conversationId=key[0],requestId=key[1],streamId=key[2],complete=complete,text=''.join(sequence[i] for i in range(total)) if complete else None,eventIds=[p['eventId'] for p in parts]))
    data['bundle'].update(streams=assembled,operations=[dict(conversationId=k[0],operationId=k[1],eventIds=v) for k,v in operations.items()])
    return validate(diagnose(data))

def signals(data,coverage=None):
    """Return detector candidates and eligible pair counts, abstaining on ambiguity."""
    records=data.get('bundle',{}).get('records',[]);by={e['id']:e for e in data['events']};findings=[];counts={c['id']:0 for c in CATALOG};lookup={c['id']:c for c in CATALOG}
    requests=defaultdict(list);deliveries=defaultdict(list)
    for r in records:
        n=r['normalized']
        if json.loads(by[r['eventId']]['evidence']['text'])['normalized']!=n:raise ValueError('Bundle normalization does not match cited event')
        key=n.get('requestId') if n['eventType']=='model_request' else n.get('deliveryId') if n['eventType']=='delivery' else None
        if isinstance(key,str):(requests if n['eventType']=='model_request' else deliveries)[(n['conversationId'],key)].append(r)
    def emit(kind,r,target,detail):
        c=lookup[kind];evidence=[dict(eventId=x['eventId'],traceLine=by[x['eventId']]['evidence']['traceLine'],excerpt=by[x['eventId']]['evidence']['text']) for x in (r,target)]
        findings.append(dict(id='bundle-'+str(len(findings)+1),detector=kind,title=c['name'],observation=detail,hypothesis='This may explain a routing or acceptance failure; intent and impact require task-specific assessment.',confidence='high',status='candidate',evidence=evidence,eventIds=[x['eventId'] for x in (r,target)],sourceIds=[],alternatives=c['alternatives'],guidance=c['guidance'],verification=c['verification'],metrics={}))
    def strings(v):return isinstance(v,list) and all(isinstance(x,str) for x in v)
    records_stop=any(r['normalized']['eventType']=='model_request' and r['normalized'].get('stopReason') is not None for r in records)
    for r in records:
        n=r['normalized'];typ=n['eventType'];conv=n['conversationId']
        if typ=='model_request':
            if not (isinstance(n.get('outputTokens'),int) and isinstance(n.get('maxTokens'),int) and n['maxTokens']>0):continue
            # A stop reason, when recorded, is the direct evidence; usage at the cap stands in only where the trace records none.
            if n.get('stopReason') is not None:
                if coverage:coverage.exclude('stop-at-cap','Stop reason recorded; it is the direct evidence')
                continue
            def cap_gap(reason,request):
                if coverage:coverage.gap('stop-at-cap',reason,request,by[r['eventId']])
            if r.get('ambiguous') or len(requests.get((conv,n.get('requestId')),[]))>1:
                cap_gap('Duplicate or ambiguous request identity','Map one record per request attempt, or an attempt-specific requestId.');continue
            if records_stop:
                cap_gap('Stop reason missing on this request although the trace records it elsewhere','Map stopReason for every request; a missing one is a mapping gap, not a cut reply.');continue
            counts['stop-at-cap']+=1
            if coverage:coverage.eligible('stop-at-cap')
            if n['outputTokens']>=n['maxTokens']:
                c=lookup['stop-at-cap'];evidence=[dict(eventId=r['eventId'],traceLine=by[r['eventId']]['evidence']['traceLine'],excerpt=by[r['eventId']]['evidence']['text'])]
                findings.append(dict(id='bundle-'+str(len(findings)+1),detector='stop-at-cap',title=c['name'],observation='outputTokens %d reached maxTokens %d and no stop reason is recorded.'%(n['outputTokens'],n['maxTokens']),hypothesis='The reply was likely cut at the token cap; a truncated payload or answer may explain the failure.',confidence='medium',status='candidate',evidence=evidence,eventIds=[r['eventId']],sourceIds=[],alternatives=c['alternatives'],guidance=c['guidance'],verification=c['verification'],metrics={'outputTokens':n['outputTokens'],'maxTokens':n['maxTokens']}))
            continue
        detector={'retrieval':'retrieved-not-submitted','tool_result':'tool-result-not-propagated','evaluation':'evaluation-artifact-mismatch'}.get(typ)
        if not detector:continue
        def gap(reason,request):
            if coverage:coverage.gap(detector,reason,request,by[r['eventId']])
        if r.get('ambiguous'):
            gap('Ambiguous source record','Disambiguate this record identity in the mapping manifest.');continue
        if typ in ('retrieval','tool_result') and n.get('success') is False:
            if coverage:coverage.exclude(detector,'Explicitly unsuccessful return; success-only detector does not apply')
            continue
        target_id=n.get('targetDeliveryId') if typ=='evaluation' else n.get('targetRequestId')
        if not isinstance(target_id,str):
            gap('Missing explicit target link','Record targetDeliveryId.' if typ=='evaluation' else 'Record targetRequestId for this result.');continue
        targets=(deliveries if typ=='evaluation' else requests).get((conv,target_id),[])
        if len(targets)!=1 or targets[0].get('ambiguous'):
            gap('Target is absent or ambiguous','Include exactly one unambiguous target record with the matching conversation and request/delivery ID.');continue
        target=targets[0];t=target['normalized']
        if typ in ('retrieval','tool_result'):
            if n.get('success') is not True:
                gap('Return success is unknown','Record explicit success for this retrieval or tool result.');continue
            if t.get('complete') is not True:
                gap('Target assembly is not declared complete','Record complete=true only for an exhaustive target request identity list.');continue
            if typ=='retrieval' and strings(n.get('chunkIds')) and strings(t.get('includedChunkIds')):
                kind='retrieved-not-submitted';counts[kind]+=1
                if coverage:coverage.eligible(kind)
                missing=sorted(set(n['chunkIds'])-set(t['includedChunkIds']))
                if missing:emit(kind,r,target,'Returned chunks absent from the complete target request identity list: '+', '.join(missing))
            elif typ=='tool_result' and isinstance(n.get('resultId'),str) and strings(t.get('toolResultIds')):
                kind='tool-result-not-propagated';counts[kind]+=1
                if coverage:coverage.eligible(kind)
                if n['resultId'] not in t['toolResultIds']:emit(kind,r,target,'Successful tool result '+n['resultId']+' absent from the complete target request identity list.')
            else:gap('Required identity list is missing or malformed','Record chunkIds and includedChunkIds as string arrays.' if typ=='retrieval' else 'Record resultId and toolResultIds as a string and string array.')
        elif typ=='evaluation':
            import re
            if all(isinstance(x,str) and re.fullmatch('[0-9a-fA-F]{64}',x) for x in (n.get('artifactHash'),t.get('artifactHash'))):
                kind='evaluation-artifact-mismatch';counts[kind]+=1
                if coverage:coverage.eligible(kind)
                if n['artifactHash'].lower()!=t['artifactHash'].lower():emit(kind,r,target,'Evaluated SHA256 differs from the explicitly linked delivered artifact SHA256.')
            else:gap('Comparable artifact hashes are missing','Record SHA256 hashes of both evaluated and explicitly linked delivered bytes.')
    return findings,counts
