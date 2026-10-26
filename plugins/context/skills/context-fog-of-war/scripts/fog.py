#!/usr/bin/env python3
"""Offline Codex trace hydration and portable artifact rendering (stdlib only)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnostics import diagnose, validate_diagnostics
from connections import connect
from candidates import discover_candidates
from wrapped import parse_calls, pair_outputs, expand_pairs, read_requests, corroborate

ROOT = Path(__file__).resolve().parents[1]
STATES = ['discovered', 'partial', 'read', 'edited']
KINDS = ['message', 'call', 'result', 'compaction', 'context', 'unknown']


def validate(data):
    """Validate against the shipped schema's supported vocabulary, plus references."""
    schema = json.loads((ROOT / 'references/session.schema.json').read_text())
    def walk(value, rule, path='$'):
        if '$ref' in rule:
            rule = schema['$defs'][rule['$ref'].split('/')[-1]]
        types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
        if 'type' in rule and (not isinstance(value, types[rule['type']]) or rule['type'] == 'integer' and isinstance(value, bool)):
            raise ValueError(f'{path}: expected {rule["type"]}')
        if 'enum' in rule and value not in rule['enum']:
            raise ValueError(f'{path}: unsupported value {value!r}')
        if isinstance(value, dict):
            for key in rule.get('required', []):
                if key not in value: raise ValueError(f'{path}: missing {key}')
            for key, val in value.items():
                if key in rule.get('properties', {}): walk(val, rule['properties'][key], path+'.'+key)
                elif rule.get('additionalProperties') is False: raise ValueError(f'{path}: unknown field {key}')
        if isinstance(value, list):
            for i, val in enumerate(value): walk(val, rule.get('items', {}), f'{path}[{i}]')
        if isinstance(value, int) and value < rule.get('minimum', value): raise ValueError(f'{path}: below minimum')
        if isinstance(value, str) and len(value) < rule.get('minLength', 0): raise ValueError(f'{path}: empty')
    walk(data, schema)
    sources = {s['id'] for s in data['sources']}
    events = {e['id'] for e in data['events']}
    if len(sources) != len(data['sources']) or len(events) != len(data['events']): raise ValueError('Duplicate IDs')
    workflow_ids = set()
    for workflow in data.get('workflows', []):
        if workflow['id'] in workflow_ids: raise ValueError('Duplicate workflow ID')
        workflow_ids.add(workflow['id'])
        if [s['kind'] for s in workflow['stages']] != ['guidance','action','evidence','outcome']: raise ValueError('Workflow requires four ordered stages')
        for stage in workflow['stages']:
            if stage['state'] != 'unknown' and not stage['evidence']: raise ValueError('Workflow status requires evidence')
            for ref in stage['evidence']:
                if 'eventId' in ref:
                    event = next((e for e in data['events'] if e['id'] == ref['eventId']), None)
                    if not event or not ref['excerpt'] or ref['excerpt'] not in event['evidence']['text']: raise ValueError('Invalid workflow event citation')
                elif not ref.get('artifact') or not ref.get('pointer'): raise ValueError('Workflow evidence requires event or artifact pointer')
    for i, event in enumerate(data['events']):
        if event['seq'] != i: raise ValueError('Event seq must match array order, starting at zero')
        for exposure in event['exposures']:
            if exposure['sourceId'] not in sources: raise ValueError('Unknown source reference')
            if 'startLine' in exposure and exposure.get('endLine', exposure['startLine']) < exposure['startLine']: raise ValueError('Reversed line range')
    for link in data['links']:
        if link['from'] not in events or link['to'] not in events: raise ValueError('Unknown event link')
    if data['schemaVersion'] == 2:
        for field in ('decisions', 'guidanceEdges', 'findings'):
            if field not in data: raise ValueError('v2 requires ' + field)
    by_event = {e['id']: e for e in data['events']}
    def unique(items):
        ids = {x['id'] for x in items}
        if len(ids) != len(items): raise ValueError('Duplicate analysis IDs')
        return ids
    decisions = unique(data.get('decisions', []))
    edges = unique(data.get('guidanceEdges', []))
    unique(data.get('findings', []))
    for collection in ('decisions', 'guidanceEdges', 'findings'):
        for item in data.get(collection, []):
            if not item['evidence']: raise ValueError('Analysis requires evidence')
            for citation in item['evidence']:
                event = by_event.get(citation['eventId'])
                if not event or citation['excerpt'] not in event['evidence']['text']:
                    raise ValueError('Citation must quote its recorded event exactly')
            if collection == 'decisions' and any(x not in edges for x in item['edgeIds']):
                raise ValueError('Unknown guidance edge')
            if collection == 'guidanceEdges':
                if any(s not in {x['id'] for x in data['sources']} for s in item.get('sourceIds', [])): raise ValueError('Unknown guidance source')
                if item['from'] not in events or item['to'] not in events: raise ValueError('Unknown guidance endpoint')
                if by_event[item['from']]['seq'] > by_event[item['to']]['seq']: raise ValueError('Guidance edges must follow trace order')
            if collection == 'findings' and item['decisionId'] not in decisions:
                raise ValueError('Unknown finding decision')
    for c in data.get('contextRecords', []):
        if c['sourceId'] not in sources or c['eventId'] not in by_event or c['evidence']['eventId'] != c['eventId'] or not c['evidence']['excerpt'] or c['evidence']['excerpt'] not in by_event[c['eventId']]['evidence']['text']: raise ValueError('Invalid context evidence')
    for c in data.get('candidates', []):
        if c['sourceId'] not in sources or c['eventId'] not in by_event or c['evidence']['eventId'] != c['eventId'] or c['evidence']['excerpt'] not in by_event[c['eventId']]['evidence']['text']: raise ValueError('Invalid candidate evidence')
    for child in data.get('childSessions', []):
        if child['parentEventId'] not in events or child['resultEventId'] not in events: raise ValueError('Invalid child session link')
        if child['status']=='hydrated': validate(child['report'])
    for item in data.get('messageRetention', []):
        if item['eventId'] not in events or item['messageEventId'] not in events: raise ValueError('Invalid message retention link')
    validate_diagnostics(data)
    return data


