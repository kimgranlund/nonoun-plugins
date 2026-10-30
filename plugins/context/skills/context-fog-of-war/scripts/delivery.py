"""Observed source delivery checks. No trace command or source path is executed/read."""
import hashlib
import json
import posixpath
import re

CATALOG = [
    {'id':'required-source-before-write','name':'Required body before first write','requires':'Cited explicit requirements, observed application mutation and cited return-observation window','rule':'A required body has no complete matching return before the first observed application mutation. Missing observation coverage is unknown.','alternatives':['Earlier injected delivery is outside the observation window','Requirement applicability needs review'],'guidance':'Inspect the explicit requirement and deliver the missing body before implementation.','verification':'Preserve the same requirements and inspect complete body returns before the first application mutation.'},
    {'id':'incomplete-source-delivery','name':'Incomplete required source delivery','requires':'Explicit required body and observed partial, metadata-only or clipped return','rule':'Recorded limited output does not establish a complete required body. Tool clipping and intentional command bounds remain distinct.','alternatives':['A focused portion may suffice for the task','Another unrecorded channel may have delivered the source'],'guidance':'Recover the required missing portions with matching source identity; preserve intentional bounds in the evidence.','verification':'Verify contiguous matching body coverage or a complete body return before the governed action.'},
    {'id':'unfinished-continuation','name':'Unfinished executable continuation','requires':'Returned executable next.args, source identity and a cited complete observation window','rule':'A returned executable continuation has no matching complete recovery in the observed window. A follow-up request alone is insufficient.','alternatives':['The task deliberately stopped after a sufficient portion','Recovery may exist outside the observation window'],'guidance':'Follow the returned next.args until complete, preserving source identity and revision.','verification':'Record all matching pages through completion and verify no missing ranges.'},
    {'id':'excluded-source-read','name':'Read from an explicitly excluded location','requires':'Cited fresh-builder exclusion policy and attributable returned source read','rule':'A returned read falls within an explicitly excluded path, outside sanctioned exceptions. Requests and inventory alone do not establish reads.','alternatives':['The policy applicability may need review','A separately authorized exception may be missing'],'guidance':'Use the stated context boundary and record any explicit exception before consuming the source.','verification':'Repeat the bounded source-read check with the same policy and sanctioned examples.'},
]
SPECS = {
    'required-source-before-write':('explicit required sources before an observed application mutation','Record cited required source identities, application path scope, the mutation result, and a cited complete returned-read observation window.','Observed absence is not proof of unread, unsubmitted or misunderstood context.'),
    'incomplete-source-delivery':('required sources with attributable limited returns','Record an explicit required body and matching returned ranges, clipping metadata or body-page envelopes.','Intentional partial reads are not tool-output truncation and may be sufficient for another task.'),
    'unfinished-continuation':('returned executable continuations in a complete observation window','Preserve next.args, source identity/hash, matching result pages and a cited observation cutoff.','Hidden helper calls or missing result telemetry prevent a completeness verdict.'),
    'excluded-source-read':('attributable returned reads under explicit fresh-builder exclusions','Record the applicable intent and exclusion policy, sanctioned exceptions and matched source returns.','No ledger, history or solution read is inferred from a path mention, request or edit.'),
}

def path(value):
    if not isinstance(value,str) or not value:return None
    filename,separator,fragment=value.replace('\\','/').partition('#')
    return posixpath.normpath(filename)+(separator+fragment if separator else '')

def beneath(value,prefix):
    value,prefix=path(value),path(prefix)
    if value:value=value.split('#',1)[0]
    if prefix:prefix=prefix.split('#',1)[0]
    return bool(value and prefix and (value==prefix or value.startswith(prefix.rstrip('/')+'/')))

def citation(value,by):
    if not isinstance(value,dict):return None
    e=by.get(value.get('eventId'));text=value.get('excerpt')
    if not e or not isinstance(text,str) or not text or text not in e['evidence']['text']:return None
    if value.get('traceLine',e['evidence']['traceLine'])!=e['evidence']['traceLine']:return None
    return dict(eventId=e['id'],traceLine=e['evidence']['traceLine'],excerpt=text)

