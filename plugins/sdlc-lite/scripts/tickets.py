#!/usr/bin/env python3
"""Tickets are .sdlc/<slug>/handoff.md files that open with front matter (see skills/handoff-format).
This script is the only writer of .sdlc/roadmap.md.

Usage: tickets.py [--root DIR] {new <type> <slug> ["title"] [--numbered] | close <slug> [--force] [--reason TEXT] [--ack-warnings TEXT] [--dry-run] [--skip N[,N...]] [--expect DIGEST] [--numbered] | roadmap [--numbered] | check [--numbered] | archive [--dry-run] [--numbered] | selftest}
  --root    dir holding ticket dirs (default: .sdlc in the cwd, like board.py)
  new       copy <root>/_templates/<type>.md (else <plugin>/skills/ticket/templates/<type>.md),
            stamp the next id, today's date and the title, then regenerate the roadmap.
            Numbered mode (--numbered, or a `ticket_folders: numbered` line in <root>/config) names
            the folder NNNN-<slug> after the stamped id; the slug is given bare. On success,
            new --numbered persists the mode by adding that line to <root>/config if it is absent
  close     after /file: read the task's newest filer-L*.md, refuse while its Warnings are open
            (unless --force), file each Follow-ups bullet as a proposed idea ticket with
            from: <id>, set the ticket done, then regenerate the roadmap. Numbered mode (as for new)
            names each follow-up folder NNNN-<slug> after that follow-up's own new id. On success,
            close --numbered persists the mode in <root>/config, as new --numbered does.
            In numbered mode, closing a NNNN-<slug> folder renames it to .NNNN-<slug> (after the
            handoff and follow-ups are written, before the roadmap) so ls and Finder hide it; the
            output adds `; moved to .<slug>` and each follow-up's context names the new folder.
            A plain slug folder never moves. close refuses, writing nothing, when .<slug> already
            exists, and names the dot folder (`already closed`) when only .<slug> holds the ticket.
            close --dry-run adds a `rename <slug> -> .<slug>` line.
            With no filer-L*.md here, close refuses and, when another git worktree's same-relative
            <slug>/ holds one (glob only, never read), names each such folder: commit or copy it into
            this tree, then rerun close.
            A follow-up whose normalized title (lowercase, words only) or slug base (no -N suffix, no
            NNNN- prefix) equals any other ticket's, any status, is a duplicate: close skips it and
            names it in the output. Follow-ups in the same filer are not checked against each other.
            close --dry-run applies the same refusals, then lists each Follow-ups bullet as
            `<i>. <title> [<slug>]` with any `duplicate of T-NNNN (<slug>)` or `skip (--skip)` mark,
            then one `open T-NNNN <title> [<slug>]` line per other proposed, ready or blocked
            ticket in id order, and writes nothing. close --skip N[,N...] files every follow-up except the named 1-based
            indices from that listing; an index out of range refuses and writes nothing. Skipped
            follow-ups get no id. The dry run's last line is `expect <digest>`, a digest of the full
            ordered Follow-ups bullets; --skip needs --expect <digest> from that line and refuses
            without it. close --expect DIGEST refuses, writing nothing, when the current Follow-ups
            no longer match (the list changed since the dry run, so the indices may point at other
            items). Plain close without --skip needs no token. --dry-run, --skip and --expect
            refuse together with --reason
  archive   numbered mode only: rename every existing done or dropped NNNN-<slug> folder to
            .NNNN-<slug>, then regenerate the roadmap. Refuses, writing nothing, outside numbered
            mode, on a bad ticket, or when any target .NNNN-<slug> exists. --dry-run prints one
            `<name> -> .<name>` line per folder and writes nothing. --numbered persists the mode
            close --reason TEXT is for a ticket whose work other tickets did: it skips the filer
            (no filer needed, warnings and follow-ups ignored), sets the ticket done, appends a
            ## Closed section with today's date and TEXT, and files no follow-ups
            close --ack-warnings TEXT closes while the filer's Warnings are open, for warnings that no
            longer apply: follow-ups, duplicates, --dry-run, --skip/--expect and the numbered rename work
            as for a plain close, and the handoff gains a ## Closed section with today's date,
            `warnings acknowledged: TEXT`, and the Warnings text quoted line by line (`> `). It refuses,
            writing nothing, with --force, with --reason, with empty TEXT, or when Warnings is None
  roadmap   regenerate <root>/roadmap.md in dependency order (refuses on any ticket problem, including,
            in numbered mode (as for new), the NNNN-<slug> prefix/id rule)
  check     validate every ticket; fail if roadmap.md is missing or stale. Numbered mode (as for new)
            also fails a NNNN-<slug> folder whose id is not T-NNNN. Outside numbered mode, when every
            ticket folder has an NNNN- prefix, prints a warning (exit stays 0) that the config line is missing
  selftest  build fixtures in a temp dir and prove every check failure fires

Ids across git worktrees: new and close stamp each id above the max across the same-relative ticket root
(<worktree>/<root relative to its toplevel>) in every `git worktree list` tree, so parallel worktrees never
reuse an id. Outside git, or when git fails, the local root decides alone. A worktree with no such dir yet
is skipped, and malformed tickets in another tree are ignored there. Branches not checked out in any
worktree are not seen; check catches a clash after merge (duplicate id, naming both folders).

A handoff with no front matter is not a ticket and is skipped. Dirs starting with _ or . are skipped,
except a closed-ticket folder .NNNN-<slug>: it is a ticket in every mode and command (ids, depends, from,
roadmap), and check fails it unless its status is done or dropped (rename it without the dot to reopen).
Build progress is not tracked here: /board derives it from each task's step artifacts.
"""
import argparse
import datetime
import hashlib
import heapq
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import order as run_order

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
REQUIRED = ('id', 'title', 'type', 'status', 'size', 'priority', 'depends', 'created')
ENUMS = {
    'type': ('feature', 'bug', 'chore', 'spike', 'idea'),
    'status': ('proposed', 'ready', 'blocked', 'done', 'dropped'),
    'size': ('S', 'M', 'L', 'XL'),
    'priority': ('P1', 'P2', 'P3'),
}
GLYPH = {'proposed': '⏳', 'ready': '🔵', 'blocked': '🔴', 'done': '🟢', 'dropped': '⚪'}
ID_RE = re.compile(r'T-\d{4}')
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
SLUG_RE = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')
PREFIX_RE = re.compile(r'\d{4}-')
DOT_RE = re.compile(r'\.\d{4}-[a-z0-9]+(-[a-z0-9]+)*')  # a closed-ticket folder: .NNNN-<slug>, fullmatch
CONFIG_RE = re.compile(r'\s*ticket_folders\s*:\s*numbered\s*(?:#.*)?')

HEADER = """# Roadmap

GENERATED by `tickets.py roadmap` from ticket front matter. Do not edit by hand: change the ticket's `handoff.md` front matter and regenerate.
New ticket: `/ticket new <feature|bug|chore|spike|idea> <slug> "title"`. Build progress per ticket: `/board`.
"""


class Fail(Exception):
    """A refusal: the message goes to stderr and the command exits 1. Never a traceback."""


# ---------- parsing ----------

def parse_value(v):
    v = v.strip()
    if v.startswith('"'):
        m = re.match(r'"([^"]*)"\s*(?:#.*)?$', v) or re.match(r'"(.*)"$', v)
        return m.group(1) if m else v
    v = re.sub(r'(^|\s+)#.*$', '', v).strip()
    if v.startswith('[') and v.endswith(']'):
        return [x.strip().strip('"') for x in v[1:-1].split(',') if x.strip()]
    return v


def parse(text):
    """Front matter dict, or None when the text has no front matter block."""
    text = text.replace('\r\n', '\n')
    m = re.match(r'---\n(.*?)^---[ \t]*$', text, re.S | re.M)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith('#') or ':' not in line:
            continue
        k, v = line.split(':', 1)
        meta[k.strip()] = parse_value(v)
    return meta


def load(root):
    """[(slug, meta)] for every <root>/<dir>/handoff.md with front matter, sorted by slug.
    Dirs starting with _ or . are skipped, except a closed-ticket folder .NNNN-<slug> (DOT_RE)."""
    if not root.is_dir():
        return []
    out = []
    for d in sorted(p for p in root.iterdir()
                    if p.is_dir() and (not p.name.startswith(('_', '.')) or DOT_RE.fullmatch(p.name))):
        h = d / 'handoff.md'
        if h.is_file():
            meta = parse(h.read_text(encoding='utf-8'))
            if meta is not None:
                out.append((d.name, meta))
    return out


def config_numbered(root):
    """True when <root>/config has a `ticket_folders: numbered` line. A missing file or any other
    content means plain slug folders; blank and # comment lines are ignored."""
    path = root / 'config'
    if not path.is_file():
        return False
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if CONFIG_RE.fullmatch(line):
            return True
    return False


def ensure_numbered_config(root):
    """Persist numbered mode: append `ticket_folders: numbered` to <root>/config (created if missing)
    unless config_numbered(root) already holds. Adds a newline first if the file lacks a trailing one."""
    if config_numbered(root):
        return
    path = root / 'config'
    old = path.read_text(encoding='utf-8') if path.is_file() else ''
    if old and not old.endswith('\n'):
        old += '\n'
    path.write_text(old + 'ticket_folders: numbered\n', encoding='utf-8')


GIT_ENV_DROP = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE')


def worktree_roots(root):
    """The same-relative ticket root in every other git worktree of root's repo: <worktree>/<rel>, where rel is
    root relative to its worktree's toplevel. Only existing dirs; the current root is left out. [] when git is
    missing, a git call fails, or root is outside the toplevel (not in git: the local root decides alone).
    GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE are dropped so an outer git context cannot redirect the lookup."""
    try:
        here = root.resolve()
        anchor = here
        while not anchor.is_dir() and anchor != anchor.parent:
            anchor = anchor.parent
        env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}

        def git(*args):
            p = subprocess.run(['git', '-C', str(anchor), *args], env=env, capture_output=True, text=True)
            if p.returncode:
                raise ValueError(p.stderr.strip())
            return p.stdout

        top = pathlib.Path(git('rev-parse', '--show-toplevel').strip())
        rel = here.relative_to(top.resolve())
        out = []
        for line in git('worktree', 'list', '--porcelain').splitlines():
            if not line.startswith('worktree '):
                continue
            other = (pathlib.Path(line[len('worktree '):]) / rel).resolve()
            if other != here and other.is_dir():
                out.append(other)
        return out
    except (OSError, ValueError):
        return []


def id_floor(root):
    """The highest ticket number in every other worktree's same-relative root (worktree_roots), else 0.
    Malformed tickets and unreadable files there are ignored: another tree's problems never fail this one."""
    floor = 0
    for r in worktree_roots(root):
        try:
            ts = load(r)
        except (OSError, UnicodeDecodeError):
            continue
        for _, m in ts:
            i = m.get('id')
            if isinstance(i, str) and ID_RE.fullmatch(i):
                floor = max(floor, int(i[2:]))
    return floor


def folder_name(slug, tid, numbered):
    """The ticket's directory name: NNNN-<slug> from id T-NNNN in numbered mode, else the bare slug."""
    return f'{tid[2:]}-{slug}' if numbered else slug


def deps_of(m):
    d = m.get('depends', [])
    return d if isinstance(d, list) else []


# ---------- validation ----------

def order(ts):
    """Kahn's algorithm, ties by id ascending. Returns (ordered [(slug, meta)], {stuck id: its deps}, by_id).
    Stuck ids sit on or behind a dependency cycle.
    Only tickets with a string id are placed; dangling depends are ignored here (problems() reports them)."""
    by_id = {}
    for slug, m in ts:
        i = m.get('id')
        if isinstance(i, str) and i not in by_id:
            by_id[i] = (slug, m)
    need = {i: {d for d in deps_of(m) if d in by_id} for i, (_, m) in by_id.items()}
    users = {i: set() for i in by_id}
    for i, ds in need.items():
        for d in ds:
            users[d].add(i)
    left = {i: len(ds) for i, ds in need.items()}
    ready = [i for i, n in left.items() if n == 0]
    heapq.heapify(ready)
    out = []
    while ready:
        i = heapq.heappop(ready)
        out.append(by_id[i])
        for u in users[i]:
            left[u] -= 1
            if left[u] == 0:
                heapq.heappush(ready, u)
    placed = {m['id'] for _, m in out}
    return out, {i: need[i] for i in by_id if i not in placed}, by_id