def inventory(repo):
    try:
        result = subprocess.run(['git', '-C', str(repo), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], capture_output=True, check=True)
        paths = sorted(set(result.stdout.decode().split('\0')) - {''})
        mode = 'Git tracked and unignored working-tree files'
    except (OSError, subprocess.CalledProcessError):
        paths = []
        for folder, dirs, files in os.walk(repo, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in {'.git', 'node_modules', '.venv', '__pycache__'} and not Path(folder, d).is_symlink())
            paths += [str(Path(folder, f).relative_to(repo)) for f in sorted(files)]
        mode = 'Directory inventory; excludes .git, node_modules, .venv, __pycache__; no symlink traversal'
    # Inventory names only: no unrelated file contents are copied into the artifact.
    paths = [p for p in paths if (repo / p).is_file() and not (repo / p).is_symlink()]
    try:
        revision = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, check=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError): revision = 'unknown'
    return paths, mode, revision


def tool_outcome(value, settlement):
    if settlement=='rejected': return 'failed'
    if isinstance(value,dict):
        if value.get('isError') is True:return 'failed'
        metadata=value.get('metadata')
        code=value.get('exit_code',metadata.get('exit_code') if isinstance(metadata,dict) else None)
        if isinstance(code,int) and not isinstance(code,bool):return 'succeeded' if code==0 else 'failed'
    if isinstance(value,str):
        match=re.search(r'(?:Process exited with code|Process exit code:)\s*(\d+)',value)
        if match:return 'succeeded' if int(match[1])==0 else 'failed'
    return 'unknown'


def scrub_media(value):
    if isinstance(value, dict):
        return {k: ('[Image bytes omitted; original trace contains image]' if k == 'image_url' and isinstance(v,str) and v.startswith('data:') else scrub_media(v)) for k,v in value.items()}
    if isinstance(value,list): return [scrub_media(v) for v in value]
    return value


