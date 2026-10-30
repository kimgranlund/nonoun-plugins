"""Conservative Claude Code JSONL adapter. Never execute recorded commands."""
import hashlib
import json
import os
import re
from pathlib import Path

VERSION = '1.1.0'

def records(trace, through_line=None):
    with Path(trace).open() as stream:
        for line, text in enumerate(stream,1):
            if through_line and line>through_line: break
            try: value=json.loads(text)
            except ValueError: yield line, None; continue
            yield line, value if isinstance(value,dict) else None

def scrub(value, warnings, include_system_prompt=False):
    if isinstance(value,list): return [scrub(v,warnings,include_system_prompt) for v in value]
    if not isinstance(value,dict): return value
    if value.get('type') in ('thinking','redacted_thinking','image','document'):
        warnings.add('Thinking/image/document bytes omitted.')
        return {'type':value['type'],'omitted':True}
    if value.get('type')=='prompt_snapshot' and not include_system_prompt:
        warnings.add('Prompt snapshot omitted by default.');return {'type':'prompt_snapshot','omitted':True}
    result={}
    for k,v in value.items():
        if k in ('credential_org','signature','thinking','artifactLedger','artifact_ledger'):
            warnings.add('Private identity/ledger/reasoning fields omitted.');continue
        if k=='systemPrompt' and not include_system_prompt:
            warnings.add('System prompt omitted; use --include-system-prompt to include it.');continue
        result[k]=scrub(v,warnings,include_system_prompt)
    return result