def cycles(ts):
    """Each dependency cycle once, as a list of ids ending where it started."""
    _, stuck, _ = order(ts)
    seen, found = set(), []
    for start in sorted(stuck):
        if start in seen:
            continue
        path, pos, i = [], {}, start
        # every stuck id has a dep that is also stuck, so this walk always ends in a cycle
        while i not in pos and i not in seen:
            pos[i] = len(path)
            path.append(i)
            i = min(d for d in stuck[i] if d in stuck)
        seen.update(path)
        if i in pos:
            found.append(path[pos[i]:] + [i])
    return found


def problems(ts, numbered=False):
    """One line per problem, each naming the ticket slug.
    numbered also fails a NNNN-<slug> (or .NNNN-<slug>) folder whose id is not T-NNNN; plain slugs are never
    prefix-checked. In any mode, a .NNNN-<slug> folder fails unless its status is done or dropped."""
    errs, ids = [], {}
    for slug, m in ts:
        if DOT_RE.fullmatch(slug) and m.get('status') not in ('done', 'dropped'):
            errs.append(f'{slug}: closed ticket folder (dot prefix) has status {m.get("status")!r}; want done or '
                        f'dropped (rename it to {slug[1:]} to reopen)')
        name = slug.lstrip('.')
        if numbered and PREFIX_RE.match(name) and isinstance(m.get('id'), str):
            nnnn = name[:4]
            if m['id'] != f'T-{nnnn}':
                errs.append(f'{slug}: folder prefix {nnnn}- does not match id {m["id"]!r} (want T-{nnnn})')
        for k in REQUIRED:
            if k not in m:
                errs.append(f'{slug}: missing {k}')
        for k, allowed in ENUMS.items():
            if k in m and m[k] not in allowed:
                errs.append(f'{slug}: {k}={m[k]!r} not in {"|".join(allowed)}')
        if 'id' in m:
            i = m['id']
            if not isinstance(i, str) or not ID_RE.fullmatch(i) or i == 'T-0000':
                errs.append(f'{slug}: id {i!r} is not T-NNNN (T-0000 is the template placeholder)')
            elif i in ids:
                errs.append(f'{slug}: duplicate id {i}, also used by {ids[i]}')
            else:
                ids[i] = slug
        if 'created' in m and not (isinstance(m['created'], str) and DATE_RE.fullmatch(m['created'])):
            errs.append(f'{slug}: created {m["created"]!r} is not YYYY-MM-DD')
        if 'depends' in m and not isinstance(m['depends'], list):
            errs.append(f'{slug}: depends {m["depends"]!r} is not a list like [T-0002]')
        if 'from' in m and not isinstance(m['from'], str):
            errs.append(f'{slug}: from {m["from"]!r} is not a single ticket id')
    for slug, m in ts:
        for dep in deps_of(m):
            if dep not in ids:
                errs.append(f'{slug}: depends on {dep}, which no ticket has')
        f = m.get('from')
        if isinstance(f, str) and f not in ids:
            errs.append(f'{slug}: from {f}, which no ticket has')
    for cyc in cycles(ts):
        errs.append(f'{ids.get(cyc[0], cyc[0])}: dependency cycle {" -> ".join(cyc)}')
    return errs


# ---------- roadmap ----------

def render(ts):
    rows = ['| ID | Ticket | Title | Type | Size | Pri | Depends on | Status |',
            '|---|---|---|---|---|---|---|---|']
    ordered, _, _ = order(ts)
    for slug, m in ordered:
        deps = ', '.join(m['depends']) or 'none'
        title = m['title'].replace('|', '\\|')
        rows.append(f"| {m['id']} | [{slug}]({slug}/handoff.md) | {title} | {m['type']} | {m['size']} | "
                    f"{m['priority']} | {deps} | {GLYPH[m['status']]} {m['status']} |")
    return HEADER + '\n' + '\n'.join(rows) + '\n'


def write_roadmap(root, ts):
    path = root / 'roadmap.md'
    path.write_bytes(render(ts).encode('utf-8'))
    return path


def stale(root, ts):
    path = root / 'roadmap.md'
    if not path.exists():
        return bool(ts)
    return path.read_bytes() != render(ts).encode('utf-8')


# ---------- commands ----------

def template_types(root):
    dirs = [root / '_templates', PLUGIN / 'skills' / 'ticket' / 'templates']
    return sorted({p.stem for d in dirs if d.is_dir() for p in d.glob('*.md')})


def template(root, kind):
    for d in (root / '_templates', PLUGIN / 'skills' / 'ticket' / 'templates'):
        p = d / f'{kind}.md'
        if p.is_file():
            return p
    raise Fail(f'no template for type {kind!r}; available types: {", ".join(template_types(root))}')


