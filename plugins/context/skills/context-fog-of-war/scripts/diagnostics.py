"""Conservative, deterministic diagnostic candidates. Never execute trace content."""
import argparse
import json
import re
import shlex
from pathlib import Path

VERSION = '1.0.0'
CATALOG = [
 {'id':'failed-discovery','name':'Failed discovery','requires':'Matched call/result, lookup request, explicit failure signal','rule':'Failed lookup command with a concrete missing resource or catalog error; no-match exit 1 alone is excluded.','alternatives':['Intentional probe','Environment mismatch','An optional resource was absent'],'guidance':'Check the entry-point path, supported catalog vocabulary and environment prerequisites. Add a direct pointer or corrective error only if this lookup was necessary.','verification':'Replay comparable discovery tasks. Compare failed lookup counts and time to the target, while checking routing correctness.'},
 {'id':'repeated-retrieval','name':'Repeated retrieval','requires':'Two recorded read/partial exposures for the same source with known overlapping coverage','rule':'Full reread or overlapping explicit ranges, without a recorded intervening edit or compaction. Deduplicate within an event.','alternatives':['Unrecorded file change','Context eviction not visible in the trace','Deliberate verification'],'guidance':'Consider a stable summary, a narrower range, or an explicit reminder of already retrieved guidance. Do not remove a reread solely because it is repeated.','verification':'Compare repeated returns on equivalent runs; confirm correctness and necessary verification are preserved.'},
 {'id':'truncation','name':'Truncated return','requires':'Explicit output truncation marker in a returned tool output','rule':'Tool-output warning reports truncation. Partial exposure alone is insufficient.','alternatives':['The useful portion arrived before the cutoff','The limit was intentional'],'guidance':'Use bounded searches or focused line ranges; fetch the omitted region only if it contains needed evidence.','verification':'Confirm the required information is returned without truncation; compare output volume and follow-up retrievals.'},
 {'id':'broken-reference','name':'Broken reference','requires':'Failed lookup target previously present in returned guidance','rule':'An exact path from a failed lookup appears in earlier returned AGENTS.md, SKILL.md or README guidance. Only a candidate: provenance is not proof of instruction.','alternatives':['Example path rather than instruction','Different working directory or snapshot','A stale runtime environment'],'guidance':'Inspect the cited guidance and resolve the path in its intended scope. Correct the pointer or state its prerequisites if it is genuinely broken.','verification':'Run the documented route from a clean matching environment and verify the intended target resolves.'},
 {'id':'late-guidance','name':'Potentially late guidance','requires':'First observed read of scoped AGENTS.md or SKILL.md after an edit beneath its directory','rule':'Directory proximity suggests applicability; it does not prove the instruction governed the edit. Prior injected guidance is not ruled out.','alternatives':['Guidance was injected earlier','Instruction did not apply','Edit was intentionally preparatory'],'guidance':'Review applicability and earlier instruction delivery. If this guidance governs the edit, expose it before the editing entry point.','verification':'Repeat the task and verify guidance delivery precedes the governed action; check correctness, not just ordering.'}
]

from reconstruct import CATALOG as BUNDLE_CATALOG
CATALOG += BUNDLE_CATALOG
from delivery import CATALOG as DELIVERY_CATALOG
CATALOG += DELIVERY_CATALOG

def unpack(value):
    if isinstance(value,str):
        try:return unpack(json.loads(value))
        except (ValueError,TypeError):return value
    if isinstance(value,dict):
        if 'block' in value:
            block=value['block']
            return unpack(block.get('content','')) if isinstance(block,dict) and block.get('type')=='tool_result' else ''
        if 'output' in value:return unpack(value['output'])
        if 'content' in value:return unpack(value['content'])
        if 'text' in value:return unpack(value['text'])
        return ''
    if isinstance(value,list):return '\n'.join(unpack(x) for x in value)
    return ''

def explicit_failure(value):
    if isinstance(value,str):
        try:return explicit_failure(json.loads(value))
        except (ValueError,TypeError):
            m=re.search(r'(?:^|\n)(?:Process exited with code|Process exit code:)\s*(\d+)',value)
            return bool(m and int(m.group(1))!=0)
    if isinstance(value,dict):
        if isinstance(value.get('exit_code'),int):return value['exit_code']!=0
        return explicit_failure(value.get('output',value.get('content',[])))
    if isinstance(value,list):return any(explicit_failure(x.get('text','')) for x in value if isinstance(x,dict))
    return False

