"""Optional enforced evaluator-file exclusion for bounded macOS author trials."""
import json,os,subprocess,sys,tempfile
from pathlib import Path

def qualify(config,lane):
    config=Path(config).resolve();data=json.loads(config.read_text())
    if data.get('schemaVersion')!=1 or not data.get('privateRoots'):raise ValueError('Declare schemaVersion=1 and nonempty privateRoots')
    roots=[Path(x).resolve(strict=True) for x in data['privateRoots']]
    if not all(r.is_dir() for r in roots):raise ValueError('Private roots must be directories')
    lane=Path(lane).resolve()
    if any(r==Path('/') or r==lane or r in lane.parents or lane in r.parents for r in roots):raise ValueError('Private roots must be separate from author lane')
    binary=Path('/usr/bin/sandbox-exec')
    if not binary.is_file():raise ValueError('Enforced evaluator-file isolation unavailable; do not claim clean context')
    clauses=''.join('(deny file-read* file-write* (subpath '+json.dumps(str(r))+'))' for r in roots)
    profile='(version 1)(allow default)'+clauses
    prefix=[str(binary),'-p',profile]
    # Never mutate evaluator or sealed roots. Qualify enumeration and a synthetic canary.
    with tempfile.TemporaryDirectory(prefix='isolation-canary-',dir=str(lane)) as scratch:
        a=Path(scratch)/'allowed';a.write_text('allowed')
        secret=Path(scratch)/'private';secret.write_text('private')
        testprefix=[str(binary),'-p',profile+'(deny file-read* file-write* (literal '+json.dumps(str(secret))+'))']
        code='from pathlib import Path;import sys;Path(sys.argv[1]).read_bytes()'
        denied=subprocess.run(testprefix+[sys.executable,'-c',code,str(secret)],capture_output=True)
        permitted=subprocess.run(testprefix+[sys.executable,'-c',code,str(a)],capture_output=True)
        if denied.returncode==0 or permitted.returncode!=0:raise ValueError('Evaluator exclusion canary failed')
        for root in roots:
            code='from pathlib import Path;import sys;list(Path(sys.argv[1]).iterdir())'
            probe=subprocess.run(prefix+[sys.executable,'-c',code,str(root)],capture_output=True)
            if probe.returncode==0:raise ValueError('Private root enumeration not denied')
    return prefix,{'mode':'macos-filesystem-exclusion','privateRoots':[str(r) for r in roots],'qualified':True,'scope':'Direct/inherited filesystem access only. No evaluator HTTP server during author trials; same-user external services are outside this boundary.'}