def hydrate(trace, repo, trace_root=None, title=None, source_roots=None, through_line=None):
    paths, mode, revision = inventory(repo)
    data = {'schemaVersion': 2, 'decisions': [], 'guidanceEdges': [], 'findings': [], 'session': {'title': title or trace.stem, 'trace': trace.name, 'traceSha256': hashlib.sha256(trace.read_bytes()).hexdigest(), 'repo': repo.name, 'revision': revision, 'host':'codex', 'adapterVersion':'1.2.0'}, 'coverage': {'inventory': mode, 'warnings': ['Snapshot is an analyzer inventory, not proof of historical file content.', 'Exposure does not establish understanding, causal influence, or active-context retention.', 'Literal sequential and Promise.all/allSettled wrappers are decoded in input order without executing code. Dynamic or ambiguous wrappers remain opaque. Compound reads require returned-content corroboration against allowed current sources.']}, 'sources': [], 'events': [], 'links': []}
    source_map = {}
    def source(path, inventoried=False):
        if path not in source_map:
            source_map[path] = f's{len(source_map)+1}'
            data['sources'].append({'id': source_map[path], 'path': path, 'inventoried': inventoried})
        return source_map[path]
    for path in paths: source(path, True)
    calls = {}
    recorded_store={};store_event=None
    cwd = trace_root or str(repo)
    trace_base = cwd
    counts = {'malformed': 0, 'ignored': 0, 'unmatched': 0, 'opaque': 0, 'wrapped_decoded': 0, 'wrapped_opaque': 0}
    roots = [repo.resolve()] + [Path(p).expanduser().resolve() for p in (source_roots or [])]
    def normalize(path, workdir):
        # Lexical path mapping only. Never resolve/read trace-provided filesystem paths.
        if not path or any(x in path for x in ['$', '*', '?', '\n']): return None
        abs_path = os.path.normpath(path if path.startswith('/') else os.path.join(workdir, path))
        rel = os.path.relpath(abs_path, trace_base)
        return rel if not rel.startswith('../') else abs_path
    def add(kind, label, payload, line, timestamp, actor='harness'):
        event = {'id': f'e{len(data["events"])+1}', 'seq': len(data['events']), 'kind': kind, 'label': label, 'actor': actor, 'timestamp': timestamp or '', 'evidence': {'traceLine': line, 'text': json.dumps(scrub_media(payload), ensure_ascii=False, indent=2)}, 'exposures': []}
        data['events'].append(event)
        assembly = payload if payload.get('type') == 'context_assembly' else payload.get('payload', {})
        if isinstance(assembly, dict) and assembly.get('type') == 'context_assembly':
            event['kind'] = 'context'
            for item in assembly.get('sources', []) if isinstance(assembly.get('sources'), list) else []:
                if not isinstance(item, dict) or not isinstance(item.get('path'), str) or item.get('status') not in ('included', 'removed'): continue
                path = normalize(item['path'], cwd)
                if path:
                    data.setdefault('contextRecords', []).append({'sourceId': source(path), 'eventId': event['id'], 'status': item['status'], 'evidence': {'eventId': event['id'], 'excerpt': event['evidence']['text']}})
        return event
    def expose(event, path, state, basis, start=None, end=None):
        if path:
            item = {'sourceId': source(path), 'state': state, 'basis': basis}
            if start is not None: item['startLine'] = start
            if end is not None: item['endLine'] = end
            if item not in event['exposures']: event['exposures'].append(item)
    def analyze(previous,event,name,args,output):
        if name.split('.')[-1] == 'view_image' and isinstance(args,dict) and isinstance(output,dict) and output.get('type') in ('image','input_image'):
            path=normalize(args.get('path',''),cwd)
            expose(previous,path,'discovered','Literal image path in recorded request')
            expose(event,path,'read','Matched wrapper returned image pixels; bytes omitted from artifact')
            return
        if isinstance(output, str):
            try: decoded = json.loads(output)
            except ValueError: decoded = None
        else: decoded = output
        text = output if isinstance(output, str) else json.dumps(output)
        exit_code = None
        if isinstance(decoded, dict):
            text = decoded.get('output', text)
            if not isinstance(text, str): text = json.dumps(text)
            exit_code = decoded.get('exit_code', (decoded.get('metadata') or {}).get('exit_code'))
        match = re.search(r'(?:Process exited with code|Process exit code:)\s*(\d+)', text)
        if match: exit_code = int(match.group(1))
        body = text.split('Final output:\n', 1)[-1]
        if '\nOutput:\n' in body: body = body.split('\nOutput:\n', 1)[-1]
        cmd = args.get('cmd', args.get('command', ''))
        workdir = args.get('workdir', cwd)
        if not isinstance(workdir, str): workdir = cwd
        if not workdir.startswith('/'): workdir = os.path.normpath(os.path.join(cwd, workdir))
        if not isinstance(cmd, str): cmd = ''
        # Maintained paginated reader: attribute only a matched literal request and returned source field.
        try: reader_words=shlex.split(cmd)
        except ValueError: reader_words=[]
        if exit_code==0 and len(reader_words) in (4,6) and reader_words[0] in ('python','python3') and reader_words[1].endswith('/scripts/run.py') and reader_words[2]=='read' and (len(reader_words)==4 or reader_words[4]=='--page' and reader_words[5].isdigit()):
            try: page=json.loads(body)
            except (ValueError,TypeError): page=None
            if isinstance(page,dict) and page.get('source')==reader_words[3] and isinstance(page.get('content'),str):
                path=normalize(str(Path(reader_words[1]).parent.parent/reader_words[3]),workdir)
                expose(previous,path,'discovered','Literal paginated reader request')
                full=page.get('page')==1 and page.get('pages')==1 and page.get('nextPage') is None
                expose(event,path,'read' if full else 'partial','Returned paginated source matches request; pages are not file line ranges')
                return
        if name.split('.')[-1] in ('exec_command', 'shell_command'):
            requests=read_requests(cmd)
            corroborated=False
            for requested,start_line,end_line in requests:
                path=normalize(requested,workdir)
                expose(previous,path,'discovered','Literal path in recorded tool request; return not yet available')
                absolute=os.path.normpath(requested if requested.startswith('/') else os.path.join(workdir,requested))
                # Remap historical repository paths to the supplied snapshot for byte matching.
                witness=repo/path if path and not path.startswith('/') else Path(absolute)
                state=corroborate(witness,roots,body,start_line,end_line) if path and body.strip() else None
                if state:
                    corroborated=True
                    expose(event,path,state,'Returned text matches bounded current-source bytes; historical version/retention unknown',start_line if state=='partial' and start_line else None,end_line if state=='partial' and start_line else None)
            if corroborated:
                return
        try: words = shlex.split(cmd)
        except ValueError: words = []
        safe = not re.search(r'[|;&<>`\n]|\$\(', cmd)
        if name.split('.')[-1] in ('exec_command', 'shell_command') and safe and words:
            tool = words[0]
            path = None; start = end = None; state = 'partial'
            if tool == 'cat' and len(words) == 2 and not words[1].startswith('-'):
                path = normalize(words[1], workdir); state = 'read'
            elif tool == 'sed' and len(words) == 4 and words[1] == '-n':
                selection = re.fullmatch(r'(\d+),(\d+)p', words[2])
                if selection:
                    start, end = map(int, selection.groups()); path = normalize(words[3], workdir)
            elif tool == 'head' and len(words) == 4 and words[1] == '-n' and words[2].isdigit():
                start, end = 1, int(words[2]); path = normalize(words[3], workdir)
            elif tool == 'head' and len(words) == 4 and words[1] == '-c' and words[2].isdigit() and int(words[2]) > 0 and not words[3].startswith('-'):
                # Byte limits do not establish line coverage or a complete read.
                path = normalize(words[3], workdir)
            if path:
                expose(previous, path, 'discovered', 'Path named in tool request; no read assumed at call time')
                if body.strip() and exit_code == 0:
                    if re.search('truncat', text, re.I): state = 'partial'; start = end = None
                    expose(event, path, state, 'Successful single-source command with returned output', start, end)
                return
            if tool == 'rg' and exit_code in (0, 1):
                for output_line in body.splitlines():
                    if '--files' in words:
                        path = normalize(output_line.strip(), workdir)
                        if path in source_map: expose(event, path, 'discovered', 'Path returned by rg --files')
                    else:
                        found = re.match(r'(.+?):(\d+):(.*)', output_line)
                        if found:
                            path = normalize(found[1], workdir)
                            expose(event, path, 'partial', 'Numbered search result', int(found[2]), int(found[2]))
                return
        if name.split('.')[-1] == 'apply_patch' and exit_code in (None, 0) and 'Success.' in body:
            for marker, path in re.findall(r'^([AMD]) (.+)$', body, re.M):
                expose(event, normalize(path, cwd), 'edited', 'Successful apply_patch output; edit is not evidence of a prior read')
            return
        counts['opaque'] += 1
        return
    trace_lines=trace.read_text().splitlines()
    if through_line is not None: trace_lines=trace_lines[:through_line]
    data['session']['traceSha256']=hashlib.sha256(('\n'.join(trace_lines)+'\n').encode()).hexdigest()
    if through_line is not None: data['coverage']['warnings'].append(f'Trace cutoff: original line {through_line}.')
    for line, raw in enumerate(trace_lines, 1):
        if not raw.strip(): continue
        try:
            record = json.loads(raw)
            if not isinstance(record, dict): raise ValueError()
        except (ValueError, TypeError): counts['malformed'] += 1; continue
        payload = record.get('payload', record)
        if not isinstance(payload, dict):
            add('unknown', 'Unrecognized record', record, line, record.get('timestamp')); continue
        typ = record.get('type')
        sub = payload.get('type', typ)
        if typ in ('token_usage_record','world_state') or sub == 'reasoning':
            counts['ignored'] += 1; continue
        ts = record.get('timestamp', '')
        if typ == 'session_meta':
            if not trace_root and payload.get('cwd'): cwd = trace_base = payload['cwd']
            data['session']['title'] = title or payload.get('id', trace.stem)
            continue
        if typ == 'turn_context':
            cwd = payload.get('cwd', cwd)
            add('context', 'Recorded turn context', payload, line, ts)
            continue
        if typ == 'compacted' or sub in ('context_compacted', 'compaction'):
            add('compaction', 'Context compaction · retention unknown', payload, line, ts); continue
        if sub in ('function_call', 'custom_tool_call'):
            name = payload.get('name', 'unknown')
            args = payload.get('arguments', payload.get('input', {}))
            if isinstance(args, str):
                try: args = json.loads(args)
                except ValueError: args = {'input': args}
            if not isinstance(args, dict): args = {'input': args}
            cmd = args.get('cmd', args.get('command', ''))
            if not isinstance(cmd, str): cmd = ''
            event = add('call', name + (': ' + cmd[:110] if cmd else ''), payload, line, ts)
            calls[payload.get('call_id', event['id'])] = (event, name, args)
            continue
        if sub in ('function_call_output', 'custom_tool_call_output'):
            event = add('result', 'Tool output', payload, line, ts)
            call = calls.pop(payload.get('call_id'), None)
            if not call: counts['unmatched'] += 1; continue
            previous, name, args = call
            event['label'] = name + ' → output'
            data['links'].append({'from': previous['id'], 'to': event['id'], 'kind': 'recorded', 'reason': 'Matched Codex call_id'})
            output = payload.get('output', '')
            if name.split('.')[-1] == 'exec':
                from stored import snapshot,prefix_outputs
                code=args.get('input','')
                stored_snapshot=snapshot(code,output)
                consumer=bool(recorded_store) and 'load(' in code
                nested=parse_calls(code,{'__recorded_store__':recorded_store}) if consumer else parse_calls(code)
                paired=pair_outputs(output,nested) if nested else None
                partial_store=False
                if consumer and paired is None:
                    nested=parse_calls(code,{'__recorded_store__':recorded_store},_prefix=True)
                    paired=prefix_outputs(output,nested) if nested else None
                    partial_store=paired is not None
                if stored_snapshot is not None:
                    recorded_store=stored_snapshot;store_event=event['id']
                    counts['stored_snapshots']=counts.get('stored_snapshots',0)+1
                elif nested is None and not consumer:
                    recorded_store={};store_event=None
                if consumer and paired is not None and store_event:
                    data['links'].append({'from':store_event,'to':previous['id'],'kind':'recorded','reason':'Literal store/load lookup from an explicitly emitted snapshot; image returns paired in emission order'})
                    counts['stored_consumers']=counts.get('stored_consumers',0)+1
                if partial_store:
                    counts['stored_opaque_suffix']=counts.get('stored_opaque_suffix',0)+1
                    data['coverage']['warnings'].append('Stored-loop attribution recovered only a verified emitted prefix at trace line '+str(line)+'. Remaining outputs and code are opaque.')
                expanded=expand_pairs(nested,paired) if paired is not None else None
                if expanded is None:
                    counts['wrapped_opaque'] += 1
                    if consumer:recorded_store={};store_event=None
                else:
                    counts['wrapped_decoded'] += 1
                    batches={tag.split(' slot ')[0] for _,_,_,tag in expanded if tag.startswith('Promise.')}
                    counts['parallel_batches']=counts.get('parallel_batches',0)+len(batches)
                    names=[]
                    attribution=[]
                    event['toolCalls']=[];previous['toolCalls']=[]
                    for request,result,status,tag in expanded:
                        nested_args=request['args'] if isinstance(request['args'],dict) else {'input':request['args']}
                        names.append(request['name'])
                        attribution.append({'position':tag,'tool':request['name'],'arguments':nested_args,'status':status,'output':scrub_media(result)})
                        item={'position':tag,'tool':request['name'],'arguments':json.dumps(nested_args,ensure_ascii=False,indent=2),'output':json.dumps(scrub_media(result),ensure_ascii=False,indent=2),'settlement':status,'outcome':tool_outcome(result,status)}
                        event['toolCalls'].append(item)
                        previous['toolCalls'].append(dict(item,output='',settlement='pending',outcome='pending'))
                        if status=='rejected':
                            counts['parallel_rejected']=counts.get('parallel_rejected',0)+1
                            continue
                        before_call=len(previous['exposures']);before_result=len(event['exposures'])
                        analyze(previous,event,request['name'],nested_args,result)
                        for target,offset in [(previous,before_call),(event,before_result)]:
                            for exposure in target['exposures'][offset:]:exposure['basis']=('Recorded store snapshot '+str(store_event)+' → ' if consumer else '')+tag+' → '+request['name']+': '+exposure['basis']
                    event['evidence']['text']+='\n\nDecoded tool/output attribution (input order):\n'+json.dumps(attribution,ensure_ascii=False,indent=2)
                    previous['label']='Wrapped · '+' → '.join(names)
                    event['label']='Wrapped output · '+' → '.join(names)
                    if partial_store:recorded_store={};store_event=None
            else:
                analyze(previous,event,name,args,output)
            continue
        if sub == 'message':
            actor = payload.get('role', 'unknown')
            add('message', actor.capitalize() + ' message', payload, line, ts, actor); continue
        if typ == 'event_msg':
            # Messages also occur as response_item; skip duplicates and telemetry.
            counts['ignored'] += 1; continue
        add('unknown', 'Unrecognized trace record', record, line, ts)
    for key, count in counts.items():
        if count: data['coverage']['warnings'].append(f'{key}: {count} record(s).')
    data['coverage']['warnings'].append('Bounded literal loops require matched emitted slots. store/load image loops use only explicitly emitted, validated snapshots; an ordered verified prefix may be recovered with its remaining suffix marked opaque. Hidden stored values and arbitrary result-dependent code remain unsupported. Returned-source counts are lower bounds; absent direct helper names do not establish missing internal execution.')
    if calls: data['coverage']['warnings'].append(f'{len(calls)} call(s) have no recorded output.')
    if not data['events']: raise ValueError('No usable trace events')
    return validate(diagnose(connect(discover_candidates(data))))


