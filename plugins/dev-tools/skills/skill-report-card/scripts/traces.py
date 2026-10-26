"""Read recorded Codex exec JSONL events; no producer reports required."""
import json,hashlib,re
SKILLS=('base-ui','component-variants','wireframe-review')
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(raw,max_records=10000,max_line_bytes=2097152):
    thread=None;commands={};started=set();conflicts=set();usage=[];counts={'malformedRecords':0,'unsupportedRecords':0};stop=None
    for i,line in enumerate(raw.splitlines()):
        if i>=max_records:stop='record-budget';break
        if len(line)>max_line_bytes:counts['oversizedRecords']=counts.get('oversizedRecords',0)+1;continue
        try:r=json.loads(line)
        except (ValueError,UnicodeError,RecursionError):counts['malformedRecords']+=1;continue
        if not isinstance(r,dict):counts['unsupportedRecords']+=1;continue
        if r.get('type')=='thread.started' and isinstance(r.get('thread_id'),str):
            ident=sha(r['thread_id'].encode())
            if thread is not None and thread!=ident:stop='mixed-thread-identities';break
            thread=ident
        if r.get('type')=='turn.completed' and isinstance(r.get('usage'),dict):
            u=r['usage'];keys=('input_tokens','cached_input_tokens','output_tokens')
            if all(type(u.get(k)) is int and u[k]>=0 for k in keys):usage.append({k:u[k] for k in keys})
        item=r.get('item')
        if not isinstance(item,dict) or item.get('type')!='command_execution' or not isinstance(item.get('id'),str):continue
        ident=sha(item['id'].encode())
        if r.get('type')=='item.started':started.add(ident);continue
        if r.get('type')!='item.completed':continue
        if not isinstance(item.get('command'),str) or not isinstance(item.get('aggregated_output'),str) or item.get('exit_code') is not None and type(item['exit_code']) is not int:
            counts['invalidCommandRecords']=counts.get('invalidCommandRecords',0)+1;continue
        cmd=item['command'];out=item['aggregated_output'];fingerprint=sha(json.dumps(item,sort_keys=True).encode())
        if ident in commands:
            if commands[ident]['fingerprint']!=fingerprint:conflicts.add(ident)
            else:counts['duplicateCommandRecords']=counts.get('duplicateCommandRecords',0)+1
            continue
        hints=[s for s in SKILLS if re.search(r'/'+re.escape(s)+r'(?:/|[\s\'\"]|$)',cmd)]
        readish=bool(re.search(r'\b(cat|sed|head|tail|rg|read_text|readFileSync)\b',cmd))
        commands[ident]={'fingerprint':fingerprint,'outputBytes':len(out.encode()),'exit':item['exit_code'],'skillHints':hints,'readish':readish,'record':i}
    usable=[v for k,v in commands.items() if k not in conflicts]
    hints=sorted({s for c in usable for s in c['skillHints']})
    observations={'schemaVersion':1,'adapterVersion':'codex-exec-trace/1.0.0','traceSHA256':sha(raw),'threadIdentityHash':thread,'skillHints':hints,'attribution':'command-path-reference-only','recordedCommands':len(commands),'unresolvedStartedCommands':len(started-set(commands)),'conflictingCommandIdentities':len(conflicts),'loggedCommandOutputUtf8Bytes':sum(c['outputBytes'] for c in usable),'recordedSuccessfulExits':sum(c['exit']==0 for c in usable),'recordedNonzeroExits':sum(c['exit'] is not None and c['exit']!=0 for c in usable),'unknownExits':sum(c['exit'] is None for c in usable),'readContainingCommandOutputBytes':sum(c['outputBytes'] for c in usable if c['readish']),'classifier':'read-containing-command-heuristic-includes-mixed-commands','reportedUsageEvents':usage,'coverage':{'counts':counts,'stopReason':stop,'completeCaptureEstablished':False},'performanceEligible':False,'attemptDenominator':None,'measuredKpis':0,'limits':['Logged decoded command output bytes are not model-context bytes or model tokens.','Recorded usage counters cover the logged turn; they are not skill-specific retrieval cost.','Command path references are use hints, not proof of instruction consumption or causal skill quality.','Trace copies and command events are not independent author attempts.','Capture completeness, task/quality applicability and output truncation remain unverified.']}
    return observations
