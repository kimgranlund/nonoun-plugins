"""Command line for traces.py.

  selftest [-k FAMILY]
  ingest <repo> [--lanes-dir DIR]... [--out DIR] [--bench-dir DIR] [--rerun-criteria]
         [--load-series PATH] [--factory-transcript PATH]...
      runs ingest.run and prints the events.jsonl path.
  detect [--repo REPO] [--out DIR]
      reads <out>/events.jsonl and aux.json, runs the four detector families, merges the
      findings through findings.write, prints each note and then the findings.jsonl path.
  clusters --max N [--repo REPO] [--out DIR]
      prints findings.clusters(out, N) as JSON.
  context <log> [--backend claude|codex] [--codex-home DIR]
      prints one JSON line, sources/context.read of the log: the paths the run read, or a
      status ('log absent', 'rollout absent', ...); exit 0 whatever the status (run.sh records it).
detect and clusters resolve the out dir as ingest does (store.out_dir; REPO defaults to `.`).
None of these spawns a claude or codex process.
"""
import argparse, datetime, json, os, sys

from . import findings, ingest, selftest, store
from .sources import context
from .detectors import cost, escalation, hygiene, plan

USAGE = ('usage: traces.py selftest [-k FAMILY] | ingest <repo> [...] | detect [...] | '
         'clusters --max N [...] | context <log> [...]')


def usage():
    print(USAGE, file=sys.stderr)
    return 2


def _selftest(rest):
    family = None
    if rest:
        if len(rest) == 2 and rest[0] == '-k' and rest[1]:
            family = rest[1]
        else:
            return usage()
    return selftest.run(family)


def _parser(prog):
    return argparse.ArgumentParser(prog=f'traces.py {prog}')


def _ingest(rest):
    p = _parser('ingest')
    p.add_argument('repo')
    p.add_argument('--lanes-dir', action='append', default=[])
    p.add_argument('--out')
    p.add_argument('--bench-dir')
    p.add_argument('--rerun-criteria', action='store_true')
    p.add_argument('--load-series')
    p.add_argument('--factory-transcript', action='append', default=[])
    a = p.parse_args(rest)
    out = ingest.run(a.repo, lanes_dirs=a.lanes_dir, out=a.out, bench_dir=a.bench_dir,
                     rerun_criteria=a.rerun_criteria, load_series=a.load_series,
                     factory_transcripts=a.factory_transcript)
    print(os.path.join(out, store.EVENTS))
    return 0


def _read(out):
    rows = []
    with open(os.path.join(out, store.EVENTS), encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    with open(os.path.join(out, store.AUX), encoding='utf-8') as f:
        aux = json.load(f)
    return rows, aux


def _detect(rest):
    p = _parser('detect')
    p.add_argument('--repo', default='.')
    p.add_argument('--out')
    a = p.parse_args(rest)
    out = store.out_dir(a.repo, a.out)
    for name in (store.EVENTS, store.AUX):
        if not os.path.isfile(os.path.join(out, name)):
            print(f'traces detect: {os.path.join(out, name)} is missing; run `traces.py ingest` first',
                  file=sys.stderr)
            return 2
    rows, aux = _read(out)
    found, notes = cost.detect(rows, aux)
    found = list(found)
    for fam in (escalation, plan, hygiene):
        found.extend(fam.detect(rows, aux))
    findings.write(out, found, datetime.datetime.now(datetime.timezone.utc))
    for n in notes:
        print(n)
    print(os.path.join(out, findings.FINDINGS))
    return 0


def _clusters(rest):
    p = _parser('clusters')
    p.add_argument('--max', type=int, required=True)
    p.add_argument('--repo', default='.')
    p.add_argument('--out')
    a = p.parse_args(rest)
    out = store.out_dir(a.repo, a.out)
    print(json.dumps(findings.clusters(out, a.max), indent=2, ensure_ascii=False))
    return 0


def _context(rest):
    p = _parser('context')
    p.add_argument('log')
    p.add_argument('--backend', choices=('claude', 'codex'))
    p.add_argument('--codex-home')
    a = p.parse_args(rest)
    print(json.dumps(context.read(a.log, backend=a.backend, codex_home=a.codex_home),
                     ensure_ascii=False))
    return 0


COMMANDS = {'selftest': _selftest, 'ingest': _ingest, 'detect': _detect, 'clusters': _clusters,
            'context': _context}


def main(argv):
    argv = list(argv)
    if not argv or argv[0] not in COMMANDS:
        return usage()
    return COMMANDS[argv[0]](argv[1:])