def objects(value,depth=0):
    """Decode only recorded output envelopes and complete JSON values, never execute them."""
    if depth>12:return
    if isinstance(value,str):
        try:decoded=json.loads(value)
        except ValueError:
            # CLI preambles can precede one complete JSON return. Do not parse code examples.
            lines=value.splitlines()
            starts=[sum(len(x)+1 for x in lines[:i]) for i,x in enumerate(lines) if x.strip()=='{'][:32]
            for start in starts:
                try:decoded,end=json.JSONDecoder().raw_decode(value[start:])
                except ValueError:continue
                if not value[start+end:].strip():yield from objects(decoded,depth+1);return
            return
        if not isinstance(decoded,str):yield from objects(decoded,depth+1)
    elif isinstance(value,list):
        for item in value:yield from objects(item,depth+1)
    elif isinstance(value,dict):
        yield value
        if isinstance(value.get('block'),dict) and value['block'].get('type')=='tool_result':
            yield from objects(value['block'].get('content'),depth+1)
        for key in ('output','content','text','stdout'):
            if key in value:yield from objects(value[key],depth+1)

def command(args):
    if isinstance(args,str):
        try:args=json.loads(args)
        except ValueError:return args
    if isinstance(args,dict):
        if 'arguments' in args:return command(args['arguments'])
        return args.get('cmd',args.get('command',''))
    return ''

def self_limits(event):
    limits=[]
    for unit in event.get('toolCalls',[]):
        cmd=command(unit.get('arguments'))
        if isinstance(cmd,str):
            for match in re.finditer(r'(?<![\w-])(?:head(?:\s+(?:-n|-c)\s*\d+|\s+-\d+)?|cut\s+-[^|;&\n]+|tail\s+-c\s*\+?\d+|sed\s+-n\s+[\"\']?\d+[,\d]*p)',cmd):
                limits.append(match.group())
    return list(dict.fromkeys(limits))

def packet_record(obj,event,base):
    if not isinstance(obj.get('complete'),bool):return None
    kind=obj.get('kind','')
    if kind=='complete-file':return None # A receipt establishes a written file, not a body return.
    if not all(isinstance(obj.get(k),int) and not isinstance(obj.get(k),bool) for k in ('offset','end','total')):return None
    start,end,total=(obj[k] for k in ('offset','end','total'))
    if not 0<=start<=end<=total:return None
    identity=obj.get('source') or obj.get('id')
    is_metadata=kind in ('metadata-page','search-page','task-packet-page')
    if not identity and is_metadata:identity=kind+':'+str(obj.get('term',''))
    if not isinstance(identity,str):return None
    prefix=obj.get('pathBase') or base
    if prefix and not identity.startswith('/') and ':' not in identity:identity=posixpath.join(prefix,identity)
    content=obj.get('content')
    if not is_metadata and not isinstance(content,str):return None
    return dict(path=path(identity),renderer=obj.get('renderer'),hash=obj.get('sha256'),contentHash=obj.get('contentSha256'),
                offset=start,end=end,total=total,content=content,complete=obj['complete'],next=obj.get('next'),
                body=not is_metadata,event=event,kind=kind or 'legacy-source-page',validLength=len(content)==end-start if isinstance(content,str) else is_metadata)

def complete_pages(records,required_hash=None,body_required=True,return_content=False):
    groups={}
    for record in records:
        if (body_required and not record['body']) or not record['hash'] or not record['validLength']:continue
        if required_hash and record.get('contentHash')!=required_hash:continue
        key=(record['hash'],record['total'],record.get('contentHash'),record.get('renderer'))
        groups.setdefault(key,[]).append(record)
    for (_,total,content_hash,_),pages in groups.items():
        ordered=sorted(pages,key=lambda x:x['offset']);parts=[];end=0;valid=True
        if all(not p['body'] for p in pages) and not all(isinstance(p['content'],str) for p in pages):
            for p in ordered:
                if p['offset']>end:valid=False;break
                end=max(end,p['end'])
            if valid and end==total and any(p['complete'] and p['end']==total and p['next'] is None for p in pages):return None if return_content else True
            continue
        if not all(isinstance(p['content'],str) for p in pages):continue
        for p in ordered:
            if p['offset']>end:valid=False;break
            overlap=max(0,end-p['offset'])
            assembled=''.join(parts)
            if overlap and assembled[p['offset']:min(end,p['end'])]!=p['content'][:min(overlap,len(p['content']))]:valid=False;break
            if p['end']>end:parts.append(p['content'][overlap:]);end=p['end']
        if not valid or end!=total or not any(p['complete'] and p['end']==total and p['next'] is None for p in pages):continue
        body=''.join(parts)
        if content_hash and hashlib.sha256(body.encode('utf8')).hexdigest()!=content_hash:continue
        return body if return_content else True
    return None if return_content else False

