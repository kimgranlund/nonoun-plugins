from pathlib import Path
import json, os, subprocess, sys, tempfile, time
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'plugins/sdlc-lite'
sys.path.insert(0,str(P/'scripts'))
import codex_roles

def run(cmd, **kw):
 return subprocess.run(cmd,text=True,capture_output=True,**kw)
def git(repo,*args):
 p=run(['git','-C',str(repo),*args]); assert p.returncode==0,p.stderr

env=dict(os.environ)
for k in list(env):
 if k.startswith('SDLC_'): del env[k]
with tempfile.TemporaryDirectory(prefix='sdlc-astra-review-') as tmp:
 for name in ('plain','with spaces'):
  r=Path(tmp)/name;r.mkdir();git(r,'init','-q');git(r,'-c','user.name=Review','-c','user.email=review@example.invalid','commit','--allow-empty','-qm','seed')
  h=r/'.sdlc/task/handoff.md';h.parent.mkdir(parents=True);h.write_text('## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n')
  prep=run([sys.executable,str(P/'scripts/dispatch.py'),'prepare','scout','L1',str(h)],cwd=r,env=env)
  assert prep.returncode==0, prep.stderr
  d=json.loads(prep.stdout)
  payload={'tool_name':'Agent','agent_type':'sdlc-lite:conductor','cwd':str(r),'tool_input':{k:d[k] for k in ('subagent_type','name','model','prompt','run_in_background')}}
  hook=run(['bash',str(P/'hooks/block-role-spawn.sh')],input=json.dumps(payload),env=env)
  print('prepared spawn',name,'hook_exit=',hook.returncode,'stderr=',hook.stderr.strip())
  ep={'tool_name':'Edit','tool_input':{'file_path':str(h)}}
  he=run(['bash',str(P/'hooks/warn-handoff-edit.sh')],input=json.dumps(ep),env=dict(env,SDLC_HANDOFF_EDIT_MODE='deny'))
  print('handoff guard',name,'attempt_status=',json.loads(Path(d['attempt_file']).read_text())['status'],'running_markers=',len(list(h.parent.glob('*.running'))),'deny_exit=',he.returncode,'stderr=',repr(he.stderr))
  (h.parent/'scout-L1.running').write_text('probe\n')
  he2=run(['bash',str(P/'hooks/warn-handoff-edit.sh')],input=json.dumps(ep),env=dict(env,SDLC_HANDOFF_EDIT_MODE='deny'))
  print('handoff guard positive control',name,'marker_added_deny_exit=',he2.returncode)
 # Real exchange in child process, no model/host invocation.
 for label,first in [('missing',''),('stale','profile: 0.0.0+stale\n'),('current','profile: '+codex_roles.fingerprint('sdlc-scout-l1')+'\n')]:
  req=Path(tmp)/(label+'.request.json');rep=Path(tmp)/(label+'.md')
  text=first+'## Map\nNone\n\n## Entry points\nNone\n\n## Not found\nNone\n\n## Carry forward\nNone\n';rep.write_text(text)
  code='import sys;sys.path.insert(0,sys.argv[1]);from codex_exchange import wait_for_agent;sys.exit(wait_for_agent("scout","L1","Read seed","gpt-5.6-terra","low",sys.argv[2],10))'
  child=subprocess.Popen([sys.executable,'-c',code,str(P/'scripts'),str(req)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
  deadline=time.monotonic()+5
  while not req.exists() and time.monotonic()<deadline: time.sleep(.01)
  assert req.exists(),'request never appeared'
  response=run([sys.executable,str(P/'scripts/codex_exchange.py'),str(req),str(rep)],env=env)
  out,err=child.communicate(timeout=12)
  event=json.loads(out)
  print('fingerprint',label,'helper=',codex_roles.check_loaded('sdlc-scout-l1',text)[0],'respond_exit=',response.returncode,'exchange_exit=',child.returncode,'is_error=',event['is_error'],'request_status=',json.loads(req.read_text())['status'])
print('contradictory_profiles=',sum('nothing before the first heading' in data['developer_instructions'] and '# Profile fingerprint' in data['developer_instructions'] for _,data in codex_roles.definitions()))

# Standard YAML parsing is a format check, not a live Claude loader check.
import yaml
for label, files in [('agents', sorted((P/'agents').glob('*.md'))), ('skills', sorted((P/'skills').glob('*/SKILL.md')))]:
 bad=[]
 for f in files:
  try: yaml.safe_load(f.read_text().split('---',2)[1])
  except yaml.YAMLError as e: bad.append((f.name,str(e)))
 print(label, 'count=',len(files),'invalid=',len(bad))
 for name,error in bad:
  if name in ('builder-L2.md','conductor.md'):print(name,error)
raw=(P/'agents/builder-L2.md').read_text().split('---',2)[1]
lines=[('description: '+json.dumps(x[len('description: '):])) if x.startswith('description: ') else x for x in raw.splitlines()]
yaml.safe_load('\n'.join(lines));print('quoted whole description positive control: parsed')
with tempfile.TemporaryDirectory(prefix='sdlc-astra-ask-') as td:
 r=Path(td);f=r/'.sdlc/0001-blocked/handoff.md';f.parent.mkdir(parents=True);f.write_text('---\nid: T-0001\nstatus: blocked\n---\n## Goal\nNeeds an answer.\n')
 for cmd in [['grep','-rl','^status: blocked','.sdlc/tickets'],['grep','-rl','^status: blocked','.sdlc']]:
  t=run(cmd,cwd=r);print('ask probe:',cmd,'exit=',t.returncode,'stdout=',t.stdout.strip(),'stderr=',t.stderr.strip())
