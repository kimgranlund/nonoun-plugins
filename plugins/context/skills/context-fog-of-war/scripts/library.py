#!/usr/bin/env python3
"""Publish validated reports into a per-user JSON registry and offline report library."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
import re
from pathlib import Path
import shutil
import sys
import tempfile
import time

from fog import validate, render


def default_root():
    if sys.platform == 'darwin': return Path.home()/'Library/Application Support/Context Fog of War'
    if os.name == 'nt': return Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData/Local')))/'Context Fog of War'
    return Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))/'context-fog-of-war'


def atomic(path, text):
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix='.write-')
    try:
        with os.fdopen(fd, 'w') as stream: stream.write(text)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def read_registry(root):
    path=root/'registry.json'
    if not path.exists(): return {'schemaVersion':1,'reports':[]}
    registry=json.loads(path.read_text())
    if registry.get('schemaVersion') != 1 or not isinstance(registry.get('reports'),list): raise ValueError('Invalid report registry')
    return registry


def write_index(root, registry):
    rows=[]
    for report in reversed(registry['reports']):
        esc=lambda x:html.escape(str(x),quote=True)
        rows.append('<li class="wf-card"><h2><a href="'+esc(report['html'])+'">'+esc(report['title'])+'</a></h2><p>'+esc(report['repo'])+' · '+esc(report['createdAt'])+'</p><p>'+str(report['decisions'])+' decisions · '+str(report['findings'])+' analysis findings · '+str(report.get('diagnosticFindings',0))+' diagnostic candidates · <a href="'+esc(report['json'])+'">Session JSON</a></p></li>')
    shell=(Path(__file__).resolve().parents[1]/'assets/shell.html').read_text()
    styles=''.join('<style>'+x+'</style>' for x in re.findall(r'<style>(.*?)</style>',shell,re.S))
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Context Fog-of-War · Report library</title>'+styles+'<body class="wf-product"><main class="wf-page wf-page-flow"><h1>Context Fog-of-War</h1><p>Report library · stored on this computer</p><p><a href="registry.json">JSON registry</a></p><ul class="wf-flow">'+''.join(rows)+'</ul></main></body></html>'
    atomic(root/'index.html',page)


def publish(data_path, root=None):
    root=Path(root or default_root()).expanduser().resolve()
    data_path=Path(data_path).resolve();data=json.loads(data_path.read_text());validate(data)
    encoded=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    digest=hashlib.sha256(encoded.encode()).hexdigest();identity=digest[:24]
    root.mkdir(parents=True,exist_ok=True);(root/'reports').mkdir(exist_ok=True)
    lock=root/'.registry-lock'
    for attempt in range(30):
        try:lock.mkdir();break
        except FileExistsError:
            if attempt==29:raise ValueError('Registry is busy (or a stale .registry-lock remains after a crash). Retry after checking no publisher is running.')
            time.sleep(.1)
    try:
        registry=read_registry(root)
        existing=next((r for r in registry['reports'] if r['sha256']==digest),None)
        if existing:
            write_index(root,registry)
            return dict(existing,library=str(root/'index.html'),root=str(root))
        relative=Path('reports')/identity;folder=root/relative
        with tempfile.TemporaryDirectory(dir=root,prefix='.publish-') as temp:
            stage=Path(temp)/'report';stage.mkdir()
            (stage/'session.json').write_text(encoded)
            render(data,stage/'index.html')
            page=(stage/'index.html').read_text().replace('id="library-link" hidden','id="library-link"').replace('href="__FOG_LIBRARY__"','href="../../index.html"')
            (stage/'index.html').write_text(page)
            if folder.exists():
                # Recover an interrupted publication only when immutable data matches.
                if (folder/'session.json').read_text()!=encoded:raise ValueError('Report ID collision')
            else:os.replace(stage,folder)
        entry={'id':identity,'title':data['session']['title'],'repo':data['session']['repo'],'trace':data['session']['trace'],'traceSha256':data['session']['traceSha256'],'sha256':digest,'schemaVersion':data['schemaVersion'],'createdAt':datetime.now(timezone.utc).isoformat(),'json':str(relative/'session.json'),'html':str(relative/'index.html'),'source':str(data_path),'decisions':len(data.get('decisions',[])),'findings':len(data.get('findings',[])),'diagnosticFindings':len(data.get('diagnostics',{}).get('findings',[]))}
        registry['reports'].append(entry)
        atomic(root/'registry.json',json.dumps(registry,indent=2)+'\n');write_index(root,registry)
        return dict(entry,library=str(root/'index.html'),root=str(root))
    finally:lock.rmdir()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('publish');p.add_argument('data',type=Path)
    sub.add_parser('list');sub.add_parser('path');a=parser.parse_args()
    try:
        if a.action=='publish':result=publish(a.data,a.root)
        elif a.action=='list':result=read_registry(a.root or default_root())
        else:result={'root':str(a.root or default_root())}
        print(json.dumps(result,indent=2))
    except (ValueError,OSError) as error:parser.exit(1,f'Error: {error}\n')

if __name__=='__main__':main()
