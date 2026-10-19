#!/usr/bin/env python3
"""inventory.py: read-only inventory of a git repository's documents, for planning a reorganization.

Usage:
  inventory.py [--root DIR] [--json] [--out PATH] [--top N] [--stale-days N] [--max-lines N] [--many-docs N] [--include-sdlc]
  inventory.py selftest

It reads tracked files with `git ls-files` and writes nothing into the repository. `--out PATH` writes the JSON
report to PATH and refuses a PATH inside the repository. There are no model calls and no network.

Documents: tracked md, mdx, markdown, rst, adoc, and txt files (not requirements*, robots, CMakeLists, and similar),
outside node_modules, dist, build, vendor, .worktrees, .git, any tracked path Git ignores, and `.sdlc/` plus the
`work_root:` directory of .sdlc/config when set (ticket and run records are frozen in the reorganization design;
`--include-sdlc` brings them in).

Links, as this script defines them (the reorganization draft left "link" open):
  - a link is an inline `[t](target)`, a reference definition `[id]: target`, or an HTML `href`/`src` attribute;
  - a mention is a path-shaped token ending in a document extension (also inside backticks) that resolves to a tracked document;
  - anything inside a fenced code block is ignored; external schemes (http, https, mailto, tel, data) and anchor-only
    targets are ignored; an anchor or query after the path is dropped;
  - a target resolves relative to the citing file's folder, or to the repository root when it starts with `/`; a repo-root-relative
    mention also resolves;
  - inbound counts links and mentions from every tracked text file, not only documents; a link is broken when its
    target is neither a tracked path, a folder holding tracked paths, nor an existing path on disk.

Flags per document: orphan, stale, duplicate, oversized, misplaced, broken_links. Per folder: no_entry_file (a folder
with many documents and no AGENTS.md or CLAUDE.md). Entry files and README.md are never orphans.
"""
import argparse, collections, datetime, hashlib, json, os, pathlib, re, subprocess, sys, tempfile

DOC_EXT = ('.md', '.mdx', '.markdown', '.rst', '.adoc', '.txt')
SKIP_PARTS = {'node_modules', 'dist', 'build', 'vendor', '.worktrees', '.git'}
TXT_DENY = re.compile(r'(^|/)(requirements[^/]*|robots|CMakeLists|LICENSE[^/]*|MANIFEST|CODEOWNERS|constraints[^/]*)\.txt$', re.I)
ENTRY_NAMES = ('AGENTS.md', 'CLAUDE.md')
EXTERNAL = re.compile(r'^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//)')
INLINE_LINK = re.compile(r'\]\(\s*<?([^)\s>]+)>?(?:\s+(?:"[^"]*"|\'[^\']*\'))?\s*\)')
REF_DEF = re.compile(r'^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)', re.M)
HTML_ATTR = re.compile(r'''(?:href|src)\s*=\s*["']([^"']+)["']''', re.I)
MENTION = re.compile(r'(?<![A-Za-z0-9_@.\-/])((?:\.{1,2}/)*[A-Za-z0-9_@.\-][A-Za-z0-9_@.\-/]*\.(?:md|mdx|markdown|rst|adoc|txt))(?![A-Za-z0-9_\-/])')
FENCE = re.compile(r'^\s{0,3}(```+|~~~+)')
WORD = re.compile(r'[A-Za-z0-9]+')
SELFTEST_ESCAPES = ('INVENTORY_SELFTEST_NO_ORPHAN', 'INVENTORY_SELFTEST_NO_BROKEN')


