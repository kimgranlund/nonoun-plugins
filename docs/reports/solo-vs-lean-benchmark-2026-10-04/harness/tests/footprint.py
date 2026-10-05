#!/usr/bin/env python3
# hidden check: run from the repo root of the worktree
import os, subprocess, sys, tempfile, json, hashlib
FP = ['python3', 'plugins/sdlc-lite/scripts/footprint.py']
def run(*a):
    p = subprocess.run(FP + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr
def kv(out):
    d = {}
    for l in out.splitlines():
        if ': ' in l:
            k, v = l.rsplit(': ', 1)
            d[k.strip()] = v.strip()
    return d
def mk(root, spec):
    for rel, content in spec.items():
        p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w').write(content)
def snap(root):
    h = hashlib.sha256()
    for dp, dn, fn in sorted(os.walk(root)):
        for f in sorted(fn):
            q = os.path.join(dp, f); h.update(q.encode()); h.update(open(q, 'rb').read())
    return h.hexdigest()
def rl(role, level): return json.dumps({"role": role, "level": level}) + "\n"
fails = []
def expect(name, cond):
    if not cond: fails.append(name)
with tempfile.TemporaryDirectory() as t:
    # fix-lane ticket: no planner file, one step, two role runs
    a = os.path.join(t, 'fixlane')
    mk(a, {'handoff.md': 'hello world', 'step-1/handoff.md': 'abcde', 'step-1/builder-L2.md': 'xyzxyzx',
           'step-1/runs.jsonl': rl('builder', 'L2') + rl('verifier', 'L1')})
    s0 = snap(a)
    rc, out, err = run(a); d = kv(out)
    expect('fixlane rc', rc == 0)
    expect('fixlane files', d.get('files') == '4')
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(a) for f in fs)
    md = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(a) for f in fs if f.endswith('.md'))
    expect('fixlane bytes', d.get('bytes') == str(tot))
    expect('fixlane md_bytes', d.get('md_bytes') == str(md))
    expect('fixlane steps', d.get('steps') == '1')
    expect('fixlane planner_bytes', d.get('planner_bytes') == '0')
    expect('fixlane role_runs', d.get('role_runs') == '2')
    expect('fixlane role_runs builder L2', d.get('role_runs builder L2') == '1')
    expect('fixlane role_runs verifier L1', d.get('role_runs verifier L1') == '1')
    expect('read-only', snap(a) == s0)
    # chained ticket: planner file, 3 steps, runs at two levels of the tree
    b = os.path.join(t, 'chained')
    mk(b, {'handoff.md': 'goal', 'planner-L2.md': 'p' * 300, 'planner-L3.md': 'q' * 50, 'runs.jsonl': rl('planner', 'L2') + rl('planner', 'L3'),
           'step-1/handoff.md': 'a', 'step-2/handoff.md': 'b', 'step-3/handoff.md': 'c',
           'step-1/runs.jsonl': rl('builder', 'L3'), 'step-2/runs.jsonl': rl('builder', 'L3') + rl('verifier', 'L2'), 'step-3/note.txt': 'zz'})
    rc, out, err = run(b); d = kv(out)
    expect('chained rc', rc == 0)
    expect('chained steps', d.get('steps') == '3')
    expect('chained planner_bytes', d.get('planner_bytes') == '350')
    expect('chained role_runs', d.get('role_runs') == '5')
    expect('chained role_runs builder L3', d.get('role_runs builder L3') == '2')
    expect('chained role_runs planner L2', d.get('role_runs planner L2') == '1')
    expect('chained files', d.get('files') == '10')
    # check subcommand
    rc, out, err = run('check', b, '--max-files', '10', '--max-bytes', '100000'); expect('check ok rc', rc == 0)
    rc, out, err = run('check', b, '--max-files', '9', '--max-bytes', '100000')
    expect('check files exceeded', rc == 1 and '--max-files' in (out + err) and '--max-bytes' not in (out + err))
    rc, out, err = run('check', b, '--max-files', '100', '--max-bytes', '10')
    expect('check bytes exceeded', rc == 1 and '--max-bytes' in (out + err) and '--max-files' not in (out + err))
    # negative control: one extra file flips the gate
    mk(b, {'extra.txt': 'e'})
    rc, out, err = run('check', b, '--max-files', '10', '--max-bytes', '100000'); expect('check negative control', rc == 1)
    rc, out, err = run(os.path.join(t, 'nope')); expect('missing dir', rc != 0)
if fails:
    print('FAIL: ' + ', '.join(fails)); sys.exit(1)
print('PASS')
