"""Extract visible path candidates, without asserting that they were evaluated."""
import json
import re
import posixpath


def strings(value,depth=0):
    if depth>10:return
    if isinstance(value,str):
        try: obj=json.loads(value)
        except (ValueError,TypeError): yield value;return
        if isinstance(obj,(dict,list)):yield from strings(obj,depth+1)
        else:yield value
    elif isinstance(value,list):
        for item in value:yield from strings(item,depth+1)
    elif isinstance(value,dict):
        for key in ('text','content','output','stdout','stderr','message'):
            if key in value:yield from strings(value[key],depth+1)


def discover_candidates(data):
    sources={s['path']:s['id'] for s in data['sources']}
    used={s['id'] for s in data['sources']};items=[];aliases={}
    for event in data['events']:
        # Inputs to tool calls are attempted operations, not an options inventory.
        if event['kind'] not in ('message','result','context'):continue
        raw=event['evidence']['text']
        try: obj=json.loads(raw.split('\n\nDecoded tool/output attribution (input order):')[0])
        except ValueError:continue
        texts=list(strings(obj));seen=set()
        for text in texts:
            aliases.update(re.findall(r'`(r\d+)`\s*=\s*`([^`]+)`',text))
        for text in texts:
            quoted=set(re.findall(r'`((?:/|~?/)[^`\n]+\.[A-Za-z0-9]+)`',text))
            searchable=re.sub(r'(?:https?|file|plugin)://[^\s<>]+','',text)
            paths=set(re.findall(r'(?<![\w:/])(?:~?/|\./|(?:[\w.@+-]+/)+)[\w.@+/-]*[\w@+-](?:\.[\w-]+)?',searchable))
            paths={p for p in paths if not any(p!=q and p in q for q in quoted)}|quoted
            # Repository-relative single filenames are matched only from inventory.
            paths.update(p for p in sources if len(p)>3 and re.search(r'(?<![\w./-])'+re.escape(p)+r'(?![\w./-])',text))
            for path in sorted(paths):
                if len(path)>400 or path.endswith('/') or '://' in path or path.startswith('//'):continue
                # Require a file-like leaf; URLs, command switches and arbitrary prose are excluded.
                if not re.search(r'\.[A-Za-z0-9_-]+$',path) or path.startswith(('/dev/','/tmp/')):continue
                if path not in raw:continue
                normalized=posixpath.normpath(path)
                alias,sep,tail=normalized.partition('/')
                if alias in aliases and sep:normalized=posixpath.join(aliases[alias],tail)
                if normalized in seen:continue
                seen.add(normalized)
                sid=sources.get(normalized)
                if not sid:
                    n=len(used)+1
                    while 's'+str(n) in used:n+=1
                    sid='s'+str(n);used.add(sid);sources[normalized]=sid
                    data['sources'].append({'id':sid,'path':normalized,'inventoried':False})
                pos=raw.find(path)
                items.append({'sourceId':sid,'eventId':event['id'],'kind':'available' if '(file: '+path+')' in text else 'mentioned','evidence':{'eventId':event['id'],'excerpt':raw[max(0,pos-70):pos+len(path)+100]}})
    data['candidates']=items
    note='Candidate paths are literal file-like references in recorded messages/context/tool outputs. Mention does not establish evaluation, rejection or use; hidden options and ambiguous relative/aliased paths remain unknown. Candidate discovery never reads these paths.'
    if note not in data['coverage']['warnings']:data['coverage']['warnings'].append(note)
    return data

if __name__=='__main__':
    import argparse
    from pathlib import Path
    from fog import validate
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    d=validate(discover_candidates(validate(json.loads(a.data.read_text()))));a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2)+'\n');print('Candidate references:',len(d['candidates']))
