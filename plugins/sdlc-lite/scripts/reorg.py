#!/usr/bin/env python3
"""reorg.py: apply an approved reorganization plan (moves and link fixes) in batches, one commit per batch.

Usage:
  reorg.py apply PLAN [--root DIR] [--dry-run] [--approve DIGEST]
  reorg.py selftest

Design: docs/repo-onboarding/reorganization.md and reorganization-plan-procedure.md. Standard library only, runs on
Python 3.9, no model call, no network. `--root` defaults to the Git top level of the current directory. Exit 0 on
success or a clean dry run, 1 on a refusal or a failed final check, 2 on a usage error.

Plan: a JSON file at any path, kept outside the repository:
  {"version": 1, "batches": [{"name": str, "moves": [{"from": path, "to": path}],
                              "links": [{"file": path, "old": target, "new": target}]}]}
Paths are repo-relative; `links` is optional; a batch needs at least one move or one link fix. A wrong version, an
unknown key, an empty name, or a wrong type is refused. A link fix retargets every link in `file` whose target text
equals `old`, in the file as the earlier batches left it; the fix claims that span first and writes `new` as given.

Approval: --dry-run runs every refusal except the approval, computes every batch on the in-memory tree, prints the
listing and the digest, and writes nothing. It never runs the final check, which needs the real tree. Apply without
--dry-run recomputes the same listing and digest before any write and needs --approve equal to that digest.
Digest: SHA-256 hex of the sorted lines `path <p>` for every tracked file outside .sdlc/, `file <p> <sha256>` for
every tracked non-frozen file outside .sdlc/ (always docs/layout.md), and `plan <json, sorted keys, compact>`, so an
edited document or plan refuses and a change under .sdlc/ does not.

Stdout, the same listing for dry run and apply: `batch <n>: <name>`, `move <from> -> <to>`,
`fix <file>:<line> <old> -> <new>`, `rewrite <file>:<line> <old> -> <new>` (file, line, and old text as that batch
found them, anchor and query kept; a rewrite that changes nothing prints nothing), then `baseline <file>: <target>`
per link already broken before the first batch, and last `digest <hex>`. Apply then prints `commit <sha> <name>` per
batch and `final check: pass`. Stderr: `reorg.py: refused: <reason>` per refusal; a failed check prints
`reorg.py: final check failed: <file>: <target>` lines, then `reorg.py: restored to <sha>`.

Frozen: under .sdlc/, ignored by Git, or matched (the path or a parent folder) by a `## Frozen paths` pattern of
docs/layout.md, read with onboard.parse_layout and matched with onboard.frozen_match. A missing or unparsable
docs/layout.md refuses: run onboard.py setup --init first.

Refusals, all before any write and also in the dry run: a malformed plan; docs/layout.md missing or unparsable; a move
source that is not a tracked file, is frozen, or is AGENTS.md, CLAUDE.md, README.md, or docs/layout.md; a destination
that is frozen, under .sdlc/, exists, sits under a file, or equals another destination, a tracked path, or an
untracked path after case folding; a path moved twice; a link fix whose file is frozen, is not tracked Markdown, moves
in the same batch, or has no link whose target text equals `old`; a citation the script cannot rewrite; a staged
change; uncommitted changes to a file a move or rewrite touches (other uncommitted changes never refuse); a held
.run.lock under the root (outside .git and nested work trees); outside the dry run, a missing or different --approve.

Citations. The link forms come from inventory.py (INLINE_LINK, REF_DEF, HTML_ATTR, MENTION, EXTERNAL, strip_fences,
norm_target, join_rel) and are never redefined here, so inventory and apply share one definition of a link. Markdown
is .md, .mdx, .markdown. Batches run in order on an in-memory tree: batch k reads every file as batches 1 to k-1 left
it. For batch k with move map M, every tracked non-frozen UTF-8 file C lands at C' = M.get(C, C). Per line, first
rule wins, and a span one rule claimed is not examined by a later rule:
  1. Markdown outside fenced code: link targets, external and anchor-only targets skipped. The target resolves to P
     from C's folder (from the root for a leading `/`), existing or not. When P or C moves, the new text is the path
     from C' 's folder to P' = M.get(P, P), the target's place after this batch; a leading `/` or `./` is kept.
  2. Markdown outside fenced code: mentions on no link span that name a tracked path, first through C's folder
     (rewritten to the relative path from C' 's folder to P' when P or C moves), else through the root (rewritten to
     P' when P moves). A bare AGENTS.md, CLAUDE.md, or README.md names a kind of file and is not a citation.
  3. Any file, anywhere, fenced code included: repo-root path tokens equal to a `from` (rename_refs.token_regex and
     in_url) become its `to`.
  Across batches every occurrence is examined again. Refused, naming file and line: a link or mention in fenced code
  of a Markdown file, or a mention in a non-Markdown file, that resolves from C's folder to a `from` and is not that
  repo-root path itself; a non-UTF-8 file that holds the bytes of a `from`. Frozen files are never edited. A target
  that resolves above the root stays.
Managed blocks: when a rewrite changes the body of an onboard managed block whose stored hash matches its body, the
start marker gets the block's version and the new body's hash, so onboard.py check does not call it edited. A block
already edited by hand keeps its hash.

Apply: record the start HEAD S. Per batch: `git mv` each move (parent folders created), write the batch's edits, run
the final check on the real tree, stage exactly the batch's paths, and commit `reorg: <name>` with a body of
`move <from> -> <to>` lines and `plan digest <hex>`. Final check: every link in every tracked non-frozen Markdown file
resolves to a tracked path, a folder holding tracked paths, or an existing path, unless it was broken before the first
batch (keyed by its file at the start and its resolved target, or its raw text above the root); no tracked
non-frozen file holds a repo-root token of a moved `from`; every tracked frozen file outside .sdlc/ is unchanged.
Restore, on any failure after the first write: HEAD returns to S, every touched path gets its S content and index
entry, folders the apply created and left empty are removed, other files (unrelated changes, untracked files) stay
byte-identical; exit 1.

selftest: fixture repositories in temp dirs, one gate per rule, `ok <gate> positive` and `ok <gate> negative`, then
`reorg selftest: PASS` or `FAIL`. Negative controls are in-process Impl variants passed to the gate functions; no flag
or environment variable disables a gate.
"""
import argparse
import collections
import contextlib
import fcntl
import hashlib
import io
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import onboard  # noqa: E402
import rename_refs  # noqa: E402
import inventory  # noqa: E402

MARKDOWN = ('.md', '.mdx', '.markdown')
ENTRY_NAMES = ('AGENTS.md', 'CLAUDE.md', 'README.md')
LAYOUT = 'docs/layout.md'
SETUP_FIRST = 'run onboard.py setup --init first'
LOCK_NAME = '.run.lock'
SPLIT_KEEP = re.compile(r'[^\n]*\n|[^\n]+\Z')
REFUSED = 'reorg.py: refused: '

# The parts the selftest swaps for defective variants. after: rewrite to the target's place after the batch.
# reexamine: examine occurrences an earlier batch rewrote. drop: rewrites to skip. refresh: refresh managed-block
# hashes. per_batch: one commit per batch. dry_writes: the dry run writes (defect only).
Impl = collections.namedtuple('Impl', 'after reexamine drop refresh per_batch dry_writes')
REAL = Impl(after=True, reexamine=True, drop=0, refresh=True, per_batch=True, dry_writes=False)

Batch = collections.namedtuple('Batch', 'number name moves writes fixes rewrites')


class Refused(Exception):
    def __init__(self, reasons):
        super().__init__('; '.join(reasons))
        self.reasons = list(reasons)