def execution_outcome(value):
    if isinstance(value,str):
        try:return execution_outcome(json.loads(value))
        except (ValueError,TypeError):
            m=re.search(r'(?:^|\n)(?:Process exited with code|Process exit code:)\s*(\d+)',value)
            return ('succeeded' if int(m.group(1))==0 else 'failed') if m else 'unknown'
    if isinstance(value,dict):
        if isinstance(value.get('exit_code'),int):return 'succeeded' if value['exit_code']==0 else 'failed'
        return execution_outcome(value.get('output',value.get('content',value.get('text',[]))))
    if isinstance(value,list):
        states=[execution_outcome(x) for x in value]
        if 'failed' in states:return 'failed'
        return 'succeeded' if states and all(x=='succeeded' for x in states) else 'unknown'
    return 'unknown'

LAUNCHERS=('python','python3','node')
READERS=('cat','head','tail','sed','nl','wc','less','more')
WRITES=('>','>>','>|','&>','&>>','>&')
VARIABLE=re.compile(r'\$(?:\{([A-Za-z_]\w*)\}|([A-Za-z_]\w*))')
UNRESOLVED=re.compile(r'\$(?:\{[^}]*\}|\w+|\([^)]*\)|.)?|`[^`]*`')

def expand(word,env):
    """Substitute variables assigned earlier in the same command; unknown ones stay literal."""
    for _ in range(8):
        new=VARIABLE.sub(lambda m:env.get(m.group(1) or m.group(2),m.group(0)),word)
        if new==word:break
        word=new
    return word

def names_target(target,line):
    """True when the error line names the target, or for an unresolved $VAR the literal path tail after it."""
    if '$' not in target and '`' not in target:return target in line
    tail=UNRESOLVED.split(target)[-1]
    if '/' not in tail or len(tail.strip('/'))<3:return False
    return bool(re.search(r'\S'+re.escape(tail)+r'(?![\w./-])',line))

def reader_targets(tool,args):
    """File operands of a plain reader; sed -i edits and option arguments are not targets."""
    if tool=='sed' and any(a.startswith('-i') or a.startswith('--in-place') for a in args):return []
    takes={'head':('-n','-c'),'tail':('-n','-c'),'sed':('-e','-f','--expression','--file')}.get(tool,())
    files=[];script=tool=='sed';i=0
    while i<len(args):
        a=args[i]
        if a in takes:script=False;i+=2;continue
        if a.startswith('-'):i+=1;continue
        if script:script=False
        else:files.append(a)
        i+=1
    return files

def shell_lookup(command):
    """Lookup targets in one shell command; heredoc and inline script bodies are never parsed.
    A stderr redirect or a pipe keeps a read a lookup; a stdout redirect to a file ends it. A relative
    target after cd stays relative, as the error line prints it; a $VAR target is expanded from earlier
    assignments in the same command and otherwise stays unresolved (names_target never matches it bare)."""
    if not isinstance(command,str) or '<<' in command:return []
    # 2>/dev/null, 2>&1 and 2>>log move stderr only, so they never turn a read into a write.
    command=re.sub(r'(?<!\S)2>&[12](?![^\s;&|<>])|(?<!\S)2>>?\s*[^\s;&|<>]+',' ',command)
    try:
        lex=shlex.shlex(command,posix=True,punctuation_chars=';&|<>\n');lex.whitespace=' \t\r';lex.whitespace_split=True;lex.commenters='#';tokens=list(lex)
    except ValueError:return []
    segments=[[]]
    for token in tokens:
        if token in (';','\n','&&','||','|'):segments.append([])
        else:segments[-1].append(token)
    targets=[];env={}
    for words in segments:
        if words and words[0]=='export':words=words[1:]
        assigned=0
        while assigned<len(words) and re.fullmatch(r'[A-Za-z_]\w*=.*',words[assigned],re.S):assigned+=1
        if words and assigned==len(words):
            for w in words:name,value=w.split('=',1);env[name]=expand(value,env)
            continue
        words=words[assigned:]
        if not words or any(t in WRITES or t in ('<','&') for t in words):continue
        words=[words[0]]+[expand(w,env) for w in words[1:]]
        positional=[w for w in words[1:] if not w.startswith('-')]
        if words[0] in READERS:targets+=reader_targets(words[0],words[1:])
        elif words[0] in ('rg','grep') and len(positional)>=2:targets+=positional[1:]
        elif words[0] in ('find','ls') and positional:targets+=positional[:1] if words[0]=='find' else positional
        elif words[0] in LAUNCHERS and len(words)>1 and not words[1].startswith('-'):
            names=[Path(w).name for w in words[1:]]
            if 'component-context.mjs' in names:
                rest=words[1+names.index('component-context.mjs')+1:]
                targets+=[w for w in rest if not w.startswith('-')]
            elif names[0]=='run.py' and len(words)>3 and words[2]=='read' and not words[3].startswith('-'):targets.append(words[3])
    return list(dict.fromkeys(targets))

