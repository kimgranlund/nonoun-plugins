#!/usr/bin/env python3
"""compaction_handoff.py: write, clear, or date the one `## Compaction handoff` section of a gitignored file.

  compaction_handoff.py write --file <path> [--text <body>]
  compaction_handoff.py clear --file <path>
  compaction_handoff.py status --file <path>
  compaction_handoff.py selftest

The section key is the exact H2 `## Compaction handoff`, one per file. Its span runs from that line to the next H2 or the end
of the file. No other byte of the file is changed, except that a last line with no newline gets one before a section is appended.

write   takes the body from --text or stdin. It exits 2 and writes nothing when neither CLAUDECODE nor CLAUDE_CODE_ENTRYPOINT
        is set (not a Claude Code session), when `git check-ignore -q` fails for the file (it could be committed), or when the
        body is empty or over 8 lines. Otherwise it creates the file if missing, removes the old span, and appends the H2 and
        the body at the end.
clear   removes the span and nothing else. Exit 0 also when the file or the H2 is absent.
status  prints `none` (no file or no H2), `fresh`, or `stale: written <timestamp>`, read from the body's
        `Written <YYYY-MM-DD HH:MM>` line in local time. A section is stale at over 24 hours, or with no such line
        (`stale: written unknown`).
selftest runs every case in a temporary git repository and prints one `ok: handoff: <case>` line per case.

Deterministic: no model call, no network. It never runs a compaction.
"""
import argparse
import datetime
import os
import pathlib
import re
import subprocess
import sys
import tempfile

H2 = '## Compaction handoff'
MAX_BODY_LINES = 8
STALE_HOURS = 24
HOST_VARS = ('CLAUDECODE', 'CLAUDE_CODE_ENTRYPOINT')
WRITTEN = re.compile(r'Written (\d{4}-\d{2}-\d{2} \d{2}:\d{2})')
STAMP = '%Y-%m-%d %H:%M'


def split_span(text):
    """(text without the handoff spans, the body of the last span or None). A span is the H2 line to the next H2 or the end."""
    kept, body, inside = [], None, False
    for line in text.splitlines(keepends=True):
        if line.rstrip('\r\n') == H2:
            inside, body = True, []
        elif inside and line.startswith('## '):
            inside = False
            kept.append(line)
        elif inside:
            body.append(line)
        else:
            kept.append(line)
    return ''.join(kept), (None if body is None else ''.join(body))


def read(path):
    return path.read_text(encoding='utf-8') if path.is_file() else None


def ignored(path):
    """True when git ignores the file. False outside a repository, or when git is missing."""
    try:
        r = subprocess.run(['git', 'check-ignore', '-q', path.name], cwd=str(path.parent), capture_output=True)
    except OSError:
        return False
    return r.returncode == 0


def refuse(why):
    print(f'compaction_handoff.py: refused: {why}', file=sys.stderr)
    return 2


def cmd_write(path, body):
    if not any(os.environ.get(v) for v in HOST_VARS):
        return refuse('not a Claude Code session (neither CLAUDECODE nor CLAUDE_CODE_ENTRYPOINT is set)')
    lines = body.strip('\n').splitlines()
    if not body.strip():
        return refuse('the body is empty')
    if len(lines) > MAX_BODY_LINES:
        return refuse(f'the body has {len(lines)} lines; the cap is {MAX_BODY_LINES}')
    if not path.parent.is_dir() or not ignored(path):
        return refuse(f'`git check-ignore -q {path.name}` fails; add {path.name} to .gitignore first')
    rest = split_span(read(path) or '')[0]
    if rest and not rest.endswith('\n'):
        rest += '\n'
    path.write_text(rest + H2 + '\n' + '\n'.join(lines) + '\n', encoding='utf-8')
    print(f'written: {H2} in {path} ({len(lines)} lines)')
    return 0


def cmd_clear(path):
    text = read(path)
    rest, body = split_span(text or '')
    if body is None:
        print('none')
        return 0
    path.write_text(rest, encoding='utf-8')
    print(f'cleared: {H2} in {path}')
    return 0


def cmd_status(path, now=None):
    body = split_span(read(path) or '')[1]
    if body is None:
        print('none')
        return 0
    m = WRITTEN.search(body)
    try:
        when = datetime.datetime.strptime(m.group(1), STAMP) if m else None
    except ValueError:
        when = None
    if when is None:
        print('stale: written unknown')
    elif (now or datetime.datetime.now()) - when > datetime.timedelta(hours=STALE_HOURS):
        print(f'stale: written {m.group(1)}')
    else:
        print('fresh')
    return 0