class GitError(Exception):
    pass


class CheckFailed(Exception):
    pass


# ---------------------------------------------------------------- helpers

def git(root, *args, data=None, check=True):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_LITERAL_PATHSPECS='1')
    r = subprocess.run(('git', '-C', root, '-c', 'core.quotepath=off') + args, input=data,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if check and r.returncode:
        raise GitError('git %s failed: %s' % (args[0], r.stderr.decode('utf-8', 'replace').strip()))
    return r


def zsplit(data):
    return [p.decode('utf-8', 'surrogateescape') for p in data.split(b'\0') if p]


def full(root, path):
    return os.path.join(root, *path.split('/'))


def is_md(path):
    return path.lower().endswith(MARKDOWN)


def under_sdlc(path):
    return path == '.sdlc' or path.startswith('.sdlc/')


def layout_frozen(patterns, path):
    parts = path.split('/')
    return any(onboard.frozen_match(p, '/'.join(parts[:i])) for p in patterns for i in range(1, len(parts) + 1))


def sha(data):
    return hashlib.sha256(data).hexdigest() if data is not None else 'missing'


def read_file(root, path):
    """(bytes or None, UTF-8 text or None, is a symbolic link)."""
    f = full(root, path)
    if os.path.islink(f):
        return os.readlink(f).encode('utf-8', 'surrogateescape'), None, True
    try:
        with open(f, 'rb') as fh:
            data = fh.read()
    except OSError:
        return None, None, False
    text = None
    if b'\0' not in data:
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = None
    return data, text, False


def overlaps(spans, s, e):
    return any(s < b and a < e for a, b in spans)


def link_spans(line):
    """(start, end, target start, target end, target) for each link form in one line, in rule order."""
    out = []
    for rx in (inventory.INLINE_LINK, inventory.REF_DEF, inventory.HTML_ATTR):
        for mm in rx.finditer(line):
            out.append((mm.start(), mm.end(), mm.start(1), mm.end(1), mm.group(1)))
    return out


def skipped(raw):
    return not raw or raw.startswith('#') or inventory.EXTERNAL.match(raw)


def toplevel(path):
    try:
        r = subprocess.run(['git', '-C', path, 'rev-parse', '--show-toplevel'],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
        raise Refused(['git is not available: %s' % e])
    top = r.stdout.decode('utf-8', 'surrogateescape').rstrip('\n')
    if r.returncode or not top:
        raise Refused(['%s is not inside a Git work tree' % path])
    return top


# ---------------------------------------------------------------- plan

def _path_ok(p):
    return (isinstance(p, str) and p not in ('', '.', '..') and not p.startswith('/') and '\\' not in p
            and posixpath.normpath(p) == p and p.split('/')[0] != '..')


def validate_plan(plan):
    if not isinstance(plan, dict):
        return ['the plan is not a JSON object']
    errs = []
    unknown = sorted(set(plan) - {'version', 'batches'})
    if unknown:
        errs.append('unknown key %s' % ', '.join(unknown))
    if type(plan.get('version')) is not int or plan.get('version') != 1:
        errs.append('version must be 1')
    batches = plan.get('batches')
    if not isinstance(batches, list) or not batches:
        return errs + ['batches must be a non-empty list']
    for n, b in enumerate(batches, 1):
        where = 'batch %d' % n
        if not isinstance(b, dict):
            errs.append('%s is not an object' % where)
            continue
        unknown = sorted(set(b) - {'name', 'moves', 'links'})
        if unknown:
            errs.append('%s has unknown key %s' % (where, ', '.join(unknown)))
        name = b.get('name')
        if not isinstance(name, str) or not name.strip() or '\n' in name:
            errs.append('%s has an empty or multi-line name' % where)
        moves, links = b.get('moves'), b.get('links', [])
        if not isinstance(moves, list):
            errs.append('%s: moves must be a list' % where)
            moves = []
        if not isinstance(links, list):
            errs.append('%s: links must be a list' % where)
            links = []
        if not moves and not links:
            errs.append('%s needs at least one move or one link fix' % where)
        for mv in moves:
            if not isinstance(mv, dict) or set(mv) != {'from', 'to'}:
                errs.append('%s: a move must be an object with exactly from and to' % where)
            elif not (_path_ok(mv['from']) and _path_ok(mv['to'])):
                errs.append('%s: move %r -> %r is not a pair of repo-relative paths' % (where, mv['from'], mv['to']))
        for lf in links:
            if not isinstance(lf, dict) or set(lf) != {'file', 'old', 'new'}:
                errs.append('%s: a link fix must be an object with exactly file, old, and new' % where)
            elif not _path_ok(lf['file']):
                errs.append('%s: link fix file %r is not a repo-relative path' % (where, lf['file']))
            elif not all(isinstance(lf[k], str) and lf[k] and not any(c.isspace() for c in lf[k])
                         for k in ('old', 'new')):
                errs.append('%s: link fix old and new must be non-empty targets without spaces' % where)
            elif lf['old'] == lf['new']:
                errs.append('%s: link fix in %s has old equal to new' % (where, lf['file']))
    return errs


def load_plan(path):
    try:
        with open(path, encoding='utf-8') as f:
            plan = json.load(f)
    except (OSError, UnicodeDecodeError) as e:
        raise Refused(['cannot read the plan %s: %s' % (path, e)])
    except ValueError as e:
        raise Refused(['malformed plan: not JSON (%s)' % e])
    errs = validate_plan(plan)
    if errs:
        raise Refused(['malformed plan: %s' % e for e in errs])
    return plan


# ---------------------------------------------------------------- repository state

class Repo(object):
    """The repository as apply found it: tracked paths, frozen set, file bytes and texts, dirty and staged paths."""


def is_frozen(repo, path):
    return under_sdlc(path) or path in repo.ignored or layout_frozen(repo.layout.frozen, path)


def gather(root):
    repo = Repo()
    repo.root = root
    r = git(root, 'rev-parse', '--verify', '-q', 'HEAD^{commit}', check=False)
    if r.returncode:
        raise Refused(['the repository has no commit to start from'])
    repo.head = r.stdout.decode().strip()
    path = full(root, LAYOUT)
    if not os.path.isfile(path):
        raise Refused(['%s is missing; %s' % (LAYOUT, SETUP_FIRST)])
    try:
        repo.layout = onboard.parse_layout(path)
    except onboard.LayoutError as e:
        raise Refused(['%s:%d does not parse (%s); %s' % (LAYOUT, e.line, e.reason, SETUP_FIRST)])
    except (UnicodeDecodeError, OSError) as e:
        raise Refused(['%s cannot be read (%s); %s' % (LAYOUT, e, SETUP_FIRST)])
    repo.tracked = sorted(set(zsplit(git(root, 'ls-files', '-z').stdout)))
    repo.tracked_set = set(repo.tracked)
    repo.ignored = set(zsplit(git(root, 'ls-files', '-z', '-ci', '--exclude-standard').stdout))
    repo.untracked = zsplit(git(root, 'ls-files', '-z', '--others', '--exclude-standard').stdout)
    repo.dirty = set(zsplit(git(root, 'diff', '--name-only', '-z', '--no-renames', 'HEAD', '--').stdout))
    repo.staged = zsplit(git(root, 'diff', '--cached', '--name-only', '-z', '--no-renames', 'HEAD', '--').stdout)
    repo.frozen = set(p for p in repo.tracked if is_frozen(repo, p))
    repo.raw, repo.text, repo.binary = {}, {}, {}
    for p in repo.tracked:
        if under_sdlc(p):
            continue
        data, text, link = read_file(root, p)
        repo.raw[p] = data
        if p in repo.frozen or link or data is None:
            continue
        if text is None:
            repo.binary[p] = data
        else:
            repo.text[p] = text
    if LAYOUT not in repo.raw:
        repo.raw[LAYOUT] = read_file(root, LAYOUT)[0]
    repo.frozen_hash = dict((p, sha(repo.raw.get(p))) for p in repo.frozen if not under_sdlc(p))
    return repo


def ignored_paths(root, paths):
    if not paths:
        return set()
    data = b''.join(p.encode('utf-8', 'surrogateescape') + b'\0' for p in paths)
    return set(zsplit(git(root, 'check-ignore', '--no-index', '-z', '--stdin', data=data, check=False).stdout))


def check_moves(repo, plan):
    root, frozen_pats = repo.root, repo.layout.frozen
    moves = [(mv['from'], mv['to']) for b in plan['batches'] for mv in b['moves']]
    ign = ignored_paths(root, sorted(set([f for f, _ in moves if f not in repo.tracked_set] + [t for _, t in moves])))
    tracked_fold, untracked_fold = {}, {}
    for p in repo.tracked:
        tracked_fold.setdefault(p.casefold(), p)
    for p in repo.untracked:
        untracked_fold.setdefault(p.casefold(), p)
    seen, dest, errs = set(), {}, []
    for f, t in moves:
        if f in seen:
            errs.append('%s is moved twice' % f)
        seen.add(f)
        if f in repo.frozen or under_sdlc(f) or f in ign or layout_frozen(frozen_pats, f):
            errs.append('move source %s is frozen' % f)
        elif f not in repo.tracked_set:
            errs.append('move source %s is not a tracked file' % f)
        if posixpath.basename(f) in ENTRY_NAMES or f == LAYOUT:
            errs.append('move source %s is an entry file, and entry files never move' % f)
        if under_sdlc(t) or t in ign or layout_frozen(frozen_pats, t):
            errs.append('move destination %s is frozen' % t)
        if os.path.lexists(full(root, t)):
            errs.append('move destination %s exists' % t)
        k = t.casefold()
        if k in dest:
            errs.append('move destination %s is also the destination of another move (%s)' % (t, dest[k]))
        dest.setdefault(k, t)
        if k in tracked_fold:
            errs.append('move destination %s matches the tracked path %s' % (t, tracked_fold[k]))
        if k in untracked_fold:
            errs.append('move destination %s matches the untracked path %s' % (t, untracked_fold[k]))
        parts = t.split('/')
        for i in range(1, len(parts)):
            q = '/'.join(parts[:i])
            fq = full(root, q)
            if q in repo.tracked_set or (os.path.lexists(fq) and not os.path.isdir(fq)):
                errs.append('move destination %s sits under the file %s' % (t, q))
                break
    return errs


def held_locks(root):
    """Every .run.lock under root that another process holds; .git and nested work trees are skipped."""
    held = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != '.git' and not os.path.lexists(os.path.join(folder, d, '.git')))
        if LOCK_NAME not in files:
            continue
        path = os.path.join(folder, LOCK_NAME)
        try:
            fd = os.open(path, os.O_RDONLY)
        except OSError:
            continue
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                held.append(os.path.relpath(path, root).replace(os.sep, '/'))
                continue
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
    return held


def plan_digest(repo, plan):
    lines = set()
    for p in repo.tracked:
        if under_sdlc(p):
            continue
        lines.add('path %s' % p)
        if p not in repo.frozen:
            lines.add('file %s %s' % (p, sha(repo.raw.get(p))))
    lines.add('file %s %s' % (LAYOUT, sha(repo.raw.get(LAYOUT))))
    lines.add('plan %s' % json.dumps(plan, sort_keys=True, separators=(',', ':')))
    return hashlib.sha256('\n'.join(sorted(lines)).encode('utf-8', 'surrogateescape')).hexdigest()


# ---------------------------------------------------------------- rewriting

def link_target(raw, c, base, base2, m, impl):
    """The rewritten link target, or None when the link stays."""
    if skipped(raw):
        return None
    t = inventory.norm_target(raw)
    if not t:
        return None
    p = inventory.join_rel(base, t)
    if p is None or (p not in m and c not in m):
        return None
    p2 = m.get(p, p) if impl.after else p
    suffix = raw[len(re.split(r'[#?]', raw, 1)[0]):]
    if t.startswith('/'):
        new = '/' + p2
    else:
        new = posixpath.relpath(p2, base2 or '.')
        if t.startswith('./') and not (new == '..' or new.startswith('../')):
            new = './' + new
    if t.endswith('/') and not new.endswith('/'):
        new += '/'
    return new + suffix


def resolve_mention(t, base, tracked):
    """(path, found through the citing folder) for a mention that names a tracked path, else None."""
    a = inventory.join_rel(base, t)
    if a is not None and a in tracked:
        return a, True
    b = inventory.join_rel('', t)
    if b is not None and b in tracked:
        return b, False
    return None


def mention_target(t, p, relative, c, base2, m, impl):
    p2 = m.get(p, p) if impl.after else p
    if relative:
        if p not in m and c not in m:
            return None
        new = posixpath.relpath(p2, base2 or '.')
        if t.startswith('./') and not (new == '..' or new.startswith('../')):
            new = './' + new
        return new
    return p2 if p in m else None


def unrewritable(raw, base, m):
    """The moved path a fenced or non-Markdown citation names through the citing folder, else None."""
    if skipped(raw):
        return None
    t = inventory.norm_target(raw)
    if not t:
        return None
    p = inventory.join_rel(base, t)
    if p in m and t not in (p, '/' + p):
        return p
    return None


def rewrite_file(c, text, m, tracked, fixes, matched, impl, done, budget):
    """One file through one batch: (new text, events, refusals, rewritten positions)."""
    c2 = m.get(c, c)
    base, base2 = posixpath.dirname(c), posixpath.dirname(c2)
    md = is_md(c)
    lines = text.split('\n')
    plain = inventory.strip_fences(text).split('\n') if md else lines
    tokens = [(f, rename_refs.token_regex(f)) for f in sorted(m)]
    out, events, refusals, new_done = [], [], [], set()
    for i, line in enumerate(lines):
        claimed, reps = [], []
        if md and plain[i] == line:
            for s, e, gs, ge, raw in link_spans(line):
                if overlaps(claimed, s, e):
                    continue
                claimed.append((s, e))
                if raw in fixes:
                    matched.add((c, raw))
                    reps.append((gs, ge, fixes[raw], 'fix', raw))
                    continue
                new = link_target(raw, c, base, base2, m, impl)
                if new is not None:
                    reps.append((gs, ge, new, 'rewrite', raw))
            for mm in inventory.MENTION.finditer(line):
                s, e = mm.span(1)
                if overlaps(claimed, s, e):
                    continue
                t = mm.group(1)
                if '/' not in t and t in ENTRY_NAMES:
                    continue
                found = resolve_mention(t, base, tracked)
                if found is None:
                    continue
                claimed.append((s, e))
                new = mention_target(t, found[0], found[1], c, base2, m, impl)
                if new is not None:
                    reps.append((s, e, new, 'rewrite', t))
        elif m:
            cands = [raw for _, _, _, _, raw in link_spans(line)] if md else []
            cands += [mm.group(1) for mm in inventory.MENTION.finditer(line)]
            for raw in cands:
                p = unrewritable(raw, base, m)
                if p is not None:
                    where = 'fenced code' if md else 'a non-Markdown file'
                    refusals.append('citation %s:%d: %s in %s names %s, which moves; rewrite it by hand first'
                                    % (c, i + 1, raw, where, p))
        for f, rx in tokens:
            for mt in rx.finditer(line):
                s, e = mt.span()
                if overlaps(claimed, s, e) or rename_refs.in_url(line, s):
                    continue
                claimed.append((s, e))
                reps.append((s, e, m[f], 'rewrite', f))
        pieces, pos, length = [], 0, 0
        for s, e, new, kind, old in sorted(reps):
            if new == old:
                continue
            if not impl.reexamine and (c, i, s) in done:
                continue
            if kind == 'rewrite' and budget[0] > 0:
                budget[0] -= 1
                continue
            pieces.append(line[pos:s])
            length += s - pos
            new_done.add((c2, i, length))
            pieces.append(new)
            length += len(new)
            pos = e
            events.append((kind, i + 1, s, old, new))
        pieces.append(line[pos:])
        out.append(''.join(pieces))
    return '\n'.join(out), events, refusals, new_done


def refresh_block(before, after):
    """Refresh the start marker hash of an unedited managed block whose body a rewrite changed."""
    if before == after:
        return after
    f0 = onboard.find_block(before)
    if f0.status != 'block' or onboard.digest(f0.block.text) != f0.block.digest:
        return after
    f1 = onboard.find_block(after)
    if f1.status != 'block' or f1.block.text == f0.block.text:
        return after
    lines = SPLIT_KEEP.findall(after)
    old = lines[f1.block.start]
    lines[f1.block.start] = (onboard.START_MARKER % (f0.block.version, onboard.digest(f1.block.text))
                             + old[len(old.rstrip('\r\n')):])
    return ''.join(lines)


def compute(repo, plan, impl):
    """Every batch on the in-memory tree: (batches, refusals, start paths a move or rewrite touches)."""
    text, binary = dict(repo.text), dict(repo.binary)
    tracked = set(repo.tracked)
    origin = dict((p, p) for p in repo.tracked)
    done, budget = set(), [impl.drop]
    batches, refusals, touched = [], [], set()
    for n, b in enumerate(plan['batches'], 1):
        m = collections.OrderedDict((mv['from'], mv['to']) for mv in b['moves'])
        fixes = {}
        for lf in b.get('links', []):
            f, old, new = lf['file'], lf['old'], lf['new']
            if f in repo.frozen or under_sdlc(f):
                refusals.append('link fix file %s is frozen' % f)
            elif f not in tracked or not is_md(f) or f not in text:
                refusals.append('link fix file %s is not a tracked Markdown file' % f)
            elif f in m:
                refusals.append('link fix file %s moves in the same batch' % f)
            elif fixes.setdefault(f, {}).setdefault(old, new) != new:
                refusals.append('link fixes in %s give %s two new targets' % (f, old))
        matched = set()
        fix_ev, rew_ev, writes, new_text, new_binary, new_done = [], [], {}, {}, {}, set()
        for c in sorted(tracked):
            c2 = m.get(c, c)
            if c in binary:
                data = binary[c]
                for f in m:
                    at = data.find(f.encode('utf-8', 'surrogateescape'))
                    if at >= 0:
                        refusals.append('citation %s:%d: the file is not UTF-8 text and holds %s, which moves; '
                                        'rewrite it by hand first' % (c, data.count(b'\n', 0, at) + 1, f))
                new_binary[c2] = data
                continue
            if c not in text:
                continue
            before = text[c]
            after, evs, refs, nd = rewrite_file(c, before, m, tracked, fixes.get(c, {}), matched, impl, done, budget)
            refusals.extend(refs)
            if impl.refresh:
                after = refresh_block(before, after)
            new_text[c2] = after
            new_done |= nd
            if after != before:
                writes[c2] = after
                touched.add(origin[c])
            for kind, line, col, old, new in evs:
                (fix_ev if kind == 'fix' else rew_ev).append((c, line, col, old, new))
        for f in sorted(fixes):
            for old in sorted(fixes[f]):
                if (f, old) not in matched:
                    refusals.append('link fix in %s: no link has the target %s' % (f, old))
        for f in m:
            touched.add(origin.get(f, f))
        batches.append(Batch(n, b['name'], list(m.items()), writes, sorted(fix_ev), sorted(rew_ev)))
        text, binary, done = new_text, new_binary, new_done
        origin = dict((m.get(p, p), o) for p, o in origin.items())
        tracked = set(m.get(p, p) for p in tracked)
    return batches, refusals, touched


# ---------------------------------------------------------------- check

def broken(root, tracked, texts, frozen, origin):
    """(baseline key, file, raw target) for every link in a non-frozen Markdown text that does not resolve."""
    tracked_set, dirs = set(tracked), set()
    for p in tracked:
        d = posixpath.dirname(p)
        while d and d not in dirs:
            dirs.add(d)
            d = posixpath.dirname(d)
    out = []
    for path in sorted(texts):
        if not is_md(path) or path in frozen or under_sdlc(path):
            continue
        base = posixpath.dirname(path)
        for line in inventory.strip_fences(texts[path]).split('\n'):
            claimed = []
            for s, e, _, _, raw in link_spans(line):
                if overlaps(claimed, s, e):
                    continue
                claimed.append((s, e))
                if skipped(raw):
                    continue
                t = inventory.norm_target(raw)
                if not t:
                    continue
                p = inventory.join_rel(base, t)
                if p is None:
                    key = (origin.get(path, path), 'raw', raw)
                elif p in tracked_set or p in dirs or os.path.exists(full(root, p)):
                    continue
                else:
                    key = (origin.get(path, path), 'path', p)
                out.append((key, path, raw))
    return out


def final_check(root, repo, baseline, origin, froms):
    """(file, target) for every problem on the real tree after a batch's writes."""
    tracked = sorted(set(zsplit(git(root, 'ls-files', '-z').stdout)))
    texts = {}
    for p in tracked:
        if p in repo.frozen or under_sdlc(p):
            continue
        _, text, link = read_file(root, p)
        if text is not None and not link:
            texts[p] = text
    problems = [(path, raw) for key, path, raw in broken(root, tracked, texts, repo.frozen, origin)
                if key not in baseline]
    rxs = [(f, rename_refs.token_regex(f)) for f in froms]
    for p in sorted(texts):
        for f, rx in rxs:
            if any(not rename_refs.in_url(texts[p], mt.start()) for mt in rx.finditer(texts[p])):
                problems.append((p, f))
    for p, h in sorted(repo.frozen_hash.items()):
        if sha(read_file(root, p)[0]) != h:
            problems.append((p, 'frozen file changed'))
    return problems


# ---------------------------------------------------------------- apply

def make_parents(root, path, created):
    missing, d = [], posixpath.dirname(path)
    while d and not os.path.isdir(full(root, d)):
        missing.append(d)
        d = posixpath.dirname(d)
    for d in reversed(missing):
        os.mkdir(full(root, d))
        created.append(d)


def commit_message(b, digest):
    body = ''.join('move %s -> %s\n' % mv for mv in b.moves) + 'plan digest %s\n' % digest
    return ('reorg: %s\n\n%s' % (b.name, body)).encode('utf-8', 'surrogateescape')


def restore(root, start, touched, created, start_tracked, err):
    paths = sorted(touched)
    old = [p for p in paths if p in start_tracked]
    fails = []
    steps = [('reset', '-q', '--soft', start)]
    for i in range(0, len(paths), 200):
        steps.append(('reset', '-q', start, '--') + tuple(paths[i:i + 200]))
    for i in range(0, len(old), 200):
        steps.append(('checkout', '-q', start, '--') + tuple(old[i:i + 200]))
    for args in steps:
        r = git(root, *args, check=False)
        if r.returncode:
            fails.append('git %s: %s' % (args[0], r.stderr.decode('utf-8', 'replace').strip()))
    for p in paths:
        f = full(root, p)
        if p not in start_tracked and os.path.lexists(f) and not os.path.isdir(f):
            os.unlink(f)
    for d in sorted(set(created), key=lambda d: d.count('/'), reverse=True):
        with contextlib.suppress(OSError):
            os.rmdir(full(root, d))
    for line in fails:
        err.write('reorg.py: restore step failed: %s\n' % line)


def apply_batches(repo, batches, digest, baseline, impl, out, err):
    root, start = repo.root, repo.head
    touched, created, froms = set(), [], []
    origin = dict((p, p) for p in repo.tracked)
    try:
        for k, b in enumerate(batches):
            for f, t in b.moves:
                touched.update((f, t))
                make_parents(root, t, created)
                git(root, 'mv', '--', f, t)
            for path in sorted(b.writes):
                touched.add(path)
                with open(full(root, path), 'wb') as fh:
                    fh.write(b.writes[path].encode('utf-8', 'surrogateescape'))
            froms.extend(f for f, _ in b.moves)
            mv = dict(b.moves)
            origin = dict((mv.get(p, p), o) for p, o in origin.items())
            problems = final_check(root, repo, baseline, origin, froms)
            if problems:
                for p, t in problems:
                    err.write('reorg.py: final check failed: %s: %s\n' % (p, t))
                raise CheckFailed()
            if b.writes:
                git(root, 'add', '--', *sorted(b.writes))
            if impl.per_batch or k == len(batches) - 1:
                git(root, 'commit', '-q', '-F', '-', data=commit_message(b, digest))
                head = git(root, 'rev-parse', 'HEAD').stdout.decode().strip()
                out.write('commit %s %s\n' % (head, b.name))
    except (GitError, OSError, CheckFailed) as e:
        if not isinstance(e, CheckFailed):
            err.write('reorg.py: %s\n' % e)
        restore(root, start, touched, created, repo.tracked_set, err)
        err.write('reorg.py: restored to %s\n' % start)
        return 1
    out.write('final check: pass\n')
    return 0


def listing(batches, baseline_rows, digest):
    lines = []
    for b in batches:
        lines.append('batch %d: %s' % (b.number, b.name))
        lines += ['move %s -> %s' % mv for mv in b.moves]
        lines += ['fix %s:%d %s -> %s' % (f, ln, old, new) for f, ln, _, old, new in b.fixes]
        lines += ['rewrite %s:%d %s -> %s' % (f, ln, old, new) for f, ln, _, old, new in b.rewrites]
    lines += ['baseline %s: %s' % row for row in baseline_rows]
    lines.append('digest %s' % digest)
    return ''.join(line + '\n' for line in lines)


def run_apply(plan_path, root=None, dry_run=False, approve=None, out=None, err=None, impl=REAL):
    """apply: refusals, then the listing, then (outside the dry run) the batches. Returns the exit status."""
    out, err = out or sys.stdout, err or sys.stderr
    try:
        plan = load_plan(plan_path)
        root = toplevel(root or os.getcwd())
        repo = gather(root)
        errs = check_moves(repo, plan)
        if repo.staged:
            errs.append('staged changes in the index (%s); commit or unstage them first' % ', '.join(repo.staged[:5]))
        errs += ['%s is held by a running role; wait for it or stop it first' % p for p in held_locks(root)]
        if errs:
            raise Refused(errs)
        batches, errs, touched = compute(repo, plan, impl)
        errs += ['uncommitted changes to %s, which this plan touches; commit or revert them first' % p
                 for p in sorted(touched & repo.dirty)]
        digest = plan_digest(repo, plan)
        if not dry_run:
            if not approve:
                errs.append('no --approve; run with --dry-run, review the listing, and pass its digest')
            elif approve != digest:
                errs.append('digest mismatch: --approve %s, but the repository and plan give %s' % (approve, digest))
        if errs:
            raise Refused(errs)
        rows = broken(root, repo.tracked, repo.text, repo.frozen, dict((p, p) for p in repo.tracked))
        baseline = set(key for key, _, _ in rows)
        shown = sorted(set((path, raw) for _, path, raw in rows))
    except Refused as e:
        for reason in e.reasons:
            err.write(REFUSED + reason + '\n')
        return 1
    except GitError as e:
        err.write('reorg.py: %s\n' % e)
        return 1
    out.write(listing(batches, shown, digest))
    if dry_run:
        if impl.dry_writes and batches and batches[0].moves:
            f, t = batches[0].moves[0]
            make_parents(root, t, [])
            git(root, 'mv', '--', f, t, check=False)
        return 0
    return apply_batches(repo, batches, digest, baseline, impl, out, err)


# ---------------------------------------------------------------- selftest

class GateFailure(AssertionError):
    pass


def expect(cond, msg):
    if not cond:
        raise GateFailure(msg)


LAYOUT_EMPTY = '## Homes\n\n## Frozen paths\n'
BASE = {
    'docs/layout.md': LAYOUT_EMPTY,
    'docs/a.md': '# A\n\nSee [b](b.md).\n',
    'docs/b.md': '# B\n\nSee [a](a.md).\n',
    'docs/c.md': '# C\n',
    'tool.py': 'P = "docs/a.md"\n',
    '.sdlc/x/n.md': 'x\n',
}


def plan1(src, dst, name='one'):
    return {'version': 1, 'batches': [{'name': name, 'moves': [{'from': src, 'to': dst}]}]}


ONE = plan1('docs/a.md', 'docs/topic/a.md')
_COUNTER = [0]


def _git(root, *args):
    r = subprocess.run(('git', '-C', root) + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        raise GateFailure('fixture git %s failed: %s' % (' '.join(args), r.stderr.decode('utf-8', 'replace')))
    return r.stdout.decode('utf-8', 'surrogateescape')


def _put(root, path, content):
    f = full(root, path)
    if not os.path.isdir(os.path.dirname(f)):
        os.makedirs(os.path.dirname(f))
    with open(f, 'wb') as fh:
        fh.write(content if isinstance(content, bytes) else content.encode('utf-8'))


def _get(root, path):
    with open(full(root, path), 'rb') as fh:
        return fh.read()


def _with(base, **changes):
    files = dict(base)
    files.update(changes)
    return files


@contextlib.contextmanager
def fixture(files=None, force=()):
    """A committed Git work tree holding files; paths in force are added past .gitignore."""
    tmp = tempfile.mkdtemp(prefix='reorg-selftest-')
    root = os.path.join(tmp, 'r')
    try:
        os.mkdir(root)
        _git(root, 'init', '-q')
        for key, value in (('user.name', 'reorg selftest'), ('user.email', 'selftest@example.com'),
                           ('commit.gpgsign', 'false'), ('core.hooksPath', os.path.join(tmp, 'no-hooks'))):
            _git(root, 'config', key, value)
        for path, content in (BASE if files is None else files).items():
            _put(root, path, content)
        _git(root, 'add', '-A')
        if force:
            _git(root, 'add', '-f', '--', *force)
        _git(root, 'commit', '-q', '-m', 'init')
        yield root
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run(root, plan, dry=False, approve=None, impl=REAL):
    _COUNTER[0] += 1
    path = os.path.join(os.path.dirname(root), 'plan-%d.json' % _COUNTER[0])
    with open(path, 'w') as f:
        json.dump(plan, f)
    o, e = io.StringIO(), io.StringIO()
    rc = run_apply(path, root, dry, approve, o, e, impl)
    return rc, o.getvalue(), e.getvalue()


def digest_of(out):
    found = [line[7:] for line in out.splitlines() if re.match(r'^digest [0-9a-f]{64}$', line)]
    return found[-1] if found else None


def apply_ok(root, plan, impl=REAL):
    rc, dry, err = run(root, plan, dry=True, impl=impl)
    expect(rc == 0, 'dry run exit %d: %s' % (rc, err.strip()))
    d = digest_of(dry)
    expect(d, 'the dry run printed no digest')
    rc, out, err = run(root, plan, approve=d, impl=impl)
    expect(rc == 0, 'apply exit %d: %s' % (rc, err.strip()))
    return dry, out


def refuses(root, plan, needle, approve=None, dry=True):
    rc, _, err = run(root, plan, dry=dry, approve=approve)
    lines = [ln for ln in err.splitlines() if ln.startswith(REFUSED)]
    expect(rc == 1 and any(needle in ln for ln in lines),
           'expected a refusal naming %r; exit %d, stderr %r' % (needle, rc, err))


def head(root):
    return _git(root, 'rev-parse', 'HEAD').strip()


def subjects(root):
    return _git(root, 'log', '--format=%s').splitlines()


def snapshot(root):
    snap = {}
    for folder, dirs, names in os.walk(root):
        rel = os.path.relpath(folder, root).replace(os.sep, '/')
        if rel == '.':
            dirs[:] = [d for d in dirs if d != '.git']
        snap[rel + '/'] = None
        for name in names:
            with open(os.path.join(folder, name), 'rb') as f:
                snap[name if rel == '.' else rel + '/' + name] = f.read()
    return snap


def same_tree(before, after):
    diff = sorted(k for k in set(before) | set(after) if before.get(k, 0) != after.get(k, 0))
    expect(not diff, 'the tree changed at %s' % ', '.join(diff))


def has(out, line):
    expect(line in out.splitlines(), 'missing line %r in:\n%s' % (line, out))


def rejected(gate, impl, needle):
    """A defective variant passed to a gate must make it fail, for the reason named by needle."""
    label = ', '.join('%s=%r' % (k, v) for k, v in impl._asdict().items() if getattr(REAL, k) != v)
    try:
        gate(impl)
    except GateFailure as e:
        expect(needle in str(e), 'variant %s failed for another reason: %s' % (label, e))
        return
    raise GateFailure('variant %s was not caught' % label)


@contextlib.contextmanager
def held(path):
    """A child process holding an exclusive flock on path until the block ends."""
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    code = ('import fcntl, sys\nf = open(sys.argv[1], "a+")\nfcntl.flock(f, fcntl.LOCK_EX)\n'
            'print("held", flush=True)\nsys.stdin.read()\n')
    child = subprocess.Popen([sys.executable, '-c', code, path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        expect(child.stdout.readline().strip() == b'held', 'the lock holder did not start')
        yield
    finally:
        child.stdin.close()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
        child.stdout.close()


# digest

def gate_digest(impl):
    with fixture() as root:
        rc, dry, err = run(root, ONE, dry=True, impl=impl)
        expect(rc == 0, 'dry run exit %d: %s' % (rc, err.strip()))
        d = digest_of(dry)
        _put(root, '.sdlc/x/n.md', 'changed\n')
        _put(root, '.sdlc/x/new.md', 'new\n')
        rc, again, err = run(root, ONE, dry=True, impl=impl)
        expect(digest_of(again) == d, 'a change under .sdlc/ changed the digest')
        rc, _, err = run(root, ONE, approve=d, impl=impl)
        expect(rc == 0, 'apply exit %d: %s' % (rc, err.strip()))


def neg_digest():
    with fixture() as root:
        d = digest_of(run(root, ONE, dry=True)[1])
        _put(root, 'docs/c.md', '# C\n\nedited\n')
        refuses(root, ONE, 'digest mismatch', approve=d, dry=False)
        expect(os.path.isfile(full(root, 'docs/a.md')) and len(subjects(root)) == 1, 'a refused apply wrote')
    with fixture() as root:
        d = digest_of(run(root, ONE, dry=True)[1])
        refuses(root, plan1('docs/a.md', 'docs/topic/a.md', name='two'), 'digest mismatch', approve=d, dry=False)


# approve

def gate_approve(impl):
    with fixture() as root:
        apply_ok(root, ONE, impl)
        expect(os.path.isfile(full(root, 'docs/topic/a.md')) and len(subjects(root)) == 2, 'the apply did not land')


def neg_approve():
    with fixture() as root:
        snap, h = snapshot(root), head(root)
        refuses(root, ONE, '--approve', dry=False)
        refuses(root, ONE, 'digest mismatch', approve='0' * 64, dry=False)
        same_tree(snap, snapshot(root))
        expect(head(root) == h, 'a refused apply moved HEAD')


# frozen

FROZEN_FILES = _with(BASE, **{
    'docs/layout.md': '## Homes\n\n## Frozen paths\n\n- `docs/archive/`\n',
    'docs/archive/old.md': '# Old\n\nSee [a](../a.md) and docs/a.md.\n\n```\n[a](../a.md)\n```\n',
    '.gitignore': 'ign/\n',
    'ign/x.md': '# I\n',
})


def gate_frozen(impl):
    with fixture(FROZEN_FILES, force=('ign/x.md',)) as root:
        before = _get(root, 'docs/archive/old.md')
        apply_ok(root, ONE, impl)
        expect(_get(root, 'docs/archive/old.md') == before, 'a frozen file changed')


def neg_frozen():
    with fixture(FROZEN_FILES, force=('ign/x.md',)) as root:
        for src, dst in (('.sdlc/x/n.md', 'docs/n.md'), ('docs/archive/old.md', 'docs/old.md'),
                         ('ign/x.md', 'docs/x.md'), ('docs/a.md', 'docs/archive/a.md')):
            refuses(root, plan1(src, dst), 'frozen')


# rewrite

REWRITE_FILES = {
    'README.md': '# R\n',
    'docs/layout.md': LAYOUT_EMPTY,
    'docs/AGENTS.md': '# docs\n',
    'docs/CLAUDE.md': '@AGENTS.md\n',
    'docs/a.md': '# A\n\nSee [b](b.md#top), [r](../README.md), and CLAUDE.md.\n',
    'docs/b.md': ('# B\n\n[inline](a.md#part)\n[ref]: a.md\n<a href="a.md">h</a>\n'
                  'Bare a.md and `a.md` and docs/a.md.\nOther [o](../other/a.md) and other/a.md.\n'),
    'other/a.md': '# O\n',
    'run.sh': 'cat docs/a.md\n',
}


def gate_rewrite(impl):
    with fixture(REWRITE_FILES) as root:
        apply_ok(root, ONE, impl)
        want = {
            'docs/topic/a.md': '# A\n\nSee [b](../b.md#top), [r](../../README.md), and CLAUDE.md.\n',
            'docs/b.md': ('# B\n\n[inline](topic/a.md#part)\n[ref]: topic/a.md\n<a href="topic/a.md">h</a>\n'
                          'Bare topic/a.md and `topic/a.md` and docs/topic/a.md.\n'
                          'Other [o](../other/a.md) and other/a.md.\n'),
            'run.sh': 'cat docs/topic/a.md\n',
        }
        for path, text in want.items():
            got = _get(root, path).decode('utf-8')
            expect(got == text, '%s is %r, expected %r' % (path, got, text))


def neg_rewrite():
    with fixture(REWRITE_FILES) as root:
        apply_ok(root, ONE)
        b = _get(root, 'docs/b.md').decode('utf-8')
        expect('Other [o](../other/a.md) and other/a.md.' in b, 'a citation of another a.md changed: %r' % b)
        a = _get(root, 'docs/topic/a.md').decode('utf-8')
        expect(a.endswith(', and CLAUDE.md.\n'), 'a bare CLAUDE.md mention changed: %r' % a)
        expect(_get(root, 'other/a.md') == b'# O\n', 'the other a.md changed')


# batches

BATCH_FILES = {
    'docs/layout.md': LAYOUT_EMPTY,
    'docs/a.md': '# A\n\nSee [b](b.md).\n',
    'docs/b.md': '# B\n\nSee [a](a.md).\n',
    'docs/d.md': '# D\n\nSee [a](a.md) and b.md here.\n',
}
BATCH_PLAN = {'version': 1, 'batches': [
    {'name': 'one', 'moves': [{'from': 'docs/a.md', 'to': 'docs/topic/a.md'},
                              {'from': 'docs/b.md', 'to': 'docs/topic/b.md'}]},
    {'name': 'two', 'moves': [{'from': 'docs/d.md', 'to': 'docs/other/d.md'}]}]}


def gate_batches(impl):
    with fixture(BATCH_FILES) as root:
        dry, _ = apply_ok(root, BATCH_PLAN, impl)
        for line in ('rewrite docs/d.md:3 a.md -> topic/a.md', 'rewrite docs/d.md:3 b.md -> topic/b.md',
                     'rewrite docs/d.md:3 topic/a.md -> ../topic/a.md',
                     'rewrite docs/d.md:3 topic/b.md -> ../topic/b.md'):
            has(dry, line)
        expect(not re.search(r'^rewrite docs/[ab]\.md:', dry, re.M), 'a same-batch link printed a rewrite')
        expect(_get(root, 'docs/other/d.md') == b'# D\n\nSee [a](../topic/a.md) and ../topic/b.md here.\n',
               'docs/other/d.md is %r' % _get(root, 'docs/other/d.md'))
        expect(_get(root, 'docs/topic/a.md') == b'# A\n\nSee [b](b.md).\n', 'docs/topic/a.md changed')


def neg_batches():
    rejected(gate_batches, REAL._replace(after=False), 'final check failed')
    rejected(gate_batches, REAL._replace(reexamine=False), 'final check failed')


# citation

def gate_citation(impl):
    with fixture(FROZEN_FILES, force=('ign/x.md',)) as root:
        rc, _, err = run(root, ONE, dry=True, impl=impl)
        expect(rc == 0, 'a citation in a frozen file refused: %s' % err.strip())


def neg_citation():
    files = _with(BASE, **{'docs/b.md': '# B\n\nSee [a](a.md).\n\n```\n[a](a.md)\n```\n'})
    with fixture(files) as root:
        refuses(root, ONE, 'docs/b.md:6')


# baseline

BASELINE_FILES = _with(BASE, **{'docs/b.md': '# B\n\nSee [a](a.md) and [gone](gone.md).\n'})


def gate_baseline(impl):
    with fixture(BASELINE_FILES) as root:
        dry, _ = apply_ok(root, ONE, impl)
        has(dry, 'baseline docs/b.md: gone.md')


def neg_baseline():
    rejected(gate_baseline, REAL._replace(drop=1), 'final check failed')


# running

def gate_running(impl):
    with fixture() as root:
        _put(root, '.sdlc/t/.run.lock', '')
        nested = os.path.join(root, 'nested')
        os.mkdir(nested)
        _git(nested, 'init', '-q')
        with held(os.path.join(nested, '.sdlc', 't', LOCK_NAME)):
            rc, _, err = run(root, ONE, dry=True, impl=impl)
        expect(rc == 0, 'an unheld lock or a nested work tree lock refused: %s' % err.strip())


def neg_running():
    with fixture() as root:
        with held(os.path.join(root, '.sdlc', 't', LOCK_NAME)):
            refuses(root, ONE, LOCK_NAME)


# collision

def gate_collision(impl):
    with fixture() as root:
        apply_ok(root, plan1('docs/a.md', 'docs/free/a.md'), impl)


def neg_collision():
    with fixture(_with(BASE, **{'docs/AGENTS.md': '# docs\n'})) as root:
        _put(root, 'docs/Extra.md', 'untracked\n')
        refuses(root, plan1('docs/a.md', 'docs/c.md'), 'docs/c.md')
        refuses(root, plan1('docs/a.md', 'docs/C.md'), 'docs/C.md')
        refuses(root, plan1('docs/a.md', 'docs/extra.md'), 'docs/extra.md')
        two = {'version': 1, 'batches': [{'name': 'one', 'moves': [
            {'from': 'docs/a.md', 'to': 'docs/x.md'}, {'from': 'docs/b.md', 'to': 'docs/x.md'}]}]}
        refuses(root, two, 'another move')
        refuses(root, plan1('docs/AGENTS.md', 'docs/guide/AGENTS.md'), 'entry file')


# dirty

def gate_dirty(impl):
    with fixture() as root:
        _put(root, 'docs/c.md', '# C\n\nlocal\n')
        apply_ok(root, ONE, impl)
        expect(_get(root, 'docs/c.md') == b'# C\n\nlocal\n', 'an unrelated modified file changed')


def neg_dirty():
    with fixture() as root:
        _put(root, 'docs/b.md', '# B\n\nSee [a](a.md).\nlocal\n')
        refuses(root, ONE, 'docs/b.md')
    with fixture() as root:
        _put(root, 'docs/c.md', '# C\nstaged\n')
        _git(root, 'add', 'docs/c.md')
        refuses(root, ONE, 'staged')


# restore

RESTORE_PLAN = {'version': 1, 'batches': [
    {'name': 'one', 'moves': [{'from': 'docs/a.md', 'to': 'docs/topic/a.md'}]},
    {'name': 'two', 'moves': [], 'links': [{'file': 'docs/b.md', 'old': 'topic/a.md', 'new': 'missing.md'}]}]}


def gate_restore(impl):
    with fixture() as root:
        apply_ok(root, ONE, impl)
        files = _git(root, 'ls-tree', '-r', '--name-only', 'HEAD').splitlines()
        expect('docs/topic/a.md' in files and 'docs/a.md' not in files, 'the move is not committed')
        expect(not _git(root, 'status', '--porcelain', '--untracked-files=no'), 'the apply left changes')


def failing_apply(root, plan, needle, impl=REAL):
    """Dry run passes; apply fails the final check naming needle and restores everything."""
    snap, h = snapshot(root), head(root)
    rc, dry, err = run(root, plan, dry=True, impl=impl)
    expect(rc == 0, 'dry run exit %d: %s' % (rc, err.strip()))
    rc, _, err = run(root, plan, approve=digest_of(dry), impl=impl)
    expect(rc == 1 and 'reorg.py: final check failed: %s' % needle in err, 'apply did not fail the check: %r' % err)
    expect('reorg.py: restored to %s' % h in err, 'no restore line: %r' % err)
    expect(head(root) == h, 'HEAD is not back at the start')
    same_tree(snap, snapshot(root))
    expect(not _git(root, 'diff', '--cached', '--name-only'), 'the index is not back at the start')


def neg_restore():
    with fixture() as root:
        _put(root, 'docs/c.md', '# C\nlocal\n')
        _put(root, 'notes.txt', 'untracked\n')
        failing_apply(root, RESTORE_PLAN, 'docs/b.md: missing.md')


# commit

COMMIT_PLAN = {'version': 1, 'batches': [
    {'name': 'one', 'moves': [{'from': 'docs/a.md', 'to': 'docs/topic/a.md'}]},
    {'name': 'two', 'moves': [{'from': 'docs/c.md', 'to': 'docs/topic/c.md'}]}]}


def gate_commit(impl):
    with fixture() as root:
        apply_ok(root, COMMIT_PLAN, impl)
        got = subjects(root)
        expect(got == ['reorg: two', 'reorg: one', 'init'], 'commit subjects are %r' % got)
        two, one = _git(root, 'log', '--format=%H', '-2').split()

        def paths(c):
            return set(_git(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', '--no-renames', c).split())
        expect(paths(one) == {'docs/a.md', 'docs/topic/a.md', 'docs/b.md', 'tool.py'}, 'commit one holds %r' % paths(one))
        expect(paths(two) == {'docs/c.md', 'docs/topic/c.md'}, 'commit two holds %r' % paths(two))
        expect('plan digest ' in _git(root, 'log', '-1', '--format=%b'), 'no plan digest in the commit body')


def neg_commit():
    rejected(gate_commit, REAL._replace(per_batch=False), 'commit subjects')


# dryrun

def gate_dryrun(impl):
    with fixture() as root:
        snap, h, index = snapshot(root), head(root), _git(root, 'ls-files', '-s')
        rc, out, err = run(root, ONE, dry=True, impl=impl)
        expect(rc == 0, 'dry run exit %d: %s' % (rc, err.strip()))
        try:
            same_tree(snap, snapshot(root))
        except GateFailure as e:
            raise GateFailure('the dry run wrote: %s' % e)
        expect(head(root) == h and _git(root, 'ls-files', '-s') == index, 'the dry run wrote: HEAD or index moved')
        for line in ('batch 1: one', 'move docs/a.md -> docs/topic/a.md', 'rewrite docs/a.md:3 b.md -> ../b.md',
                     'rewrite docs/b.md:3 a.md -> topic/a.md', 'rewrite tool.py:1 docs/a.md -> docs/topic/a.md'):
            has(out, line)
        expect(digest_of(out) and out.splitlines()[-1].startswith('digest '), 'the digest is not the last line')


def neg_dryrun():
    rejected(gate_dryrun, REAL._replace(dry_writes=True), 'the dry run wrote')


# managed

MANAGED_FILES = {
    'docs/layout.md': LAYOUT_EMPTY,
    'docs/a.md': '# A\n',
    'AGENTS.md': '# demo\n\n' + onboard.wrap_block('- [a](docs/a.md)\n'),
    'docs/AGENTS.md': ('# docs\n\n<!-- sdlc-lite:managed:start v1 sha256:000000000000 -->\n- [a](a.md)\n'
                       '<!-- sdlc-lite:managed:end -->\n'),
}


def gate_managed(impl):
    with fixture(MANAGED_FILES) as root:
        apply_ok(root, ONE, impl)
        expect('[a](docs/topic/a.md)' in _get(root, 'AGENTS.md').decode('utf-8'), 'the managed link was not rewritten')
        o, e = io.StringIO(), io.StringIO()
        onboard.run_check(root, out=o, err=e)
        labels = dict(reversed(ln.split(' ', 1)) for ln in o.getvalue().splitlines() if ' ' in ln)
        expect('AGENTS.md' in labels, 'onboard check gave no label for AGENTS.md: %r %r' % (o.getvalue(), e.getvalue()))
        expect(labels['AGENTS.md'] != 'edited', 'onboard check labels AGENTS.md edited')


def neg_managed():
    rejected(gate_managed, REAL._replace(refresh=False), 'edited')
    with fixture(MANAGED_FILES) as root:
        apply_ok(root, ONE)
        text = _get(root, 'docs/AGENTS.md').decode('utf-8')
        expect('sha256:000000000000' in text and '[a](topic/a.md)' in text,
               'a hand-edited block lost its hash or its rewrite: %r' % text)


# linkfix

LINKFIX_FILES = _with(BASE, **{'docs/b.md': '# B\n\nSee [x](old.md).\n'})


def fix_plan(new, old='old.md'):
    return {'version': 1, 'batches': [{'name': 'fix', 'moves': [],
                                       'links': [{'file': 'docs/b.md', 'old': old, 'new': new}]}]}


def gate_linkfix(impl):
    with fixture(LINKFIX_FILES) as root:
        dry, _ = apply_ok(root, fix_plan('c.md'), impl)
        has(dry, 'fix docs/b.md:3 old.md -> c.md')
        expect(_get(root, 'docs/b.md') == b'# B\n\nSee [x](c.md).\n', 'the fix did not retarget the link')
        expect(subjects(root) == ['reorg: fix', 'init'], 'commits are %r' % subjects(root))


def neg_linkfix():
    with fixture(LINKFIX_FILES) as root:
        refuses(root, fix_plan('c.md', old='nomatch.md'), 'nomatch.md')
        failing_apply(root, fix_plan('missing.md'), 'docs/b.md: missing.md')


GATES = (
    ('digest', lambda: gate_digest(REAL), neg_digest),
    ('approve', lambda: gate_approve(REAL), neg_approve),
    ('frozen', lambda: gate_frozen(REAL), neg_frozen),
    ('rewrite', lambda: gate_rewrite(REAL), neg_rewrite),
    ('batches', lambda: gate_batches(REAL), neg_batches),
    ('citation', lambda: gate_citation(REAL), neg_citation),
    ('baseline', lambda: gate_baseline(REAL), neg_baseline),
    ('running', lambda: gate_running(REAL), neg_running),
    ('collision', lambda: gate_collision(REAL), neg_collision),
    ('dirty', lambda: gate_dirty(REAL), neg_dirty),
    ('restore', lambda: gate_restore(REAL), neg_restore),
    ('commit', lambda: gate_commit(REAL), neg_commit),
    ('dryrun', lambda: gate_dryrun(REAL), neg_dryrun),
    ('managed', lambda: gate_managed(REAL), neg_managed),
    ('linkfix', lambda: gate_linkfix(REAL), neg_linkfix),
)


def selftest():
    saved = dict((k, os.environ.pop(k)) for k in onboard.GIT_LOCATION_ENV if k in os.environ)
    failed = 0
    try:
        for name, positive, negative in GATES:
            for case, fn in (('positive', positive), ('negative', negative)):
                try:
                    fn()
                    print('ok %s %s' % (name, case), flush=True)
                except GateFailure as e:
                    failed += 1
                    print('FAIL %s %s: %s' % (name, case, e), flush=True)
                except Exception as e:  # noqa: BLE001 - a crash is a failure, reported by type
                    failed += 1
                    print('FAIL %s %s: crashed: %s: %s' % (name, case, type(e).__name__, e), flush=True)
    finally:
        os.environ.update(saved)
    print('reorg selftest: %s' % ('FAIL' if failed else 'PASS'))
    return 1 if failed else 0


# ---------------------------------------------------------------- command line

def main(argv=None):
    ap = argparse.ArgumentParser(prog='reorg.py', description=__doc__.split('\n', 1)[0])
    sub = ap.add_subparsers(dest='cmd')
    sub.required = True
    sp = sub.add_parser('apply', help='apply a reorganization plan (dry run first)')
    sp.add_argument('plan', help='the plan JSON file')
    sp.add_argument('--root', help='the repository (default: the Git top level of the current directory)')
    sp.add_argument('--dry-run', action='store_true', help='print the listing and the digest; write nothing')
    sp.add_argument('--approve', metavar='DIGEST', help='the digest the dry run printed')
    sub.add_parser('selftest', help='run the gates on temp fixtures')
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding='utf-8', errors='surrogateescape')
    return run_apply(args.plan, args.root, args.dry_run, args.approve)


if __name__ == '__main__':
    sys.exit(main())
