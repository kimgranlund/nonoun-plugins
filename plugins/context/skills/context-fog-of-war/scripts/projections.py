"""Corroborate returned component-context projections; never execute recorded code."""
import hashlib,json,shlex
from pathlib import Path

def component_projections(command,workdir,output,roots):
    if not isinstance(command,str) or any(x in command for x in ['<<','`','$(','|']):return []
    bases=[]
    for line in command.replace(';','\n').splitlines():
        try:w=shlex.split(line)
        except ValueError:continue
        if len(w)>=3 and Path(w[0]).name in ('python','python3') and Path(w[1]).name=='run.py' and w[2]=='component-context.mjs':
            w=['node',str(Path(w[1]).parent/'component-context.mjs'),*w[3:]]
        if len(w)<2 or Path(w[0]).name!='node' or Path(w[1]).name!='component-context.mjs':continue
        if any('$' in x for x in w):continue
        script=Path(w[1]);script=script if script.is_absolute() else Path(workdir)/script
        base=script.parent.parent
        if '--root' in w:
            i=w.index('--root')
            if i+1>=len(w):continue
            base=Path(w[i+1]);base=base if base.is_absolute() else Path(workdir)/base
        bases.append(base)
    result=[]
    for line in output.splitlines():
        try:p=json.loads(line)
        except (ValueError,TypeError):continue
        if not isinstance(p,dict) or p.get('schemaVersion')!=1 or not isinstance(p.get('sources'),list):continue
        for source in p['sources']:
            if not isinstance(source,dict) or not isinstance(source.get('path'),str):continue
            for base in bases:
                path=(base/source['path']).resolve()
                if not any(path==r or r in path.parents for r in roots):continue
                try:
                    if path.stat().st_size>1000000:continue
                    raw=path.read_bytes()
                    if hashlib.sha256(raw).hexdigest()!=source.get('sha256'):continue
                    original=json.loads(raw)
                except (OSError,ValueError):continue
                covered=[]
                if isinstance(original,dict):
                    if 'shared' in p and p['shared']=={k:v for k,v in original.items() if k!='families'}:covered.append('shared constraints')
                    if 'runtimeAPI' in p and p['runtimeAPI']==original:covered.append('runtime API')
                    records=p.get('records',[])
                    if 'contract' in p:records=[{'id':p.get('id'),'contract':p['contract']}]
                    if isinstance(records,list):
                        for item in records:
                            if not isinstance(item,dict) or not isinstance(item.get('contract'),dict):continue
                            candidates=original.get('families',[original])
                            if any(item['contract']==c and item.get('id')==c.get('id') for c in candidates if isinstance(c,dict)):covered.append('record '+str(item['id']))
                if covered:result.append((str(path),', '.join(covered)));break
    return list(dict.fromkeys(result))

def prose_projections(command,workdir,output,roots):
    """Verify literal launcher pages against exact bounded source bytes; no code execution."""
    if not isinstance(command,str) or any(x in command for x in ['<<','`','$','|']):return []
    requests=[]
    for line in command.replace(';','\n').splitlines():
        try:w=shlex.split(line)
        except ValueError:continue
        if len(w) not in (4,6) or Path(w[0]).name not in ('python','python3') or Path(w[1]).name!='run.py' or w[2]!='read':continue
        if len(w)==6 and (w[4]!='--page' or not w[5].isdigit()):continue
        script=Path(w[1]);script=script if script.is_absolute() else Path(workdir)/script
        root=script.resolve().parent.parent;path=(root/w[3]).resolve()
        if root not in path.parents or not any(path==r or r in path.parents for r in roots):continue
        requests.append((path,w[3],int(w[5]) if len(w)==6 else 0))
    result=[]
    for line in output.splitlines():
        try:packet=json.loads(line)
        except (ValueError,TypeError):continue
        if not isinstance(packet,dict):continue
        for path,relative,index in requests:
            if packet.get('source')!=relative or packet.get('page')!=index:continue
            try:
                if path.stat().st_size>1000000:continue
                raw=path.read_bytes()
                if hashlib.sha256(raw).hexdigest()!=packet.get('sha256'):continue
                pages=[];page=''
                for chunk in raw.decode().splitlines(keepends=True):
                    if len(chunk.encode())>4000:raise ValueError('Long line')
                    if len((page+chunk).encode())>4000:pages.append(page);page=''
                    page+=chunk
                if page or not pages:pages.append(page)
                if index>=len(pages) or pages[index]!=packet.get('content') or packet.get('pages')!=len(pages):continue
                result.append((str(path),f'page {index+1}/{len(pages)}'))
            except (OSError,ValueError):continue
    return list(dict.fromkeys(result))