def git(root, *args, check=True):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    r = subprocess.run(['git', '-C', str(root), '-c', 'core.quotepath=off', *args], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env)
    if check and r.returncode != 0:
        raise SystemExit(f'inventory.py: git {" ".join(args)} failed: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout.decode('utf-8', 'replace')


def toplevel(path):
    r = subprocess.run(['git', '-C', str(path), 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise SystemExit('inventory.py: not inside a git work tree')
    return pathlib.Path(r.stdout.decode().strip())


def strip_fences(text):
    out, fence = [], None
    for line in text.split('\n'):
        m = FENCE.match(line)
        if m:
            mark = m.group(1)[0]
            if fence is None:
                fence = mark
            elif fence == mark:
                fence = None
            out.append('')
        else:
            out.append('' if fence else line)
    return '\n'.join(out)


def norm_target(raw):
    t = raw.strip().strip('<>')
    t = re.split(r'[#?]', t, 1)[0]
    return t


def join_rel(base_dir, target):
    if target.startswith('/'):
        p = os.path.normpath(target.lstrip('/'))
    else:
        p = os.path.normpath(os.path.join(base_dir, target))
    return None if p.startswith('..') else p.replace(os.sep, '/')


def record_prefixes(root):
    """Prefixes of the tracked work records: .sdlc/ plus the work_root of <root>/.sdlc/config, when set."""
    import roots
    try:
        return roots.record_prefixes(root)
    except (roots.Fail, OSError, ValueError):
        return ('.sdlc/',)


def is_doc(path, include_sdlc=False, prefixes=('.sdlc/',)):
    if not path.lower().endswith(DOC_EXT):
        return False
    if any(part in SKIP_PARTS for part in path.split('/')):
        return False
    if not include_sdlc and path.startswith(prefixes):
        return False
    if path.lower().endswith('.txt') and TXT_DENY.search(path):
        return False
    return True


def read_text(root, path, limit=1_000_000):
    p = root / path
    try:
        if p.stat().st_size > limit:
            return None
        data = p.read_bytes()
    except OSError:
        return None
    if b'\0' in data[:4096]:
        return None
    return data.decode('utf-8', 'replace')


def last_commit_dates(root):
    out = git(root, 'log', '--format=@%cI', '--name-only', '--no-renames')
    dates, cur = {}, None
    for line in out.split('\n'):
        if line.startswith('@'):
            cur = line[1:]
        elif line and cur and line not in dates:
            dates[line] = cur
    return dates


def parse_date(s):
    try:
        return datetime.datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def shingles(text, n=5):
    words = [w.lower() for w in WORD.findall(text)]
    if len(words) < 30:
        return set()
    out = set()
    for i in range(len(words) - n + 1):
        h = int(hashlib.md5(' '.join(words[i:i + n]).encode()).hexdigest()[:8], 16)
        if h % 3 == 0:
            out.add(h)
    return out


def first_heading(text):
    body = text
    if body.startswith('---\n'):
        end = body.find('\n---', 4)
        if end != -1:
            body = body[end + 4:]
    for line in body.split('\n'):
        m = re.match(r'^\s{0,3}#{1,6}\s+(.*\S)', line)
        if m:
            return m.group(1).strip()
    for line in body.split('\n'):
        if line.strip():
            return line.strip()[:80]
    return ''


def build(root, stale_days=180, max_lines=500, many_docs=8, dup_threshold=0.6, env=None, include_sdlc=False):
    env = os.environ if env is None else env
    tracked = [p for p in git(root, 'ls-files').split('\n') if p]
    ignored = set(p for p in git(root, 'ls-files', '-ci', '--exclude-standard').split('\n') if p)
    tracked_set = set(tracked)
    dirs = set()
    for p in tracked:
        d = os.path.dirname(p)
        while d:
            dirs.add(d)
            d = os.path.dirname(d)
    prefixes = record_prefixes(root)
    docs = sorted(p for p in tracked if is_doc(p, include_sdlc, prefixes) and p not in ignored)
    doc_set = set(docs)
    skipped = sorted(p for p in tracked if p.lower().endswith(DOC_EXT) and p not in doc_set)
    dates = last_commit_dates(root)
    newest = max((parse_date(d) for d in dates.values() if parse_date(d)), default=None)

    def resolves(p):
        return p in tracked_set or p in dirs or (root / p).exists()

    texts, links_out, broken = {}, collections.defaultdict(list), collections.defaultdict(list)
    inbound = collections.defaultdict(set)
    for path in tracked:
        if path in ignored or any(part in SKIP_PARTS for part in path.split('/')):
            continue
        text = read_text(root, path)
        if text is None:
            continue
        if path in doc_set:
            texts[path] = text
        body = strip_fences(text) if path in doc_set else text
        base = os.path.dirname(path)
        if path in doc_set:
            raw = [m.group(1) for m in INLINE_LINK.finditer(body)] + [m.group(1) for m in REF_DEF.finditer(body)] \
                + [m.group(1) for m in HTML_ATTR.finditer(body)]
            for r in raw:
                if not r or r.startswith('#') or EXTERNAL.match(r):
                    continue
                t = norm_target(r)
                if not t:
                    continue
                p = join_rel(base, t)
                if p is None or not resolves(p):
                    if 'INVENTORY_SELFTEST_NO_BROKEN' not in env:
                        broken[path].append(r)
                    continue
                if p in doc_set and p != path:
                    links_out[path].append(p)
                    inbound[p].add(path)
        for m in MENTION.finditer(body):
            t = m.group(1)
            for cand in (join_rel(base, t), join_rel('', t)):
                if cand and cand in doc_set and cand != path:
                    inbound[cand].add(path)
                    if path in doc_set and cand not in links_out[path]:
                        links_out[path].append(cand)
                    break

    rows = {}
    shingle_sets = {}
    for path in docs:
        text = texts.get(path, '')
        entry = os.path.basename(path) in ENTRY_NAMES
        d = os.path.dirname(path)
        rows[path] = {
            'path': path, 'bytes': len(text.encode('utf-8')), 'lines': text.count('\n') + (1 if text and not text.endswith('\n') else 0),
            'heading': first_heading(text), 'last_commit': dates.get(path),
            'inbound': sorted(inbound.get(path, ())), 'outbound': sorted(set(links_out.get(path, ()))),
            'broken_links': sorted(set(broken.get(path, ()))), 'entry_file': entry,
            'folder_has_entry': any(f'{d}/{n}'.lstrip('/') in tracked_set for n in ENTRY_NAMES), 'flags': [],
        }
        if not entry:
            shingle_sets[path] = shingles(text)

    for path, row in rows.items():
        exempt = row['entry_file'] or os.path.basename(path).lower().startswith('readme')
        if not row['inbound'] and not exempt and 'INVENTORY_SELFTEST_NO_ORPHAN' not in env:
            row['flags'].append('orphan')
        dt = parse_date(row['last_commit'])
        if newest and dt and (newest - dt).days > stale_days:
            row['flags'].append('stale')
        if row['lines'] > max_lines:
            row['flags'].append('oversized')
        if row['broken_links']:
            row['flags'].append('broken_links')

    by_head = collections.defaultdict(list)
    for path, row in rows.items():
        if not row['entry_file'] and row['heading'] and not os.path.basename(path).lower().startswith('readme'):
            by_head[row['heading'].lower()].append(path)
    dup_of = collections.defaultdict(set)
    for paths in by_head.values():
        if len(paths) > 1:
            for a in paths:
                dup_of[a].update(b for b in paths if b != a)
    index = collections.defaultdict(list)
    for path, sh in shingle_sets.items():
        for h in sh:
            index[h].append(path)
    seen = set()
    for path, sh in shingle_sets.items():
        if not sh:
            continue
        cand = collections.Counter(o for h in sh for o in index[h] if o != path)
        for other, _ in cand.items():
            key = tuple(sorted((path, other)))
            if key in seen:
                continue
            seen.add(key)
            osh = shingle_sets[other]
            if osh and len(sh & osh) / len(sh | osh) >= dup_threshold:
                dup_of[path].add(other)
                dup_of[other].add(path)
    for path, others in dup_of.items():
        rows[path]['flags'].append('duplicate')
        rows[path]['duplicate_of'] = sorted(others)

    for path, row in rows.items():
        if row['entry_file']:
            continue
        own = os.path.dirname(path)
        neigh = [os.path.dirname(p) for p in set(row['outbound']) | set(row['inbound'])
                 if not os.path.basename(p) in ENTRY_NAMES and not os.path.basename(p).lower().startswith('readme')]
        if len(neigh) < 3:
            continue
        top, n = collections.Counter(neigh).most_common(1)[0]
        parent = os.path.dirname(own)
        if top != own and top != parent and not top.startswith(own + '/') and n / len(neigh) >= 0.6:
            row['flags'].append('misplaced')
            row['suggest_folder'] = top
            row['misplaced_evidence'] = f'{n} of {len(neigh)} linked documents are in {top or "."}'

    per_dir = collections.defaultdict(list)
    for path in docs:
        per_dir[os.path.dirname(path)].append(path)
    folders = []
    for d, paths in sorted(per_dir.items()):
        has_entry = any(f'{d}/{n}'.lstrip('/') in tracked_set for n in ENTRY_NAMES)
        folders.append({'folder': d or '.', 'documents': len(paths), 'entry_file': has_entry,
                        'flags': ['no_entry_file'] if len(paths) >= many_docs and not has_entry else []})
    counts = collections.Counter(f for r in rows.values() for f in r['flags'])
    head = git(root, 'rev-parse', '--short', 'HEAD', check=False).strip() or None
    return {
        'root': str(root), 'head': head, 'documents': [rows[p] for p in docs], 'folders': folders, 'skipped': skipped,
        'summary': {'documents': len(docs), 'skipped': len(skipped), 'flag_counts': dict(sorted(counts.items())),
                    'folders_without_entry': sum(1 for f in folders if f['flags']),
                    'thresholds': {'include_sdlc': include_sdlc, 'stale_days': stale_days, 'max_lines': max_lines, 'many_docs': many_docs, 'duplicate': dup_threshold}},
    }


def render(rep, top=10):
    s = rep['summary']
    out = [f'inventory of {rep["root"]} at {rep["head"]}',
           f'documents {s["documents"]}, skipped (generated, vendored, ignored) {s["skipped"]}, folders without entry file {s["folders_without_entry"]}',
           'flags: ' + (', '.join(f'{k} {v}' for k, v in s['flag_counts'].items()) or 'none')]
    for flag in ('orphan', 'stale', 'duplicate', 'oversized', 'misplaced', 'broken_links'):
        rows = [r for r in rep['documents'] if flag in r['flags']]
        if not rows:
            continue
        out.append(f'\n{flag} ({len(rows)}, first {min(top, len(rows))}):')
        key = (lambda r: -r['lines']) if flag == 'oversized' else (lambda r: r['path'])
        for r in sorted(rows, key=key)[:top]:
            extra = {'misplaced': r.get('misplaced_evidence', ''), 'duplicate': ', '.join(r.get('duplicate_of', [])[:2]),
                     'oversized': f'{r["lines"]} lines', 'stale': r['last_commit'] or '', 'broken_links': ', '.join(r['broken_links'][:2])}.get(flag, '')
            out.append(f'  {r["path"]}' + (f'  ({extra})' if extra else ''))
    bad = [f for f in rep['folders'] if f['flags']]
    if bad:
        out.append(f'\nfolders with many documents and no entry file ({len(bad)}):')
        out += [f'  {f["folder"]}  ({f["documents"]} documents)' for f in bad[:top]]
    return '\n'.join(out)


def main(argv):
    ap = argparse.ArgumentParser(prog='inventory.py', description='read-only document inventory of a git repository')
    ap.add_argument('--root', default='.')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--out')
    ap.add_argument('--top', type=int, default=10)
    ap.add_argument('--stale-days', type=int, default=180)
    ap.add_argument('--max-lines', type=int, default=500)
    ap.add_argument('--many-docs', type=int, default=8)
    ap.add_argument('--include-sdlc', action='store_true')
    a = ap.parse_args(argv)
    root = toplevel(pathlib.Path(a.root).resolve())
    rep = build(root, a.stale_days, a.max_lines, a.many_docs, include_sdlc=a.include_sdlc)
    if a.out:
        dest = pathlib.Path(a.out).resolve()
        if dest == root or root in dest.parents:
            print(f'inventory.py: refusing to write inside the repository: {dest}', file=sys.stderr)
            return 2
        dest.write_text(json.dumps(rep, indent=1) + '\n')
    print(json.dumps(rep, indent=1) if a.json else render(rep, a.top))
    return 0


# ---- selftest ----

def _run(cmd, cwd, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')
    e.update(env or {})
    return subprocess.run(cmd, cwd=cwd, env=e, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


PARA = ('This paragraph repeats the same plain sentences so that two documents look like copies of each other, because '
        'the words are identical from the first line to the last and the overlap measure sees that clearly. ') * 3


def _fixture(tmp):
    root = tmp / 'fx'
    root.mkdir()
    _run(['git', 'init', '-q'], root)
    _write(root, '.gitignore', 'generated/\n')
    _write(root, 'AGENTS.md', '# Agents\n')
    _write(root, 'README.md', '# Readme\nSee [guide](docs/guide.md).\n')
    _write(root, 'docs/guide.md', '# Guide\n[ref](api/ref.md) [old](old.md) [a](dup-a.md) [b](dup-b.md) [big](big.md) [broken](broken.md)\n'
                                  '```\n[ignored](nowhere.md)\n```\n')
    _write(root, 'docs/orphan.md', '# Lonely note\nNobody links here.\n')
    _write(root, 'docs/old.md', '# Old\nThis is old.\n')
    _write(root, 'docs/dup-a.md', '# Copy A\n' + PARA)
    _write(root, 'docs/dup-b.md', '# Copy B\n' + PARA)
    _write(root, 'docs/big.md', '# Big\n' + 'line\n' * 600)
    _write(root, 'docs/broken.md', '# Broken\n[gone](missing.md) [ok](guide.md)\n')
    _write(root, 'docs/api/AGENTS.md', '# Api\n')
    _write(root, 'docs/api/ref.md', '# Ref\n[guide](../guide.md)\n')
    _write(root, 'docs/api/x.md', '# X\n[ref](ref.md)\n')
    _write(root, 'docs/api/y.md', '# Y\n[ref](ref.md)\n')
    _write(root, 'docs/ops/runbook.md', '# Runbook\n[a](../api/ref.md) [b](../api/x.md) [c](../api/y.md) [g](../guide.md)\n')
    for i in range(9):
        _write(root, f'docs/misc/n{i}.md', f'# Note {i}\n[g](../guide.md)\n')
    _write(root, 'scripts/run.sh', '# see docs/guide.md and docs/mentioned.md\n')
    _write(root, 'docs/mentioned.md', '# Mentioned only by a script\n')
    _write(root, 'node_modules/pkg/README.md', '# vendored\n')
    _write(root, 'generated/x.md', '# generated\n')
    _write(root, '.sdlc/t/handoff.md', '# Ticket\nrecord\n')
    _run(['git', 'add', '-A'], root)
    _run(['git', 'add', '-f', 'node_modules/pkg/README.md', 'generated/x.md'], root)
    _run(['git', 'commit', '-q', '-m', 'old', '--date', '2020-01-01T00:00:00'], root,
         {'GIT_COMMITTER_DATE': '2020-01-01T00:00:00', 'GIT_AUTHOR_DATE': '2020-01-01T00:00:00'})
    for rel in ('docs/guide.md', 'docs/orphan.md', 'docs/big.md', 'docs/api/ref.md'):
        p = root / rel
        p.write_text(p.read_text() + '\nupdated\n')
    _run(['git', 'commit', '-qam', 'new'], root)
    return root


def _clean(tmp):
    root = tmp / 'clean'
    root.mkdir()
    _run(['git', 'init', '-q'], root)
    _write(root, 'AGENTS.md', '# Agents\n')
    _write(root, 'README.md', '# Readme\n[a](docs/a.md)\n')
    _write(root, 'docs/a.md', '# A\n[back](../README.md)\n')
    _run(['git', 'add', '-A'], root)
    _run(['git', 'commit', '-q', '-m', 'c'], root)
    return root


def _check_flags(rep):
    """Return the failed expectations on the main fixture (empty means all hold)."""
    rows = {r['path']: r for r in rep['documents']}
    fl = lambda p: rows[p]['flags'] if p in rows else None
    bad = []

    def want(cond, msg):
        if not cond:
            bad.append(msg)
    want('orphan' in (fl('docs/orphan.md') or []), 'docs/orphan.md is not flagged orphan')
    want('orphan' not in (fl('docs/guide.md') or []), 'docs/guide.md wrongly orphan')
    want('orphan' not in (fl('docs/mentioned.md') or []) and 'docs/mentioned.md' in rows, 'a script mention does not count as inbound')
    want('orphan' not in (fl('README.md') or []) and 'orphan' not in (fl('AGENTS.md') or []), 'entry file or README flagged orphan')
    want('stale' in (fl('docs/old.md') or []), 'docs/old.md is not stale')
    want('stale' not in (fl('docs/guide.md') or []), 'docs/guide.md wrongly stale')
    want('duplicate' in (fl('docs/dup-a.md') or []) and 'duplicate' in (fl('docs/dup-b.md') or []), 'dup-a and dup-b are not flagged duplicate')
    want('duplicate' not in (fl('docs/guide.md') or []), 'docs/guide.md wrongly duplicate')
    want('oversized' in (fl('docs/big.md') or []), 'docs/big.md is not oversized')
    want('broken_links' in (fl('docs/broken.md') or []) and rows.get('docs/broken.md', {}).get('broken_links') == ['missing.md'], 'docs/broken.md broken link not found')
    want(rows.get('docs/guide.md', {}).get('broken_links') == [], 'docs/guide.md has a broken link it should not have')
    want('nowhere.md' not in sum((r['broken_links'] for r in rep['documents']), []), 'a link inside a code fence was counted')
    want('misplaced' in (fl('docs/ops/runbook.md') or []) and rows.get('docs/ops/runbook.md', {}).get('suggest_folder') == 'docs/api',
         'docs/ops/runbook.md is not misplaced toward docs/api')
    want('misplaced' not in (fl('docs/api/ref.md') or []), 'docs/api/ref.md wrongly misplaced')
    folders = {f['folder']: f for f in rep['folders']}
    want(folders.get('docs/misc', {}).get('flags') == ['no_entry_file'], 'docs/misc is not flagged no_entry_file')
    want(folders.get('docs/api', {}).get('flags') == [], 'docs/api wrongly flagged')
    want(all(not p.startswith(('node_modules/', 'generated/')) for p in rows), 'vendored or ignored paths were inventoried')
    want({'node_modules/pkg/README.md', 'generated/x.md'} <= set(rep['skipped']), 'vendored and ignored paths are not listed as skipped')
    return bad


def selftest():
    fails = []

    def expect(label, cond, detail=''):
        if not cond:
            fails.append(f'{label} {detail}'.strip())
    with tempfile.TemporaryDirectory(prefix='inventory-selftest.') as t:
        tmp = pathlib.Path(t)
        fx, cl = _fixture(tmp), _clean(tmp)

        def tree(root):
            return sorted((str(p.relative_to(root)), p.stat().st_mtime_ns, p.stat().st_size) for p in root.rglob('*')
                          if '.git' not in p.relative_to(root).parts and p.is_file())
        before = tree(fx)
        rep = build(fx)
        expect('read-only: the worktree is unchanged after a run', tree(fx) == before)
        for m in _check_flags(rep):
            expect('fixture:', False, m)
        expect('.sdlc records are skipped by default', not any(r['path'].startswith('.sdlc/') for r in rep['documents']))
        expect('--include-sdlc brings .sdlc records in', any(r['path'] == '.sdlc/t/handoff.md' for r in build(fx, include_sdlc=True)['documents']))
        wr = tmp / 'wr'
        wr.mkdir()
        _run(['git', 'init', '-q'], wr)
        for rel, text in (('.sdlc/config', 'work_root: docs/work\n'), ('docs/work/0001-a/handoff.md', '# Ticket\n'),
                          ('docs/guide.md', '# Guide\n')):
            _write(wr, rel, text)
        _run(['git', 'add', '-A'], wr)
        _run(['git', 'commit', '-q', '-m', 'w'], wr)
        expect('work_root records are skipped by default', [r['path'] for r in build(wr)['documents']] == ['docs/guide.md'])
        expect('--include-sdlc brings work_root records in',
               any(r['path'] == 'docs/work/0001-a/handoff.md' for r in build(wr, include_sdlc=True)['documents']))
        crep = build(cl)
        expect('negative control: the clean fixture reports no flags', not crep['summary']['flag_counts'] and
               not any(f['flags'] for f in crep['folders']), str(crep['summary']['flag_counts']))
        for esc, label in (('INVENTORY_SELFTEST_NO_ORPHAN', 'orphan'), ('INVENTORY_SELFTEST_NO_BROKEN', 'broken')):
            mut = build(fx, env={esc: '1'})
            expect(f'negative control: with the {label} check dropped the fixture assertions fail', bool(_check_flags(mut)))
        out_in = fx / 'out.json'
        expect('--out inside the repository is refused',
               subprocess.run([sys.executable, __file__, '--root', str(fx), '--out', str(out_in)], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).returncode == 2 and not out_in.exists())
        out_ok = tmp / 'report.json'
        r = subprocess.run([sys.executable, __file__, '--root', str(fx), '--json', '--out', str(out_ok)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        expect('--json with --out outside the repository writes valid json', r.returncode == 0 and
               json.loads(out_ok.read_text())['summary']['documents'] == rep['summary']['documents'])
        txt = subprocess.run([sys.executable, __file__, '--root', str(fx)], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode()
        expect('text report names each flag', all(w in txt for w in ('orphan', 'stale', 'duplicate', 'oversized', 'misplaced', 'broken_links')))
        nongit = tmp / 'plain'
        nongit.mkdir()
        expect('a folder that is not a git work tree exits nonzero',
               subprocess.run([sys.executable, __file__, '--root', str(nongit)], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0)
    for f in fails:
        print('FAIL', f)
    print('inventory selftest: ' + ('FAIL' if fails else 'PASS'))
    return 1 if fails else 0


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        sys.exit(selftest())
    sys.exit(main(sys.argv[1:]))