def lookup_request(args):
    """Literal lookup targets requested by a call's recorded arguments, or [] when none is established."""
    if isinstance(args,str):
        try:args=json.loads(args)
        except ValueError:
            from wrapped import parse_calls
            calls=parse_calls(args) or []
            if not calls:return shell_lookup(args)
            items=[i for c in calls for i in c.get('items',[c])]
            return list(dict.fromkeys(t for i in items for t in lookup_request(i.get('args'))))
    if not isinstance(args,dict):return []
    if 'arguments' in args:return lookup_request(args['arguments'])
    command=args.get('cmd',args.get('command'))
    if isinstance(command,list) and command and isinstance(command[-1],str):command=command[-1]
    return shell_lookup(command)

def single_lookup(args):
    """Only a plain one-file reader can own a generic missing-file error."""
    if isinstance(args,str):
        try:return single_lookup(json.loads(args))
        except ValueError:command=args
    elif isinstance(args,dict):
        if 'arguments' in args:return single_lookup(args['arguments'])
        command=args.get('cmd',args.get('command'))
    else:return False
    if not isinstance(command,str) or re.search(r'[|;&<>`\n$]',command):return False
    try:words=shlex.split(command)
    except ValueError:return False
    return bool(words and words[0] in READERS and len(shell_lookup(command))==1)

def cite(event,needle=None):
    text=event['evidence']['text'];pos=text.find(needle) if needle else 0
    pos=max(0,pos)
    return {'eventId':event['id'],'traceLine':event['evidence']['traceLine'],'excerpt':text[max(0,pos-90):pos+330]}

