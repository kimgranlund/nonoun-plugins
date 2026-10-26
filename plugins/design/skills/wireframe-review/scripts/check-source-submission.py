import pathlib,sys,json,subprocess,os,tempfile
s=pathlib.Path(__file__).resolve().parents[1];t=pathlib.Path(tempfile.mkdtemp(prefix='source-submission-check-',dir='/private/tmp'))
sys.path.insert(0,str(s/'scripts/lib'));from source_submission import submission,seal
rows=[]
for mode in ['root','nested','final','custom-final','missing','escape','undeclared']:
 lane=t/mode;lane.mkdir();source=lane/'request';source.mkdir();(source/'unit.html').write_text('<p>source</p>');(source/'controller.js').write_text('controller bytes')
 if mode=='custom-final': (source/'controller.js').rename(source/'actions.js')
 expected={'sources':[{'path':'request','placement':'standalone'}]};packet={'sources':[{'path':'request','placement':'standalone','controller':'controller.js'}]}
 if mode in ['missing','escape']:packet['sources'][0]['controller']='missing.js' if mode=='missing' else '../outside.js'
 if mode not in ['final','custom-final','undeclared']:(lane/('submission.json' if mode=='root' else 'request/submission.json')).write_text(json.dumps(packet))
 try:
  got=submission(lane,expected,'request/actions.js' if mode=='custom-final' else 'request/controller.js' if mode=='final' else 'request')
  if mode in ['missing','escape']:raise AssertionError('negative accepted')
  assert ('controller' in got['sources'][0])==(mode!='undeclared')
  seal(lane,got,lane/'sealed');assert (lane/('sealed/0/actions.js' if mode=='custom-final' else 'sealed/0/controller.js')).read_text()=='controller bytes'
  rows.append({'mode':mode,'pass':True})
 except ValueError:
  assert mode in ['missing','escape'];rows.append({'mode':mode,'rejected':True})
# Exercise real runner with deterministic executable, no model calls.
bin=t/'bin';bin.mkdir();fake=bin/'codex';fake.write_text('''#!/usr/bin/env python3
import sys,pathlib,json
args=sys.argv;lane=pathlib.Path(args[args.index('-C')+1]);sys.stdin.read();source=lane/'request';source.mkdir();(source/'unit.html').write_text('<p>source</p>');(source/'controller.js').write_text('controller bytes')
if lane.name=='runner-nested':(source/'submission.json').write_text(json.dumps({'sources':[{'path':'request','controller':'controller.js'}]}))
pathlib.Path(args[args.index('-o')+1]).write_text('request/controller.js')
''');fake.chmod(0o755)
for mode in ['runner-nested','runner-final']:
 lane=t/mode;lane.mkdir();(lane/'prompt.txt').write_text('fixture');(lane/'expected.json').write_text(json.dumps({'sources':[{'path':'request'}]}))
 subprocess.run([sys.executable,str(s/'scripts/run-eval-attempt.py'),str(lane),'3','fake','low','--source-only'],env=dict(os.environ,PATH=str(bin)+os.pathsep+os.environ['PATH']),check=True)
 result=json.loads((lane/'runner-result.json').read_text());assert result['boundaryError'] is None and result['snapshot'];packet=json.loads((lane/'submission-source/submission.json').read_text());assert packet['sources'][0]['controller']=='controller.js';rows.append({'mode':mode,'pass':True,'result':result})
(t/'metadata-checks.json').write_text(json.dumps({'pass':True,'rows':rows},indent=2));print('PASS metadata controls and real runner nested/final entry')
