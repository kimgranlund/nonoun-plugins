#!/usr/bin/env python3
"""T-0458 overlay retest: run one replay cell end to end and append its run-log line.

usage: cell.py <task> <L1|L5> <A|B> <rep>

Clone the task repo into the tmp prefix, check out the base, run setup, place the handoff, run the
steps.py lint and the builder prepare with the armB root, run the builder headless with the arm root,
record it priced from the transcript, run one verifier (armB root) unless the builder blocked, grade the
hidden check, then append one line to the run log and save the rows and results to the evidence folder.
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TREE = Path('/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v')
TMP = TREE / '.worktrees/tmp/0458-s1-builder-L3'
EVID = TREE / 'docs/reports/2026-10-12-builder-overlay-retest'
RUNLOG = TREE / '.sdlc/.0458-builder-overlay-retest/run-log.md'
NONOUN = Path('/Users/kimgranlund/Projects/nonoun')
LANE = 'T-0458 overlay retest: replay a solo ticket as one builder step'

TASKS = {
    'rts-step10': dict(source='blocked note', repo=NONOUN / 'agent-ui', base='0e18b7086906ff7359698a043cbe486c0c980495',
                       setup='npm ci', copy=NONOUN / 'agent-ui/.sdlc/response-type-selection/step-10/handoff.md',
                       rel='.sdlc/response-type-selection/step-10/handoff.md',
                       blocked_sha='fceea3cca477040b376e1a67be7e4a3011bf2b503ebda5ad974523ebe1dd9ea8', hidden=None),
    'ndc-step2': dict(source='blocked note', repo=NONOUN / 'ultimate-tokens', base='7f05eb50d6d33dec5de2557d91c8fcd107e7a2e4',
                      setup='npm ci', copy=None, rel='.sdlc/native-dom-charts/step-2/handoff.md',
                      blocked_sha='6c2cd3e60200db0f8a79411e76b9163c7d8f35eb39c6ce25f2cf19816ab688cd', hidden=None),
    't0368': dict(source='non-pass', repo=NONOUN / 'sdlc-lite', base='6a14c1658afa9715ad2695c6c35b2cda44be5bfc', setup=None,
                  copy=None, rel='.sdlc/0368-prune-flag/handoff.md', blocked_sha=None,
                  hidden='grep -q "dispatch.py prune" plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -q "dispatch.py prune" plugins/sdlc-lite/skills/fanout/SKILL.md'),
    't0373': dict(source='non-pass', repo=NONOUN / 'sdlc-lite', base='687d169e100f5a28cf9e3e6ca5b63cdc22b30b4b', setup=None,
                  copy=None, rel='.sdlc/0373-codex-role-preflight/handoff.md', blocked_sha=None,
                  hidden='grep -qi "readiness and resume" plugins/sdlc-lite/agents/solo.md && grep -qi "readiness and resume" plugins/sdlc-lite/skills/agent/SKILL.md'),
    't0378': dict(source='non-pass', repo=NONOUN / 'sdlc-lite', base='b599114e2746e41bc227910242d988ef64cbdfe0', setup=None,
                  copy=None, rel='.sdlc/0378-red-checkpoint-builder/handoff.md', blocked_sha=None,
                  hidden='out=$(python3 plugins/sdlc-lite/scripts/redck.py selftest 2>&1); printf "%s\\n" "$out" | grep -qF "ok: a handoff changed after the original checkpoint" && printf "%s\\n" "$out" | grep -qF "ok: an unbound control"'),
}


def run(cmd, cwd, env=None, timeout=None, shell=False):
    return subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=timeout, shell=shell)


def child_env(role, extra=None):
    env = dict(os.environ)
    for k in ('FANOUT_ROOT', 'FANOUT_HANDOFF', 'FANOUT_PLUGIN_ROOT', 'CLAUDE_CODE_AGENT', 'SDLC_LANE_OVERRIDE',
              'SDLC_LIFECYCLE_CHILD', 'SDLC_ATTEMPT_NAME', 'SDLC_BASE_SHA', 'SDLC_TMP_WORKTREES'):
        env.pop(k, None)
    env['SDLC_ROLE'] = role
    env.update(extra or {})
    return env


def section(text, name):
    m = re.search(r'^## %s\s*\n(.*?)(?=^## |\Z)' % re.escape(name), text, re.M | re.S)
    return m.group(1).strip() if m else ''


def minutes(attempt):
    try:
        a = json.loads(Path(attempt).read_text())
        s, f = datetime.fromisoformat(a['started_at']), datetime.fromisoformat(a['finished_at'])
        return round((f - s).total_seconds() / 60, 1), a.get('status')
    except (OSError, KeyError, ValueError):
        return None, None


def dispatch_role(cell, handoff, role, level, root, reason, log, extra_env=None):
    """prepare with the armB root, run headless with `root`, record; return (dispatch, row, result text, minutes)."""
    armB = TMP / 'armB/plugins/sdlc-lite'
    env = child_env('conductor', extra_env)
    p = run(['python3', str(armB / 'scripts/dispatch.py'), 'prepare', role, level, handoff, '--routing-reason', reason], cell, env)
    log.append('prepare %s %s rc=%d stderr=%s' % (role, level, p.returncode, p.stderr.strip()[:400]))
    if p.returncode != 0:
        raise SystemExit('prepare refused (%d): %s %s' % (p.returncode, p.stdout[-800:], p.stderr[-800:]))
    d = json.loads(p.stdout)
    run_env = child_env(role, {'SDLC_HEADLESS': '1', 'SDLC_TMP_WORKTREES': d['tmp_prefix'],
                               'SDLC_BASE_SHA': d.get('base_sha') or ''})
    cmd = ['claude', '-p', '--plugin-dir', str(root / 'plugins/sdlc-lite'), '--agent', 'sdlc-lite:%s-%s' % (role, level),
           '--model', d['model'], '--effort', d['effort'], '--dangerously-skip-permissions', '--output-format', 'json', d['prompt']]
    log.append('run %s-%s model=%s effort=%s plugin-dir=%s' % (role, level, d['model'], d['effort'], root / 'plugins/sdlc-lite'))
    c = run(cmd, cell, run_env, timeout=3000)
    try:
        out = json.loads(c.stdout)
    except ValueError:
        raise SystemExit('claude output not json rc=%d: %s %s' % (c.returncode, c.stdout[-800:], c.stderr[-800:]))
    text = out.get('result') or ''
    res = Path(d['result'])
    if not res.is_file() or not res.read_text().strip():
        res.write_text(text if text.endswith('\n') else text + '\n')
    text = res.read_text()
    sid = out.get('session_id')
    tr = glob.glob(os.path.expanduser('~/.claude/projects/*/%s.jsonl' % sid))
    log.append('session %s transcript=%s duration_ms=%s cli_cost=%s' % (sid, tr[:1], out.get('duration_ms'), out.get('total_cost_usd')))
    rec = ['python3', str(armB / 'scripts/dispatch.py'), 'record', d['dispatch_file'], '--duration-ms', str(out.get('duration_ms') or 0)]
    if tr:
        rec += ['--transcript', tr[0]]
    r = run(rec, cell, child_env('conductor'))
    log.append('record %s rc=%d %s' % (role, r.returncode, (r.stdout + r.stderr).strip()[-300:]))
    rows = [json.loads(l) for l in (Path(handoff_dir(cell, handoff)) / 'runs.jsonl').read_text().splitlines() if l.strip()]
    row = [x for x in rows if x.get('attempt_id') == d['attempt_id']]
    mins, status = minutes(d['attempt_file'])
    return d, (row[0] if row else None), text, mins


def handoff_dir(cell, handoff):
    return (Path(cell) / handoff).parent


def block_tag(status, notes):
    first = notes.strip().splitlines()[0].strip().lower() if notes.strip() else ''
    if status.startswith('inherited red'):
        return 'inherited red'
    for tag in ('plan defect', 'stale lane', 'inherited red'):
        if first.startswith(tag):
            return tag
    return 'other'


def main():
    task, level, arm, rep = sys.argv[1:5]
    t = TASKS[task]
    name = 'rt-%s-%s-%s-%s' % (task, level, arm, rep)
    cell = TMP / name
    log = []
    if cell.exists():
        raise SystemExit('cell exists: %s' % cell)
    run(['git', 'clone', '-q', '--shared', str(t['repo']), str(cell)], TMP).check_returncode()
    run(['git', 'checkout', '-q', '--detach', t['base']], cell).check_returncode()
    if t['setup']:
        s = run(t['setup'], cell, shell=True, timeout=1200)
        log.append('setup %r rc=%d' % (t['setup'], s.returncode))
    hp = cell / t['rel']
    if t['copy']:
        hp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(t['copy'], hp)
    sha = hashlib.sha256(hp.read_bytes()).hexdigest()
    note = ''
    if t['blocked_sha']:
        note = 'handoff sha256 %s %s blocked row %s' % (sha[:12], 'matches' if sha == t['blocked_sha'] else 'MISMATCH vs', t['blocked_sha'][:12])
    log.append('handoff %s sha256=%s %s' % (t['rel'], sha, note))
    armB = TMP / 'armB/plugins/sdlc-lite'
    lint = run(['python3', str(armB / 'scripts/steps.py'), 'lint', str(hp.parent)], cell)
    log.append('steps.py lint rc=%d %s' % (lint.returncode, (lint.stdout + lint.stderr).strip()[-300:]))
    if lint.returncode != 0:
        raise SystemExit('lint refused: %s' % '\n'.join(log))
    extra = {'SDLC_LANE_OVERRIDE': LANE} if t['repo'].name == 'sdlc-lite' else {}
    root = TMP / ('arm' + arm)
    d, brow, btext, bmin = dispatch_role(cell, t['rel'], 'builder', level, root, 'T-0458 overlay retest arm %s' % arm, log, extra)
    status = section(btext, 'Status').splitlines()[0].strip().lower() if section(btext, 'Status') else 'missing'
    notes = section(btext, 'Notes')
    blocked = status.startswith('blocked') or status.startswith('inherited red') or status == 'missing'
    tag = block_tag(status, notes) if blocked else 'none'
    vrow, vtext, vmin, verdict = None, '', 0, 'n/a'
    if not blocked:
        vl = 'L1' if level == 'L1' else 'L3'
        vd, vrow, vtext, vmin = dispatch_role(cell, t['rel'], 'verifier', vl, TMP / 'armB', 'T-0458 overlay retest arm %s verifier' % arm, log)
        v = section(vtext, 'Verdict')
        verdict = v.splitlines()[0].strip().lower() if v else 'missing'
    hidden = 'n/a'
    if t['hidden'] and not blocked:
        h = run(t['hidden'], cell, child_env('conductor'), shell=True, timeout=600)
        hidden = 'pass' if h.returncode == 0 else 'fail'
    bc = brow.get('cost_usd') if brow else None
    vc = vrow.get('cost_usd') if vrow else 0
    first = notes.strip().splitlines()[0] if (blocked and notes.strip()) else ''
    rowtxt = '| %s | %s | %s | %s | %s | %.2f | %s | %s | %s | %s | %s | %.2f | %s |' % (
        task, t['source'], level, arm, rep, bc or 0, bmin, 'yes' if blocked else 'no', tag, hidden, verdict, vc or 0, vmin or 0)
    line = '- %s %s status=%s cost_usd=%s verifier_cost_usd=%s %s; block Notes: %s; %s\n' % (
        datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), rowtxt, status, bc, vc, note, first or 'none', ' '.join(' / '.join(log[-1:]).split()))
    with open(RUNLOG, 'a') as f:
        f.write(line)
    EVID.mkdir(parents=True, exist_ok=True)
    out = EVID / name
    out.mkdir(exist_ok=True)
    (out / 'builder.md').write_text(btext)
    if vtext:
        (out / 'verifier.md').write_text(vtext)
    with open(out / 'rows.jsonl', 'w') as f:
        for r in (brow, vrow):
            if r:
                f.write(json.dumps(r, separators=(',', ':')) + '\n')
    (out / 'log.txt').write_text('\n'.join(log) + '\n')
    print(rowtxt)
    print('\n'.join(log))
    print('status:', status, '| notes first line:', first)


if __name__ == '__main__':
    main()
