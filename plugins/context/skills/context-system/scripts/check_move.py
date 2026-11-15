#!/usr/bin/env python3
"""Check a planned move of files in a corpus before it is made, and the result after it.

Usage: check_move.py --before DIR --map MAP.json [--consumers DIR ...] [--after DIR] [--strict]

MAP.json is the move, written before anything is moved:
  {"moves": [{"from": "voice.md", "to": "shared/voice.md"}, {"from": "run.md", "to": "old/run.md", "edited": true}],
   "adds": ["OVERVIEW.md"], "removes": ["scratch.md"], "consumersUpdated": ["jobs/publish.sh"]}
Paths are relative to the corpus root. `edited` says the moved file's text changes too (its links were rewritten).
`consumersUpdated` lists files under a --consumers folder that are changed in the same change.

Before the move (always):
  unknown-source    A `from` or `removes` path that is not a file under --before.
  overwrite         A `to` or `adds` path that is already a file under --before and is not moved away or removed.
  case-collision    A `to` or `adds` path that differs only by letter case from a file that stays, or from another
                    destination. On a file system that folds case the second write replaces the first without an error.
  outside-referrer  A file under --consumers that names a moved or removed file and is not in `consumersUpdated`.
  outside-reader    (warning) A file under --consumers that names the corpus folder: it may reach a moved file through
                    a pattern or a built path. Read it.

After the move (with --after):
  lost-file         A file that should be there is not: a kept file, a `to` or an `adds` path.
  parity            A moved file whose bytes differ from its source and that the map does not mark `edited`.
  count             The number of files is not: files before, minus removes, plus adds. An overwrite shows up here.
  unaccounted       A file under --after that the map does not explain.
  not-removed       (warning) A `from` path that still exists after the move.

Names are compared as written on disk, never through a case-folding lookup. --consumers folders are read as text
whatever their suffix (scripts, configs, schedules). Each finding is one line: SEVERITY RULE WHERE: problem. Fix: fix.
Exit 0 when there are no errors (warnings allowed unless --strict), 1 on errors, 2 when an input cannot be read.
Standard library only; runs on Python 3.9.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

SKIP = ('.git', '__pycache__', 'node_modules')


def listing(root):
    """Relative POSIX paths of the files under root, spelled as the directory lists them."""
    out = set()
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in files:
            if name != '.DS_Store':
                out.add(Path(folder, name).relative_to(root).as_posix())
    return out


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(before, plan, consumers=(), after=None):
    f = []  # (severity, rule, where, problem, fix)
    have = listing(before)
    moves = plan.get('moves', [])
    sources = [m['from'] for m in moves]
    removes, adds = list(plan.get('removes', [])), list(plan.get('adds', []))
    for p in sources + removes:
        if p not in have:
            f.append(('ERROR', 'unknown-source', p, 'not a file under the corpus root.', 'write the path as the directory lists it.'))
    stays = have - set(sources) - set(removes)
    folded, seen = {p.casefold(): p for p in stays}, {}
    for d in [m['to'] for m in moves] + adds:
        if d in stays:
            f.append(('ERROR', 'overwrite', d, 'a file with this path stays in place.', 'move that file first, or choose another destination.'))
        elif d.casefold() in folded:
            f.append(('ERROR', 'case-collision', d, f'differs only by case from {folded[d.casefold()]}, which stays in place.',
                      'rename or move that file in the same map, or choose another destination.'))
        if d.casefold() in seen and seen[d.casefold()] != d:
            f.append(('ERROR', 'case-collision', d, f'differs only by case from the destination {seen[d.casefold()]}.', 'choose distinct names.'))
        seen.setdefault(d.casefold(), d)
    gone = {Path(p).name: p for p in sources + removes}
    updated = set(plan.get('consumersUpdated', []))
    for c in consumers:
        c = Path(c)
        for rel in sorted(listing(c)):
            if (c / rel).resolve().is_relative_to(Path(before).resolve()):
                continue
            try:
                lines = (c / rel).read_text(encoding='utf-8').split('\n')
            except (OSError, UnicodeDecodeError):
                continue
            for n, line in enumerate(lines, 1):
                for name, p in gone.items():
                    if name in line:
                        if rel not in updated:
                            f.append(('ERROR', 'outside-referrer', f'{rel}:{n}', f'names {p}, which the map moves or removes.',
                                      'hold the file, or change this consumer in the same change and list it under consumersUpdated.'))
            if rel not in updated:
                for n, line in enumerate(lines, 1):
                    if Path(before).resolve().name in line:
                        f.append(('WARNING', 'outside-reader', f'{rel}:{n}', 'names the corpus folder; a pattern or a built path may reach a moved file.',
                                  'read it, then hold what it reads or list it under consumersUpdated.'))
                        break
    if after is not None:
        now = listing(after)
        expect = stays | {m['to'] for m in moves} | set(adds)
        for p in sorted(expect - now):
            f.append(('ERROR', 'lost-file', p, 'expected after the move and not there.', 'restore it from the source before removing anything else.'))
        for p in sorted(now - expect):
            if p in sources:
                f.append(('WARNING', 'not-removed', p, 'the source of a move is still there.', 'remove it once the copy is verified.'))
            else:
                f.append(('ERROR', 'unaccounted', p, 'the map does not explain this file.', 'add it to the map, or remove it.'))
        for m in moves:
            if m['from'] in have and m['to'] in now and not m.get('edited') and digest(Path(before) / m['from']) != digest(Path(after) / m['to']):
                f.append(('ERROR', 'parity', m['to'], f'bytes differ from {m["from"]}.', 'copy it again, or mark the move edited if its text was meant to change.'))
        want = len(have) - len(removes) + len(adds)
        got = len(now - (set(sources) - expect))
        if got != want:
            f.append(('ERROR', 'count', str(after), f'{got} files, expected {want} ({len(have)} before, {len(removes)} removed, {len(adds)} added).',
                      'find the file that was replaced or dropped; a write to a name that differs only by case replaces the file.'))
    return f


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--before', required=True, help='the corpus root before the move (or an untouched copy of it)')
    ap.add_argument('--map', required=True, help='the move, as JSON')
    ap.add_argument('--consumers', action='append', default=[], help='a folder outside the corpus that may read it by path; repeatable')
    ap.add_argument('--after', help='the corpus root after the move')
    ap.add_argument('--strict', action='store_true', help='warnings fail too')
    args = ap.parse_args(argv)
    for d in [args.before, *args.consumers, *([args.after] if args.after else [])]:
        if not Path(d).is_dir():
            print(f'ERROR read {d}: not a directory. Fix: pass a folder.')
            return 2
    try:
        plan = json.loads(Path(args.map).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'ERROR read {args.map}: {exc}. Fix: write the move as JSON.')
        return 2
    findings = check(args.before, plan, args.consumers, args.after)
    for sev, rule, where, problem, fix in findings:
        print(f'{sev} {rule} {where}: {problem} Fix: {fix}')
    errors = sum(x[0] == 'ERROR' for x in findings)
    print(f'check_move: {errors} error(s), {len(findings) - errors} warning(s)')
    return 1 if errors or (args.strict and findings) else 0


if __name__ == '__main__':
    sys.exit(main())