def hydrate(trace, repo, trace_root=None, title=None, through_line=None, include_system_prompt=False, include_children=True, _seen=None, _depth=0):
    from fog import inventory, validate
    from diagnostics import diagnose
    from candidates import discover_candidates
    from connections import connect
    from wrapped import read_requests, scoped_read_requests, corroborate
    trace=Path(trace).resolve();repo=Path(repo).resolve();seen=set(_seen or ())
    if trace in seen or _depth>8: raise ValueError('Child cycle or depth limit')
    seen.add(trace)
    paths,mode,revision=inventory(repo)
    warnings={'Inventory is current analyzer knowledge, not historical exposure.',
        'Exposure is not understanding or retained context. Parent and child contexts are separate.',
        'Claude formats are report-derived; unknown fields remain inspectable. No spilled outputs are opened.'}
    data={'schemaVersion':2,'session':dict(title=title or trace.stem,trace=trace.name,traceSha256=hashlib.sha256(trace.read_bytes()).hexdigest(),repo=repo.name,revision=revision,host='claude',adapterVersion=VERSION),
        'coverage':{'inventory':mode,'warnings':[]},'sources':[],'events':[],'links':[],'decisions':[],'guidanceEdges':[],'findings':[], 'contextRecords':[], 'childSessions':[], 'messageRetention':[]}
    source_ids={};calls={};completed=set();uuids={};pending_links=[];spawns=[];cwd=str(repo);session_id=trace.stem
    def source(path):
        if path not in source_ids:
            source_ids[path]='s'+str(len(source_ids)+1);data['sources'].append(dict(id=source_ids[path],path=path,inventoried=path in paths))
        return source_ids[path]
    for path in paths:source(path)
    def norm(path,base):
        if not isinstance(path,str) or not path:return None
        if '://' in path:return path
        absolute=os.path.normpath(path if os.path.isabs(path) else os.path.join(base,path))
        # Per-record cwd is authoritative, including relocated worktrees.
        root=trace_root or base
        rel=os.path.relpath(absolute,root)
        return rel if rel!='..' and not rel.startswith('../') else absolute
    def event(kind,label,payload,line,record):
        e=dict(id='e'+str(len(data['events'])+1),seq=len(data['events']),kind=kind,label=label,actor=record.get('type','harness'),timestamp=record.get('timestamp',''),evidence=dict(traceLine=line,text=json.dumps(payload,ensure_ascii=False,indent=2)),exposures=[])
        data['events'].append(e)
        if record.get('parentUuid'):pending_links.append((record['parentUuid'],e['id'],'Recorded parentUuid message ancestry; not causal influence'))
        if record.get('sourceToolUseID'):pending_links.append(('tool:'+record['sourceToolUseID'],e['id'],'Explicit sourceToolUseID'))
        if record.get('uuid'):uuids.setdefault(record['uuid'],[]).append(e['id'])
        return e
    def exposure(e,path,state,basis,start=None,end=None):
        if not path:return
        x=dict(sourceId=source(path),state=state,basis=basis)
        if isinstance(start,int) and not isinstance(start,bool) and start>=1 and isinstance(end,int) and end>=start:x.update(startLine=start,endLine=end)
        e['exposures'].append(x)
    def candidate(e,path):
        if path:data.setdefault('candidates',[]).append(dict(sourceId=source(path),eventId=e['id'],kind='mentioned',evidence=dict(eventId=e['id'],excerpt=e['evidence']['text'])))
    def context(e,path,status='included'):
        if path:data['contextRecords'].append(dict(sourceId=source(path),eventId=e['id'],status=status,evidence=dict(eventId=e['id'],excerpt=e['evidence']['text'])))
    def link(a,b,reason):
        if a!=b:data['links'].append(dict(from_=a,to=b,kind='recorded',reason=reason))
    for line,raw in records(trace,through_line):
        if raw is None:warnings.add('Malformed JSONL records skipped.');continue
        typ=raw.get('type')
        if typ in ('cost-state','file-history-snapshot','file-history-delta','artifact-ledger'):
            warnings.add('Private accounting/history metadata omitted.');continue
        r=scrub(raw,warnings,include_system_prompt)
        if isinstance(r.get('cwd'),str):cwd=r['cwd']
        session_id=r.get('sessionId',session_id)
        message=r.get('message',{});message=message if isinstance(message,dict) else {}
        content=message.get('content',[])
        blocks=content if isinstance(content,list) else [{'type':'text','text':content}]
        if typ in ('assistant','user'):
            if not blocks: event('unknown','Empty message record',r,line,r)
            for block in blocks:
                if not isinstance(block,dict):continue
                bt=block.get('type');payload={k:v for k,v in r.items() if k not in ('message','toolUseResult')};payload['block']=block
                if r.get('isVisibleInTranscriptOnly'):
                    event('unknown','Display-only message · not model context',payload,line,r);continue
                if bt in ('tool_use','server_tool_use'):
                    name=block.get('name','Unknown tool');args=block.get('input',{});args=args if isinstance(args,dict) else {}
                    e=event('call',name,payload,line,r);identity=block.get('id')
                    if not identity or identity in calls:warnings.add('Missing/duplicate tool call IDs; ambiguous calls not paired.');calls[identity]=None;continue
                    calls[identity]=(e,name,args,cwd);uuids['tool:'+identity]=[e['id']]
                    e['toolCalls']=[dict(position='1',tool=name,arguments=json.dumps(args),output='',settlement='pending',outcome='pending')]
                    for key in ('file_path','path'):
                        if key in args:exposure(e,norm(args[key],cwd),'discovered','Recorded tool request only')
                    continue
                if bt in ('tool_result','advisor_tool_result'):
                    identity=block.get('tool_use_id');matched=calls.get(identity) if identity not in completed else None
                    # Structured result belongs to a unique result block only.
                    result_blocks=[b for b in blocks if isinstance(b,dict) and b.get('type') in ('tool_result','advisor_tool_result')]
                    structured=r.get('toolUseResult',{}) if len(result_blocks)==1 else {}
                    if not isinstance(structured,dict):structured={}
                    payload['toolUseResult']=structured
                    e=event('result',('Result · '+matched[1]) if matched else 'Unmatched tool result',payload,line,r)
                    if not matched:warnings.add('Unmatched tool results retained without exposure.');continue
                    completed.add(identity)
                    previous,name,args,call_cwd=matched;link(previous['id'],e['id'],'Matched tool_use_id '+str(identity))
                    error=block.get('is_error');outcome='failed' if error is True else 'unknown' if structured.get('interrupted') else 'succeeded' if error is False else 'unknown'
                    e['toolCalls']=[dict(position='1',tool=name,arguments=json.dumps(args),output=json.dumps(block.get('content','')),settlement='fulfilled',outcome=outcome)]
                    if error is True:continue
                    path=norm(structured.get('filePath',args.get('file_path')),call_cwd)
                    if name=='Read':
                        f=structured.get('file',{});f=f if isinstance(f,dict) else {}
                        path=norm(f.get('filePath',args.get('file_path')),call_cwd)
                        if structured.get('type')=='text' and isinstance(f.get('content'),str):
                            start,n,total=f.get('startLine'),f.get('numLines'),f.get('totalLines')
                            valid=all(isinstance(x,int) and not isinstance(x,bool) and x>=0 for x in (start,n,total)) and start>=1
                            full=valid and start==1 and n==total
                            exposure(e,path,'read' if full else 'partial','Structured Read returned text',start,start+n-1 if valid else None)
                        else:warnings.add('Read lacks attributable text/ranges; media bytes omitted without invented file exposure.')
                    elif name in ('Edit','Write'):
                        if structured.get('filePath') and (structured.get('structuredPatch') is not None or structured.get('type') in ('create','update')):
                            exposure(e,path,'edited','Structured mutation result; does not imply read')
                    elif name=='Bash':
                        stdout=structured.get('stdout','');text=stdout if isinstance(stdout,str) else ''
                        if not text and isinstance(block.get('content'),str):text=block['content']
                        spill=bool(structured.get('persistedOutputPath')) or bool(re.search(r'truncat',text,re.I))
                        if spill:warnings.add('Spilled tool output not opened; only returned portion considered.')
                        cmd=args.get('command','')
                        # Reuse the bounded source witness used by Codex. Current source
                        # bytes corroborate a literal request, never fill missing output.
                        compound=bool(isinstance(cmd,str) and re.search(r'[;&\n]',cmd))
                        if compound:
                            for target,start,end in scoped_read_requests(cmd,call_cwd):
                                p=norm(target,call_cwd)
                                exposure(previous,p,'discovered','Literal compound Bash request; lexical path scope')
                                witness=repo/p if p and not p.startswith('/') else Path(target)
                                state=corroborate(witness,[repo],text,start,end) if text and not structured.get('interrupted') else None
                                if state:
                                    exposure(e,p,state,'Recorded output matches bounded source bytes for a literal compound request; snapshot revision and attempted cd success are unverified',start if state=='partial' else None,end if state=='partial' else None)
                            warnings.add('Compound Bash reads require matching bounded source bytes; lexical cd requests and current snapshot matches do not prove historical revision or shell directory state.')
                        if isinstance(cmd,str) and not re.search(r'[|;&<>`\n]|\$\(',cmd):
                            req=read_requests(cmd)
                            for target,start,end in req:
                                p=norm(target,call_cwd);exposure(previous,p,'discovered','Literal Bash read request')
                                if error is False and text and len(req)==1 and not structured.get('interrupted'):
                                    exposure(e,p,'read' if cmd.startswith('cat ') and not spill else 'partial','Successful single-source Bash return',start if not spill else None,end if not spill else None)
                    elif name=='Skill':pass # Body arrival, not call success, establishes returned guidance.
                    elif name=='Agent':
                        agent=structured.get('agentId')
                        if isinstance(agent,str):spawns.append((agent,previous['id'],e['id']))
                    elif name in ('Glob','Grep'):
                        for target in structured.get('filenames',[]) if isinstance(structured.get('filenames'),list) else []:
                            candidate(e,norm(target,call_cwd))
                        if name=='Grep' and args.get('output_mode')=='content':
                            text=block.get('content','')
                            for target,num in re.findall(r'^([^\n:]+):(\d+):',text if isinstance(text,str) else '',re.M):
                                exposure(e,norm(target,call_cwd),'partial','Numbered Grep return',int(num),int(num))
                    elif name=='ToolSearch':
                        for tool in structured.get('matches',[]) if isinstance(structured.get('matches'),list) else []:
                            if isinstance(tool,str):candidate(e,'tool://'+tool)
                    elif name in ('WebFetch','WebSearch','Artifact','ArtifactData'):
                        url=args.get('url')
                        if isinstance(url,str) and url.startswith(('https://','http://')):
                            exposure(previous,url,'discovered','Requested external source')
                            if error is False and block.get('content'):exposure(e,url,'partial','External return; complete source coverage unknown')
                    elif name not in ('TaskStop','TaskOutput','Monitor','AskUserQuestion','ToolSearch','SendMessage'):
                        warnings.add('Unsupported tools retained without inferred file exposure.')
                    continue
                kind='compaction' if r.get('isCompactSummary') else 'context' if r.get('isMeta') else 'message'
                e=event(kind,'Injected context' if kind=='context' else 'Claude '+str(bt),payload,line,r)
                text=block.get('text','')
                if r.get('isMeta') and isinstance(text,str):
                    match=re.search(r'^Base directory for this skill: (.+)$',text,re.M)
                    if match:
                        path=norm(match.group(1).strip()+'/SKILL.md',cwd)
                        exposure(e,path,'partial','Injected skill text; full on-disk file equivalence unverified');context(e,path)
            continue
        if typ=='attachment':
            a=r.get('attachment',{});a=a if isinstance(a,dict) else {};at=a.get('type','unknown')
            e=event('context','Attachment · '+at,r,line,r)
            path=norm(a.get('path',a.get('filename')),cwd)
            if at in ('nested_memory','file','edited_text_file') and path:
                if isinstance(a.get('content',a.get('snippet')),str):
                    exposure(e,path,'partial' if at=='edited_text_file' else 'read','Explicit attached content');context(e,path)
                else:exposure(e,path,'discovered','Attachment names path without contents')
            elif at=='instructions':
                for f in a.get('files',[]) if isinstance(a.get('files'),list) else []:
                    p=norm(f.get('path',f.get('filename')) if isinstance(f,dict) else f,cwd)
                    if p:
                        context(e,p)
                        exposure(e,p,'read' if isinstance(f,dict) and isinstance(f.get('content'),str) else 'discovered','Explicit instruction attachment; contents only when present')
            elif at in ('skill_listing','invoked_skills','skill_mention'):
                for name in a.get('names',[]) if isinstance(a.get('names'),list) else []:
                    if isinstance(name,str):candidate(e,'skill://'+name)
            elif at in ('agent_listing_delta','deferred_tools_delta','deferred_tools_record','mcp_instructions_delta'):
                namespace='agent://' if at=='agent_listing_delta' else 'tool://'
                for field,status in [('added','included'),('removed','removed')]:
                    for name in a.get(field,[]) if isinstance(a.get(field),list) else []:
                        if isinstance(name,str):context(e,namespace+name,status)
                warnings.add('Catalog deltas interpreted only for explicit added/removed string arrays; other shapes remain raw evidence.')
            elif at=='compact_file_reference':exposure(e,path,'discovered','Retained path reference only')
            # Catalog/reminder/hook/unknown attachments stay inspectable, never fabricated file reads.
            continue
        e=event('compaction' if typ=='system' and r.get('subtype')=='compact_boundary' else 'unknown', 'Claude '+str(r.get('subtype',typ)),r,line,r)
        if e['kind']=='compaction':
            metadata=r.get('compactMetadata',{})
            preserved=metadata.get('preservedMessages',{}) if isinstance(metadata,dict) else {}
            if isinstance(preserved,dict) and isinstance(preserved.get('allUuids'),list):
                known={x for x in preserved['allUuids'] if isinstance(x,str)}
                for uuid,ids in uuids.items():
                    if uuid.startswith('tool:'):continue
                    for eid in ids:
                        if eid!=e['id']:data['messageRetention'].append(dict(eventId=e['id'],messageEventId=eid,status='included' if uuid in known else 'removed'))
                warnings.add('Compaction message retention recorded separately; it does not prove file-byte retention.')
    for parent,child,reason in pending_links:
        for eid in uuids.get(parent,[]):link(eid,child,reason)
    data['links']=[{'from':x['from_'],'to':x['to'],'kind':x['kind'],'reason':x['reason']} for x in data['links']]
    matched_events={l['from'] for l in data['links'] if l['reason'].startswith('Matched tool_use_id')}
    if any(c and c[0]['id'] not in matched_events for c in calls.values()):warnings.add('Calls without results remain pending.')
    for agent,parent,result in spawns:
        entry=dict(agentId=agent,parentEventId=parent,resultEventId=result,status='unavailable')
        if not re.fullmatch(r'[A-Za-z0-9_-]+',agent):warnings.add('Unsafe child agent ID ignored.');continue
        child=trace.parent/trace.stem/'subagents'/('agent-'+agent+'.jsonl')
        if include_children and not through_line and child.is_file() and not child.is_symlink() and child.resolve().is_relative_to(trace.parent.resolve()):
            try:
                entry['report']=hydrate(child,repo,trace_root,agent,include_system_prompt=include_system_prompt,_seen=seen,_depth=_depth+1);entry['status']='hydrated'
            except (ValueError,OSError) as exc:warnings.add('Child unavailable: '+str(exc))
        else:warnings.add('Child unavailable, disabled, or omitted for parent cutoff: '+agent)
        data['childSessions'].append(entry)
    if not data['events']:raise ValueError('No usable Claude trace events')
    data['coverage']['warnings']=sorted(warnings)
    display_only={e['id']:e['evidence']['text'] for e in data['events'] if e['label'].startswith('Display-only')}
    for e in data['events']:
        if e['id'] in display_only:e['evidence']['text']='[Display-only content excluded from context extraction]'
    explicit_candidates=data.get('candidates',[])
    data=discover_candidates(data)
    data['candidates'].extend(c for c in explicit_candidates if c not in data['candidates'])
    data=connect(data)
    for e in data['events']:
        if e['id'] in display_only:e['evidence']['text']=display_only[e['id']]
    return validate(diagnose(data))