def diagnose(data):
    from coverage_report import Coverage
    coverage=Coverage()
    events=data['events'];by={e['id']:e for e in events};sources={s['id']:s for s in data['sources']};findings=[]
    parents={l['to']:by[l['from']] for l in data['links'] if l['from'] in by and by[l['from']]['kind']=='call'}
    assessed={c['id']:0 for c in CATALOG}; catalog={c['id']:c for c in CATALOG}
    def add(detector,title,observation,evidence,source_ids=(),confidence='medium',metrics=None):
        c=catalog[detector];findings.append({'id':'diag-'+str(len(findings)+1),'detector':detector,'title':title,'observation':observation,'hypothesis':'This pattern may create avoidable context-routing work; the trace alone does not establish harm.' if detector!='late-guidance' else 'The guidance may have arrived after an action it governs; applicability and prior delivery are unverified.','confidence':confidence,'status':'candidate','evidence':evidence,'eventIds':list(dict.fromkeys(x['eventId'] for x in evidence)),'sourceIds':list(source_ids),'alternatives':c['alternatives'],'guidance':c['guidance'],'verification':c['verification'],'metrics':metrics or {}})
    reads={};edits={};guidance=[];failed=[];seen_guidance=set()
    for e in events:
        if e['kind']=='compaction':reads.clear()
        unique={}
        for x in e['exposures']:unique.setdefault(x['sourceId'],[]).append(x)
        for sid,xs in unique.items():
            if any(x['state']=='edited' for x in xs):edits[sid]=e;reads.pop(sid,None)
            rs=[x for x in xs if x['state'] in ('read','partial')]
            if not rs:continue
            x=next((x for x in rs if x['state']=='read'),rs[0]);assessed['repeated-retrieval']+=1
            old=reads.get(sid);overlap=None
            if old:
                prev,px=old
                if x['state']=='read' or px['state']=='read':overlap=True
                elif all(k in x and k in px for k in ('startLine','endLine')):overlap=max(x['startLine'],px['startLine'])<=min(x['endLine'],px['endLine'])
                if overlap is None:coverage.gap('repeated-retrieval','Partial returns lack comparable ranges','Record startLine/endLine for both partial returns, or explicit full-return metadata.',e)
                else:coverage.eligible('repeated-retrieval')
                if overlap:add('repeated-retrieval','Repeated return: '+sources[sid]['path'],'The same source was returned at steps %d and %d with overlapping coverage. No intervening edit or compaction is recorded.'%(prev['seq']+1,e['seq']+1),[cite(prev),cite(e)],[sid],metrics={'observedReturns':2})
            if not old:coverage.exclude('repeated-retrieval','No earlier return since the last observed edit/compaction')
            reads[sid]=(e,x)
            path=sources[sid]['path'];name=Path(path).name
            if name in ('SKILL.md','AGENTS.md','CLAUDE.md','README.md'):
                guidance.append((e,sid))
                if name!='README.md' and sid not in seen_guidance:
                    coverage.eligible('late-guidance')
                    assessed['late-guidance']+=1;scope=str(Path(path).parent).rstrip('/')+'/'
                    prior=[(s,ev) for s,ev in edits.items() if ev['seq']<e['seq'] and sources[s]['path'].startswith(scope)] if scope!='./' else []
                    if prior:
                        target,ev=prior[-1];add('late-guidance','Guidance first observed after a nearby edit','The first recorded return of '+path+' follows an edit beneath the same directory. Scope is a heuristic, not a verified obligation.',[cite(ev),cite(e)],[sid,target],'low')
                seen_guidance.add(sid)
        if e['kind']!='result':continue
        from truncation import sites
        locations=sites(e)
        if locations:
            parent=parents.get(e['id'])
            layers=', '.join(sorted(set(x['layer'] for x in locations)))
            add('truncation','Returned output was truncated · '+layers,'Recorded truncation at '+layers+'. Outer aggregation prevents reliable slot attribution; nested markers belong to command-output envelopes. Downstream harm is unproven.',([cite(parent)] if parent else [])+[cite(e,locations[0]['marker'])],confidence='high',metrics={'truncatedReturns':1,'truncationSites':locations})
        parent=parents.get(e['id']);units=e.get('toolCalls') or [{'output':e['evidence']['text'],'arguments':parent['evidence']['text'] if parent else '', 'outcome':execution_outcome(e['evidence']['text'])}]
        for unit in units:
            output=unpack(unit.get('output',''));args=unit.get('arguments','');assessed['truncation']+=1
            tool_lookup=unit.get('tool') in ('Read','Glob','Grep') or bool(re.search(r'read_file|readFile',args))
            requested=[] if tool_lookup else lookup_request(args);lookup=tool_lookup or bool(requested)
            if unit.get('output') not in (None,'',[],{}):coverage.eligible('truncation')
            else:coverage.gap('truncation','Output envelope missing','Preserve the result envelope for this call, including truncation metadata.',e)
            if not lookup:continue
            if not parent:
                coverage.gap('failed-discovery','Lookup result has no matched call','Record the call ID linking this lookup result to its request.',e);continue
            assessed['failed-discovery']+=1
            status=unit.get('outcome')
            if status not in ('failed','rejected','succeeded','success'):status=execution_outcome(unit.get('output'))
            if status not in ('failed','rejected','succeeded','success'):
                coverage.gap('failed-discovery','Lookup execution status is unknown','Record exit_code or explicit success/failure for this lookup result.',e)
            else:coverage.eligible('failed-discovery')
            error=re.search(r'(?:No such file or directory|Unknown component id: [\w-]+|cannot (?:access|open)|command not found)',output,re.I)
            if not error or unit.get('outcome') not in ('failed','rejected'):continue
            # In a compound command the error must name a requested target, or it may belong to another subcommand.
            line=output[output.rfind('\n',0,error.start())+1:output.find('\n',error.end()) if '\n' in output[error.end():] else len(output)]
            if requested and not any(names_target(t,line) for t in requested) and not (single_lookup(args) and line.strip().lower()=='no such file or directory'):
                if all('$' in t or '`' in t for t in requested):coverage.gap('failed-discovery','Lookup target is an unresolved variable','Record the expanded path, or assign the variable earlier in the same command.',e)
                continue
            if not any(f['detector']=='failed-discovery' and e['id'] in f['eventIds'] for f in findings):add('failed-discovery','Lookup failed: '+error.group(),'A matched lookup call returned a recorded failure. This establishes a failed attempt, not a wasted or unnecessary attempt.',[cite(parent),cite(e,error.group())],metrics={'failedResults':1})
            # Exact literal paths from the request, not arbitrary paths printed in output.
            targets=re.findall(r'(?:/[\w.~-]+){2,}(?:\.[\w-]+)?|[\w.-]+/[\w./-]+',args)
            for target in dict.fromkeys(targets):
                if any(g['seq']<parent['seq'] for g,_ in guidance):coverage.eligible('broken-reference')
                else:coverage.gap('broken-reference','No earlier returned guidance to compare','Preserve the earlier guidance return containing the alleged pointer; a current file cannot establish historical instructions.',parent)
                assessed['broken-reference']+=1
                prior=next(((g,s) for g,s in reversed(guidance) if g['seq']<parent['seq'] and target in unpack(g['evidence']['text'])),None)
                if prior:
                    g,sid=prior;add('broken-reference','Previously exposed path failed to resolve','The failed lookup requested '+target+', which appears in earlier returned guidance. Verify that this path, rather than another command in the batch, caused the failure.',[cite(g,target),cite(parent,target),cite(e,error.group())],[sid],'low');break
    if data.get('bundle'):
        from reconstruct import signals
        extra,counts=signals(data,coverage);findings.extend(extra);assessed.update(counts)
    from delivery import analyze as analyze_delivery
    delivery_counts,delivery_summary=analyze_delivery(data,coverage,add,cite)
    assessed.update(delivery_counts)
    from triage import classify
    for finding in findings:finding['triage']=classify(finding,by)
    data['diagnostics']={'version':VERSION,'catalog':CATALOG,'findings':findings,'coverage':[{'detector':c['id'],'assessed':assessed[c['id']],'findings':sum(f['detector']==c['id'] for f in findings),'status':'assessed' if assessed[c['id']] else 'insufficient-evidence'} for c in CATALOG],'limits':['Candidates are not proven defects or causal explanations. Confidence describes the observed signal, not the proposed remedy.','No exact retained-context accounting, relevance verdict, wasted-token estimate, or counterfactual improvement is inferred.','Unknown/opaque wrappers and missing outcomes reduce coverage. No findings does not mean no problems.','No baseline comparison was performed; proposed validations require comparable tasks and correctness checks.','Guidance applicability is directory-based unless separately reviewed. Search failure detection excludes ordinary no-match exit codes.']}
    data['diagnostics']['delivery']=delivery_summary
    matched_calls={parent['id'] for parent in parents.values()}
    for e in events:
        if e['kind']=='call' and e['id'] not in matched_calls:
            coverage.gap('truncation','Call has no matched result','Record the matching result envelope or explicit failure/cancellation for this call.',e)
            args=e['evidence']['text']
            if re.search(r'\b(?:Read|Glob|Grep)\b|read_file|readFile',args) or lookup_request(args):
                coverage.gap('failed-discovery','Lookup call has no matched result','Record the matching lookup result and explicit execution status.',e)
    coverage.finish(data['diagnostics']['coverage'],data)
    return data

