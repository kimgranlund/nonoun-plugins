"""Rerun: run a passed step's acceptance criteria at its base-sha, to see which never went red.

run(repo, rows, thresholds=None) returns a list of records, one per span run (or per step dir
whose base worktree could not be made). It takes each step dir the rows name (a row with a step
number; paths are relative to repo) whose newest verifier result (order.newest) has verdict pass
(steps.verdict_or_none) and that holds a `base-sha` file, and from its handoff.md the command
spans of each acceptance criterion line (steps.line_spans over steps.criteria_indexed), minus
the (guard) spans (steps.guard_spans) and minus the spans steps.guard_skipped flags. Each span
runs through steps.run_guard (`bash -c`, own session, killed on timeout) with SDLC_BASE_SHA set
to the base-sha, cwd a detached throwaway worktree of repo at that sha, and the per-span timeout
thresholds' rerun_timeout_secs.

Worktrees live under $SDLC_TMP_WORKTREES/traces-rerun-<pid> when that variable is set, else
under a tempfile.mkdtemp() dir (outside repo). In `finally` each one is removed with
`git worktree remove --force`, then `git worktree prune` runs and the root dir is deleted, so
`git worktree list` of repo is unchanged by a run.

A record is {step_dir, handoff, line (1-based, in handoff), span, base_sha, exit_code (None on
timeout), timed_out}, or {step_dir, handoff, base_sha, error} when the worktree failed.
"""
import os, shutil, subprocess, tempfile

import order  # same scripts/ dir: newest-result ordering
import steps  # same scripts/ dir: criteria spans, guard rules, span runner

from .detectors import thresholds as _thresholds
from .sources import git


def _git(repo, *args):
    try:
        p = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                           errors='replace', env=git._env(), stdin=subprocess.DEVNULL,
                           timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)
    return p.returncode, (p.stderr or p.stdout).strip()


def _step_dirs(rows):
    out = set()
    for r in rows or []:
        if not isinstance(r, dict) or r.get('step') is None:
            continue
        srcs = [s for s in r.get('sources') or [] if isinstance(s, str) and s]
        if srcs:
            out.add(os.path.dirname(srcs[0]).replace(os.sep, '/'))
    return sorted(out)


def _base(d):
    try:
        with open(os.path.join(d, 'base-sha'), encoding='utf-8') as f:
            first = (f.read().splitlines() or [''])[0].strip()
    except (OSError, UnicodeDecodeError):
        return None
    return first or None


def criteria(handoff):
    """[(line number, span)] of the non-guard, runnable command spans of a step handoff."""
    try:
        with open(handoff, encoding='utf-8') as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return []
    guards = set(steps.guard_spans(text))
    out = []
    for i, line in steps.criteria_indexed(text.splitlines()):
        for span in steps.line_spans(line):
            if span in guards or steps.guard_skipped(span):
                continue
            out.append((i + 1, span))
    return out


def _passed(d):
    newest = order.newest(d, 'verifier')
    return bool(newest) and steps.verdict_or_none(newest) == 'pass'


def run(repo, rows, thresholds=None):
    repo = os.path.abspath(repo)
    timeout = _thresholds.merged(thresholds)['rerun_timeout_secs']
    jobs = []
    for rel in _step_dirs(rows):
        d = os.path.join(repo, rel)
        base = _base(d)
        if not base or not os.path.isdir(d) or not _passed(d):
            continue
        spans = criteria(os.path.join(d, 'handoff.md'))
        if spans:
            jobs.append((rel, base, spans))
    if not jobs:
        return []
    tmp_root = os.environ.get('SDLC_TMP_WORKTREES')
    if tmp_root:
        root = os.path.join(tmp_root, f'traces-rerun-{os.getpid()}')
        os.makedirs(root, exist_ok=True)
    else:
        root = tempfile.mkdtemp(prefix='traces-rerun-')
    made, out = {}, []
    try:
        for rel, base, spans in jobs:
            handoff = f'{rel}/handoff.md'
            if base not in made:
                wt = os.path.join(root, f'wt-{len(made) + 1}')
                rc, err = _git(repo, 'worktree', 'add', '--detach', '--quiet', wt, base)
                made[base] = (wt, None) if rc == 0 else (None, err or f'exit {rc}')
            wt, err = made[base]
            if wt is None:
                out.append({'step_dir': rel, 'handoff': handoff, 'base_sha': base, 'error': err})
                continue
            for line, span in spans:
                rc, _ = steps.run_guard(span, wt, timeout, base)
                out.append({'step_dir': rel, 'handoff': handoff, 'line': line, 'span': span,
                            'base_sha': base, 'exit_code': rc, 'timed_out': rc is None})
    finally:
        for wt, _ in made.values():
            if wt:
                _git(repo, 'worktree', 'remove', '--force', wt)
        _git(repo, 'worktree', 'prune')
        shutil.rmtree(root, ignore_errors=True)
    return out