def selftest():
    me = str(pathlib.Path(__file__).resolve())
    clean = {k: v for k, v in os.environ.items() if k not in HOST_VARS and not k.startswith('GIT_')}
    inside = dict(clean, CLAUDECODE='1')
    bad = []

    def run(env, *args, stdin=None):
        return subprocess.run([sys.executable, me, *args], env=env, input=stdin, capture_output=True, text=True)

    def case(name, cond):
        print(('ok: ' if cond else 'FAIL: ') + 'handoff: ' + name)
        if not cond:
            bad.append(name)

    def stamp(hours):
        return (datetime.datetime.now() - datetime.timedelta(hours=hours)).strftime(STAMP)
    with tempfile.TemporaryDirectory() as d:
        repo = pathlib.Path(d)
        subprocess.run(['git', 'init', '-q', str(repo)], env=clean, check=True, capture_output=True)
        (repo / '.gitignore').write_text('CLAUDE.local.md\n', encoding='utf-8')
        f, tracked = repo / 'CLAUDE.local.md', repo / 'notes.md'
        before = 'Keep me.\n\n' + H2 + '\nold body\n\n## Other\nstay\n'
        kept = 'Keep me.\n\n## Other\nstay\n'
        f.write_text(before, encoding='utf-8')
        r1 = run(inside, 'write', '--file', str(f), '--text', 'GOAL first\nNEXT one')
        once = f.read_text(encoding='utf-8')
        r2 = run(inside, 'write', '--file', str(f), stdin='GOAL second\n')
        twice = f.read_text(encoding='utf-8')
        new = repo / 'sub' / 'CLAUDE.local.md'
        new.parent.mkdir()
        r3 = run(inside, 'write', '--file', str(new), '--text', 'GOAL third')
        case('write replaces the one handoff H2',
             (r1.returncode, r2.returncode, r3.returncode) == (0, 0, 0) and once == kept + H2 + '\nGOAL first\nNEXT one\n'
             and twice == kept + H2 + '\nGOAL second\n' and new.read_text(encoding='utf-8') == H2 + '\nGOAL third\n')
        r1 = run(clean, 'clear', '--file', str(f))
        cleared = f.read_text(encoding='utf-8')
        r2 = run(clean, 'clear', '--file', str(f))
        r3 = run(clean, 'clear', '--file', str(repo / 'absent.md'))
        case('clear removes only the handoff H2', (r1.returncode, r2.returncode, r3.returncode) == (0, 0, 0) and cleared == kept
             and f.read_text(encoding='utf-8') == kept and r2.stdout == 'none\n' and not (repo / 'absent.md').exists())
        r1 = run(inside, 'write', '--file', str(tracked), '--text', 'GOAL x')
        tracked.write_text('mine\n', encoding='utf-8')
        r2 = run(inside, 'write', '--file', str(tracked), '--text', 'GOAL x')
        case('write refuses a file that is not gitignored',
             (r1.returncode, r2.returncode) == (2, 2) and tracked.read_text(encoding='utf-8') == 'mine\n' and 'check-ignore' in r1.stderr)
        r1 = run(inside, 'write', '--file', str(f), '--text', '\n'.join(f'line {i}' for i in range(9)))
        r2 = run(inside, 'write', '--file', str(f), '--text', '\n'.join(f'line {i}' for i in range(8)))
        eight = f.read_text(encoding='utf-8')
        f.write_text(kept, encoding='utf-8')
        r3 = run(inside, 'write', '--file', str(f), '--text', '\n'.join(f'line {i}' for i in range(9)))
        case('write refuses a body over 8 lines', (r1.returncode, r2.returncode, r3.returncode) == (2, 0, 2)
             and eight.count('\nline ') == 8 and f.read_text(encoding='utf-8') == kept)
        r1 = run(clean, 'write', '--file', str(f), '--text', 'GOAL x')
        r2 = run(dict(clean, CLAUDE_CODE_ENTRYPOINT='cli'), 'write', '--file', str(f), '--text', 'GOAL x')
        case('write refuses outside Claude Code', r1.returncode == 2 and 'Claude Code' in r1.stderr and r2.returncode == 0
             and f.read_text(encoding='utf-8') == kept + H2 + '\nGOAL x\n')
        run(clean, 'clear', '--file', str(f))
        none = run(clean, 'status', '--file', str(f)).stdout
        old = stamp(25)
        run(inside, 'write', '--file', str(f), '--text', f'Written {old} by /sdlc-lite:plan compaction.\nGOAL x')
        stale = run(clean, 'status', '--file', str(f)).stdout
        run(inside, 'write', '--file', str(f), '--text', f'Written {stamp(23)} by /sdlc-lite:plan compaction.\nGOAL x')
        fresh = run(clean, 'status', '--file', str(f)).stdout
        run(inside, 'write', '--file', str(f), '--text', 'GOAL x')
        undated = run(clean, 'status', '--file', str(f)).stdout
        case('status reports a section older than 24 hours',
             (none, stale, fresh, undated) == ('none\n', f'stale: written {old}\n', 'fresh\n', 'stale: written unknown\n'))
    print(f'compaction_handoff selftest: {"FAIL" if bad else "PASS"} (6 cases)')
    return 1 if bad else 0


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    ap = argparse.ArgumentParser(prog='compaction_handoff.py', description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('write', 'clear', 'status'):
        p = sub.add_parser(name)
        p.add_argument('--file', required=True)
        if name == 'write':
            p.add_argument('--text')
    a = ap.parse_args(argv)
    path = pathlib.Path(a.file).resolve()
    if a.cmd == 'write':
        return cmd_write(path, a.text if a.text is not None else sys.stdin.read())
    return cmd_clear(path) if a.cmd == 'clear' else cmd_status(path)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
