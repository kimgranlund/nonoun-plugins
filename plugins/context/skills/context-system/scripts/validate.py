#!/usr/bin/env python3
"""Validate the optional local JSON profile. Never execute or fetch corpus content."""
import argparse
import hashlib
import json
from pathlib import Path

RELATIONS = ('depends_on', 'governed_by', 'references', 'supersedes')
REQUIRED = ('id', 'location', 'kind', 'summary', 'revision', 'sha256')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError('Expected nonempty root-relative path')
    root = Path(root).resolve()
    path = (root / value).resolve()
    if root not in path.parents:
        raise ValueError('Path escapes corpus root: ' + value)
    return path


def validate(root, value, descriptor=False):
    issues = []
    checked = 0
    def issue(code, location, detail):
        issues.append(dict(code=code, location=location, detail=detail))
    def check_file(path, expected=None):
        nonlocal checked
        try:
            data = local(root, path).read_bytes()
            checked += len(data)
            if expected is not None and digest(data) != expected:
                issue('stale-hash', path, 'Recorded bytes differ from current bytes')
        except (ValueError, OSError) as e:
            issue('unavailable-path', str(path), str(e))
    if not isinstance(value, dict):
        return dict(valid=False, issues=[dict(code='shape', location='root', detail='Expected object')], validationBytes=0)
    if descriptor:
        entries = [value]
    else:
        if type(value.get('schemaVersion')) is not int or value.get('schemaVersion') != 1:
            issue('version', 'schemaVersion', 'Expected integer 1')
        check_file(value.get('entry'))
        entries = value.get('artifacts')
    if not isinstance(entries, list):
        issue('shape', 'artifacts', 'Expected array')
        entries = []
    ids = {}; aliases = {}; dependencies = {}
    for index, a in enumerate(entries):
        where = 'artifacts/' + str(index)
        if not isinstance(a, dict):
            issue('shape', where, 'Expected descriptor object'); continue
        for key in REQUIRED:
            if not isinstance(a.get(key), str) or not a[key].strip():
                issue('required', where + '/' + key, 'Expected nonempty string')
        identity = a.get('id')
        if isinstance(identity, str):
            if identity in ids: issue('duplicate-id', where, identity)
            ids[identity] = a
        expected = a.get('sha256')
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
            issue('hash-format', where, 'Expected lowercase SHA256')
        check_file(a.get('location'), expected)
        al = a.get('aliases', [])
        if not isinstance(al, list) or any(not isinstance(x, str) or not x for x in al):
            issue('shape', where + '/aliases', 'Expected nonempty string array'); al = []
        for alias in al:
            if alias in aliases: issue('duplicate-alias', where, alias)
            aliases[alias] = identity
        rel = a.get('relationships', {})
        if not isinstance(rel, dict):
            issue('shape', where + '/relationships', 'Expected object'); rel = {}
        for name, targets in rel.items():
            if name not in RELATIONS or not isinstance(targets, list) or any(not isinstance(t, str) or not t for t in targets):
                issue('relationship-shape', where, name)
        if isinstance(identity, str):
            dependencies[identity] = [x for k in ('governed_by','depends_on') for x in rel.get(k, []) if isinstance(x,str)] if all(isinstance(rel.get(k,[]),list) for k in ('governed_by','depends_on')) else []
        if 'directives' in a and (not isinstance(a['directives'], dict) or any(not isinstance(v,str) for v in a['directives'].values())):
            issue('shape', where + '/directives', 'Expected string-valued object')
        for key in ('owner','authority'):
            if key in a and (not isinstance(a[key],str) or not a[key]):issue('shape',where+'/'+key,'Expected nonempty string')
        if a.get('status','active') not in ('active','deprecated'):issue('shape',where+'/status','Expected active or deprecated')
        # Optional generated artifact provenance is checked as bytes, never mtime.
        sources = a.get('sourceDigests', {})
        if not isinstance(sources, dict):issue('shape', where+'/sourceDigests', 'Expected object')
        else:
            for path, sha in sources.items():
                if not isinstance(sha,str) or len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha):issue('hash-format',where+'/sourceDigests','Expected lowercase SHA256')
                check_file(path, sha)
    for alias in aliases:
        if alias in ids:issue('alias-collision',alias,'Alias shadows stable ID')
    if not descriptor:
        for identity,a in ids.items():
            rel=a.get('relationships',{})
            if not isinstance(rel,dict):continue
            for targets in rel.values():
                if isinstance(targets,list):
                    for target in targets:
                        if isinstance(target,str) and target not in ids:issue('missing-reference',identity,target)
        active=set(); done=set()
        def visit(identity, trail):
            if identity in active:issue('cycle',identity,' -> '.join(trail+[identity]));return
            if identity in done:return
            active.add(identity)
            for target in dependencies.get(identity,[]):visit(target,trail+[identity])
            active.remove(identity);done.add(identity)
        for identity in ids:visit(identity,[])
        routes=value.get('routes',[])
        if not isinstance(routes,list):issue('shape','routes','Expected array');routes=[]
        intents=set()
        for i,route in enumerate(routes):
            if not isinstance(route,dict) or not isinstance(route.get('intent'),str) or not route['intent'] or not isinstance(route.get('target'),str):
                issue('shape','routes/'+str(i),'Expected intent and target strings');continue
            if route['intent'] in intents:issue('ambiguous-route',route['intent'],'Multiple targets for the same intent')
            intents.add(route['intent'])
            if route['target'] not in ids:issue('missing-reference',route['intent'],route['target'])
    return dict(valid=not issues, issues=issues, validationBytes=checked,
                limits=['Byte identity is not semantic freshness.', 'Corpus authority never overrides harness instructions.',
                        'Standalone descriptor checks cannot resolve relationships without a registry.'] if descriptor else ['Byte identity is not semantic freshness.', 'Static validation does not establish runtime delivery or correct summaries.'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--registry',type=Path);group.add_argument('--descriptor',type=Path)
    args=p.parse_args()
    try:result=validate(args.root,json.loads((args.registry or args.descriptor).read_text()),bool(args.descriptor))
    except (OSError,ValueError) as e:result=dict(valid=False,issues=[dict(code='input',detail=str(e))])
    print(json.dumps(result,indent=2));return 0 if result['valid'] else 1

if __name__=='__main__':raise SystemExit(main())
