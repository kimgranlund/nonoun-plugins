"""Qualify the real bounded runner's evaluator-file exclusion; no model calls."""
from pathlib import Path
import tempfile,json,subprocess,os,sys
s=Path(__file__).resolve().parent;r=Path(tempfile.mkdtemp(prefix='eval-isolation-check-',dir='/private/tmp'));private=r/'private';private.mkdir();secret=private/'rubric.txt';secret.write_text('private rubric');lane=r/'author';lane.mkdir();(lane/'alias').symlink_to(secret);config=r/'isolation.json';config.write_text(json.dumps({'schemaVersion':1,'privateRoots':[str(private)]}));bin=r/'bin';bin.mkdir();fake=bin/'codex';fake.write_text('''#!/usr/bin/env python3
import sys,pathlib,json
args=sys.argv;lane=pathlib.Path(args[args.index('-C')+1]);sys.stdin.read();denied=[]
for f in [lane.parent/'private/rubric.txt',lane/'alias']:
 try:f.read_text();denied.append(False)
 except PermissionError:denied.append(True)
try:(lane.parent/'private/rubric.txt').write_text('overwrite');denied.append(False)
except PermissionError:denied.append(True)
(lane/'access.json').write_text(json.dumps(denied));assert all(denied)
source=lane/'request';source.mkdir();(source/'unit.html').write_text('<p>source</p>');pathlib.Path(args[args.index('-o')+1]).write_text('request')
''');fake.chmod(0o755);(lane/'prompt.txt').write_text('fixture');(lane/'expected.json').write_text(json.dumps({'sources':[{'path':'request'}]}));subprocess.run([sys.executable,str(s/'run-eval-attempt.py'),str(lane),'5','fake','low','--source-only','--isolation',str(config)],env=dict(os.environ,PATH=str(bin)+os.pathsep+os.environ['PATH']),check=True);result=json.loads((lane/'runner-result.json').read_text());assert result['isolation']['qualified'] and result['snapshot'];assert secret.read_text()=='private rubric';assert json.loads((lane/'access.json').read_text())==[True,True,True]
# Discriminating unprotected fixture can read the same canary.
assert secret.read_text();bad=r/'bad.json';bad.write_text(json.dumps({'schemaVersion':1,'privateRoots':[str(lane)]}));sys.path.insert(0,str(s/'lib'));from eval_isolation import qualify
try:qualify(bad,lane);raise AssertionError('Overlapping root accepted')
except ValueError:pass
(r/'result.json').write_text(json.dumps({'status':'pass','directReadDenied':True,'symlinkReadDenied':True,'privateWriteDenied':True,'allowedSourceSealed':True,'overlapRejected':True,'unprotectedReadControl':True,'runner':result},indent=2));print(r/'result.json')
