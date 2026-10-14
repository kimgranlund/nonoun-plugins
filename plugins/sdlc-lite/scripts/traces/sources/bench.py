"""Bench baseline reader: the passed-step cost baseline of a bench dir's results.

baseline(bench_dir) returns a dict over <bench_dir>/results/*/step-<n>/ (never a .superseded- dir),
the step dirs read from each result dir's records dir (order.records_dir: results/runtime/tasks/<run>/,
or the result dir itself when it holds its records in place; the `runtime` name is no result dir):
  median_cost_per_passed_step  the median step cost over counted steps, or None when no step
                               counts or the results dir is missing;
  steps   the (result dir, step n, cost) tuples that counted: a step counts when its newest
          verifier (order.newest) has verdict pass (steps.verdict_or_none); its cost is the sum
          of cost_usd over that step dir's runs.jsonl;
  hidden  {result dir: the hidden_check: value of its grade.md, or None}.
default_bench_dir() follows scripts/bench-dir.sh: $SDLC_BENCH_DIR, else <git toplevel>/bench
when it exists, else the plugin's own bench/.
"""
import os, re, statistics, subprocess

import order  # same scripts/ dir
import steps

from . import runs

STEP_RE = re.compile(r'^step-(\d+)$')
HIDDEN_RE = re.compile(r'^\s*hidden_check:\s*(.*?)\s*$')


def _hidden(result_dir):
    try:
        with open(os.path.join(result_dir, 'grade.md'), encoding='utf-8') as f:
            for line in f:
                m = HIDDEN_RE.match(line)
                if m:
                    return m.group(1)
    except (OSError, UnicodeDecodeError):
        pass
    return None


def _cost(step_dir):
    total = 0.0
    for rec in runs.read(step_dir)[0]:
        c = rec.get('cost_usd')
        if isinstance(c, (int, float)) and not isinstance(c, bool):
            total += c
    return total


def baseline(bench_dir):
    out = {'median_cost_per_passed_step': None, 'steps': [], 'hidden': {}}
    results = os.path.join(bench_dir, 'results')
    try:
        names = sorted(os.listdir(results))
    except OSError:
        return out
    for name in names:
        rdir = os.path.join(results, name)
        if name == 'runtime' or not os.path.isdir(rdir):
            continue
        out['hidden'][rdir] = _hidden(rdir)   # grade.md stays in the result dir
        rec = str(order.records_dir(rdir))
        try:
            snames = os.listdir(rec)
        except OSError:
            snames = []
        found = []
        for sname in snames:
            m = STEP_RE.match(sname)  # anchored: step-<n>.superseded-<k> never matches
            sdir = os.path.join(rec, sname)
            if m and os.path.isdir(sdir):
                found.append((int(m.group(1)), sdir))
        for n, sdir in sorted(found):
            v = order.newest(sdir, 'verifier')
            if v and steps.verdict_or_none(v) == 'pass':
                out['steps'].append((rdir, n, _cost(sdir)))
    if out['steps']:
        out['median_cost_per_passed_step'] = statistics.median(c for _, _, c in out['steps'])
    return out


def default_bench_dir():
    env = os.environ.get('SDLC_BENCH_DIR')
    if env:
        return os.path.abspath(env)
    try:
        top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True,
                             text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        top = ''
    if top and os.path.isdir(os.path.join(top, 'bench')):
        return os.path.join(top, 'bench')
    here = os.path.dirname(os.path.abspath(__file__))  # scripts/traces/sources
    return os.path.normpath(os.path.join(here, '..', '..', '..', 'bench'))
