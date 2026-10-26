"""Run one bounded Codex lane; evaluator prompt and sources live outside the skill."""
import json,os,signal,subprocess,sys,time
from pathlib import Path

def main():
    args=sys.argv[1:];isolation_path=None
    if '--isolation' in args:
        i=args.index('--isolation')
        if i+1>=len(args):raise SystemExit('--isolation needs a config path')
        isolation_path=args[i+1];del args[i:i+2]
    source_only=len(args)==5 and args[4]=='--source-only'
    if len(args)!=4 and not source_only: raise SystemExit('Usage: run-eval-attempt.py LANE_DIR CAP_SECONDS MODEL EFFORT [--source-only] [--isolation CONFIG.json]')
    lane=Path(args[0]).resolve();cap=float(args[1]);model,effort=args[2:4]
    prefix=[];isolation={'mode':'unenforced','qualified':False,'scope':'Not eligible for enforced clean-context claims'}
    if isolation_path:
        sys.path.insert(0,str(Path(__file__).parent/'lib'))
        from eval_isolation import qualify
        prefix,isolation=qualify(isolation_path,lane)
    if cap<=0: raise SystemExit('Positive cap required')
    if (lane/'submission.json').exists() or (lane/'events.jsonl').exists(): raise SystemExit('Fresh lane required; preserve prior attempts')
    if source_only:
        sys.path.insert(0,str(Path(__file__).parent/'lib'))
        from source_submission import submission,seal
        expected=json.loads((lane/'expected.json').read_text())
    gate=Path(__file__).with_name('eval-submit.mjs')
    prompt=(lane/'prompt.txt').read_text()+f'\nOperational submission entry: invoke node {gate} {lane} MANIFEST NEW_OUTPUT PLAYWRIGHT [generate options] instead of generate.mjs directly. Exactly one attempt is admitted, including a failed compile. Stop after it returns.\n'
    if source_only: prompt=(lane/'prompt.txt').read_text()+'\nSubmit sources only using submission.json with sources [{path, placement, controller?}], or a normal final naming the source directories and controller paths. Do not assemble, generate or validate; evaluator handles these after sealing.\n'
    start=time.monotonic();reason='completed';snapshot=None;boundary_error=None
    with (lane/'events.jsonl').open('x') as events:
        p=subprocess.Popen(prefix+['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','-m',model,'-c',f'model_reasoning_effort="{effort}"','-s','danger-full-access','-C',str(lane),'--json','-o',str(lane/'final.txt'),'-'],stdin=subprocess.PIPE,stdout=events,stderr=subprocess.STDOUT,text=True,start_new_session=True)
        p.stdin.write(prompt);p.stdin.close()
        while p.poll() is None:
            receipt=lane/'submission.json'
            try:
                if source_only:
                    packet=submission(lane,expected)
                    submitted=packet is not None
                    if submitted: snapshot=seal(lane,packet,lane/'submission-source')
                else: submitted=receipt.exists() and json.loads(receipt.read_text()).get('status')=='complete'
            except (ValueError,OSError) as error:
                if source_only:
                    boundary_error=str(error);reason='boundary error';os.killpg(p.pid,signal.SIGTERM);break
                submitted=False
            if submitted or time.monotonic()-start>=cap:
                reason='first submission complete' if submitted else 'time cap'
                if p.poll() is None:
                    try: os.killpg(p.pid,signal.SIGTERM)
                    except ProcessLookupError: pass
                break
            time.sleep(.05)
        try: p.wait(timeout=3)
        except subprocess.TimeoutExpired: os.killpg(p.pid,signal.SIGKILL);p.wait()
    if source_only and snapshot is None and boundary_error is None and p.returncode==0 and (lane/'final.txt').exists():
        try:
            packet=submission(lane,expected,(lane/'final.txt').read_text())
            if packet is not None: snapshot=seal(lane,packet,lane/'submission-source');reason='source submitted on final return'
        except (ValueError,OSError) as error: boundary_error=str(error);reason='boundary error'
    (lane/'runner-result.json').write_text(json.dumps({'isolation':isolation,'sourceOnly':source_only,'snapshot':snapshot,'boundaryError':boundary_error,'stopReason':reason,'exit':p.returncode,'elapsedSeconds':round(time.monotonic()-start,3),'model':model,'effort':effort,'protocolBypassCoverage':'Direct generate calls must be audited from traces; same-user filesystem access is not sandbox prevention.'},indent=2))
if __name__=='__main__': main()
