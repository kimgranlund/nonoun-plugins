#!/usr/bin/env python3
"""Resolve a known Node runtime and execute a kit command without a shell or install."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path

def resolve():
 explicit=os.environ.get('UI_NODE_PATH')
 candidates=[explicit] if explicit else [shutil.which('node'),str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')]
 tried=[]
 for candidate in dict.fromkeys(candidates):
  if not candidate:continue
  try:
   result=subprocess.run([candidate,'--version'],capture_output=True,text=True,timeout=5,check=True)
   if not result.stdout.strip().startswith('v'):raise ValueError('Unexpected version response')
   return str(Path(candidate).resolve()),result.stdout.strip()
  except (OSError,ValueError,subprocess.SubprocessError) as e:tried.append({'path':candidate,'error':str(e)})
 raise SystemExit('Node runtime unavailable; set UI_NODE_PATH to an installed executable. No install or crawl attempted. '+json.dumps(tried))

def main():
 args=sys.argv[1:]
 if args and args[0]=='read':
  if len(args) not in (2,4) or len(args)==4 and args[2]!='--page':raise SystemExit('Usage: run.py read KIT_RELATIVE_FILE [--page N]')
  root=Path(__file__).resolve().parent.parent;file=(root/args[1]).resolve()
  if root not in file.parents or file.stat().st_size>1000000:raise SystemExit('Expected bounded file inside kit')
  raw=file.read_bytes();text=raw.decode('utf-8')
  if '\x00' in text:raise SystemExit('Text files only')
  pages=[];page=''
  for line in text.splitlines(keepends=True):
   if len(line.encode())>4000:raise SystemExit('Line exceeds4000 bytes; use a structured projection for this file')
   if len((page+line).encode())>4000:pages.append(page);page=''
   page+=line
  if page or not pages:pages.append(page)
  index=int(args[3]) if len(args)==4 else 0
  if index<0 or index>=len(pages):raise SystemExit('Page out of range')
  print(json.dumps({'source':args[1],'sha256':hashlib.sha256(raw).hexdigest(),'page':index,'pages':len(pages),'nextPage':index+1 if index+1<len(pages) else None,'content':pages[index]},ensure_ascii=False));return
 node,version=resolve()
 if args==['--check']:
  print(json.dumps({'node':node,'version':version,'resolved':True}));return
 if not args:raise SystemExit('Usage: python3 scripts/run.py --check | SCRIPT.mjs [ARGS]')
 script=(Path(__file__).parent/args[0]).resolve()
 if script.parent!=Path(__file__).resolve().parent or script.suffix!='.mjs' or not script.is_file():raise SystemExit('Expected an existing base-ui scripts/*.mjs command')
 raise SystemExit(subprocess.call([node,str(script),*args[1:]],env={**os.environ,'PATH':str(Path(node).parent)+os.pathsep+os.environ.get('PATH','')}))
if __name__=='__main__':main()