def render(data, output):
    validate(data)
    shell = (ROOT / 'assets/shell.html').read_text()
    # JSON is inert text; escaping < prevents </script> from ending the data block.
    embedded = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    output.parent.mkdir(parents=True, exist_ok=True)
    children=data.get('childSessions',[])
    if children:
        manifest=[]
        for index, child in enumerate(children):
            if child['status']!='hydrated':
                manifest.append({k:v for k,v in child.items() if k!='report'});continue
            name=output.stem+'-child-'+str(index+1)
            render(child['report'],output.parent/(name+'.html'))
            (output.parent/(name+'.json')).write_text(json.dumps(child['report'],indent=2)+'\n')
            manifest.append(dict(agentId=child['agentId'],parentEventId=child['parentEventId'],resultEventId=child['resultEventId'],html=name+'.html',json=name+'.json'))
        (output.parent/(output.stem+'-sessions.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    output.write_text(shell.replace('/*__FOG_CSS__*/', (ROOT / 'assets/app.css').read_text()).replace('/*__FOG_JS__*/', (ROOT / 'assets/app.js').read_text()).replace('"__FOG_DATA__"', embedded))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    h = sub.add_parser('hydrate'); h.add_argument('--trace', type=Path, required=True); h.add_argument('--repo', type=Path, required=True); h.add_argument('--trace-root'); h.add_argument('--title'); h.add_argument('--out', type=Path, required=True); h.add_argument('--source-root', action='append', default=[], help='Additional allowed current-source root for returned-byte corroboration'); h.add_argument('--through-line', type=int, help='Inclusive original trace cutoff'); h.add_argument('--host',choices=['auto','codex','claude'],default='auto'); h.add_argument('--include-system-prompt',action='store_true'); h.add_argument('--no-children',action='store_true')
    r = sub.add_parser('render'); r.add_argument('--data', type=Path, required=True); r.add_argument('--out', type=Path, required=True)
    v = sub.add_parser('validate'); v.add_argument('data', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'hydrate':
            if not args.repo.is_dir(): raise ValueError('--repo must be an extracted snapshot directory')
            if args.through_line is not None and args.through_line < 1: raise ValueError('--through-line must be positive')
            host=args.host
            if host=='auto':
                from claude import records
                kinds=set()
                for line,record in records(args.trace,args.through_line):
                    if record:
                        if record.get('type')=='session_meta': kinds.add('codex')
                        if record.get('sessionId') and record.get('type') in ('user','assistant','attachment'): kinds.add('claude')
                    if line>=100: break
                if len(kinds)!=1: raise ValueError('Cannot identify trace host; pass --host explicitly')
                host=kinds.pop()
            if host=='claude':
                from claude import hydrate as hydrate_claude
                data=hydrate_claude(args.trace,args.repo.resolve(),args.trace_root,args.title,args.through_line,args.include_system_prompt,not args.no_children)
            else:
                data = hydrate(args.trace, args.repo.resolve(), args.trace_root, args.title, args.source_root, args.through_line)
                data['session'].update(host='codex',adapterVersion='1.2.0')
            args.out.parent.mkdir(parents=True, exist_ok=True); args.out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        elif args.action == 'render': render(json.loads(args.data.read_text()), args.out)
        else: validate(json.loads(args.data.read_text()))
    except (ValueError, OSError) as error: parser.exit(1, f'Error: {error}\n')
    print('Validated' if args.action == 'validate' else str(args.out))

if __name__ == '__main__': main()
