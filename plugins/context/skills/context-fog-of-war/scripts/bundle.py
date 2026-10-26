"""Bounded, inert session-bundle parsing and declarative field mapping (stdlib)."""
import fnmatch
import copy
import hashlib
import json
import os
from pathlib import Path

VERSION='1.0.0'
TYPES={'model_request','retrieval','tool_result','delivery','evaluation','stream_chunk'}
FIELDS={'eventId','conversationId','requestId','targetRequestId','operationId','attempt','timestamp','chunkIds','includedChunkIds','toolResultIds','resultId','success','complete','artifactHash','deliveryId','targetDeliveryId','streamId','sequence','totalChunks','text','maxTokens','outputTokens','stopReason'}
DEFAULT={'version':1,'rules':[{'filePattern':'*','recordPath':'','fields':{'eventType':'/eventType',**{k:'/'+k for k in sorted(FIELDS)}}}]}

def hash_value(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def pointer(value,path):
    if path=='':return value
    if not isinstance(path,str) or not path.startswith('/'):raise ValueError('Expected JSON pointer')
    for key in path[1:].split('/'):
        key=key.replace('~1','/').replace('~0','~')
        value=value[int(key)] if isinstance(value,list) else value[key]
    return value

def validate_manifest(manifest):
    if not isinstance(manifest,dict):raise ValueError('Mapping must be an object')
    if manifest.get('version')!=1 or not isinstance(manifest.get('rules'),list) or not manifest['rules']:raise ValueError('Mapping requires version 1 and nonempty rules')
    for rule in manifest['rules']:
        if not isinstance(rule,dict):raise ValueError('Mapping rule must be an object')
        if not isinstance(rule.get('filePattern'),str) or not isinstance(rule.get('fields'),dict):raise ValueError('Invalid mapping rule')
        if rule.get('eventType') not in TYPES|{None}:raise ValueError('Unsupported event type')
        for key,path in rule['fields'].items():
            if key not in FIELDS|{'eventType'} or not isinstance(path,str) or (path and not path.startswith('/')):raise ValueError('Unknown field or invalid pointer')
        if not isinstance(rule.get('decodeJson',[]),list) or any(not isinstance(x,str) or not x.startswith('/') for x in rule.get('decodeJson',[])):raise ValueError('Invalid decodeJson pointer list')
        if not isinstance(rule.get('recordPath',''),str) or (rule.get('recordPath') and not rule['recordPath'].startswith('/')):raise ValueError('Invalid recordPath')
    return manifest

def ingest(folder,manifest=None,exclude=None,max_files=1000,max_bytes=8*1024*1024,max_total=64*1024*1024):
    folder=Path(folder).resolve()
    if not folder.is_dir():raise ValueError('Bundle must be a directory')
    manifest=validate_manifest(manifest or DEFAULT)
    inventory=[];records=[];issues=[];total=0;count=0
    excluded=Path(exclude).resolve() if exclude else None
    for base,dirs,files in os.walk(folder,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in {'.git','node_modules','.venv','dist','build','__pycache__'} and not Path(base,d).is_symlink() and (not excluded or Path(base,d).resolve()!=excluded))
        for name in sorted(files):
            path=Path(base,name);rel=path.relative_to(folder).as_posix();count+=1
            if count>max_files:raise ValueError('Bundle file limit exceeded; narrow the selected folder')
            if path.is_symlink():inventory.append(dict(file=rel,status='symlink-skipped'));continue
            size=path.stat().st_size
            if size>max_bytes or total+size>max_total:
                inventory.append(dict(file=rel,status='size-limit',size=size));issues.append('size-limit');continue
            raw=path.read_bytes();total+=len(raw);sha=hashlib.sha256(raw).hexdigest()
            item=dict(file=rel,sha256=sha,size=size,status='artifact');inventory.append(item)
            suffix=path.suffix.lower()
            if suffix not in ('.json','.jsonl','.ndjson','.har','.log','.txt'):continue
            try:text=raw.decode('utf-8')
            except UnicodeDecodeError:issues.append('non-utf8');continue
            roots=[]
            if suffix in ('.json','.har'):
                try:roots=[(json.loads(text),'',1)]
                except ValueError:item['status']='parse-error';issues.append('parse-error');continue
            else:
                for line,value in enumerate(text.splitlines(),1):
                    if not value.strip():continue
                    try:roots.append((json.loads(value),'',line))
                    except ValueError:issues.append('unstructured-line')
            item['status']='parsed';matched=0
            rules=[r for r in manifest['rules'] if fnmatch.fnmatchcase(rel,r['filePattern'])]
            for value,_,line in roots:
                for rule in rules:
                    baseptr=rule.get('recordPath','')
                    try:selected=pointer(value,baseptr)
                    except (KeyError,IndexError,TypeError,ValueError):issues.append('record-path-missing');continue
                    entries=list(enumerate(selected)) if isinstance(selected,list) else [(None,selected)]
                    for index,entry in entries:
                        if not isinstance(entry,dict):issues.append('nonobject-record');continue
                        original=entry;entry=copy.deepcopy(entry)
                        decode_failed=False
                        for ptr in rule.get('decodeJson',[]):
                            try:
                                parent_path,_,key=ptr.rpartition('/')
                                parent=pointer(entry,parent_path);key=key.replace('~1','/').replace('~0','~')
                                if isinstance(parent,list):key=int(key)
                                parent[key]=json.loads(parent[key])
                            except (ValueError,TypeError,KeyError,IndexError):decode_failed=True
                        if decode_failed:issues.append('embedded-json-parse-error');continue
                        normalized={}
                        for key,ptr in rule['fields'].items():
                            try:normalized[key]=pointer(entry,ptr)
                            except (KeyError,IndexError,TypeError,ValueError):pass
                        if 'eventType' in rule:normalized['eventType']=rule['eventType']
                        if normalized.get('eventType') not in TYPES:continue
                        if not isinstance(normalized.get('conversationId'),str) or not normalized['conversationId']:
                            issues.append('missing-conversation-id');continue
                        invalid=False
                        for key,val in normalized.items():
                            if key in {'chunkIds','includedChunkIds','toolResultIds'}:
                                invalid |= not isinstance(val,list) or not all(isinstance(x,str) for x in val)
                            elif key in {'success','complete'}:invalid |= not isinstance(val,bool)
                            elif key in {'attempt','sequence','totalChunks','maxTokens','outputTokens'}:invalid |= not isinstance(val,int) or isinstance(val,bool) or val<0
                            else:invalid |= not isinstance(val,str)
                        if invalid:issues.append('invalid-field-types');continue
                        provenance=dict(file=rel,sha256=sha,pointer=baseptr+('/'+str(index) if index is not None else ''),line=line)
                        records.append(dict(normalized=normalized,original=original,provenance=provenance));matched+=1
            item['mappedRecords']=matched
            if roots and not matched:issues.append('unmapped-records')
    if not records:issues.append('no-mapped-session-records')
    return dict(version=VERSION,fingerprint=hash_value(inventory),mappingHash=hash_value(manifest),inventory=inventory,manifest=manifest,issues=sorted(set(issues)),records=records)