def stamp(root, ts, kind, slug, title='', origin=None, context=None, numbered=False, floor=0):
    """Text and meta of a new ticket, validated against ts (which must already be clean). Writes nothing.
    The new id is one above the max of ts's ids and floor (id_floor: the max in every other git worktree).
    origin adds `from: <id>` right after the created: line; context replaces the body of ## Context.
    numbered checks for and validates under the folder name folder_name(slug, <new id>, True)."""
    if not SLUG_RE.fullmatch(slug):
        raise Fail(f'slug {slug!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
    tpl = template(root, kind)
    nums = [int(m['id'][2:]) for _, m in ts]
    tid = f'T-{max(nums + [floor]) + 1:04d}'
    name = folder_name(slug, tid, numbered)
    d = root / name
    if d.exists() or any(s == name for s, _ in ts):
        raise Fail(f'{name}: {d} already exists; nothing written')
    text = tpl.read_text(encoding='utf-8')
    text = text.replace('id: T-0000', f'id: {tid}', 1)
    text = text.replace('created: YYYY-MM-DD', f'created: {datetime.date.today().isoformat()}', 1)
    if title:
        clean = ' '.join(title.replace('"', "'").split())
        text = text.replace('title: ""', f'title: "{clean}"', 1)
    if origin:
        text, n = re.subn(r'^(created:.*)$', lambda m: f'{m.group(1)}\nfrom: {origin}', text, count=1, flags=re.M)
        if not n:
            raise Fail(f'{tpl}: template has no created: line to put from: after; nothing written')
    if context is not None:
        m = re.search(r'^## Context[ \t]*\n(.*?)(?=^## |\Z)', text, re.S | re.M)
        if not m:
            raise Fail(f'{tpl}: template has no ## Context section; nothing written')
        gap = '\n\n' if m.end(1) < len(text) else '\n'
        text = text[:m.start(1)] + context.strip('\n') + gap + text[m.end(1):]
    meta = parse(text)
    if meta is None:
        raise Fail(f'{tpl}: template has no front matter; nothing written')
    if numbered and meta.get('id') != tid:
        raise Fail(f'{tpl}: template has no id: T-0000 line to stamp, so the folder cannot be numbered; '
                   f'nothing written')
    errs = problems(ts + [(name, meta)], numbered)
    if errs:
        raise Fail('\n'.join(errs + [f'{tpl}: template gives a bad ticket; nothing written']))
    return text, meta


def cmd_new(root, kind, slug, title='', origin=None, context=None, numbered=False):
    flag = numbered
    numbered = numbered or config_numbered(root)
    if not SLUG_RE.fullmatch(slug):
        raise Fail(f'slug {slug!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
    if numbered and PREFIX_RE.match(slug):
        raise Fail(f'slug {slug!r} already starts with NNNN-: numbered mode adds the prefix itself, so this '
                   f'would double it; pass the bare slug {slug[5:]!r}; nothing written')
    template(root, kind)
    if not numbered and (root / slug).exists():
        raise Fail(f'{slug}: {root / slug} already exists; nothing written')
    ts = load(root)
    errs = problems(ts, numbered)
    if errs:
        raise Fail('\n'.join(errs + ['refusing to add a ticket: fix the problems above first']))
    text, meta = stamp(root, ts, kind, slug, title, origin, context, numbered, floor=id_floor(root))
    d = root / folder_name(slug, meta['id'], numbered)
    d.mkdir(parents=True)
    path = d / 'handoff.md'
    path.write_text(text, encoding='utf-8')
    if flag:
        ensure_numbered_config(root)
    write_roadmap(root, load(root))
    return str(path)


def section(text, heading):
    """Body of `## <heading>` up to the next `## ` heading or EOF, stripped; None if the heading is absent."""
    text = text.replace('\r\n', '\n')
    m = re.search(rf'^## {re.escape(heading)}[ \t]*(?:\n|\Z)(.*?)(?=^## |\Z)', text, re.S | re.M)
    return m.group(1).strip() if m else None


BULLET_RE = re.compile(r'(?:[-*]|\d+[.)])[ \t]+(.*)')


def bullets(body):
    """Top-level list items (marker at column 0). Every later non-blank line joins the current item,
    so no text after the first bullet is dropped. Text before the first bullet is a lead-in."""
    items = []
    for line in body.splitlines():
        m = BULLET_RE.fullmatch(line.rstrip())
        if m:
            items.append([m.group(1).strip()])
        elif items and line.strip():
            items[-1].append(line.strip())
    return [' '.join(x for x in parts if x) for parts in items if any(parts)]


def is_none(text):
    # "None" or "None." optionally followed by an explanation ("None. All steps passed."), never "None of ..."
    return re.match(r'none(\.(\s|$)|$)', text.strip(), re.I) is not None


def follow_up_title(plain):
    """A <= 70 char title for a follow-up bullet's cleaned text, never cut mid-word."""
    if len(plain) <= 70:
        return plain
    m = re.search(r'[.!?] ', plain)
    if m and m.start() == 0:
        return follow_up_title(plain[m.end():])
    if m and m.start() <= 70:
        return plain[:m.start()]
    cut = plain.rfind(' ', 0, 68)
    if cut == -1:
        return plain[:67] + '...'
    return plain[:cut].rstrip(' ,;:.-') + '...'


def norm_title(s):
    """Lowercase words only, for the follow-up duplicate check: 'Fix #12' -> 'fix 12'."""
    return ' '.join(re.findall(r'[a-z0-9]+', s.lower()))


def strip_prefix(name):
    """name without its NNNN- prefix(es) and a closed folder's dot: '0002-beta' and '.0002-beta' -> 'beta'."""
    if DOT_RE.fullmatch(name):
        name = name[1:]
    while PREFIX_RE.match(name):
        name = name[5:]
    return name


def follow_digest(items):
    """The token that ties --skip indices to the exact Follow-ups list a dry run showed: a short sha256 of
    the full ordered bullet texts (items is bullets(follow), or [] for None), so reordering, adding,
    removing, or rewording any item changes it."""
    return hashlib.sha256('\n'.join(items).encode('utf-8')).hexdigest()[:12]


def parse_skip(text):
    """--skip N[,N...] as a list of ints; a token that is not an integer is a refusal, not a traceback."""
    out = []
    for tok in text.split(','):
        try:
            out.append(int(tok.strip()))
        except ValueError:
            raise Fail(f'--skip {text!r}: {tok.strip()!r} is not an integer; give 1-based indices like '
                       f'--skip 2,3; nothing written') from None
    return out


def cmd_close(root, slug, force=False, numbered=False, reason=None, dry_run=False, skip=None, expect=None,
              ack_warnings=None):
    """Read the newest filer-L*.md: refuse on open warnings, file follow-ups as proposed idea tickets
    with from: <id>, set the ticket done, regenerate the roadmap. Every refusal writes nothing.
    numbered (or <root>/config) names each follow-up folder NNNN-<slug> after its own new id.
    On success, --numbered persists `ticket_folders: numbered` in <root>/config, as new does.
    reason (not None) skips the filer: set done, append a ## Closed section, file no follow-ups.
    A follow-up matching any other ticket (ts, never the one being closed) by normalized title or slug base is skipped as a duplicate.
    skip: 1-based Follow-ups indices not to file. dry_run: same refusals, list the plan, write nothing.
    The dry run ends with `expect <digest>` (follow_digest). expect: that digest; required with skip (unless
    dry_run), and any mismatch with the current Follow-ups refuses, so stale indices are never applied.
    Numbered mode archives a NNNN-<slug> folder: after writing, rename it to .NNNN-<slug>, then the roadmap.
    With no filer here, the refusal names every other worktree's same-relative <slug>/ holding a filer-L*.md
    (glob only, never read), so work filed in a lane worktree can be committed or copied in.
    ack_warnings (not None): pass the open-warnings gate with a recorded reason instead of force; the write
    appends a ## Closed section with the date, `warnings acknowledged: <why>` and the Warnings quoted with `> `.
    It refuses with force, with reason, when empty, and when the filer's Warnings is None."""
    if ack_warnings is not None and force:
        raise Fail(f'{slug}: --ack-warnings records why open warnings no longer apply, so it does not combine '
                   f'with --force; use one; nothing written')
    if ack_warnings is not None and reason is not None:
        raise Fail(f'{slug}: --ack-warnings closes through the filer and --reason skips it, so they do not '
                   f'combine; use one; nothing written')
    if ack_warnings is not None and not ack_warnings.strip():
        raise Fail(f'{slug}: empty --ack-warnings; give the reason the open warnings no longer apply; '
                   f'nothing written')
    if reason is not None and (dry_run or skip is not None or expect is not None):
        raise Fail(f'{slug}: --reason files no follow-ups, so it does not combine with --dry-run, --skip '
                   f'or --expect; '
                   f'nothing written')
    flag = numbered
    numbered = numbered or config_numbered(root)
    if not SLUG_RE.fullmatch(slug):
        raise Fail(f'slug {slug!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
    d = root / slug
    h = d / 'handoff.md'
    dot = root / ('.' + slug)
    archive = bool(numbered and PREFIX_RE.match(slug))
    final = dot.name if archive else slug
    if not h.is_file() and (dot / 'handoff.md').is_file():
        raise Fail(f'{slug}: already closed (folder {dot.name}); nothing written')
    raw = h.read_bytes().decode('utf-8') if h.is_file() else None
    meta = parse(raw) if raw is not None else None
    if meta is None:
        raise Fail(f'{h}: missing or has no front matter, so it is not a ticket; nothing written')
    if archive and dot.exists():
        raise Fail(f'{slug}: close would rename it to {dot.name}, but {dot} already exists; nothing written')
    ts = load(root)
    errs = problems(ts, numbered)
    if errs:
        raise Fail('\n'.join(errs + ['refusing to close: fix the problems above first']))
    pid = meta['id']
    if meta['status'] == 'done':
        raise Fail(f'{slug}: {pid} is already closed (status: done); a second close would file duplicate '
                   f'follow-ups; nothing written')
    fm = re.match(r'---\r?\n.*?^---[ \t]*\r?$', raw, re.S | re.M)
    head, n = re.subn(r'^([ \t]*status[ \t]*:[ \t]*)[^\s#]+', r'\g<1>done', raw[:fm.end()], count=1, flags=re.M)
    if reason is not None:
        why = reason.strip()
        if not why:
            raise Fail(f'{slug}: empty --reason; give the reason the ticket is closed; nothing written')
        if not n:
            raise Fail(f'{h}: no status: line in front matter; nothing written')
        body = raw[fm.end():]
        if body and not body.endswith('\n'):
            body += '\n'
        body += f'\n## Closed\n\n{datetime.date.today().isoformat()}: {why}\n'
        h.write_bytes((head + body).encode('utf-8'))
        if archive:
            d.rename(dot)
        write_roadmap(root, load(root))
        if flag:
            ensure_numbered_config(root)
        moved = f'; moved to {dot.name}' if archive else ''
        return f'{pid} done (closed by reason: {why}); no follow-ups filed{moved}'
    filers = [pathlib.Path(p) for p in run_order.ordered(d, 'filer')]
    if not filers:
        held = []
        for r in worktree_roots(root):
            try:
                if any((r / d.name).glob('filer-L*.md')):
                    held.append(str(r / d.name))
            except OSError:
                pass
        hint = (f'; a filer record exists in {", ".join(held)}; commit or copy it into this tree, then rerun close'
                if held else '')
        raise Fail(f'{slug}: no filer-L*.md in {d}; run /file on the task first{hint}; nothing written')
    filer = filers[-1]
    text = filer.read_text(encoding='utf-8')
    warnings, follow = section(text, 'Warnings'), section(text, 'Follow-ups')
    if warnings is None or follow is None:
        raise Fail(f'{filer}: missing a ## Warnings or ## Follow-ups section; nothing written')
    if ack_warnings is not None and is_none(warnings):
        raise Fail(f'{slug}: no open warnings to acknowledge in {filer.name}; rerun without --ack-warnings; '
                   f'nothing written')
    if not is_none(warnings) and not force and ack_warnings is None:
        raise Fail(f'{slug}: filer warnings are open, not closing (rerun with --ack-warnings "<why>" to record '
                   f'why they no longer apply, or --force to override):\n{warnings}')
    items = [] if is_none(follow) else bullets(follow)
    if not is_none(follow) and not items:
        raise Fail(f'{filer}: Follow-ups is prose with no top-level bullet (-, *, 1.), so its items cannot be '
                   f'filed; rewrite it as a list or "None"; nothing written:\n{follow}')
    digest = follow_digest(items)
    if skip is not None and not dry_run and expect is None:
        raise Fail(f'{slug}: --skip needs --expect <digest> from the dry run that listed the indices '
                   f'(run close --dry-run first); nothing written')
    if expect is not None and expect.strip() != digest:
        raise Fail(f'{slug}: --expect {expect} does not match the current Follow-ups in {filer.name} '
                   f'(digest {digest}); the list changed since the dry run, so the --skip indices may point '
                   f'at other items; rerun close --dry-run; nothing written')
    skipped = sorted(set(skip or ()))
    for i in skipped:
        if not 1 <= i <= len(items):
            raise Fail(f'{slug}: --skip {i} is out of range: Follow-ups has {len(items)} item(s)'
                       + (f', so indices run 1 to {len(items)}' if items else '') + '; nothing written')

    # the other tickets to check each follow-up against (never the one being closed):
    # (normalized title, folder without NNNN-, id, folder)
    known = [(norm_title(m['title']) if isinstance(m.get('title'), str) else '', strip_prefix(x), m['id'], x)
             for x, m in ts if m.get('id') != pid and x != slug]
    # ids stay above every other worktree's max; follow-ups after the first count up from `after`
    floor = id_floor(root)
    # plan everything first, so a refusal in the middle writes nothing
    planned, after, lines, dups = [], list(ts), [], []
    for i, item in enumerate(items, 1):
        no_emphasis = re.sub(r'(?<!\w)_{1,2}(\S.*?\S|\S)_{1,2}(?!\w)', r'\1', item)
        plain = ' '.join(re.sub(r'[`*\[\]()]', '', no_emphasis).split())
        title = follow_up_title(plain)
        base = '-'.join(re.findall(r'[a-z0-9]+', plain.lower())[:5]) or 'follow-up'
        if numbered:
            base = strip_prefix(base) or 'follow-up'
        if i in skipped:
            lines.append(f'{i}. {title} [{base}] skip (--skip)')
            continue
        key, nt = strip_prefix(base), norm_title(title)
        dup = next(((kid, kname) for kt, kbase, kid, kname in known if (nt and kt == nt) or kbase == key), None)
        if dup:
            mark = f'duplicate of {dup[0]} ({dup[1]})'
            dups.append(f'{title} ({mark})')
            lines.append(f'{i}. {title} [{base}] {mark}')
            continue
        if numbered:
            tid = f'T-{max(max((int(x["id"][2:]) for _, x in after), default=0), floor) + 1:04d}'
        s, k = base, 2
        while ((root / (name := folder_name(s, tid, True) if numbered else s)).exists()
               or any(x == name for x, _ in after)):
            s, k = f'{base}-{k}', k + 1
        ctx = f'Follow-up from {pid} ({final}/{filer.name}):\n\n{item}'
        t, m = stamp(root, after, 'idea', s, title, origin=pid, context=ctx, numbered=numbered, floor=floor)
        planned.append((name, t))
        after.append((name, m))
        lines.append(f'{i}. {title} [{name}]')
    if not n:
        raise Fail(f'{h}: no status: line in front matter; nothing written')
    if dry_run:
        opens = [f'open {m["id"]} {m.get("title", "")} [{x}]'
                 for x, m in sorted(ts, key=lambda e: e[1]['id'])
                 if m.get('status') in ('proposed', 'ready', 'blocked') and m['id'] != pid]
        return '\n'.join([f'{pid} dry run: {len(items)} proposed follow-up(s); nothing written'] + lines + opens
                         + ([f'rename {slug} -> {dot.name}'] if archive else [])
                         + ([f'ack warnings: {ack_warnings.strip()}'] if ack_warnings is not None else [])
                         + [f'expect {digest}'])

    for s, t in planned:
        (root / s).mkdir()
        (root / s / 'handoff.md').write_text(t, encoding='utf-8')
    body = raw[fm.end():]
    if ack_warnings is not None:
        if body and not body.endswith('\n'):
            body += '\n'
        quoted = '\n'.join(f'> {ln}' if ln.strip() else '>' for ln in warnings.splitlines())
        body += (f'\n## Closed\n\n{datetime.date.today().isoformat()}: warnings acknowledged: '
                 f'{ack_warnings.strip()}\n\n{quoted}\n')
    h.write_bytes((head + body).encode('utf-8'))
    if archive:
        d.rename(dot)
    write_roadmap(root, load(root))
    if flag:
        ensure_numbered_config(root)
    out = f'{pid} done; {len(planned)} follow-up ticket(s): ' + (', '.join(s for s, _ in planned) or 'none')
    if dups:
        out += '; skipped duplicate(s): ' + ', '.join(dups)
    if skipped:
        out += '; skipped by --skip: ' + ', '.join(map(str, skipped))
    if archive:
        out += f'; moved to {dot.name}'
    if ack_warnings is not None:
        out += f'; warnings acknowledged: {ack_warnings.strip()}'
    return out


def cmd_roadmap(root, numbered=False):
    numbered = numbered or config_numbered(root)
    ts = load(root)
    errs = problems(ts, numbered)
    if errs:
        raise Fail('\n'.join(errs + ['roadmap not written: fix the problems above first']))
    root.mkdir(parents=True, exist_ok=True)
    return f'wrote {write_roadmap(root, ts)}'


def cmd_check(root, numbered=False):
    numbered = numbered or config_numbered(root)
    ts = load(root)
    errs = problems(ts, numbered)
    if errs:
        raise Fail('\n'.join(errs))
    if stale(root, ts):
        raise Fail(f'roadmap.md: stale or missing, run tickets.py --root {root} roadmap')
    ok = f'ok: {len(ts)} tickets, roadmap current'
    if not numbered and ts and all(PREFIX_RE.match(slug) or DOT_RE.fullmatch(slug) for slug, _ in ts):
        return (ok + f"\nwarning: every ticket folder has an NNNN- prefix but {root}/config lacks "
                f"'ticket_folders: numbered'; add that line (or run new/close --numbered once) to enforce it")
    return ok


def cmd_archive(root, numbered=False, dry_run=False):
    flag = numbered
    numbered = numbered or config_numbered(root)
    if not numbered:
        raise Fail(f'archive renames NNNN-<slug> folders and needs numbered mode (--numbered or '
                   f'ticket_folders: numbered in {root}/config); nothing written')
    ts = load(root)
    errs = problems(ts, numbered)
    if errs:
        raise Fail('\n'.join(errs + ['nothing written: fix the problems above first']))
    names = [name for name, m in ts if PREFIX_RE.match(name) and not name.startswith('.')
             and m.get('status') in ('done', 'dropped')]
    taken = [f'.{n}' for n in names if (root / f'.{n}').exists()]
    if taken:
        raise Fail(f'archive: {", ".join(taken)} already exist(s); nothing written')
    if dry_run:
        return '\n'.join(f'{n} -> .{n}' for n in names) if names else 'nothing to archive'
    if not names:
        return 'nothing to archive'
    for n in names:
        (root / n).rename(root / f'.{n}')
    write_roadmap(root, load(root))
    if flag:
        ensure_numbered_config(root)
    return f'archived {len(names)} folder(s): ' + ', '.join(f'{n} -> .{n}' for n in names)


def run(root, cmd, args=(), **kw):
    """(exit code, stdout, stderr). The CLI and the selftest both go through here.
    kw goes to new, close, roadmap, check and archive (numbered=)."""
    try:
        if cmd == 'new':
            return 0, cmd_new(root, *args, **kw), ''
        if cmd == 'close':
            return 0, cmd_close(root, *args, **kw), ''
        if cmd == 'roadmap':
            return 0, cmd_roadmap(root, **kw), ''
        if cmd == 'check':
            return 0, cmd_check(root, **kw), ''
        if cmd == 'archive':
            return 0, cmd_archive(root, **kw), ''
        raise Fail(f'unknown command {cmd!r}')
    except Fail as e:
        return 1, '', str(e)


# ---------- selftest ----------

def selftest():
    misses = []

    def expect(label, cond):
        if not cond:
            misses.append(label)

    def edit(root, slug, pattern, repl):
        h = root / slug / 'handoff.md'
        old = h.read_text(encoding='utf-8')
        new = re.sub(pattern, repl, old, count=1, flags=re.M)
        if new == old:
            raise AssertionError(f'selftest mutation did not apply: {slug} {pattern!r}')
        h.write_text(new, encoding='utf-8')

    with tempfile.TemporaryDirectory() as tmp:
        base = pathlib.Path(tmp) / 'base' / '.sdlc'
        rc_a, out_a, err_a = run(base, 'new', ('feature', 'alpha', 'Alpha | one'))
        rc_b, out_b, err_b = run(base, 'new', ('bug', 'beta', 'Fix #12'))
        expect(f'new alpha: rc={rc_a} {err_a}', rc_a == 0 and out_a.endswith('alpha/handoff.md'))
        expect(f'new beta: rc={rc_b} {err_b}', rc_b == 0)
        ids = {s: m.get('id') for s, m in load(base)}
        expect(f'ids T-0001 then T-0002, got {ids}', ids == {'alpha': 'T-0001', 'beta': 'T-0002'})
        expect('quoted title keeps "#"', dict(load(base)).get('beta', {}).get('title') == 'Fix #12')
        edit(base, 'alpha', r'^depends:.*$', 'depends: [T-0002]')
        rc, _, err = run(base, 'check')
        expect(f'edited depends makes roadmap stale: rc={rc} {err}', rc == 1 and 'stale' in err)
        run(base, 'roadmap')
        first = (base / 'roadmap.md').read_bytes()
        run(base, 'roadmap')
        expect('roadmap is byte-stable across runs', (base / 'roadmap.md').read_bytes() == first)
        rm = first.decode('utf-8')
        expect('T-0002 row before T-0001 row', 0 <= rm.find('| T-0002 |') < rm.find('| T-0001 |'))
        expect('"|" in title escaped', 'Alpha \\| one' in rm)
        rc, out, err = run(base, 'check')
        expect(f'clean base passes check: rc={rc} {err}', rc == 0 and out == 'ok: 2 tickets, roadmap current')

        before = (base / 'alpha' / 'handoff.md').read_bytes()
        rc, _, err = run(base, 'new', ('idea', 'alpha'))
        expect('new on an existing slug refuses and writes nothing',
               rc == 1 and (base / 'alpha' / 'handoff.md').read_bytes() == before)
        rc, _, err = run(base, 'new', ('epic', 'gamma'))
        expect(f'new with an unknown type lists the types: {err}',
               rc == 1 and all(t in err for t in ENUMS['type']) and not (base / 'gamma').exists())
        rc, _, err = run(base, 'new', ('idea', 'Bad_Slug'))
        expect('new with a bad slug refuses', rc == 1 and not (base / 'Bad_Slug').exists())

        n = [0]

        def case(mutate):
            n[0] += 1
            root = pathlib.Path(tmp) / f'case{n[0]}' / '.sdlc'
            shutil.copytree(base, root)
            mutate(root)
            return root

        # negative control: a handoff with no front matter is not a ticket and not an error
        def plain(root):
            (root / 'plain').mkdir()
            (root / 'plain' / 'handoff.md').write_text('## Goal\nNo front matter here.\n', encoding='utf-8')
        rc, out, err = run(case(plain), 'check')
        expect(f'handoff without front matter still passes: rc={rc} {err}', rc == 0 and 'ok: 2 tickets' in out)

        def hand_edit(root):
            with (root / 'roadmap.md').open('a', encoding='utf-8') as f:
                f.write('hand edit\n')

        mutations = [
            ('bad type', lambda r: edit(r, 'alpha', r'^type:.*$', 'type: epic'), "type='epic'"),
            ('bad status', lambda r: edit(r, 'alpha', r'^status:.*$', 'status: wip'), "status='wip'"),
            ('bad size', lambda r: edit(r, 'alpha', r'^size:.*$', 'size: XXL'), "size='XXL'"),
            ('bad priority', lambda r: edit(r, 'alpha', r'^priority:.*$', 'priority: P0'), "priority='P0'"),
            ('missing field', lambda r: edit(r, 'alpha', r'^size:.*\n', ''), 'alpha: missing size'),
            ('bad id', lambda r: edit(r, 'alpha', r'^id:.*$', 'id: T-12'), "alpha: id 'T-12' is not T-NNNN"),
            ('bad created', lambda r: edit(r, 'alpha', r'^created:.*$', 'created: 2026-9-1'),
             "alpha: created '2026-9-1' is not YYYY-MM-DD"),
            ('duplicate id', lambda r: edit(r, 'beta', r'^id:.*$', 'id: T-0001'),
             'beta: duplicate id T-0001, also used by alpha'),
            ('dangling depends', lambda r: edit(r, 'alpha', r'^depends:.*$', 'depends: [T-0099]'),
             'alpha: depends on T-0099'),
            ('dangling from', lambda r: edit(r, 'alpha', r'^created:(.*)$', r'created:\1\nfrom: T-0099'),
             'alpha: from T-0099'),
            ('cycle', lambda r: edit(r, 'beta', r'^depends:.*$', 'depends: [T-0001]'), 'cycle T-0001 -> T-0002 -> T-0001'),
            ('self-cycle', lambda r: edit(r, 'alpha', r'^depends:.*$', 'depends: [T-0001]'), 'cycle T-0001 -> T-0001'),
            ('stale roadmap', hand_edit, 'stale'),
        ]
        for label, mutate, want in mutations:
            rc, _, err = run(case(mutate), 'check')
            expect(f'{label}: check did not fail with {want!r} (rc={rc}, stderr={err!r})', rc == 1 and want in err)
        rc, _, err = run(case(mutations[0][1]), 'roadmap')
        expect('roadmap refuses on a bad ticket', rc == 1 and "type='epic'" in err)
        rc, _, err = run(case(mutations[0][1]), 'new', ('idea', 'delta'))
        expect('new refuses on a bad ticket', rc == 1 and "type='epic'" in err)

        def snap(root):
            return {p.relative_to(root): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}

        # ---- numbered folders: base holds T-0001 and T-0002, so the next id is T-0003 ----
        def tree(root):
            return sorted(p.name for p in root.iterdir())

        def config(text):
            def put(root):
                (root / 'config').write_text(text, encoding='utf-8')
            return put

        def both(*fs):
            def put(root):
                for f in fs:
                    f(root)
            return put

        def numbered_ok(label, root, rc, out, err, slug):
            ids = dict(load(root))
            got = ids.get(f'0003-{slug}', {}).get('id')
            expect(f'{label}: folder 0003-{slug} with id T-0003, rc={rc} out={out!r} err={err!r} '
                   f'tree={tree(root)} id={got!r}',
                   rc == 0 and out.endswith(f'0003-{slug}/handoff.md') and got == 'T-0003'
                   and not (root / slug).exists() and run(root, 'check')[0] == 0
                   and run(root, 'check', numbered=True)[0] == 0)

        root = case(lambda r: None)
        rc, out, err = run(root, 'new', ('feature', 'gamma'), numbered=True)
        numbered_ok('new --numbered', root, rc, out, err, 'gamma')

        # new --numbered persists `ticket_folders: numbered` in <root>/config, so plain check enforces it
        expect(f'new --numbered writes config with the numbered line: tree={tree(root)}',
               (root / 'config').is_file() and config_numbered(root))
        (root / '0003-gamma').rename(root / '0009-gamma')
        run(root, 'roadmap')
        rc, _, err = run(root, 'check')
        expect(f'after new --numbered, plain check fails a renamed 0009-gamma: rc={rc} {err!r}',
               rc == 1 and "0009-gamma: folder prefix 0009- does not match id 'T-0003'" in err)
        root = case(config('# keep me\nother: x\n'))
        rc, _, err = run(root, 'new', ('feature', 'gamma'), numbered=True)
        text = (root / 'config').read_text(encoding='utf-8') if (root / 'config').is_file() else ''
        expect(f'new --numbered keeps existing config lines and adds the numbered line once: {text!r}',
               rc == 0 and text.startswith('# keep me\nother: x\n')
               and len([ln for ln in text.splitlines() if CONFIG_RE.fullmatch(ln)]) == 1)
        for label, mutate in (('twice', lambda r: None), ('line present', config('ticket_folders: numbered\n'))):
            root = case(mutate)
            run(root, 'new', ('feature', 'gamma'), numbered=True)
            if label == 'twice':
                run(root, 'new', ('feature', 'delta'), numbered=True)
            text = (root / 'config').read_text(encoding='utf-8') if (root / 'config').is_file() else ''
            expect(f'new --numbered ({label}) leaves one ticket_folders: numbered line: {text!r}',
                   len([ln for ln in text.splitlines() if CONFIG_RE.fullmatch(ln)]) == 1)
        root = case(lambda r: None)
        rc, _, err = run(root, 'new', ('feature', 'gamma'))
        expect(f'plain new writes no config: rc={rc} tree={tree(root)}', rc == 0 and not (root / 'config').exists())

        root = case(config('# tickets\n\nticket_folders: numbered\n'))
        rc, out, err = run(root, 'new', ('feature', 'gamma'))
        numbered_ok('new with config ticket_folders: numbered', root, rc, out, err, 'gamma')

        # a slug already carrying NNNN- in numbered mode: refuses, names the double prefix, writes nothing
        for label, mutate, kw in (('flag', lambda r: None, {'numbered': True}),
                                  ('config', config('ticket_folders: numbered\n'), {})):
            root = case(mutate)
            before = snap(root)
            rc, _, err = run(root, 'new', ('feature', '0007-gamma'), **kw)
            expect(f'new 0007-gamma in numbered mode ({label}) refuses on the double prefix: rc={rc} {err!r}',
                   rc == 1 and 'double' in err and snap(root) == before)

        # an existing numbered folder with the final name refuses and writes nothing
        root = case(lambda r: (r / '0003-gamma').mkdir())
        before = snap(root)
        rc, _, err = run(root, 'new', ('feature', 'gamma'), numbered=True)
        expect(f'new --numbered onto an existing 0003-gamma refuses: rc={rc} {err!r}',
               rc == 1 and '0003-gamma' in err and snap(root) == before)

        # negative control: plain mode (no flag; config absent, or config saying anything else) is a bare slug
        for label, mutate in (('no config', lambda r: None),
                              ('other config', config('# ticket_folders: numbered\nticket_folders: plain\n'))):
            root = case(mutate)
            rc, out, err = run(root, 'new', ('feature', 'gamma'))
            expect(f'plain mode ({label}) new gives bare folder gamma: rc={rc} out={out!r} err={err!r} '
                   f'tree={tree(root)}',
                   rc == 0 and out.endswith('/gamma/handoff.md') and dict(load(root)).get('gamma', {}).get('id')
                   == 'T-0003' and not any(PREFIX_RE.match(n) for n in tree(root)))
        root = case(lambda r: None)
        rc, out, err = run(root, 'new', ('feature', '0007-gamma'))
        expect(f'plain mode still takes a digit-led slug as-is: rc={rc} {err!r}',
               rc == 0 and (root / '0007-gamma' / 'handoff.md').is_file())
        rc, _, err = run(root, 'check')
        rc_n, _, err_n = run(root, 'check', numbered=True)
        expect(f'digit-led plain slug: plain check passes, check --numbered names it: rc={rc} {err!r} '
               f'rc_n={rc_n} {err_n!r}', rc == 0 and rc_n == 1 and '0007-gamma' in err_n)

        # ---- NNNN-/id rule: numbered mode only; a rename makes the roadmap stale, so regenerate it ----
        def renamed(to):
            def put(root):
                (root / 'alpha').rename(root / to)
                run(root, 'roadmap')
            return put

        mismatch = "0005-alpha: folder prefix 0005- does not match id 'T-0001'"
        for label, mutate, kw in (('flag', renamed('0005-alpha'), {'numbered': True}),
                                  ('config', both(renamed('0005-alpha'), config('ticket_folders: numbered\n')), {})):
            rc, _, err = run(case(mutate), 'check', **kw)
            expect(f'prefix mismatch ({label}): rc={rc} {err!r}', rc == 1 and mismatch in err)
        rc, out, err = run(case(renamed('0005-alpha')), 'check')
        expect(f'prefix mismatch is not checked in plain mode: rc={rc} {out!r} {err!r}',
               rc == 0 and out == 'ok: 2 tickets, roadmap current' and 'prefix' not in err)
        rc, _, err = run(case(renamed('0001-alpha')), 'check', numbered=True)
        expect(f'matching 0001-alpha passes check --numbered: rc={rc} {err!r}', rc == 0)
        rc, _, err = run(case(lambda r: None), 'check', numbered=True)
        expect(f'plain slugs get no prefix error in numbered mode: rc={rc} {err!r}', rc == 0)

        # check warns (exit 0) when every folder is NNNN- but <root>/config lacks the numbered line
        def renamed_beta(root):
            (root / 'beta').rename(root / '0002-beta')
            run(root, 'roadmap')
        all_numbered = both(renamed('0001-alpha'), renamed_beta)
        rc, out, err = run(case(all_numbered), 'check')
        expect(f'all-numbered folders, no config: check warns and exits 0: rc={rc} {out!r} {err!r}',
               rc == 0 and out.startswith('ok: 2 tickets') and 'warning' in out and "ticket_folders: numbered" in out)
        for label, mutate in (('with config', both(all_numbered, config('ticket_folders: numbered\n'))),
                              ('plain slugs', lambda r: None),
                              ('mixed', renamed('0001-alpha'))):
            rc, out, err = run(case(mutate), 'check')
            expect(f'no numbered-config warning ({label}): rc={rc} {out!r} {err!r}',
                   rc == 0 and 'warning' not in out + err)
        rc, out, err = run(pathlib.Path(tmp) / 'empty-warn' / '.sdlc', 'check')
        expect(f'no numbered-config warning (empty root): rc={rc} {out!r}', rc == 0 and 'warning' not in out + err)
        # roadmap follows the same rule: numbered mode refuses on a mismatch and writes nothing
        for label, mutate, kw in (('flag', renamed('0005-alpha'), {'numbered': True}),
                                  ('config', both(renamed('0005-alpha'), config('ticket_folders: numbered\n')), {})):
            root = case(mutate)
            before = snap(root)
            rc, _, err = run(root, 'roadmap', **kw)
            expect(f'roadmap refuses on a prefix mismatch ({label}) and writes nothing: rc={rc} {err!r}',
                   rc == 1 and mismatch in err and 'roadmap not written' in err and snap(root) == before)
        rc, out, err = run(case(renamed('0005-alpha')), 'roadmap')
        expect(f'plain roadmap ignores a prefix mismatch: rc={rc} {out!r} {err!r}', rc == 0 and 'prefix' not in err)
        rc, _, err = run(case(renamed('0001-alpha')), 'roadmap', numbered=True)
        expect(f'matching 0001-alpha passes roadmap --numbered: rc={rc} {err!r}', rc == 0)
        root = case(both(renamed('0005-alpha'), config('ticket_folders: numbered\n')))
        before = snap(root)
        for cmd, args in (('new', ('feature', 'gamma')), ('close', ('beta',))):
            rc, _, err = run(root, cmd, args)
            expect(f'numbered {cmd} refuses on an existing prefix mismatch and writes nothing: rc={rc} {err!r}',
                   rc == 1 and '0005-alpha: folder prefix' in err and 'fix the problems above first' in err
                   and snap(root) == before)
        root = case(renamed('0005-alpha'))
        rc, _, err = run(root, 'new', ('feature', 'gamma'))
        expect(f'plain new ignores an existing prefix mismatch: rc={rc} {err!r}',
               rc == 0 and (root / 'gamma' / 'handoff.md').is_file())

        # ---- close: each case in its own copy of base; alpha (T-0001) is the ticket being closed ----
        def filer(name, warnings, follow, mtime=None, slug='alpha'):
            def put(root):
                p = root / slug / name
                p.write_text(f'## Warnings\n{warnings}\n\n## PR title\nx\n\n## Follow-ups\n{follow}\n', encoding='utf-8')
                if mtime is not None:
                    os.utime(p, (mtime, mtime))
            return put

        def fresh(root, before):
            return {s: m for s, m in load(root) if s not in before}

        def status(root, slug='alpha'):
            return dict(load(root)).get(slug, {}).get('status')

        long_item = ('Split the runner into a preflight module and an exec module so the Fable swap can be '
                     'tested on its own')
        short_first_sentence_item = ('Optional id and status columns in board.py. T-0001 listed this as '
                                      'optional, and the plan left it out of scope.')
        underscore_item = '`follow_up_title` in tickets.py returns a mangled title with underscores stripped'
        good = filer('filer-L1.md', 'None', f'- Quote the `--root` flag in the docs\n'
                     f'- {long_item[:60]}\n  {long_item[60:]}\n'
                     f'- {short_first_sentence_item}\n'
                     f'- {underscore_item}')

        def with_body_status(root):
            with (root / 'alpha' / 'handoff.md').open('a', encoding='utf-8') as f:
                f.write('\nstatus: this body line is not front matter\n')

        # (a) Warnings None, two bullets (a backtick, and one over 70 chars wrapped onto a continuation line)
        root = case(both(good, with_body_status))
        before_h = (root / 'alpha' / 'handoff.md').read_bytes()
        rc, out, err = run(root, 'close', ('alpha',))
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(a) close: rc={rc} out={out!r} err={err!r}',
               rc == 0 and out.startswith('T-0001 done; 4 follow-up ticket(s): '))
        expect(f'(a) four idea/proposed tickets from T-0001, got {made}', len(made) == 4 and all(
            m.get('type') == 'idea' and m.get('status') == 'proposed' and m.get('from') == 'T-0001'
            for m in made.values()))
        titles = sorted(m.get('title', '') for m in made.values())
        expect(f'(a) titles clean and <= 70 chars: {titles}',
               all(len(t) <= 70 and '`' not in t for t in titles) and 'Quote the --root flag in the docs' in titles)
        expect(f'(a) short-first-sentence bullet title is the sentence without its final period: {titles}',
               'Optional id and status columns in board.py' in titles)
        expect(f'(a) underscore inside a word survives cleanup (not mangled to followuptitle): {titles}',
               any('follow_up_title' in t for t in titles) and not any('followuptitle' in t for t in titles))
        empty_first_sentence_title = follow_up_title('. ' + 'x' * 80)
        expect(f'(a) empty first sentence falls through to whole-word cut: {empty_first_sentence_title!r}',
               bool(empty_first_sentence_title) and not empty_first_sentence_title.startswith('.'))
        long_title = next((t for t in titles if t.endswith('...')), None)
        expect(f'(a) long_item title ends with ...: {titles}', long_title is not None)
        prefix = long_title[:-3]
        expect(f'(a) long_item title is a whole-word prefix of long_item, no trailing space/punct before ...: '
               f'{long_title!r}',
               long_item.startswith(prefix) and len(long_item) > len(prefix)
               and long_item[len(prefix)] == ' ' and prefix == prefix.rstrip()
               and (not prefix or prefix[-1] not in ',;:.-'))
        ctx = ''.join((root / s / 'handoff.md').read_text(encoding='utf-8') for s in made)
        expect('(a) context names the source and keeps the joined continuation line',
               'Follow-up from T-0001 (alpha/filer-L1.md):' in ctx and long_item in ctx)
        expect('(a) parent done, rest byte-identical, body status line untouched',
               (root / 'alpha' / 'handoff.md').read_bytes()
               == before_h.replace(b'status: proposed', b'status: done', 1)
               and b'status: this body line is not front matter' in before_h)
        rc, out, err = run(root, 'check')
        expect(f'(a) check passes after close: rc={rc} {err}', rc == 0 and 'ok: 6 tickets' in out)

        # (b) Warnings open, no --force: refuses and writes nothing
        warned = filer('filer-L1.md', 'step-2 verifier fail', '- Add retry to fetch')
        root = case(warned)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(b) open warnings refuse, name --force and the warning: rc={rc} {err!r}',
               rc == 1 and '--force' in err and 'step-2 verifier fail' in err)
        expect('(b) refusal wrote nothing (handoff, ticket count, roadmap)', snap(root) == before
               and len(load(root)) == 2 and status(root) == 'proposed')
        expect(f'(b) refusal names --ack-warnings before --force: {err!r}',
               '--ack-warnings "<why>"' in err and err.find('--ack-warnings') < err.find('--force'))

        # (c) the same with --force closes
        root = case(warned)
        rc, out, err = run(root, 'close', ('alpha', True))
        expect(f'(c) --force closes: rc={rc} {err!r}', rc == 0 and status(root) == 'done'
               and len(fresh(root, {'alpha', 'beta'})) == 1)

        # (d) Follow-ups None: no tickets, parent done
        root = case(filer('filer-L1.md', 'None.', 'None'))
        rc, out, err = run(root, 'close', ('alpha',))
        expect(f'(d) follow-ups None: rc={rc} {out!r} {err!r}', rc == 0 and '0 follow-up' in out
               and not fresh(root, {'alpha', 'beta'}) and status(root) == 'done' and run(root, 'check')[0] == 0)

        # (e) no filer file: refuses, names /file
        root = case(lambda r: None)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(e) no filer file refuses: rc={rc} {err!r}', rc == 1 and '/file' in err and snap(root) == before)

        # (f) prose follow-ups with no bullet: refuses, writes nothing
        root = case(filer('filer-L1.md', 'None', 'We should add retry to fetch and document the flag.'))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(f) prose follow-ups refuse: rc={rc} {err!r}', rc == 1 and snap(root) == before)

        # (g) a second close on a done ticket: refuses, no duplicate tickets
        root = case(good)
        run(root, 'close', ('alpha',))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha', True))
        expect(f'(g) second close refuses: rc={rc} {err!r}', rc == 1 and 'already closed' in err and snap(root) == before)

        # (h) the newest filer file is picked by recorded run order in runs.jsonl, never by file time
        def runs(*names):
            def put(root):
                (root / 'alpha' / 'runs.jsonl').write_text(''.join(
                    f'{{"role": "filer", "level": "{n[6:8]}", "file": "{n}"}}\n' for n in names), encoding='utf-8')
            return put

        bad = 'step-1 verifier fail'
        root = case(both(both(filer('filer-L2.md', bad, 'None', mtime=1_000_000),
                              filer('filer-L1.md', 'None', 'None', mtime=1_000_000)),
                         runs('filer-L2.md', 'filer-L1.md')))
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(h) equal mtimes: runs.jsonl picks the lower-named filer recorded last: rc={rc} {err!r}',
               rc == 0 and status(root) == 'done')
        root = case(both(both(filer('filer-L2.md', bad, 'None', mtime=2_000_000),
                              filer('filer-L1.md', 'None', 'None', mtime=1_000_000)),
                         runs('filer-L2.md', 'filer-L1.md')))
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(h) inverse mtimes: runs.jsonl still decides: rc={rc} {err!r}', rc == 0 and status(root) == 'done')
        # no records: name (level) order, filer-L2.md beats a newer filer-L1.md
        root = case(both(filer('filer-L1.md', bad, 'None', mtime=2_000_000),
                         filer('filer-L2.md', 'None', 'None', mtime=1_000_000)))
        rc, _, err = run(root, 'close', ('alpha',))
        expect(f'(h) no runs.jsonl: name order decides, not mtime: rc={rc} {err!r}', rc == 0 and status(root) == 'done')

        # (i) numbered close: each follow-up folder is NNNN-<slug> with its own id; alpha keeps its name
        numbered_follow = filer('filer-L1.md', 'None', '- Add retry to fetch\n- Add retry to fetch\n'
                                '- 0042 fix the parser')
        for label, mutate, kw in (('flag', numbered_follow, {'numbered': True}),
                                  ('config', both(numbered_follow, config('ticket_folders: numbered\n')), {})):
            root = case(mutate)
            rc, out, err = run(root, 'close', ('alpha',), **kw)
            made = fresh(root, {'alpha', 'beta'})
            ok = all(re.match(r'\d{4}-', s) and s[:4] == m.get('id', '')[2:] for s, m in made.items())
            expect(f'(i) numbered close ({label}): rc={rc} {err!r} made={sorted(made)}',
                   rc == 0 and len(made) == 3 and ok and status(root) == 'done'
                   and sorted(made) == ['0003-add-retry-to-fetch', '0004-add-retry-to-fetch',
                                        '0005-fix-the-parser'] and run(root, 'check')[0] == 0)
        # (i) a clash on the final numbered name appends -2
        root = case(both(filer('filer-L1.md', 'None', '- Add retry to fetch'),
                         lambda r: (r / '0003-add-retry-to-fetch').mkdir()))
        rc, out, err = run(root, 'close', ('alpha',), numbered=True)
        expect(f'(i) numbered clash appends -2: rc={rc} {err!r} {out!r}',
               rc == 0 and (root / '0003-add-retry-to-fetch-2' / 'handoff.md').is_file())
        # (i) negative control: no flag, no config -> bare-slug follow-ups
        root = case(numbered_follow)
        rc, out, err = run(root, 'close', ('alpha',))
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(i) plain close keeps bare slugs: rc={rc} {sorted(made)}',
               rc == 0 and sorted(made) == ['0042-fix-the-parser', 'add-retry-to-fetch', 'add-retry-to-fetch-2'])
        expect(f'(i) plain close writes no config: tree={tree(root)}', not (root / 'config').exists())
        # (j) close --numbered persists `ticket_folders: numbered`, like new --numbered; a refusal writes none
        root = case(numbered_follow)
        rc, out, err = run(root, 'close', ('alpha',), numbered=True)
        expect(f'(j) close --numbered writes config with the numbered line: rc={rc} {err!r} tree={tree(root)}',
               rc == 0 and (root / 'config').is_file() and config_numbered(root))
        root = case(filer('filer-L1.md', 'step-1 verifier fail', '- Add retry to fetch'))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), numbered=True)
        expect(f'(j) refused close --numbered writes no config: rc={rc} {err!r}',
               rc == 1 and not (root / 'config').exists() and snap(root) == before)

        # (k) --reason closes with no filer file: done, a ## Closed section, check passes
        root = case(lambda r: None)
        rc, out, err = run(root, 'close', ('alpha',), reason='done by T-0002')
        text = (root / 'alpha' / 'handoff.md').read_text(encoding='utf-8')
        expect(f'(k) --reason closes without a filer: rc={rc} {err!r} {out!r}',
               rc == 0 and status(root) == 'done' and 'reason' in out
               and text.rstrip().endswith(f'## Closed\n\n{datetime.date.today().isoformat()}: done by T-0002')
               and run(root, 'check')[0] == 0)
        # (l) --reason ignores a filer with open warnings and follow-ups
        root = case(filer('filer-L1.md', 'step-1 verifier fail', '- Add retry to fetch'))
        rc, out, err = run(root, 'close', ('alpha',), reason='superseded')
        expect(f'(l) --reason ignores the filer: rc={rc} {err!r}',
               rc == 0 and status(root) == 'done' and not fresh(root, {'alpha', 'beta'}))
        # (m) an empty or whitespace-only reason refuses and writes nothing
        for why in ('', '   '):
            root = case(lambda r: None)
            before = snap(root)
            rc, _, err = run(root, 'close', ('alpha',), reason=why)
            expect(f'(m) empty --reason {why!r} refuses: rc={rc} {err!r}', rc == 1 and snap(root) == before)
        # (n) --reason on a done ticket still refuses
        root = case(lambda r: None)
        run(root, 'close', ('alpha',), reason='first')
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), reason='second')
        expect(f'(n) --reason on done refuses: rc={rc} {err!r}',
               rc == 1 and 'already closed' in err and snap(root) == before)
        # (o) --force with --reason closes; --numbered with --reason persists the config
        root = case(lambda r: None)
        rc, _, err = run(root, 'close', ('alpha', True), reason='x')
        expect(f'(o) --force --reason closes: rc={rc} {err!r}', rc == 0 and status(root) == 'done')
        root = case(lambda r: None)
        rc, _, err = run(root, 'close', ('alpha',), numbered=True, reason='x')
        expect(f'(o) --numbered --reason persists config: rc={rc} {err!r}',
               rc == 0 and status(root) == 'done' and config_numbered(root))

        # (p) --dry-run lists every bullet with its index and duplicate mark, and writes nothing
        three = '- Add retry to fetch\n- Quote the docs\n- Split the runner'
        root = case(filer('filer-L1.md', 'None', '- Add retry to fetch\n- Fix #12\n- Quote the docs'))
        before = snap(root)
        rc, out, err = run(root, 'close', ('alpha',), numbered=True, dry_run=True)
        lines = out.splitlines()
        expect(f'(p) dry run lists 1 to 3, marks Fix #12 as a duplicate of beta, writes nothing: rc={rc} '
               f'out={out!r} err={err!r} tree={tree(root)}',
               rc == 0 and snap(root) == before and status(root) == 'proposed'
               and lines[:1] == ['T-0001 dry run: 3 proposed follow-up(s); nothing written']
               and [ln.split('.', 1)[0] for ln in lines[1:-1] if not ln.startswith('open ')] == ['1', '2', '3']
               and lines[-1] == 'expect ' + follow_digest(['Add retry to fetch', 'Fix #12', 'Quote the docs'])
               and lines[2].startswith('2. Fix #12 ') and lines[2].endswith('duplicate of T-0002 (beta)')
               and 'duplicate' not in lines[1] + lines[3])
        # (p2) open tickets listed: an open ticket with its full title; not done/dropped, not the closed one
        def open_mix(r):
            filer('filer-L1.md', 'None', '- Add retry to fetch')(r)
            cmd_new(r, 'bug', 'gone', 'Gone bug')
            edit(r, 'gone', r'^status:.*$', 'status: dropped')
        root = case(open_mix)
        rc, out, err = run(root, 'close', ('alpha',), dry_run=True)
        opens = [ln for ln in out.splitlines() if ln.startswith('open ')]
        beta = next(m for x, m in load(root) if x == 'beta')
        expect(f'(p2) open tickets listed: beta with full title, not dropped gone, not alpha: rc={rc} {out!r} {err!r}',
               rc == 0 and opens == [f'open T-0002 {beta["title"]} [beta]']
               and out.splitlines()[-1].startswith('expect '))
        root = case(filer('filer-L1.md', 'step-2 verifier fail', '- Add retry to fetch'))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), dry_run=True)
        expect(f'(p) dry run with open warnings and no --force refuses: rc={rc} {err!r}',
               rc == 1 and '--force' in err and snap(root) == before)

        # (q) --skip files every other follow-up, and the rest take consecutive ids
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, err = run(root, 'close', ('alpha',), skip=[2], expect=follow_digest(bullets(three)))
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(q) --skip 2 files bullets 1 and 3 only: rc={rc} out={out!r} err={err!r} made={sorted(made)}',
               rc == 0 and status(root) == 'done' and len(made) == 2
               and sorted(m.get('title') for m in made.values()) == ['Add retry to fetch', 'Split the runner']
               and sorted(m.get('id') for m in made.values()) == ['T-0003', 'T-0004']
               and 'skipped by --skip: 2' in out)

        # (r) --skip out of range refuses, names the index and the count, writes nothing
        for bad, follow in ((4, three), (0, three), (1, 'None')):
            root = case(filer('filer-L1.md', 'None', follow))
            before = snap(root)
            for dry in (True, False):
                token = None if dry else follow_digest([] if follow == 'None' else bullets(follow))
                rc, _, err = run(root, 'close', ('alpha',), skip=[bad], dry_run=dry, expect=token)
                count = 0 if follow == 'None' else 3
                expect(f'(r) --skip {bad} (dry_run={dry}) with {count} bullet(s) refuses: rc={rc} {err!r}',
                       rc == 1 and f'--skip {bad} ' in err and f'has {count} item' in err and snap(root) == before)
        try:
            parse_skip('2,x')
            bad_token = None
        except Fail as e:
            bad_token = str(e)
        expect(f'(r) a non-integer --skip token is a refusal: {bad_token!r}',
               bad_token is not None and "'x'" in bad_token and parse_skip('3, 1') == [3, 1])

        # (s) a plain close skips duplicates of existing tickets (by title, by slug base) and names them
        root = case(filer('filer-L1.md', 'None', '- Fix #12\n- Beta\n- Add retry to fetch'))
        rc, out, err = run(root, 'close', ('alpha',))
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(s) duplicates of beta skipped on close: rc={rc} out={out!r} err={err!r} made={sorted(made)}',
               rc == 0 and sorted(made) == ['add-retry-to-fetch'] and 'skipped duplicate(s)' in out
               and out.count('T-0002 (beta)') == 2 and run(root, 'check')[0] == 0)

        # (s2) the ticket being closed is not a duplicate target: follow-ups that start with its own
        # title ("Alpha | one" -> "alpha one") are filed, and colliding slugs take a -2 suffix
        root = case(filer('filer-L1.md', 'None', '- Alpha one\n- Alpha one.'))
        rc, out, err = run(root, 'close', ('alpha',), dry_run=True)
        expect(f'(s2) dry run marks no bullet a duplicate of the closing ticket: rc={rc} out={out!r} err={err!r}',
               rc == 0 and 'duplicate' not in out and '1. Alpha one ' in out and '2. Alpha one. ' in out)
        rc, out, err = run(root, 'close', ('alpha',))
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(s2) close files both follow-ups, the second as -2: rc={rc} out={out!r} err={err!r} '
               f'made={sorted(made)}',
               rc == 0 and sorted(made) == ['alpha-one', 'alpha-one-2'] and 'duplicate' not in out
               and run(root, 'check')[0] == 0)

        # (t) --reason does not combine with --dry-run or --skip
        for kw in ({'dry_run': True}, {'skip': [1]}, {'expect': 'x'}):
            root = case(filer('filer-L1.md', 'None', three))
            before = snap(root)
            rc, _, err = run(root, 'close', ('alpha',), reason='superseded', **kw)
            expect(f'(t) --reason with {kw} refuses and writes nothing: rc={rc} {err!r}',
                   rc == 1 and '--reason' in err and snap(root) == before)

        # (v) --skip is tied to the dry run's list: a changed Follow-ups list refuses, unchanged closes.
        # (v4) a plain close with no --skip and no --expect needs no token; case (s) covers it too.
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, _ = run(root, 'close', ('alpha',), dry_run=True)
        old = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        filer('filer-L1.md', 'None', '- Quote the docs\n- Add retry to fetch\n- Split the runner')(root)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), skip=[2], expect=old)
        expect(f'(v1) a reordered Follow-ups list refuses stale --skip indices: rc={rc} {err!r}',
               rc == 1 and 'does not match' in err and 'filer-L1.md' in err and err.endswith('nothing written')
               and snap(root) == before and status(root) == 'proposed')
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, _ = run(root, 'close', ('alpha',), dry_run=True)
        token = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        rc, out, err = run(root, 'close', ('alpha',), skip=[2], expect=token)
        expect(f'(v2) an unchanged list closes with --skip --expect: rc={rc} {out!r} {err!r}',
               rc == 0 and status(root) == 'done' and len(fresh(root, {'alpha', 'beta'})) == 2)
        root = case(filer('filer-L1.md', 'None', three))
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), skip=[2])
        expect(f'(v3) --skip without --expect refuses: rc={rc} {err!r}',
               rc == 1 and '--expect' in err and 'nothing written' in err and snap(root) == before)
        root = case(filer('filer-L1.md', 'None', three))
        rc, out, err = run(root, 'close', ('alpha',))
        expect(f'(v4) plain close needs no token: rc={rc} {err!r}', rc == 0 and status(root) == 'done')
        tail = ' and a retry budget that callers can tune per request without touching the runner at all'
        long3 = f'- Add retry to fetch{tail}\n- Quote the docs\n- Split the runner'
        root = case(filer('filer-L1.md', 'None', long3))
        rc, out, _ = run(root, 'close', ('alpha',), dry_run=True)
        old = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        filer('filer-L1.md', 'None', long3.replace('at all', 'ever'))(root)
        before = snap(root)
        rc, _, err = run(root, 'close', ('alpha',), skip=[2], expect=old)
        expect(f'(v5) rewording past the title cut refuses: rc={rc} {err!r}',
               rc == 1 and 'does not match' in err and snap(root) == before)

        # (u) numbered close archives a NNNN-<slug> folder as .NNNN-<slug>; every command still sees it
        def numbered_x(root):
            rc, _, err = run(root, 'new', ('feature', 'x'), numbered=True)  # 0003-x, T-0003; persists config
            if rc:
                raise AssertionError(f'selftest fixture 0003-x not made: {err}')

        def x_filer(follow):
            return filer('filer-L1.md', 'None', follow, slug='0003-x')

        root = case(both(numbered_x, x_filer('- Add retry to fetch')))
        rc, out, err = run(root, 'close', ('0003-x',))
        made = fresh(root, {'alpha', 'beta', '.0003-x'})
        ctx = ''.join((root / s / 'handoff.md').read_text(encoding='utf-8') for s in made)
        expect(f'(u) numbered close with a filer renames 0003-x to .0003-x: rc={rc} out={out!r} err={err!r} '
               f'tree={tree(root)}',
               rc == 0 and out.endswith('; moved to .0003-x') and not (root / '0003-x').exists()
               and (root / '.0003-x' / 'filer-L1.md').is_file() and status(root, '.0003-x') == 'done'
               and sorted(made) == ['0004-add-retry-to-fetch']
               and 'Follow-up from T-0003 (.0003-x/filer-L1.md):' in ctx and run(root, 'check')[0] == 0)
        rm = (root / 'roadmap.md').read_text(encoding='utf-8')
        expect(f'(u) roadmap lists .0003-x: {rm!r}', '| T-0003 | [.0003-x](.0003-x/handoff.md) |' in rm)
        before = snap(root)
        for kw in ({}, {'reason': 'again'}, {'dry_run': True}):
            rc, _, err = run(root, 'close', ('0003-x',), **kw)
            expect(f'(u) closing again by the old name {kw} refuses with already closed: rc={rc} {err!r}',
                   rc == 1 and 'already closed (folder .0003-x)' in err and snap(root) == before)
        edit(root, 'beta', r'^depends:.*$', 'depends: [T-0003]')
        run(root, 'roadmap')
        rc, out, err = run(root, 'check')
        expect(f'(u) depends: [T-0003] on the dot folder resolves: rc={rc} {out!r} {err!r}',
               rc == 0 and 'ok: 4 tickets' in out)

        root = case(numbered_x)
        rc, out, err = run(root, 'close', ('0003-x',), reason='done elsewhere')
        text = (root / '.0003-x' / 'handoff.md').read_text(encoding='utf-8') if (root / '.0003-x').is_dir() else ''
        expect(f'(u) numbered --reason close renames: rc={rc} out={out!r} err={err!r} tree={tree(root)}',
               rc == 0 and out.endswith('; moved to .0003-x') and not (root / '0003-x').exists()
               and '## Closed' in text and status(root, '.0003-x') == 'done' and run(root, 'check')[0] == 0)
        rc, out, err = run(root, 'new', ('feature', 'y'), numbered=True)
        got = dict(load(root)).get('0004-y', {}).get('id')
        expect(f'(u) next new --numbered after a dot folder gets T-0004: rc={rc} {out!r} {err!r} id={got!r}',
               rc == 0 and got == 'T-0004')
        count = len(load(root))
        (root / '.hidden').mkdir()
        (root / '.hidden' / 'handoff.md').write_bytes((root / 'beta' / 'handoff.md').read_bytes())
        (root / '.board-state.json').write_text('{}', encoding='utf-8')
        rc, out, err = run(root, 'check')
        expect(f'(u) .hidden/handoff.md and .board-state.json are not tickets: rc={rc} {out!r} {err!r}',
               len(load(root)) == count == 4 and rc == 0 and out.startswith('ok: 4 tickets'))
        edit(root, '.0003-x', r'^status:.*$', 'status: ready')
        for label in ('numbered by config', 'plain mode'):
            if label == 'plain mode':
                (root / 'config').unlink()
            rc, _, err = run(root, 'check')
            expect(f'(u) check ({label}) fails a dot folder with status ready: rc={rc} {err!r}',
                   rc == 1 and '.0003-x: closed ticket folder' in err and 'done or dropped' in err)
        edit(root, '.0003-x', r'^status:.*$', 'status: dropped')
        run(root, 'roadmap')
        rc, out, err = run(root, 'check', numbered=True)
        expect(f'(u) a dropped dot folder passes: rc={rc} {out!r} {err!r}', rc == 0)

        # (u) the rename target already exists: refuses on every close path and writes nothing
        for kw in ({}, {'reason': 'x'}, {'dry_run': True}):
            root = case(both(numbered_x, x_filer('- Add retry to fetch'), lambda r: (r / '.0003-x').mkdir()))
            before = snap(root)
            rc, _, err = run(root, 'close', ('0003-x',), **kw)
            expect(f'(u) close {kw} onto an existing .0003-x refuses: rc={rc} {err!r}',
                   rc == 1 and '.0003-x' in err and 'nothing written' in err and snap(root) == before
                   and (root / '0003-x' / 'handoff.md').is_file())

        # (u) the dry run shows the rename line and writes nothing
        root = case(both(numbered_x, x_filer('- Add retry to fetch')))
        before = snap(root)
        rc, out, err = run(root, 'close', ('0003-x',), dry_run=True)
        expect(f'(u) dry run shows the rename and writes nothing: rc={rc} {out!r} {err!r}',
               rc == 0 and 'rename 0003-x -> .0003-x' in out.splitlines() and snap(root) == before
               and not (root / '.0003-x').exists())

        # (u) numbered: a .NNNN- folder still gets the prefix/id rule; a dot folder counts as prefixed
        def closed_as(to):
            def put(root):
                edit(root, 'alpha', r'^status:.*$', 'status: done')
                (root / 'alpha').rename(root / to)
                run(root, 'roadmap')
            return put
        rc, _, err = run(case(closed_as('.0005-alpha')), 'check', numbered=True)
        expect(f'(u) .0005-alpha with id T-0001 fails check --numbered: rc={rc} {err!r}',
               rc == 1 and ".0005-alpha: folder prefix 0005- does not match id 'T-0001'" in err)
        rc, out, err = run(case(both(closed_as('.0001-alpha'), renamed_beta)), 'check')
        expect(f'(u) .0001-alpha plus 0002-beta, no config: the numbered-config warning fires: rc={rc} {out!r}',
               rc == 0 and 'warning' in out)
        expect("(u) strip_prefix drops a closed folder's dot", strip_prefix('.0002-beta') == 'beta')

        # (u) negative controls: plain mode, and a plain slug in numbered mode, never rename
        for label, mutate in (('plain mode', lambda r: None),
                              ('numbered, plain slug', config('ticket_folders: numbered\n'))):
            for kw in ({'reason': 'x'}, {}):
                root = case(both(mutate, filer('filer-L1.md', 'None', 'None')))
                rc, out, err = run(root, 'close', ('alpha',), **kw)
                expect(f'(u) {label} close {kw} does not rename alpha: rc={rc} {out!r} {err!r} tree={tree(root)}',
                       rc == 0 and status(root) == 'done' and not (root / '.alpha').exists()
                       and (root / 'alpha' / 'handoff.md').is_file() and 'moved' not in out)

        # (w) --ack-warnings closes past open warnings with a recorded reason; warned: 'step-2 verifier fail'
        today = datetime.date.today().isoformat()
        # (w1) ack close: done, the follow-up filed, a ## Closed section quoting the warning, check passes
        root = case(warned)
        rc, out, err = run(root, 'close', ('alpha',), ack_warnings='committed later')
        text = (root / 'alpha' / 'handoff.md').read_text(encoding='utf-8')
        expect(f'(w1) --ack-warnings closes with open warnings: rc={rc} out={out!r} err={err!r} text={text!r}',
               rc == 0 and status(root) == 'done' and len(fresh(root, {'alpha', 'beta'})) == 1
               and out.endswith('; warnings acknowledged: committed later')
               and text.rstrip().endswith(f'## Closed\n\n{today}: warnings acknowledged: committed later\n\n'
                                          f'> step-2 verifier fail')
               and run(root, 'check')[0] == 0)
        # (w2) a multi-line Warnings section is quoted line by line, verbatim after `> `
        root = case(filer('filer-L1.md', '- step-2 verifier fail\n- nothing committed yet', '- Add retry to fetch'))
        rc, out, err = run(root, 'close', ('alpha',), ack_warnings='fixed on main')
        text = (root / 'alpha' / 'handoff.md').read_text(encoding='utf-8')
        expect(f'(w2) multi-line warnings quoted line by line: rc={rc} {err!r} text={text!r}',
               rc == 0 and text.rstrip().endswith(f'{today}: warnings acknowledged: fixed on main\n\n'
                                                  f'> - step-2 verifier fail\n> - nothing committed yet'))
        # (w3) --ack-warnings with --force, (w4) with --reason, (w5) empty or whitespace: refuse, write nothing
        for label, args, kw, want in (('w3', ('alpha', True), {'ack_warnings': 'x'}, '--force'),
                                      ('w4', ('alpha',), {'ack_warnings': 'x', 'reason': 'y'}, '--reason'),
                                      ('w5', ('alpha',), {'ack_warnings': ''}, 'empty --ack-warnings'),
                                      ('w5', ('alpha',), {'ack_warnings': '   '}, 'empty --ack-warnings')):
            root = case(warned)
            before = snap(root)
            rc, _, err = run(root, 'close', args, **kw)
            expect(f'({label}) --ack-warnings {args} {kw} refuses and writes nothing: rc={rc} {err!r}',
                   rc == 1 and '--ack-warnings' in err and want in err and err.endswith('nothing written')
                   and snap(root) == before and status(root) == 'proposed')
        # (w6) with Warnings None there is nothing to acknowledge: refuses, plain and dry run
        for kw in ({}, {'dry_run': True}):
            root = case(filer('filer-L1.md', 'None', '- Add retry to fetch'))
            before = snap(root)
            rc, _, err = run(root, 'close', ('alpha',), ack_warnings='x', **kw)
            expect(f'(w6) --ack-warnings with no open warnings refuses {kw}: rc={rc} {err!r}',
                   rc == 1 and 'rerun without --ack-warnings' in err and snap(root) == before)
        # (w7) dry run with --ack-warnings on open warnings lists the plan, ends with expect, writes nothing
        root = case(warned)
        before = snap(root)
        rc, out, err = run(root, 'close', ('alpha',), ack_warnings='committed later', dry_run=True)
        lines = out.splitlines()
        expect(f'(w7) --ack-warnings dry run: rc={rc} out={out!r} err={err!r}',
               rc == 0 and lines[-1] == 'expect ' + follow_digest(['Add retry to fetch'])
               and 'ack warnings: committed later' in lines and snap(root) == before)
        # (w8) --ack-warnings with --skip/--expect files only the unskipped follow-ups
        root = case(filer('filer-L1.md', 'step-2 verifier fail', three))
        rc, out, _ = run(root, 'close', ('alpha',), ack_warnings='ok', dry_run=True)
        token = out.splitlines()[-1].split(' ', 1)[1] if rc == 0 else ''
        rc, out, err = run(root, 'close', ('alpha',), ack_warnings='ok', skip=[2], expect=token)
        made = fresh(root, {'alpha', 'beta'})
        expect(f'(w8) --ack-warnings --skip 2 files 1 and 3: rc={rc} out={out!r} err={err!r} made={sorted(made)}',
               rc == 0 and status(root) == 'done'
               and sorted(m.get('title') for m in made.values()) == ['Add retry to fetch', 'Split the runner']
               and 'skipped by --skip: 2' in out and 'warnings acknowledged: ok' in out)
        # (w9) numbered: an ack close renames 0003-x to .0003-x and the moved handoff holds ## Closed
        root = case(both(numbered_x, filer('filer-L1.md', 'step-2 verifier fail', '- Add retry to fetch',
                                           slug='0003-x')))
        rc, out, err = run(root, 'close', ('0003-x',), numbered=True, ack_warnings='committed later')
        text = (root / '.0003-x' / 'handoff.md').read_text(encoding='utf-8') if (root / '.0003-x').is_dir() else ''
        expect(f'(w9) numbered ack close renames and keeps ## Closed: rc={rc} out={out!r} err={err!r} '
               f'tree={tree(root)}',
               rc == 0 and '; moved to .0003-x' in out and not (root / '0003-x').exists()
               and status(root, '.0003-x') == 'done' and '## Closed' in text
               and 'warnings acknowledged: committed later' in text and '> step-2 verifier fail' in text
               and run(root, 'check')[0] == 0)

        # archive: done and dropped NNNN- folders move to .NNNN-, a ready one stays
        def arch_base(root):
            for slug, st in (('alpha', 'done'), ('beta', 'dropped')):
                edit(root, slug, r'^status:.*$', f'status: {st}')
            (root / 'alpha').rename(root / '0001-alpha')
            (root / 'beta').rename(root / '0002-beta')
            run(root, 'new', ('feature', 'gamma'), numbered=True)
            run(root, 'roadmap')
        root = case(arch_base)
        before = snap(root)
        rc, out, err = run(root, 'archive', dry_run=True)
        expect(f'archive dry run lists renames and writes nothing: rc={rc} {out!r} {err!r}',
               rc == 0 and out.splitlines() == ['0001-alpha -> .0001-alpha', '0002-beta -> .0002-beta']
               and snap(root) == before)
        rc, out, err = run(root, 'archive')
        expect(f'archive moves done and dropped, keeps ready: rc={rc} {out!r} {err!r} tree={tree(root)}',
               rc == 0 and 'archived 2 folder(s)' in out and (root / '.0001-alpha').is_dir()
               and (root / '.0002-beta').is_dir() and (root / '0003-gamma').is_dir()
               and not (root / '0001-alpha').exists() and not (root / '0002-beta').exists())
        rc, out, err = run(root, 'check')
        expect(f'check passes after archive: rc={rc} {out!r} {err!r}', rc == 0)
        rc, out, err = run(root, 'archive')
        expect(f'second archive reports nothing to archive: rc={rc} {out!r}', rc == 0 and out == 'nothing to archive')
        root = case(both(arch_base, lambda r: (r / '.0002-beta').mkdir()))
        before = snap(root)
        rc, out, err = run(root, 'archive')
        expect(f'archive collision refuses and writes nothing: rc={rc} {err!r}',
               rc == 1 and '.0002-beta' in err and snap(root) == before and (root / '0001-alpha').is_dir())
        root = case(lambda r: edit(r, 'alpha', r'^status:.*$', 'status: done'))
        run(root, 'roadmap')
        before = snap(root)
        rc, out, err = run(root, 'archive')
        expect(f'archive in plain mode refuses and writes nothing: rc={rc} {err!r}',
               rc == 1 and 'numbered mode' in err and snap(root) == before and (root / 'alpha').is_dir())

        # ---- worktrees: new and close stamp ids above the max across every git worktree's same-relative root ----
        if shutil.which('git') is None:
            print('tickets selftest: git not found; skipping the worktree id cases')
        else:
            genv = {k: v for k, v in os.environ.items() if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE')}

            def git(cwd, *args):
                p = subprocess.run(['git', '-C', str(cwd), *args], env=genv, capture_output=True, text=True)
                if p.returncode:
                    raise AssertionError(f'selftest git fixture failed: git {" ".join(args)}: {p.stderr.strip()}')

            def tid(root, slug):
                return dict(load(root)).get(slug, {}).get('id')

            wtmp = pathlib.Path(tmp) / 'worktrees'
            wtmp.mkdir()
            main_dir, nosdlc_dir = wtmp / 'main', wtmp / 'nosdlc'
            m_root, w_root, n_root = main_dir / '.sdlc', wtmp / 'wt' / '.sdlc', nosdlc_dir / '.sdlc'
            git(wtmp, 'init', '-q', 'main')
            rc, _, err = run(m_root, 'new', ('feature', 'alpha'))
            expect(f'worktree: first id in a fresh repo is T-0001: rc={rc} {err!r}', rc == 0 and tid(m_root, 'alpha')
                   == 'T-0001')
            git(main_dir, 'add', '-A')
            git(main_dir, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                'commit', '--no-verify', '-qam', 'alpha')
            git(main_dir, 'worktree', 'add', '-q', '../wt', '-b', 'wt')
            git(main_dir, 'worktree', 'add', '-q', '../nosdlc', '-b', 'nosdlc')
            shutil.rmtree(n_root)  # a worktree with no .sdlc dir yet: skipped, never an error
            rc_b, _, err_b = run(m_root, 'new', ('feature', 'beta'))
            rc_g, _, err_g = run(w_root, 'new', ('feature', 'gamma'))
            expect(f'worktree: beta in main is T-0002, then gamma in wt is T-0003 (not T-0002): rc={rc_b},{rc_g} '
                   f'{err_b!r} {err_g!r} beta={tid(m_root, "beta")!r} gamma={tid(w_root, "gamma")!r}',
                   rc_b == 0 and rc_g == 0 and err_b == err_g == '' and tid(m_root, 'beta') == 'T-0002'
                   and tid(w_root, 'gamma') == 'T-0003')
            # plain close in wt: main's delta (T-0004) sits above wt's max (T-0003), so the follow-up is T-0005
            rc, _, err = run(m_root, 'new', ('feature', 'delta'))
            expect(f'worktree: delta in main counts wt gamma, so it is T-0004: rc={rc} {err!r} '
                   f'got={tid(m_root, "delta")!r}', rc == 0 and tid(m_root, 'delta') == 'T-0004')
            filer('filer-L1.md', 'None', '- Add retry to fetch', slug='gamma')(w_root)
            rc, out, err = run(w_root, 'close', ('gamma',))
            made = fresh(w_root, {'alpha', 'gamma'})
            expect(f'worktree: plain close in wt stamps its follow-up above main T-0004, as T-0005: rc={rc} {out!r} '
                   f'{err!r} made={made}',
                   rc == 0 and [m.get('id') for m in made.values()] == ['T-0005'] and run(w_root, 'check')[0] == 0)
            # numbered close in wt: main's epsilon (T-0006) sits above wt's max (T-0005); folder 0007- matches T-0007
            rc, _, err = run(m_root, 'new', ('feature', 'epsilon'))
            expect(f'worktree: epsilon in main is T-0006: rc={rc} {err!r} got={tid(m_root, "epsilon")!r}',
                   rc == 0 and tid(m_root, 'epsilon') == 'T-0006')
            filer('filer-L1.md', 'None', '- Quote the docs', slug='alpha')(w_root)
            rc, out, err = run(w_root, 'close', ('alpha',), numbered=True)
            made = fresh(w_root, {'alpha', 'gamma', 'add-retry-to-fetch'})
            expect(f'worktree: numbered close in wt names the follow-up 0007-quote-the-docs with id T-0007: rc={rc} '
                   f'{out!r} {err!r} made={made}',
                   rc == 0 and {s: m.get('id') for s, m in made.items()} == {'0007-quote-the-docs': 'T-0007'}
                   and run(w_root, 'check')[0] == 0)
            # the worktree with no .sdlc yet: new there creates the root and still counts every other tree
            rc, _, err = run(n_root, 'new', ('feature', 'zeta'))
            expect(f'worktree: first ticket in a worktree with no .sdlc yet is T-0008: rc={rc} {err!r} '
                   f'got={tid(n_root, "zeta")!r}', rc == 0 and err == '' and tid(n_root, 'zeta') == 'T-0008')
            # close in main with the filer record only in wt (alpha, filed there above): refuse, name wt's folder
            before = snap(m_root)
            rc, _, err = run(m_root, 'close', ('alpha',))
            expect(f'worktree: close in main names the wt folder holding the filer record, writes nothing: rc={rc} '
                   f'{err!r}', rc == 1 and snap(m_root) == before and str((w_root / 'alpha').resolve()) in err
                   and '/file' in err and 'nothing written' in err)

        # outside git (no worktrees to consult) the local root decides: the first id is T-0001
        solo = pathlib.Path(tmp) / 'solo' / '.sdlc'
        rc, _, err = run(solo, 'new', ('feature', 'solo'))
        expect(f'outside git the first id is T-0001, no stderr: rc={rc} {err!r} got={dict(load(solo)).get("solo")}',
               rc == 0 and err == '' and dict(load(solo)).get('solo', {}).get('id') == 'T-0001')

        empty = pathlib.Path(tmp) / 'empty' / '.sdlc'
        rc, out, _ = run(empty, 'check')
        expect('zero tickets and no roadmap passes', rc == 0 and out.startswith('ok: 0 tickets'))

    if misses:
        print('tickets selftest: FAIL, these did not bite:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('tickets selftest: PASS')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog='tickets.py', description=__doc__.split('\n')[0])
    ap.add_argument('--root', default='.sdlc', help='dir holding ticket dirs (default: .sdlc in the cwd)')
    sub = ap.add_subparsers(dest='cmd')
    p = sub.add_parser('new', help='stamp a typed ticket with the next id')
    p.add_argument('type')
    p.add_argument('slug')
    p.add_argument('title', nargs='?', default='')
    p.add_argument('--numbered', action='store_true',
                   help='name the folder NNNN-<slug> after the new id and persist '
                        '`ticket_folders: numbered` in <root>/config (also on via that config)')
    p = sub.add_parser('close', help='after /file: file follow-ups as tickets (skipping duplicates of existing '
                                     'tickets), set the ticket done; --dry-run lists them first; '
                                     'or --reason TEXT: set it done without a filer file; '
                                     '--ack-warnings TEXT: close while filer warnings are open, with a reason')
    p.add_argument('slug')
    p.add_argument('--force', action='store_true', help='close even while the filer warnings are open')
    p.add_argument('--reason', metavar='TEXT',
                   help='close without a filer file (work done elsewhere): set done, append a ## Closed '
                        'section with the date and TEXT, file no follow-ups (refuses with --dry-run, --skip or --expect)')
    p.add_argument('--ack-warnings', metavar='TEXT',
                   help='close while the filer warnings are open: record TEXT and the quoted warnings in a '
                        '## Closed section, file follow-ups as normal (refuses with --force, with --reason, '
                        'with empty TEXT, or when no warnings are open)')
    p.add_argument('--dry-run', action='store_true',
                   help='apply the same refusals, then list each follow-up as <i>. <title> [<slug>] with any '
                        'duplicate or --skip mark, then one `open T-NNNN <title> [<slug>]` line per other proposed, '
                        'ready or blocked ticket, then a last line `expect <digest>`; write nothing')
    p.add_argument('--skip', metavar='N[,N...]',
                   help='file every follow-up except these 1-based indices from the --dry-run listing; '
                        'an index out of range refuses and writes nothing; needs --expect')
    p.add_argument('--expect', metavar='DIGEST',
                   help='the digest from the --dry-run last line (expect <digest>); required with --skip; '
                        'close refuses, writing nothing, when the Follow-ups list changed since that dry run')
    p.add_argument('--numbered', action='store_true',
                   help='name each follow-up folder NNNN-<slug> after its own new id and, on success, persist '
                        '`ticket_folders: numbered` in <root>/config (also on via that config)')
    p = sub.add_parser('roadmap', help='regenerate roadmap.md')
    p.add_argument('--numbered', action='store_true',
                   help='also refuse on a NNNN-<slug> folder whose id is not T-NNNN (also on via <root>/config)')
    p = sub.add_parser('check', help='validate tickets and roadmap freshness')
    p.add_argument('--numbered', action='store_true',
                   help='also fail a NNNN-<slug> folder whose id is not T-NNNN (also on via <root>/config)')
    p = sub.add_parser('archive', help='numbered mode: rename done and dropped NNNN-<slug> folders to .NNNN-<slug>')
    p.add_argument('--dry-run', action='store_true', help='print each <name> -> .<name> rename; write nothing')
    p.add_argument('--numbered', action='store_true',
                   help='turn numbered mode on and, on success, persist it in <root>/config '
                        '(also on via that config)')
    sub.add_parser('selftest', help='prove every check failure fires')
    a = ap.parse_args(argv)
    cmd = a.cmd or 'check'
    if cmd == 'selftest':
        return selftest()
    args = {'new': lambda: (a.type, a.slug, a.title), 'close': lambda: (a.slug, a.force)}.get(cmd, tuple)()
    kw = {'numbered': getattr(a, 'numbered', False)} if cmd in ('new', 'close', 'roadmap', 'check', 'archive') else {}
    if cmd == 'archive':
        kw['dry_run'] = a.dry_run
    if cmd == 'close':
        kw['reason'] = a.reason
        kw['ack_warnings'] = a.ack_warnings
        kw['dry_run'] = a.dry_run
        kw['expect'] = a.expect
        try:
            kw['skip'] = None if a.skip is None else parse_skip(a.skip)
        except Fail as e:
            print(e, file=sys.stderr)
            return 1
    rc, out, err = run(pathlib.Path(a.root), cmd, args, **kw)
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