def task_bodies(packet,event,base):
    """Expand complete recorded packet bodies only; references never become bodies."""
    if packet.get('kind')!='task-packet' or packet.get('complete') is not True or not isinstance(packet.get('bodies'),list):return []
    results=[]
    for body in packet['bodies']:
        if not isinstance(body,dict) or body.get('kind')!='body' or body.get('complete') is not True:continue
        content=body.get('content');identity=body.get('source');digest=body.get('sha256')
        if not isinstance(content,str) or not content or not isinstance(identity,str) or not identity:continue
        if not digest or hashlib.sha256(content.encode('utf8')).hexdigest()!=digest:continue
        # Selected JSON records are complete projections, never a whole-file read.
        whole=body.get('projection')=='complete-file' or ('#' in identity and body.get('projection') in ('json-pointer','markdown-section'))
        prefix=packet.get('pathBase') or base
        if prefix and not identity.startswith('/') and ':' not in identity:identity=posixpath.join(prefix,identity)
        results.append(dict(path=path(identity),renderer=packet.get('selection',{}).get('renderer'),hash=digest,contentHash=digest,offset=0,end=len(content),total=len(content),content=content,complete=True,next=None,body=whole,event=event,kind='task-packet-body',validLength=True))
    return results

def analyze(data,coverage,add,cite):
    events=data['events'];by={e['id']:e for e in events};sources={s['id']:s for s in data['sources']}
    counts={c['id']:0 for c in CATALOG};contract=data.get('deliveryContract') or {}
    if not isinstance(contract,dict):raise ValueError('deliveryContract must be an object')
    for key in ('applicationPaths','excludedPaths','sanctionedPaths'):
        if not isinstance(contract.get(key,[]),list) or not all(isinstance(x,str) and x for x in contract.get(key,[])):raise ValueError('deliveryContract.'+key+' must contain nonempty path strings')
    mode=contract.get('mode','analyst-supplied')
    if mode not in ('analyst-supplied','observed','authored-replay','retrospective-policy'):raise ValueError('Unsupported deliveryContract mode')
    original_add=add
    def add(*args,**kwargs):
        kwargs.setdefault('metrics',{})['contractMode']=mode
        original_add(*args,**kwargs)
    policy=citation(contract.get('evidence'),by)
    requirements=contract.get('requiredSources',[]) if isinstance(contract.get('requiredSources',[]),list) else []
    app_paths=contract.get('applicationPaths',[]);intent=contract.get('intent')
    window=contract.get('observationWindow') or {};window_cite=citation(window.get('evidence'),by)
    window_end=by.get(window.get('throughEventId'))
    # This is a cited analyst assertion of extraction completeness, never context/retention.
    complete_window=bool(window.get('sourceReturnsComplete') is True and window_cite and window_end)
    writes=[e for e in events if e['kind']=='result' and any(x.get('state')=='edited' and any(beneath(sources.get(x.get('sourceId'),{}).get('path'),p) for p in app_paths) for x in e.get('exposures',[]))]
    first_write=min(writes,key=lambda e:e['seq']) if writes else None
    cutoff=first_write['seq'] if first_write else window_end['seq']+1 if window_end else None
    window_ok=bool(complete_window and cutoff is not None and window_end['seq']>=(first_write['seq'] if first_write else cutoff-1))
    packets=[];direct_packets=[];returns=[];requested={};clipped=set();bounds={}
    from truncation import sites
    for e in events:
        for x in e.get('exposures',[]):
            sid=x.get('sourceId');sp=path(sources.get(sid,{}).get('path'))
            if not sp:continue
            if x.get('state')=='discovered' and e['kind']=='call':requested.setdefault(sp,[]).append(e['id'])
            if x.get('state') in ('read','partial') and e['kind'] in ('result','context','attachment'):
                returns.append(dict(path=sp,sourceId=sid,event=e,exposure=x))
        if e['kind']!='result':continue
        if sites(e):clipped.add(e['id'])
        bounds[e['id']]=self_limits(e)
        seen=set()
        payloads=[u.get('output') for u in e.get('toolCalls',[]) if u.get('outcome') not in ('failed','rejected')]
        payloads.append(e['evidence']['text'])
        for payload in payloads:
            for obj in objects(payload):
                if obj.get('kind')=='task-packet':direct_packets.append((obj,e))
                r=packet_record(obj,e,contract.get('sourceBase',''))
                if r:
                    key=json.dumps({k:v for k,v in r.items() if k!='event'},sort_keys=True)
                    if key not in seen:packets.append(r);seen.add(key)
    # Reconstruct complete task-packet transports before inspecting inner bodies.
    # The terminal event is delivery time; later recovery cannot erase earlier gaps.
    packet_groups={}
    for p in packets:
        if p['kind']=='task-packet-page' and p['event']['id'] not in clipped and (cutoff is None or p['event']['seq']<cutoff):
            packet_groups.setdefault((p['path'],p['hash']),[]).append(p)
    for pages in packet_groups.values():
        content=complete_pages(pages,body_required=False,return_content=True)
        if isinstance(content,str):
            try:obj=json.loads(content)
            except ValueError:continue
            if isinstance(obj,dict):direct_packets.append((obj,max(pages,key=lambda p:p['event']['seq'])['event']))
    body_keys=set()
    for obj,e in direct_packets:
        if e['id'] in clipped or (cutoff is not None and e['seq']>=cutoff):continue
        for body in task_bodies(obj,e,contract.get('sourceBase','')):
            key=(body['path'],body['hash'],e['id'])
            if key not in body_keys:packets.append(body);body_keys.add(key)
    summary={'contractMode':mode,'contractQualification':'Supplied requirement/policy and extraction-completeness interpretations; exact citations are checked, their semantics are not independently proved.','firstObservedWrite':first_write['id'] if first_write else None,'observationWindow':{'completeReturnsAsserted':complete_window,'evidence':window_cite,'throughEventId':window_end['id'] if window_end else None},'sources':[]}
    if not requirements:
        for detector in ('required-source-before-write','incomplete-source-delivery'):
            coverage.gap(detector,'Explicit required source identities are absent','Supply task-specific required bodies with exact requirement citations; do not expand the entire manifest.')
    for req in requirements:
        if not isinstance(req,dict):continue
        source_path=path(req.get('path'));req_cite=citation(req.get('evidence'),by)
        if not source_path or not req_cite:
            coverage.gap('required-source-before-write','Required source lacks a valid requirement citation','Cite the observed instruction or supplied requirement declaring this body required.');continue
        native=[r for r in returns if r['path']==source_path and (cutoff is None or r['event']['seq']<cutoff)]
        selected=[r for r in packets if r['path']==source_path and (req.get('renderer') is None or r['renderer']==req['renderer']) and (cutoff is None or r['event']['seq']<cutoff)]
        unclipped=[r for r in selected if r['event']['id'] not in clipped]
        native_full=any(r['exposure']['state']=='read' and r['event']['id'] not in clipped and not bounds.get(r['event']['id']) for r in native) and not req.get('contentHash')
        fulfilled=bool(native_full or complete_pages(unclipped,req.get('contentHash')))
        limited=[r['event'] for r in native if r['exposure']['state']=='partial' or r['event']['id'] in clipped or bounds.get(r['event']['id'])]+[r['event'] for r in selected]
        ids=list(dict.fromkeys(r['sourceId'] for r in native))
        summary['sources'].append({'path':source_path,'availableInInventory':any(path(s.get('path'))==source_path and s.get('inventoried') for s in sources.values()),'requestedEventIds':requested.get(source_path,[]),'returnedEventIds':list(dict.fromkeys([r['event']['id'] for r in native]+[r['event']['id'] for r in selected])),'completeBodyObserved':fulfilled,'state':'complete-return-observed' if fulfilled else 'incomplete-return-observed' if limited else 'no-return-recorded' if window_ok else 'unknown'})
        counts['required-source-before-write']+=1
        if not first_write:
            coverage.gap('required-source-before-write','No observed application mutation','Record the application path scope and an attributable successful mutation result.');continue
        if not window_ok:
            coverage.gap('required-source-before-write','Returned-read observation window is incomplete or uncited','Supply a cited assessment that relevant returned-read evidence through the first observed application mutation was captured.',first_write)
            if limited and not fulfilled:coverage.gap('incomplete-source-delivery','Later recovery coverage is unknown','Preserve matching recovery results or a cited complete returned-read observation window.',limited[-1])
            continue
        coverage.eligible('required-source-before-write')
        evidence=[req_cite,window_cite,cite(first_write)]
        if not fulfilled:
            add('required-source-before-write','Required body has no complete recorded return: '+source_path,'No complete matching body return for '+source_path+' is recorded before the first observed application mutation. This is an observed coverage gap, not proof that the agent never read or understood the source.',evidence+[cite(e) for e in limited[-2:]],ids,metrics={'path':source_path,'firstWriteEventId':first_write['id'],'returnedEvidence':bool(limited)})
        if limited:
            counts['incomplete-source-delivery']+=1;coverage.eligible('incomplete-source-delivery')
            if not fulfilled:
                reasons=[]
                if any(e['id'] in clipped for e in limited):reasons.append('explicit tool clipping')
                if any(bounds.get(e['id']) for e in limited):reasons.append('intentional command bounds')
                if any(not r['body'] and r['kind']!='task-packet-body' for r in selected):reasons.append('metadata only')
                if any(not r['body'] and r['kind']=='task-packet-body' for r in selected):reasons.append('selected source projection')
                if any(r['body'] for r in selected) or any(r['exposure']['state']=='partial' for r in native):reasons.append('partial body or missing matching ranges')
                add('incomplete-source-delivery','Required source delivery remains incomplete: '+source_path,'Observed delivery does not establish the complete required body before the application mutation: '+', '.join(reasons or ['no complete matching body receipt'])+'.',evidence+[cite(e) for e in limited[-2:]],ids,metrics={'path':source_path,'limitations':reasons,'intentionalBounds':list(dict.fromkeys(b for e in limited for b in bounds.get(e['id'],[])))})
    for p in packets:
        if p.get('next') and not (isinstance(p['next'],dict) and isinstance(p['next'].get('args'),list) and p['next']['args']):
            counts['unfinished-continuation']+=1
            coverage.gap('unfinished-continuation','Continuation has no executable next.args','Preserve an executable continuation argument list; a legacy offset descriptor is not an observed executable command.',p['event'])
    # Continuations are assessed only within a cited complete observation window.
    candidates=[p for p in packets if isinstance(p.get('next'),dict) and isinstance(p['next'].get('args'),list) and p['next']['args'] and all(isinstance(x,str) for x in p['next']['args']) and not p['complete'] and (cutoff is None or p['event']['seq']<cutoff)]
    seen=set()
    for p in candidates:
        key=(p['path'],p['hash'],p['renderer'])
        if key in seen:continue
        seen.add(key);counts['unfinished-continuation']+=1
        if not window_ok:
            coverage.gap('unfinished-continuation','Continuation recovery window is incomplete or uncited','Preserve matching follow-up results and a cited complete observation window; hidden helper execution stays unknown.',p['event']);continue
        if not p['hash']:
            coverage.gap('unfinished-continuation','Continuation lacks source revision identity','Preserve the delivery identity/hash used by the continuation.',p['event']);continue
        matching=[r for r in packets if (r['path'],r['hash'],r['renderer'])==key and r['event']['seq']<cutoff and r['event']['id'] not in clipped]
        coverage.eligible('unfinished-continuation')
        complete=complete_pages(matching,body_required=p['body'])
        if not complete:
            add('unfinished-continuation','Executable continuation has no complete recorded recovery','The returned next.args for '+p['path']+' has no matching complete delivery in the cited observation window. Requests alone and different source hashes do not establish recovery.',[cite(p['event']),window_cite]+([cite(first_write)] if first_write else []),metrics={'path':p['path'],'sha256':p['hash'],'nextArgs':p['next']['args'],'cutoffEventId':first_write['id'] if first_write else window_end['id']})
    excluded=contract.get('excludedPaths',[]);sanctioned=contract.get('sanctionedPaths',[])
    if intent!='fresh-builder' or not policy or not excluded:
        if intent=='maintenance':coverage.exclude('excluded-source-read','Maintenance intent does not inherit fresh-builder exclusions')
        else:coverage.gap('excluded-source-read','Explicit fresh-builder exclusion policy is absent','Supply the applicable fresh-builder intent, excluded path prefixes and exact policy citation.')
    else:
        exclusion_returns=list(returns)
        for p in packets:
            if (p['body'] or p['kind']=='task-packet-body') and p['content'] and not any(r['path']==p['path'] and r['event']['id']==p['event']['id'] for r in exclusion_returns):
                sid=next((sid for sid,source in sources.items() if path(source['path'])==p['path']),None)
                exclusion_returns.append({'path':p['path'],'event':p['event'],'sourceId':sid})
        for r in exclusion_returns:
            counts['excluded-source-read']+=1
            if not any(beneath(r['path'],p) for p in excluded):continue
            if any(beneath(r['path'],p) for p in sanctioned):coverage.exclude('excluded-source-read','Returned source is an explicitly sanctioned example');continue
            coverage.eligible('excluded-source-read')
            add('excluded-source-read','Returned source is explicitly excluded: '+r['path'],'An attributable returned source read falls within the cited fresh-builder exclusion policy. This does not infer any additional history, ledger or solution reads.',[policy,cite(r['event'])],[r['sourceId']] if r['sourceId'] else [],metrics={'path':r['path']})
    return counts,summary
