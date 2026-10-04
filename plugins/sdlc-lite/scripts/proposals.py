#!/usr/bin/env python3
"""proposals.py: repeated failures in past runs, filed as evidence-backed candidate proposals.

scan reads the run records under the .sdlc folder (role results, runs.jsonl files, and notes.md), finds
patterns seen two or more times, and writes one proposal per pattern. Nothing is applied: a proposal moves
forward only through accept (which needs a valid eval), reject (which needs a reason), and promote (which
files an idea ticket through tickets.py new). scan never writes a source file and never changes a status.

Sources (walked under --root with os.walk: names sorted, symlinks not followed, dot folders included; the
top-level proposals, messages, runtime, and dogfood dirs and the --proposals dir are skipped)
  runs.jsonl   one JSON object per line; a line whose role or level is not a string is skipped
  role result  a file named (builder|verifier)-L[1-5](-<suffix>)?.md; sections parse as in results.py
  notes.md     <root>/notes.md lines of the form `- fix-now: <text>` or `- decide: <text>`

Patterns (a key with two or more occurrences becomes a candidate)
  verifier-fail <dir>    verifier results in one dir with Verdict fail
  replan <dir>           planner lines in one runs.jsonl
  builder-bump <dir>     distinct builder levels in one runs.jsonl
  next-attempt <text>    the same `## For the next attempt` text (lowercased) in different dirs
  plan-defect            `plan defect:` lines in failing verifiers and blocked builders
  follow-up <tag> <text> the same notes.md follow-up line
  A dir subject is repo-relative, with the leading dot dropped from a closed ticket folder .NNNN-<slug>.

Proposal file: <proposals>/<kind>-<first 8 hex of sha256(pattern)>[-<k>]/proposal.md
  ---
  id: P-NNNN
  title: <one line>
  status: candidate | accepted | rejected | promoted
  pattern: <kind> <subject>
  occurrences: <number of evidence lines>
  created: YYYY-MM-DD
  eval:                       (empty until accept stamps the repo-relative eval path)
  accepted: YYYY-MM-DD        (each later field only once stamped)
  rejected: YYYY-MM-DD
  reason: <text>
  promoted: YYYY-MM-DD
  ticket: T-NNNN
  ---

  ## Evidence

  - <repo-relative path>:<line> (<where>) "<quote>"

  ## Proposed change

  <one line saying what to examine, never a patch>

CLI (global options come before the subcommand)
  proposals.py [--root DIR] [--proposals DIR] [--plugin DIR] <cmd>
    --root DIR        the .sdlc folder (default: .sdlc); the repo dir is its resolved parent
    --proposals DIR   where proposals live (default: <root>/proposals)
    --plugin DIR      the dir holding scripts/evals.py and scripts/tickets.py
                      (default: the parent of this script's dir)
  scan               file new candidates and refresh the evidence of known ones
  list               one tab-separated line per proposal: id, status, occurrences, folder, title
                     (or `<folder>\\tinvalid: <reason>`); always exits 0
  show <id>          print the proposal file
  accept <id> --eval PATH
                     candidate to accepted; PATH must be a valid eval directly in <root>/evals/
  reject <id> --reason TEXT
                     candidate to rejected
  promote <id>       accepted to promoted: file an idea ticket with tickets.py new and record its id
  selftest           run the temp-dir regression cases, including the negative controls
Exit codes: 0 ok, 1 refusal, 2 usage error. Refusals print `proposals.py: <reason>` on stderr.
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

KINDS = ('verifier-fail', 'replan', 'builder-bump', 'next-attempt', 'plan-defect', 'follow-up')
FIELDS = ('id', 'title', 'status', 'pattern', 'occurrences', 'created', 'eval',
          'accepted', 'rejected', 'reason', 'promoted', 'ticket')
ALWAYS = FIELDS[:7]
REQUIRED = ('id', 'title', 'status', 'pattern', 'occurrences', 'created')
STATUSES = ('candidate', 'accepted', 'rejected', 'promoted')
FORWARD = {('candidate', 'accepted'), ('candidate', 'rejected'), ('accepted', 'promoted')}
SKIP_TOP = ('proposals', 'messages', 'runtime', 'dogfood')

ROLE_RE = re.compile(r'(builder|verifier)-L[1-5](-[A-Za-z0-9-]+)?\.md')
NOTE_RE = re.compile(r'- ((?i:fix-now|decide)):[ \t]*(\S.*)')
DOT_TICKET_RE = re.compile(r'\.\d{4}-.+')
FIELD_LINE_RE = re.compile(r'([a-z]+):(?: (.*))?')
ID_RE = re.compile(r'P-\d{4}')

TITLES = {
    'verifier-fail': 'Repeated verifier fails in %s',
    'replan': 'Repeated planner runs in %s',
    'builder-bump': 'Builder level bump in %s',
    'next-attempt': 'Repeated next-attempt advice: %s',
    'plan-defect': 'Repeated plan defect verdicts',
    'follow-up': 'Repeated %s follow-up: %s',
}
CHANGES = {
    'verifier-fail': 'Examine why this step failed verification more than once: its criteria, its level, '
                     'or its handoff.',
    'replan': 'Examine what the first plan missed and whether a planner rule or the level rubric would have '
              'caught it.',
    'builder-bump': 'Examine why the lower builder level could not finish this step and whether the planner '
                    'picked too low a level.',
    'next-attempt': 'Examine whether this repeated advice belongs in a role contract or a planner rule.',
    'plan-defect': 'Examine the planner rules behind these criteria and whether steps.py lint could refuse them.',
    'follow-up': 'Examine whether this repeated follow-up needs one ticket or a rule instead of more notes.',
}


class Refusal(Exception):
    """A command refuses; the message is the reason."""


# ---------------------------------------------------------------- text helpers

def clean(t):
    """Em dashes to -, whitespace runs to one space, stripped."""
    return ' '.join(t.replace('\u2014', '-').split())


def cut(t, n):
    return t[:n - 3].rstrip() + '...' if len(t) > n else t


def quote(text):
    return cut(clean(text), 160)


def drop(line):
    """The line stripped, without one leading `- ` or `* `."""
    s = line.strip()
    if s.startswith('- ') or s.startswith('* '):
        s = s[2:]
    return s


def today():
    return datetime.date.today().isoformat()


def repo_of(root):
    return Path(root).resolve().parent


def rel(path, repo):
    p = Path(path).resolve()
    try:
        return p.relative_to(repo).as_posix()
    except ValueError:
        return p.as_posix()


def subject_of(dirpath, repo):
    parts = Path(dirpath).relative_to(repo).parts
    return '/'.join(p[1:] if DOT_TICKET_RE.fullmatch(p) else p for p in parts)


def read_source(path):
    """The text of one source file (a role result, a runs.jsonl, or notes.md). Never writes."""
    return Path(path).read_text(encoding='utf-8', errors='replace')  # rule: read-only


# ---------------------------------------------------------------- sources

def sections(lines):
    """{name: [(line index, text), ...]} for each first `## <name>` heading, body to the next `## ` line."""
    out = {}
    cur = None
    for i, line in enumerate(lines):
        if line.startswith('## '):
            name = line.rstrip()[3:]
            if name in out:
                cur = None
            else:
                out[name] = []
                cur = out[name]
            continue
        if cur is not None:
            cur.append((i, line))
    return out


def key_value(body):
    """(line index, value) of the first non-blank body line, stripped and lowercased, else (None, '')."""
    for i, line in body:
        if line.strip():
            return i, line.strip().lower()
    return None, ''


def heading_above(lines, i):
    for j in range(i - 1, -1, -1):
        if lines[j].startswith('## '):
            return lines[j].rstrip()
    return '(top)'


def collect(root, proposals):
    """{(kind, subject): [(path, line, where, quote, extra), ...]} from every source under root."""
    root = Path(root).resolve()
    repo = root.parent
    proposals = Path(proposals).resolve()
    found = {}

    def add(kind, subj, path, line, where, q, extra=''):
        found.setdefault((kind, subj), []).append((rel(path, repo), line, where, q, extra))

    for dirpath, dirnames, filenames in os.walk(str(root)):
        here = Path(dirpath)
        keep = []
        for name in sorted(dirnames):
            if here == root and name in SKIP_TOP:
                continue
            if (here / name).resolve() == proposals:
                continue
            keep.append(name)
        dirnames[:] = keep
        subj = subject_of(here, repo)
        seen_advice = set()
        for name in sorted(filenames):
            path = here / name
            if name == 'runs.jsonl':
                try:
                    text = read_source(path)
                except OSError:
                    continue
                levels = set()
                for n, line in enumerate(text.split('\n'), 1):
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(obj, dict):
                        continue
                    role, level = obj.get('role'), obj.get('level')
                    if not isinstance(role, str) or not isinstance(level, str):
                        continue
                    q = 'role=%s level=%s' % (role, level)
                    f = obj.get('file')
                    if isinstance(f, str) and f:
                        q += ' file=%s' % f
                    if role == 'planner':
                        add('replan', subj, path, n, 'run', quote(q))
                    if role == 'builder' and level not in levels:
                        levels.add(level)
                        add('builder-bump', subj, path, n, 'run', quote(q))
            elif here == root and name == 'notes.md':
                try:
                    text = read_source(path)
                except OSError:
                    continue
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    m = NOTE_RE.fullmatch(line)
                    if not m:
                        continue
                    tag = m.group(1).lower()
                    body = m.group(2)
                    add('follow-up', '%s %s' % (tag, clean(body).lower()), path, i + 1,
                        heading_above(lines, i), quote(line[2:]), (tag, body))
            elif ROLE_RE.fullmatch(name):
                try:
                    text = read_source(path)
                except OSError:
                    continue
                lines = text.split('\n')
                secs = sections(lines)
                verifier = name.startswith('verifier-')
                if verifier:
                    vi, verdict = key_value(secs.get('Verdict', []))
                    failing = verdict == 'fail'
                    if failing:
                        add('verifier-fail', subj, path, vi + 1, '## Verdict', quote(verdict))
                    advice = secs.get('For the next attempt')
                    if advice is not None:
                        joined = clean(' '.join(d for d in (drop(l) for _, l in advice) if d))
                        norm = joined.lower()
                        ai, _ = key_value(advice)
                        if norm and not re.match(r'none(\.(\s|$)|$)', norm) and norm not in seen_advice:
                            seen_advice.add(norm)
                            add('next-attempt', norm, path, ai + 1, '## For the next attempt', quote(joined))
                else:
                    _, status = key_value(secs.get('Status', []))
                    failing = status == 'blocked'
                if failing:
                    for i, line in enumerate(lines):
                        d = drop(line)
                        if d.startswith('plan defect:'):
                            add('plan-defect', '', path, i + 1, heading_above(lines, i), quote(d))
    return found


def pattern_of(kind, subj):
    return kind if kind == 'plan-defect' else '%s %s' % (kind, subj)


def title_of(kind, subj, first):
    if kind in ('verifier-fail', 'replan', 'builder-bump'):
        return TITLES[kind] % subj
    if kind == 'next-attempt':
        return TITLES[kind] % cut(first[3], 60)
    if kind == 'follow-up':
        tag, body = first[4]
        return TITLES[kind] % (tag, cut(clean(body), 60))
    return TITLES[kind]


# ---------------------------------------------------------------- proposal files

def parse(text):
    """(fields, body, None) for a valid proposal text, else (fields or None, body or None, reason)."""
    lines = text.split('\n')
    if lines[0] != '---':
        return None, None, 'no front matter'
    end = next((i for i in range(1, len(lines)) if lines[i] == '---'), None)
    if end is None:
        return None, None, 'no front matter'
    pairs = []
    for i in range(1, end):
        m = FIELD_LINE_RE.fullmatch(lines[i])
        if not m:
            return None, None, 'bad front matter line %d' % (i + 1)
        pairs.append((m.group(1), m.group(2) or ''))
    for name, _ in pairs:
        if name not in FIELDS:
            return None, None, 'unknown field %s' % name
    seen = set()
    for name, _ in pairs:
        if name in seen:
            return None, None, 'duplicate field %s' % name
        seen.add(name)
    fields = dict(pairs)
    body = '\n'.join(lines[end + 1:])
    for name in REQUIRED:
        if not fields.get(name):
            return fields, body, 'missing field %s' % name
    bad = None
    if not ID_RE.fullmatch(fields['id']):
        bad = 'id'
    elif fields['status'] not in STATUSES:
        bad = 'status'
    elif not fields['occurrences'].isdigit():
        bad = 'occurrences'
    else:
        try:
            datetime.date.fromisoformat(fields['created'])
        except ValueError:
            bad = 'created'
        if bad is None and fields['pattern'].split(' ')[0] not in KINDS:
            bad = 'pattern'
    if bad:
        return fields, body, 'bad field %s: %s' % (bad, fields[bad])
    heads = [l.rstrip() for l in lines[end + 1:]]
    for h in ('Evidence', 'Proposed change'):
        if '## ' + h not in heads:
            return fields, body, 'missing ## %s' % h
    return fields, body, None


def section_body(body, name):
    """The lines of `## <name>` up to the next `## ` line."""
    return sections(body.split('\n')).get(name, [])


def render_front(fields):
    out = ['---']
    for name in FIELDS:
        if name in ALWAYS or name in fields:
            v = fields.get(name) or ''
            out.append(name + ':' + (' ' + v if v else ''))
    out.append('---')
    return '\n'.join(out) + '\n'


def render_body(evidence, change):
    return '\n## Evidence\n\n%s\n\n## Proposed change\n\n%s\n' % ('\n'.join(evidence), change)


def evidence_line(occ):
    path, line, where, q, _ = occ
    return '- %s:%d (%s) "%s"' % (path, line, where, q)


class Proposal(object):
    def __init__(self, path, text):
        self.path = path
        self.folder = path.parent.name
        self.text = text
        self.fields, self.body, self.reason = parse(text)


def load_all(proposals):
    out = []
    d = Path(proposals)
    if not d.is_dir():
        return out
    for sub in sorted(d.iterdir()):
        f = sub / 'proposal.md'
        if sub.is_dir() and f.is_file():
            out.append(Proposal(f, f.read_text(encoding='utf-8')))
    return out


def write_proposal(proposals, path, text):
    """The one writer of proposal files; refuses a path outside the proposals dir."""
    base = Path(proposals).resolve()
    p = Path(path).resolve()
    if base not in p.parents:
        raise Refusal('refusing to write %s outside %s' % (p, base))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def find(proposals, pid, repo):
    hits = [p for p in load_all(proposals) if p.reason is None and p.fields['id'] == pid]
    if not hits:
        raise Refusal('no proposal %s' % pid)
    if len(hits) > 1:
        raise Refusal('id %s is used twice: %s' % (pid, ', '.join(rel(p.path, repo) for p in hits)))
    return hits[0]


def forward(prop, new):
    cur = prop.fields['status']
    if (cur, new) not in FORWARD:  # rule: forward
        raise Refusal('cannot move %s from %s to %s' % (prop.fields['id'], cur, new))


def stamp(proposals, prop, **updates):
    fields = dict(prop.fields)
    fields.update(updates)
    write_proposal(proposals, prop.path, render_front(fields) + prop.body)


# ---------------------------------------------------------------- commands

def cmd_scan(args, root, proposals, plugin):
    repo = repo_of(root)
    props = load_all(proposals)
    ids = {}
    for p in props:
        if p.reason:
            raise Refusal('%s: %s' % (rel(p.path, repo), p.reason))
        pid = p.fields['id']
        if pid in ids:
            raise Refusal('%s: id %s is used twice: %s, %s' % (rel(p.path, repo), pid, rel(ids[pid].path, repo),
                                                              rel(p.path, repo)))
        ids[pid] = p
    known = {}
    for p in sorted(props, key=lambda p: p.fields['id']):
        known.setdefault(p.fields['pattern'], p)
    top = max([int(pid[2:]) for pid in ids] + [0])
    found = collect(root, proposals)
    order = sorted(found, key=lambda k: (KINDS.index(k[0]), pattern_of(*k)))
    new = updated = unchanged = 0
    for kind, subj in order:
        evidence = sorted(found[(kind, subj)], key=lambda o: (o[0], o[1]))
        pattern = pattern_of(kind, subj)
        if len(evidence) < 2:  # rule: threshold
            continue
        lines = [evidence_line(o) for o in evidence]
        if pattern in known:  # rule: known
            p = known[pattern]
            change = '\n'.join(l for _, l in section_body(p.body, 'Proposed change')).strip()
            fields = dict(p.fields)
            fields['occurrences'] = str(len(lines))
            text = render_front(fields) + render_body(lines, change)
            if text != p.text:
                write_proposal(proposals, p.path, text)
                print('updated %s %s (%d occurrences)' % (fields['id'], p.folder, len(lines)))
                updated += 1
            else:
                unchanged += 1
            continue
        top += 1
        fields = {'id': 'P-%04d' % top, 'title': title_of(kind, subj, evidence[0]), 'status': 'candidate',
                  'pattern': pattern, 'occurrences': str(len(lines)), 'created': today(), 'eval': ''}
        base = '%s-%s' % (kind, hashlib.sha256(pattern.encode('utf-8')).hexdigest()[:8])
        folder, k = base, 2
        while (Path(proposals) / folder / 'proposal.md').exists():
            folder, k = '%s-%d' % (base, k), k + 1
        write_proposal(proposals, Path(proposals) / folder / 'proposal.md',
                       render_front(fields) + render_body(lines, CHANGES[kind]))
        print('new %s %s (%d occurrences)' % (fields['id'], folder, len(lines)))
        new += 1
    print('proposals scan: %d new, %d updated, %d unchanged' % (new, updated, unchanged))
    return 0


def cmd_list(args, root, proposals, plugin):
    props = load_all(proposals)
    for p in sorted(props, key=lambda p: ((p.fields or {}).get('id', ''), p.folder)):
        if p.reason:
            print('%s\tinvalid: %s' % (p.folder, p.reason))
        else:
            f = p.fields
            print('\t'.join([f['id'], f['status'], f['occurrences'], p.folder, f['title']]))
    return 0


def cmd_show(args, root, proposals, plugin):
    p = find(proposals, args.id, repo_of(root))
    sys.stdout.write(p.text)
    return 0


def load_evals(plugin):
    path = Path(plugin) / 'scripts' / 'evals.py'
    spec = importlib.util.spec_from_file_location('sdlc_proposals_evals', str(path))
    if spec is None or spec.loader is None:
        raise Refusal('cannot load %s' % path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_accept(args, root, proposals, plugin):
    repo = repo_of(root)
    p = find(proposals, args.id, repo)
    forward(p, 'accepted')
    evals_dir = (Path(root) / 'evals').resolve()
    shown = rel(evals_dir, repo)
    reason = None
    path = None
    if not args.eval:
        reason = 'no eval given: pass --eval <file in %s/>' % shown
    else:
        path = Path(args.eval)
        if not path.is_file():
            reason = 'no such eval: %s' % args.eval
        elif path.resolve().parent != evals_dir:
            reason = 'eval %s is not in %s/' % (args.eval, shown)
        else:
            why = load_evals(plugin).validate_eval(path, repo)
            if why:
                reason = 'invalid eval %s: %s' % (args.eval, why)
    if reason:  # rule: eval
        raise Refusal(reason)
    ev = rel(path, repo) if path is not None else ''
    stamp(proposals, p, status='accepted', eval=ev, accepted=today())
    print('accepted %s (eval %s)' % (p.fields['id'], ev))
    return 0


def cmd_reject(args, root, proposals, plugin):
    p = find(proposals, args.id, repo_of(root))
    forward(p, 'rejected')
    text = clean(args.reason or '')
    if not text:  # rule: reason
        raise Refusal('reject needs --reason TEXT')
    stamp(proposals, p, status='rejected', rejected=today(), reason=text)
    print('rejected %s' % p.fields['id'])
    return 0


def set_section(text, heading, body):
    """text with the body of `## <heading>` replaced, or the section appended when the text lacks it."""
    m = re.search(r'^## ' + re.escape(heading) + r'[ \t]*\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    if not m:
        return text.rstrip('\n') + '\n\n## %s\n\n%s\n' % (heading, body)
    gap = '\n\n' if m.end(1) < len(text) else '\n'
    return text[:m.start(1)] + body + gap + text[m.end(1):]


def cmd_promote(args, root, proposals, plugin):
    repo = repo_of(root)
    p = find(proposals, args.id, repo)
    forward(p, 'promoted')
    f = p.fields
    cmd = [sys.executable, str(Path(plugin) / 'scripts' / 'tickets.py'), '--root', str(args.root),
           'new', 'idea', p.folder, f['title']]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if proc.returncode != 0:
        raise Refusal('tickets.py new failed: %s' % proc.stderr.strip())
    out = [l for l in proc.stdout.split('\n') if l.strip()]
    if not out:
        raise Refusal('tickets.py new printed no handoff path')
    handoff = Path(out[-1].strip())
    if not handoff.is_absolute():
        handoff = Path.cwd() / handoff
    text = handoff.read_text(encoding='utf-8')
    m = re.search(r'^id: (T-\d+)', text, re.M)
    if not m:
        raise Refusal('%s: no id: line' % rel(handoff, repo))
    tid = m.group(1)
    change = '\n'.join(l for _, l in section_body(p.body, 'Proposed change')).strip()
    evidence = '\n'.join(l for _, l in section_body(p.body, 'Evidence') if l.strip())
    context = ('From proposal %s (`%s`): pattern `%s`, %s occurrences, accepted with eval `%s`.\n\nEvidence:\n\n%s'
               % (f['id'], rel(p.path, repo), f['pattern'], f['occurrences'], f.get('eval', ''), evidence))
    text = set_section(text, 'Goal', change)
    text = set_section(text, 'Context', context)
    handoff.write_text(text, encoding='utf-8')
    stamp(proposals, p, status='promoted', promoted=today(), ticket=tid)
    print('promoted %s as %s (%s)' % (f['id'], tid, rel(handoff, repo)))
    return 0


# ---------------------------------------------------------------- selftest

VALID_EVAL = ('---\nrole: builder\nlevel: L2\nmodel: opus\neffort: low\nhost: claude\ntask_set: s\n'
              'pass_rate: 1/1\ncost_usd: unknown\ndate: 2026-10-01\nevidence: https://example.com/e\n---\n'
              '## Method\n\nm\n\n## Result\n\nr\n')


def selftest(plugin):
    me = Path(__file__).resolve()
    plugin = Path(plugin).resolve()
    day = today()
    tracked = {}
    violations = []
    runs = [0]
    report = []

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def manifest(proj):
        """sha256 of every runs.jsonl, role result, and notes.md under proj."""
        out = {}
        for dirpath, dirnames, filenames in os.walk(str(proj)):
            dirnames.sort()
            for name in filenames:
                if name in ('runs.jsonl', 'notes.md') or ROLE_RE.fullmatch(name):
                    p = Path(dirpath) / name
                    out[str(p)] = sha(p)
        return out

    def changed(old, new):
        return sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))

    def track(proj):
        tracked[proj] = manifest(proj)

    def tree(proj, skip=None):
        out = {}
        for dirpath, dirnames, filenames in os.walk(str(proj)):
            if skip is not None:
                dirnames[:] = [d for d in dirnames if Path(dirpath, d) != skip]
            for name in filenames:
                p = Path(dirpath) / name
                out[str(p.relative_to(proj))] = sha(p)
        return out

    def call(cmd, cwd):
        proc = subprocess.run([str(c) for c in cmd], cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True)
        runs[0] += 1
        for proj, old in list(tracked.items()):
            new = manifest(proj)
            for k in changed(old, new):
                violations.append('%s changed by %s' % (k, ' '.join(str(c) for c in cmd[2:])))
            tracked[proj] = new
        return proc.returncode, proc.stdout, proc.stderr

    def ev(proj, args, script=None, props=None):
        cmd = [sys.executable, script or me, '--root', proj / '.sdlc', '--plugin', plugin]
        if props is not None:
            cmd += ['--proposals', props]
        return call(cmd + args, proj)

    def w(p, text):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')

    def folder(pattern):
        return '%s-%s' % (pattern.split(' ')[0], hashlib.sha256(pattern.encode('utf-8')).hexdigest()[:8])

    def seed(proj):
        s = proj / '.sdlc'
        fail = '## Verdict\nfail\n'
        w(s / 'a/step-1/verifier-L1.md', fail)
        w(s / 'a/step-1/verifier-L1-2.md', fail)
        w(s / 'b/step-1/verifier-L1.md', fail)
        w(s / 'a/runs.jsonl', '{"role":"planner","level":"L2","file":"planner-L2.md"}\n'
                              '{"role":"planner","level":"L3"}\n')
        w(s / 'b/runs.jsonl', '{"role":"planner","level":"L2"}\n')
        w(s / 'a/step-2/runs.jsonl', '{"role":"builder","level":"L2","file":"builder-L2.md"}\n'
                                     '{"role":"builder","level":"L2","file":"builder-L2-2.md"}\n'
                                     'not json\n\n{"role":"builder","level":"L3","file":"builder-L3.md"}\n')
        w(s / 'c/step-1/verifier-L1.md', '## Verdict\npass\n\n## For the next attempt\nRerun  the gate first.\n')
        w(s / 'c/step-2/verifier-L1.md', '## Verdict\npass\n\n## For the next attempt\n- rerun the GATE first.\n')
        w(s / 'd/step-1/builder-L2.md', '## Status\nblocked\n\n## Notes\nplan defect: the guard misses a path.\n')
        w(s / 'd/step-2/verifier-L1.md', '## Verdict\nfail\n\n## Criteria\n- plan defect: criterion 2 is stale.\n')
        w(s / 'd/step-3/verifier-L1.md', '## Verdict\npass\n\n## Criteria\nplan defect: not counted on a pass.\n')
        w(s / 'notes.md', '# Notes\n\n## T-0001: One (2026-10-01)\n\n- decide: Pick  a format\n\n'
                          '## T-0002: Two (2026-10-02)\n\n- decide: pick a FORMAT\n- fix-now: only once\n')
        w(s / 'evals/0000-ok.md', VALID_EVAL)
        track(proj)
        return proj

    def singles(proj):
        s = proj / '.sdlc'
        w(s / 'a/step-1/verifier-L1.md', '## Verdict\nfail\n')
        w(s / 'a/runs.jsonl', '{"role":"planner","level":"L2"}\n')
        w(s / 'a/step-2/runs.jsonl', '{"role":"builder","level":"L2"}\n{"role":"builder","level":"L2"}\n')
        w(s / 'c/step-1/verifier-L1.md', '## Verdict\npass\n\n## For the next attempt\nRerun the gate.\n')
        w(s / 'd/step-1/builder-L2.md', '## Status\nblocked\n\n## Notes\nplan defect: once.\n')
        w(s / 'notes.md', '# Notes\n\n## T-0001: One (2026-10-01)\n\n- decide: once\n')
        track(proj)
        return proj

    def mini(proj, untracked=False):
        s = proj / '.sdlc'
        w(s / 'a/step-1/verifier-L1.md', '## Verdict\nfail\n')
        w(s / 'a/step-1/verifier-L1-2.md', '## Verdict\nfail\n')
        w(s / 'a/runs.jsonl', '{"role":"planner","level":"L2"}\n{"role":"planner","level":"L3"}\n')
        w(s / 'evals/0000-ok.md', VALID_EVAL)
        if not untracked:
            track(proj)
        return proj

    def expected(pid, title, pattern, ev_lines, change):
        return ('---\nid: %s\ntitle: %s\nstatus: candidate\npattern: %s\noccurrences: %d\ncreated: %s\neval:\n---\n'
                '\n## Evidence\n\n%s\n\n## Proposed change\n\n%s\n'
                % (pid, title, pattern, len(ev_lines), day, '\n'.join(ev_lines), change))

    def patched(t, key, marker):
        """A copy of this file with the marked rule broken, or (None, why)."""
        src = me.read_text(encoding='utf-8')
        if key == 'read-only':
            pattern = re.compile(r'^([ \t]*)return (.+?)[ \t]*' + re.escape(marker) + r'[ \t]*$', re.M)
            text, n = pattern.subn(lambda m: "%st = %s; Path(path).write_text(t + 'x', encoding='utf-8'); return t"
                                   % (m.group(1), m.group(2)), src)
        else:
            pattern = re.compile(r'^([ \t]*)if .+:([ \t]*' + re.escape(marker) + r'[ \t]*)$', re.M)
            text, n = pattern.subn(r'\1if False:\2', src)
        if n != 1:
            return None, 'marker %r matched %d lines, want exactly 1' % (marker, n)
        d = t / ('neg-' + key)
        d.mkdir()
        (d / 'proposals.py').write_text(text, encoding='utf-8')
        return d / 'proposals.py', None

    def case(name, fn):
        misses = []

        def need(cond, detail):
            if not cond:
                misses.append(detail)
        try:
            fn(need)
        except Exception as e:  # a crashed case is a failed case, not a crashed selftest
            misses.append('exception: %r' % (e,))
        report.append((name, misses))

    def read(p):
        return p.read_text(encoding='utf-8') if p.is_file() else None

    with tempfile.TemporaryDirectory() as td:
        t = Path(td).resolve()
        p1 = seed(t / 'p1')
        props1 = p1 / '.sdlc' / 'proposals'
        pats = ['verifier-fail .sdlc/a/step-1', 'replan .sdlc/a', 'builder-bump .sdlc/a/step-2',
                'next-attempt rerun the gate first.', 'plan-defect', 'follow-up decide pick a format']
        titles = ['Repeated verifier fails in .sdlc/a/step-1', 'Repeated planner runs in .sdlc/a',
                  'Builder level bump in .sdlc/a/step-2', 'Repeated next-attempt advice: Rerun the gate first.',
                  'Repeated plan defect verdicts', 'Repeated decide follow-up: Pick a format']
        evs = [
            ['- .sdlc/a/step-1/verifier-L1-2.md:2 (## Verdict) "fail"',
             '- .sdlc/a/step-1/verifier-L1.md:2 (## Verdict) "fail"'],
            ['- .sdlc/a/runs.jsonl:1 (run) "role=planner level=L2 file=planner-L2.md"',
             '- .sdlc/a/runs.jsonl:2 (run) "role=planner level=L3"'],
            ['- .sdlc/a/step-2/runs.jsonl:1 (run) "role=builder level=L2 file=builder-L2.md"',
             '- .sdlc/a/step-2/runs.jsonl:5 (run) "role=builder level=L3 file=builder-L3.md"'],
            ['- .sdlc/c/step-1/verifier-L1.md:5 (## For the next attempt) "Rerun the gate first."',
             '- .sdlc/c/step-2/verifier-L1.md:5 (## For the next attempt) "rerun the GATE first."'],
            ['- .sdlc/d/step-1/builder-L2.md:5 (## Notes) "plan defect: the guard misses a path."',
             '- .sdlc/d/step-2/verifier-L1.md:5 (## Criteria) "plan defect: criterion 2 is stale."'],
            ['- .sdlc/notes.md:5 (## T-0001: One (2026-10-01)) "decide: Pick a format"',
             '- .sdlc/notes.md:9 (## T-0002: Two (2026-10-02)) "decide: pick a FORMAT"'],
        ]
        changes = [
            'Examine why this step failed verification more than once: its criteria, its level, or its handoff.',
            'Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.',
            'Examine why the lower builder level could not finish this step and whether the planner picked too '
            'low a level.',
            'Examine whether this repeated advice belongs in a role contract or a planner rule.',
            'Examine the planner rules behind these criteria and whether steps.py lint could refuse them.',
            'Examine whether this repeated follow-up needs one ticket or a rule instead of more notes.',
        ]
        files1 = [props1 / folder(p) / 'proposal.md' for p in pats]

        def c1(need):
            rc, out, err = ev(p1, ['scan'])
            need(rc == 0, 'scan: rc=%d %r' % (rc, err))
            want_out = ''.join('new P-%04d %s (2 occurrences)\n' % (i + 1, folder(p)) for i, p in enumerate(pats))
            want_out += 'proposals scan: 6 new, 0 updated, 0 unchanged\n'
            need(out == want_out, 'scan output %r' % out)
            got = sorted(str(f) for f in props1.glob('*/proposal.md')) if props1.is_dir() else []
            need(got == sorted(str(f) for f in files1), 'proposal files %r' % got)
            for i, f in enumerate(files1):
                want = expected('P-%04d' % (i + 1), titles[i], pats[i], evs[i], changes[i])
                have = read(f)
                need(have == want, '%s: want %r, got %r' % (f.parent.name, want, have))
        case('scan files one candidate per seeded pattern with its evidence lines', c1)

        p2 = singles(t / 'p2')

        def c2(need):
            rc, out, err = ev(p2, ['scan'])
            need(rc == 0 and out == 'proposals scan: 0 new, 0 updated, 0 unchanged\n', 'scan: rc=%d %r' % (rc, out))
            need(not (p2 / '.sdlc' / 'proposals').exists(), 'the proposals dir was created')
        case('a pattern seen once files no candidate', c2)

        def c3(need):
            before = tree(p1)
            rc, out, err = ev(p1, ['scan'])
            need(rc == 0 and out.endswith('0 new, 0 updated, 6 unchanged\n'), 'rescan: rc=%d %r' % (rc, out))
            need(tree(p1) == before, 'the tree changed: %r' % changed(before, tree(p1)))
        case('a second scan leaves the tree byte-identical', c3)

        def c4(need):
            old = read(files1[0]) or ''
            w(p1 / '.sdlc/a/step-1/verifier-L2.md', '## Verdict\nfail\n')
            track(p1)
            rc, out, err = ev(p1, ['scan'])
            need(rc == 0 and ('updated P-0001 %s (3 occurrences)\n' % folder(pats[0])) in out,
                 'rescan: rc=%d %r' % (rc, out))
            text = read(files1[0]) or ''
            lines = text.split('\n')
            need('occurrences: 3' in lines, 'no occurrences: 3 line')
            need(sum(1 for l in lines if l.startswith('- .sdlc/')) == 3, 'evidence lines: %r' % lines)
            need('- .sdlc/a/step-1/verifier-L2.md:2 (## Verdict) "fail"' in lines, 'no third evidence line')
            for k in ('id', 'title', 'created'):
                o = [l for l in old.split('\n') if l.startswith(k + ':')]
                need(o and o[0] in lines, '%s changed' % k)
            need(len(list(props1.glob('*/proposal.md'))) == 6, 'not six proposals')
        case('scan updates a known pattern instead of duplicating it', c4)

        p5 = t / 'p5'
        w(p5 / '.sdlc/0007-x/runs.jsonl', '{"role":"planner","level":"L2"}\n{"role":"planner","level":"L3"}\n')
        track(p5)

        def c5(need):
            rc, out, err = ev(p5, ['scan'])
            f = p5 / '.sdlc/proposals' / folder('replan .sdlc/0007-x') / 'proposal.md'
            need(rc == 0 and f.is_file(), 'scan: rc=%d %r %r' % (rc, out, err))
            (p5 / '.sdlc/0007-x').rename(p5 / '.sdlc/.0007-x')
            track(p5)
            rc, out, err = ev(p5, ['scan'])
            need(rc == 0 and out.startswith('updated P-0001 '), 'rescan: rc=%d %r' % (rc, out))
            lines = (read(f) or '').split('\n')
            need('pattern: replan .sdlc/0007-x' in lines, 'pattern changed: %r' % lines)
            ev_lines = [l for l in lines if l.startswith('- ')]
            need(len(ev_lines) == 2 and all(l.startswith('- .sdlc/.0007-x/') for l in ev_lines),
                 'evidence %r' % ev_lines)
            need(len(list((p5 / '.sdlc/proposals').glob('*/proposal.md'))) == 1, 'not one proposal')
        case('scan keeps the pattern of a ticket folder renamed on close', c5)

        p6 = seed(t / 'p6')

        def c6(need):
            skip = p6 / '.sdlc' / 'proposals'
            before = tree(p6, skip)
            for args in (['scan'], ['list'], ['show', 'P-0001'],
                         ['accept', 'P-0001', '--eval', str(p6 / '.sdlc/evals/0000-ok.md')],
                         ['reject', 'P-0002', '--reason', 'x']):
                rc, out, err = ev(p6, args)
                need(rc == 0, '%s: rc=%d %r' % (args[0], rc, err))
            after = tree(p6, skip)
            need(after == before, 'changed or added outside proposals: %r' % changed(before, after))
            need(len(list(skip.glob('*/proposal.md'))) == 6, 'not six proposals')
        case('scan writes only under the proposals dir', c6)

        p7 = seed(t / 'p7')

        def c7(need):
            out_dir = t / 'out7'
            before = tree(p7)
            rc, out, err = ev(p7, ['scan'], props=out_dir)
            need(rc == 0 and out.endswith('6 new, 0 updated, 0 unchanged\n'), 'scan: rc=%d %r' % (rc, out))
            need(len(list(out_dir.glob('*/proposal.md'))) == 6, 'not six proposals in --proposals')
            need(tree(p7) == before, 'wrote under the project: %r' % changed(before, tree(p7)))
            need(not (p7 / '.sdlc' / 'proposals').exists(), 'created <root>/proposals')
        case('scan with --proposals writes there and nothing under the root', c7)

        p8 = seed(t / 'p8')

        def c8(need):
            w(p8 / '.sdlc/proposals/zz-bad/proposal.md', 'no front matter here\n')
            before = tree(p8)
            rc, out, err = ev(p8, ['scan'])
            need(rc == 1, 'scan rc=%d' % rc)
            need('.sdlc/proposals/zz-bad/proposal.md' in err and 'no front matter' in err, 'stderr %r' % err)
            need(tree(p8) == before, 'the tree changed')
            rc, out, err = ev(p8, ['list'])
            need(rc == 0 and 'zz-bad\tinvalid: no front matter\n' in out, 'list: rc=%d %r' % (rc, out))
        case('scan refuses an invalid proposal and writes nothing', c8)

        def c9(need):
            rc, out, err = ev(p1, ['list'])
            want = ''.join('P-%04d\tcandidate\t%d\t%s\t%s\n' % (i + 1, 3 if i == 0 else 2, folder(p), titles[i])
                           for i, p in enumerate(pats))
            need(rc == 0 and out == want, 'list: rc=%d want %r got %r' % (rc, want, out))
            rc, out, err = ev(p1, ['show', 'P-0003'])
            need(rc == 0 and out == read(files1[2]), 'show: rc=%d %r' % (rc, out))
            rc, out, err = ev(p1, ['show', 'P-0099'])
            need(rc == 1 and 'no proposal' in err, 'show unknown: rc=%d %r' % (rc, err))
        case('list and show print the proposals', c9)

        ok_eval = p1 / '.sdlc/evals/0000-ok.md'

        def refused(need, proj, args, f, phrase):
            before = read(f)
            rc, out, err = ev(proj, args)
            need(rc == 1 and phrase in err, '%s: rc=%d %r' % (' '.join(args), rc, err))
            need(read(f) == before, '%s changed the proposal' % ' '.join(args))

        case('accept without an eval is refused',
             lambda need: refused(need, p1, ['accept', 'P-0001'], files1[0], 'no eval given'))
        case('accept with a missing eval file is refused',
             lambda need: refused(need, p1, ['accept', 'P-0001', '--eval', str(p1 / '.sdlc/evals/0009-none.md')],
                                  files1[0], 'no such eval'))

        def c12(need):
            w(p1 / 'x/0001-ok.md', VALID_EVAL)
            refused(need, p1, ['accept', 'P-0001', '--eval', str(p1 / 'x/0001-ok.md')], files1[0], 'is not in')
        case('accept with an eval outside the evals folder is refused', c12)

        def c13(need):
            w(p1 / '.sdlc/evals/0001-bad.md', '---\nrole: builder\n---\n')
            refused(need, p1, ['accept', 'P-0001', '--eval', str(p1 / '.sdlc/evals/0001-bad.md')], files1[0],
                    'invalid eval')
        case('accept with an invalid eval is refused', c13)

        def c14(need):
            before = read(files1[0]) or ''
            rc, out, err = ev(p1, ['accept', 'P-0001', '--eval', str(ok_eval)])
            need(rc == 0 and out == 'accepted P-0001 (eval .sdlc/evals/0000-ok.md)\n', 'accept: rc=%d %r %r'
                 % (rc, out, err))
            want = before.replace('status: candidate\n', 'status: accepted\n', 1).replace(
                '\neval:\n', '\neval: .sdlc/evals/0000-ok.md\naccepted: %s\n' % day, 1)
            need(read(files1[0]) == want, 'want %r, got %r' % (want, read(files1[0])))
        case('accept with a valid eval stamps status, eval, and date', c14)

        def c15(need):
            refused(need, p1, ['reject', 'P-0002'], files1[1], 'reject needs --reason')
            refused(need, p1, ['reject', 'P-0002', '--reason', '  '], files1[1], 'reject needs --reason')
        case('reject without a reason is refused', c15)

        def c16(need):
            before = read(files1[1]) or ''
            rc, out, err = ev(p1, ['reject', 'P-0002', '--reason', 'not  worth it'])
            need(rc == 0 and out == 'rejected P-0002\n', 'reject: rc=%d %r %r' % (rc, out, err))
            want = before.replace('status: candidate\n', 'status: rejected\n', 1).replace(
                '\neval:\n', '\neval:\nrejected: %s\nreason: not worth it\n' % day, 1)
            need(read(files1[1]) == want, 'want %r, got %r' % (want, read(files1[1])))
        case('reject with a reason stamps status, reason, and date', c16)

        def c17(need):
            refused(need, p1, ['promote', 'P-0003'], files1[2], 'cannot move')
            need(not (p1 / '.sdlc' / folder(pats[2])).exists(), 'a ticket folder was created')
            need(not (p1 / '.sdlc' / 'roadmap.md').exists(), 'roadmap.md was written')
        case('promote before accept is refused', c17)

        def c18(need):
            h = p1 / '.sdlc' / folder(pats[0]) / 'handoff.md'
            rc, out, err = ev(p1, ['promote', 'P-0001'])
            need(rc == 0 and out == 'promoted P-0001 as T-0001 (.sdlc/%s/handoff.md)\n' % folder(pats[0]),
                 'promote: rc=%d %r %r' % (rc, out, err))
            text = read(h) or ''
            lines = text.split('\n')
            need('id: T-0001' in lines, 'handoff id')
            need(any(l.startswith('type: idea') for l in lines), 'handoff type')
            need('title: "%s"' % titles[0] in lines, 'handoff title')
            goal = re.search(r'^## Goal\n(.*?)(?=^## |\Z)', text, re.S | re.M)
            need(goal and goal.group(1).strip() == changes[0], 'goal %r' % (goal and goal.group(1)))
            ctx = re.search(r'^## Context\n(.*?)(?=^## |\Z)', text, re.S | re.M)
            body = ctx.group(1) if ctx else ''
            for l in [l for l in (read(files1[0]) or '').split('\n') if l.startswith('- .sdlc/')]:
                need(l in body.split('\n'), 'context lacks %r' % l)
            need('From proposal P-0001 (`.sdlc/proposals/%s/proposal.md`)' % folder(pats[0]) in body,
                 'context %r' % body)
            plines = (read(files1[0]) or '').split('\n')
            for l in ('status: promoted', 'promoted: %s' % day, 'ticket: T-0001'):
                need(l in plines, 'proposal lacks %r' % l)
            rc, out, err = call([sys.executable, plugin / 'scripts' / 'tickets.py', '--root', p1 / '.sdlc', 'check'],
                                p1)
            need(rc == 0, 'tickets.py check: rc=%d %r %r' % (rc, out, err))
        case('promote after accept files an idea ticket and records its id', c18)

        def c19(need):
            rc, out, err = ev(p1, ['accept', 'P-0004', '--eval', str(ok_eval)])
            need(rc == 0, 'setup accept P-0004: rc=%d %r' % (rc, err))
            for args, f in ((['accept', 'P-0001', '--eval', str(ok_eval)], files1[0]),
                            (['accept', 'P-0002', '--eval', str(ok_eval)], files1[1]),
                            (['reject', 'P-0004', '--reason', 'r'], files1[3]),
                            (['reject', 'P-0001', '--reason', 'r'], files1[0]),
                            (['promote', 'P-0002'], files1[1])):
                refused(need, p1, args, f, 'cannot move')
        case('a backward move is refused', c19)

        def control(key, marker, proj, args, check, real_first=None):
            """Show the real script refuses or keeps the fixture, then that the mutant does not."""
            def fn(need):
                if real_first:
                    real_first(need)
                copy, why = patched(t, key, marker)
                need(copy is not None, str(why))
                if copy:
                    rc, out, err = ev(proj, args, script=copy)
                    check(need, rc, out, err)
            return fn

        def status_of(f):
            return [l for l in (read(f) or '').split('\n') if l.startswith('status:')]

        m21 = mini(t / 'm21')
        f21 = m21 / '.sdlc/proposals' / folder('verifier-fail .sdlc/a/step-1') / 'proposal.md'

        def r21(need):
            ev(m21, ['scan'])
            refused(need, m21, ['accept', 'P-0001'], f21, 'no eval given')

        case('negative control: without the eval rule accept passes with no eval', control(
            'eval', '# rule' + ': eval', m21, ['accept', 'P-0001'],
            lambda need, rc, out, err: need(rc == 0 and status_of(f21) == ['status: accepted'],
                                            'mutant accept: rc=%d %r %r' % (rc, err, status_of(f21))), r21))

        m22 = mini(t / 'm22')
        f22 = m22 / '.sdlc/proposals' / folder('verifier-fail .sdlc/a/step-1') / 'proposal.md'

        def r22(need):
            ev(m22, ['scan'])
            refused(need, m22, ['reject', 'P-0001'], f22, 'reject needs --reason')

        case('negative control: without the reason rule reject passes with no reason', control(
            'reason', '# rule' + ': reason', m22, ['reject', 'P-0001'],
            lambda need, rc, out, err: need(rc == 0 and status_of(f22) == ['status: rejected'],
                                            'mutant reject: rc=%d %r %r' % (rc, err, status_of(f22))), r22))

        m23 = mini(t / 'm23')
        f23 = m23 / '.sdlc/proposals' / folder('verifier-fail .sdlc/a/step-1') / 'proposal.md'

        def r23(need):
            ev(m23, ['scan'])
            refused(need, m23, ['promote', 'P-0001'], f23, 'cannot move')

        case('negative control: without the forward rule promote passes on a candidate', control(
            'forward', '# rule' + ': forward', m23, ['promote', 'P-0001'],
            lambda need, rc, out, err: need(rc == 0 and status_of(f23) == ['status: promoted'],
                                            'mutant promote: rc=%d %r %r' % (rc, err, status_of(f23))), r23))

        m24 = mini(t / 'm24')
        f24 = m24 / '.sdlc/proposals' / folder('verifier-fail .sdlc/a/step-1') / 'proposal.md'
        e24 = str(m24 / '.sdlc/evals/0000-ok.md')

        def r24(need):
            ev(m24, ['scan'])
            ev(m24, ['accept', 'P-0001', '--eval', e24])
            rc, out, err = ev(m24, ['promote', 'P-0001'])
            need(rc == 0 and status_of(f24) == ['status: promoted'], 'setup promote: rc=%d %r' % (rc, err))
            refused(need, m24, ['accept', 'P-0001', '--eval', e24], f24, 'cannot move')

        case('negative control: without the forward rule accept passes on a promoted proposal', control(
            'forward2', '# rule' + ': forward', m24, ['accept', 'P-0001', '--eval', e24],
            lambda need, rc, out, err: need(rc == 0 and status_of(f24) == ['status: accepted'],
                                            'mutant accept: rc=%d %r %r' % (rc, err, status_of(f24))), r24))

        def r25(need):
            rc, out, err = ev(p2, ['scan'])
            need(rc == 0 and out.startswith('proposals scan: 0 new'), 'real scan: rc=%d %r' % (rc, out))
            need(not (p2 / '.sdlc' / 'proposals').exists(), 'real scan created the proposals dir')

        case('negative control: without the threshold a pattern seen once files a candidate', control(
            'threshold', '# rule' + ': threshold', p2, ['scan'],
            lambda need, rc, out, err: need(rc == 0 and out.startswith('new P-0001 ')
                                            and len(list((p2 / '.sdlc/proposals').glob('*/proposal.md'))) >= 1,
                                            'mutant scan: rc=%d %r' % (rc, out)), r25))

        m26 = mini(t / 'm26')
        props26 = m26 / '.sdlc/proposals'

        def pattern_count(line):
            return sum(1 for f in props26.glob('*/proposal.md') if line in (read(f) or '').split('\n'))

        def r26(need):
            ev(m26, ['scan'])
            rc, out, err = ev(m26, ['scan'])
            need(rc == 0 and out.endswith('0 new, 0 updated, 2 unchanged\n'), 'real rescan: rc=%d %r' % (rc, out))
            need(pattern_count('pattern: verifier-fail .sdlc/a/step-1') == 1, 'real rescan duplicated')

        case('negative control: without the known-pattern match a second scan duplicates', control(
            'known', '# rule' + ': known', m26, ['scan'],
            lambda need, rc, out, err: need(rc == 0 and pattern_count('pattern: verifier-fail .sdlc/a/step-1') == 2,
                                            'mutant scan: rc=%d %r' % (rc, out)), r26))

        m27 = mini(t / 'm27', untracked=True)
        base27 = {}

        def r27(need):
            base27.update(manifest(m27))
            rc, out, err = ev(m27, ['scan'])
            need(rc == 0 and not changed(base27, manifest(m27)), 'real scan changed a source')

        case('negative control: a proposals.py that writes a source file fails the source check', control(
            'read-only', '# rule' + ': read-only', m27, ['scan'],
            lambda need, rc, out, err: need(len(changed(base27, manifest(m27))) >= 1,
                                            'the source check saw no change after the mutant scan: rc=%d %r'
                                            % (rc, err)), r27))

        def c20(need):
            need(runs[0] > 0, 'no command ran')
            for v in violations:
                need(False, v)
        case('no command changes a source file', c20)
        report.insert(19, report.pop())  # case 20 runs last so it sees every command, but reports in place

    failed = False
    for name, misses in report:
        if misses:
            failed = True
            for m in misses:
                print('FAIL: %s: %s' % (name, m))
        else:
            print('ok: %s' % name)
    print('proposals selftest: %s' % ('FAIL' if failed else 'PASS'))
    return 1 if failed else 0


# ---------------------------------------------------------------- main

def main(argv):
    ap = argparse.ArgumentParser(prog='proposals.py', description=__doc__.split('\n')[0])
    ap.add_argument('--root', default='.sdlc', help='the .sdlc folder (default: .sdlc)')
    ap.add_argument('--proposals', help='where proposals live (default: <root>/proposals)')
    ap.add_argument('--plugin', default=str(Path(__file__).resolve().parent.parent),
                    help='dir holding scripts/evals.py and scripts/tickets.py')
    sub = ap.add_subparsers(dest='cmd')
    sub.required = True
    sub.add_parser('scan', help='file new candidates and refresh known ones')
    sub.add_parser('list', help='one line per proposal')
    p = sub.add_parser('show', help='print one proposal')
    p.add_argument('id')
    p = sub.add_parser('accept', help='candidate to accepted, with an eval')
    p.add_argument('id')
    p.add_argument('--eval', help='a valid eval file directly in <root>/evals/')
    p = sub.add_parser('reject', help='candidate to rejected, with a reason')
    p.add_argument('id')
    p.add_argument('--reason', help='why the proposal is rejected')
    p = sub.add_parser('promote', help='accepted to promoted: file an idea ticket')
    p.add_argument('id')
    sub.add_parser('selftest', help='run the regression cases in temp dirs')
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest(args.plugin)
    root = Path(args.root)
    proposals = Path(args.proposals) if args.proposals else root / 'proposals'
    handler = {'scan': cmd_scan, 'list': cmd_list, 'show': cmd_show, 'accept': cmd_accept,
               'reject': cmd_reject, 'promote': cmd_promote}[args.cmd]
    try:
        return handler(args, root, proposals, Path(args.plugin))
    except Refusal as e:
        print('proposals.py: %s' % e, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