def validate_diagnostics(data):
    d=data.get('diagnostics')
    if d is None:return
    by={e['id']:e for e in data['events']};sources={s['id'] for s in data['sources']};ids=set()
    if d.get('version')!=VERSION or not isinstance(d.get('findings'),list):raise ValueError('Invalid diagnostics version or findings')
    for f in d['findings']:
        if f['id'] in ids or f['detector'] not in {c['id'] for c in CATALOG}:raise ValueError('Invalid diagnostic identity')
        ids.add(f['id'])
        if not f['evidence'] or any(x not in sources for x in f['sourceIds']):raise ValueError('Invalid diagnostic source/evidence')
        for c in f['evidence']:
            e=by.get(c['eventId'])
            if not e or not c['excerpt'] or c['excerpt'] not in e['evidence']['text'] or c['traceLine']!=e['evidence']['traceLine']:raise ValueError('Invalid diagnostic citation')
        t=f.get('triage')
        if t:
            if t.get('state') not in ('needs-review','likely-benign') or not t.get('reason') or not t.get('nextEvidence'):raise ValueError('Invalid triage')
            if t['state']=='likely-benign' and not t.get('evidence'):raise ValueError('Missing triage evidence')
            for c in t.get('evidence',[]):
                e=by.get(c['eventId'])
                if not e or not c['excerpt'] or c['excerpt'] not in e['evidence']['text'] or c['traceLine']!=e['evidence']['traceLine']:raise ValueError('Invalid triage citation')
        if any(x not in by for x in f['eventIds']):raise ValueError('Invalid diagnostic event')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--delivery-contract',type=Path);a=p.parse_args();d=json.loads(a.data.read_text());
    if a.delivery_contract:d['deliveryContract']=json.loads(a.delivery_contract.read_text())
    d=diagnose(d);validate_diagnostics(d);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d['diagnostics']['coverage']))
