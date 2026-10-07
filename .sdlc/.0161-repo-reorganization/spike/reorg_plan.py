#!/usr/bin/env python3
"""Spike T-0161: read-only document reorganization plan.

Throwaway prototype. It reads the repository and prints a plan; it writes nothing, moves
nothing, and creates no ticket. Rules follow docs/planning/repo-onboarding/reorganization.md
(Inventory, Frozen material, Plan). The layout parser and frozen matching are imported from
plugins/sdlc-lite/scripts/onboard.py, not copied.

Usage: reorg_plan.py --layout <path> [--json]
"""
import argparse
import json
import os
import posixpath
import re
import subprocess
import sys
from urllib.parse import unquote


def _toplevel():
    r = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        sys.exit('reorg_plan: not inside a Git work tree')
    return r.stdout.decode('utf-8', 'surrogateescape').rstrip('\n')


ROOT = _toplevel()
sys.path.insert(0, os.path.join(ROOT, 'plugins', 'sdlc-lite', 'scripts'))
from onboard import parse_layout, frozen_match, _frozen, list_documents, scan_lines, LayoutError  # noqa: E402

MARKDOWN = ('.md', '.markdown')
SCHEME = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:')
CODE_SPAN = re.compile(r'(`+)(.+?)\1')
INLINE = re.compile(r'!?\[(?:[^\[\]\\]|\\.|\[[^\]]*\])*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:"[^"]*"|\'[^\']*\'))?\s*\)')
REF_DEF = re.compile(r'^\s{0,3}\[[^\]]+\]:\s*(<[^>\n]*>|\S+)')
HTML = re.compile(r'''(?:href|src)\s*=\s*["']([^"']+)["']''', re.I)
AUTOLINK = re.compile(r'<([A-Za-z][A-Za-z0-9+.-]*:[^<>\s]*)>')
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
FORMS = ('markdown_link', 'reference_link', 'html_link', 'autolink', 'anchor',
         'backtick_path', 'code_fence', 'other', 'non_markdown', 'in_frozen_files')


# ---------------------------------------------------------------- repository facts

def _git_lines(*args):
    r = subprocess.run(['git', '-C', ROOT] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        sys.exit('reorg_plan: git %s failed: %s' % (' '.join(args), r.stderr.decode('utf-8', 'replace')))
    return sorted(p for p in r.stdout.decode('utf-8', 'surrogateescape').split('\0') if p)


def _read(path):
    try:
        with open(os.path.join(ROOT, path), 'rb') as f:
            data = f.read()
    except OSError:
        return None
    if b'\0' in data[:8192]:
        return None
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return None


class Repo(object):
    def __init__(self, layout):
        self.layout = layout
        self.tracked = [p for p in _git_lines('ls-files', '-z') if os.path.isfile(os.path.join(ROOT, p))]
        self.ignored = set(_git_lines('ls-files', '-z', '-ci', '--exclude-standard'))
        self.markdown = [p for p in self.tracked if p.lower().endswith(MARKDOWN)]
        self._text = {}

    def frozen(self, path):
        return path.startswith('.sdlc/') or path in self.ignored or _frozen(self.layout.frozen, path)

    def text(self, path):
        if path not in self._text:
            self._text[path] = _read(path)
        return self._text[path]


# ---------------------------------------------------------------- links

def _code_spans(line):
    return [(m.start(), m.end(), m.group(2).strip()) for m in CODE_SPAN.finditer(line)]


def _inside(pos, spans):
    return any(a <= pos < b for a, b, _ in spans)


def links_in_line(line):
    """(form, start, end, raw_target) for each link on a line outside a code span."""
    spans = _code_spans(line)
    out = []
    m = REF_DEF.match(line)
    if m and not _inside(m.start(1), spans):
        out.append(('reference_link', m.start(1), m.end(1), m.group(1)))
    for rx, form in ((INLINE, 'markdown_link'), (HTML, 'html_link'), (AUTOLINK, 'autolink')):
        for m in rx.finditer(line):
            if _inside(m.start(), spans):
                continue
            out.append((form, m.start(1), m.end(1), m.group(1)))
    return sorted(out, key=lambda x: (x[1], x[0]))


def split_target(raw):
    """(path, suffix, wrapped): suffix is '#frag' or '?query...'; None path for URLs and pure anchors."""
    wrapped = raw.startswith('<') and raw.endswith('>')
    t = raw[1:-1] if wrapped else raw
    if SCHEME.match(t) or t.startswith('#') or not t:
        return None, '', wrapped
    cut = min([i for i in (t.find('#'), t.find('?')) if i >= 0] or [len(t)])
    return t[:cut], t[cut:], wrapped


def resolve(src, path):
    """Repository-relative target of a link path written in src. '..' prefix means outside the repo."""
    p = unquote(path)
    if p.startswith('/'):
        return posixpath.normpath(p.lstrip('/'))
    return posixpath.normpath(posixpath.join(posixpath.dirname(src), p))


def exists(target):
    if target == '..' or target.startswith('../'):
        return False
    return os.path.exists(os.path.join(ROOT, target))


def relink(path, new_target, new_src):
    if path.startswith('/'):
        return '/' + new_target
    rel = posixpath.relpath(new_target, posixpath.dirname(new_src) or '.')
    if path.startswith('./') and not rel.startswith('../'):
        rel = './' + rel
    return rel


def link_records(repo, path):
    """Every link (not in a fence or code span) in one Markdown file."""
    text = repo.text(path)
    if text is None:
        return []
    out = []
    for n, (line, fenced) in enumerate(scan_lines(text), 1):
        if fenced:
            continue
        for form, a, b, raw in links_in_line(line):
            tpath, suffix, wrapped = split_target(raw)
            if tpath is None:
                continue
            out.append({'line': n, 'form': form, 'raw': raw, 'path': tpath, 'suffix': suffix,
                        'wrapped': wrapped, 'target': resolve(path, tpath)})
    return out


# ---------------------------------------------------------------- classification

def home_match(glob, rel):
    """A home glob against a path relative to docs/. A glob without a slash matches the file name."""
    return frozen_match(glob, rel if '/' in glob else posixpath.basename(rel))


def classify(repo):
    homes = repo.layout.homes
    placed, misplaced, unplaced, ambiguities = [], [], [], []
    candidates = [p for p in list_documents(ROOT) if p.startswith('docs/') and not repo.frozen(p)]
    for path in candidates:
        rel = path[len('docs/'):]
        matches = sorted((h, g) for h, globs in homes.items() for g in globs if home_match(g, rel))
        match_homes = sorted(set(h for h, _ in matches))
        under = [h for h in homes if rel.startswith(h)]
        if len(match_homes) > 1:
            ambiguities.append({'kind': 'multi_home', 'paths': [path],
                                'detail': 'globs of %s all match' % ', '.join(match_homes)})
        elif len(match_homes) == 1:
            home = match_homes[0]
            if home in under:
                placed.append(path)
            else:
                glob = [g for h, g in matches if h == home][0]
                misplaced.append({'from': path, 'to': 'docs/' + home + posixpath.basename(rel),
                                  'rule': '`%s` takes `%s`' % (home, glob)})
        elif '/' in rel:
            placed.append(path)
        else:
            unplaced.append(path)
    moves = []
    by_dest = {}
    for m in misplaced:
        by_dest.setdefault(m['to'].lower(), []).append(m)
    tracked_lower = set(p.lower() for p in repo.tracked)
    for dest, group in sorted(by_dest.items()):
        srcs = sorted(m['from'] for m in group)
        if len(group) > 1:
            ambiguities.append({'kind': 'name_collision', 'paths': srcs + [group[0]['to']],
                                'detail': 'two or more files would move to one destination'})
            continue
        m = group[0]
        if dest in tracked_lower or os.path.exists(os.path.join(ROOT, m['to'])):
            ambiguities.append({'kind': 'name_collision', 'paths': [m['from'], m['to']],
                                'detail': 'destination already exists (case folded)'})
            continue
        if repo.frozen(m['to']):
            ambiguities.append({'kind': 'into_frozen', 'paths': [m['from'], m['to']],
                                'detail': 'destination home is frozen'})
            continue
        moves.append(m)
    return candidates, sorted(placed), sorted(moves, key=lambda m: m['from']), sorted(unplaced), \
        sorted(ambiguities, key=lambda a: (a['kind'], a['paths']))


# ---------------------------------------------------------------- plan

def rewrites_for(repo, moves):
    moved = dict((m['from'], m['to']) for m in moves)
    rewrites, frozen_cites = [], []
    for path in repo.markdown:
        is_frozen = repo.frozen(path)
        for rec in link_records(repo, path):
            tgt = rec['target']
            if not (path in moved or tgt in moved):
                continue
            if is_frozen:
                if tgt in moved:
                    frozen_cites.append({'file': path, 'line': rec['line'], 'target': rec['raw']})
                continue
            new_path = relink(rec['path'], moved.get(tgt, tgt), moved.get(path, path))
            if new_path == rec['path']:
                continue
            new_raw = new_path + rec['suffix']
            if rec['wrapped']:
                new_raw = '<' + new_raw + '>'
            rewrites.append({'file': path, 'line': rec['line'], 'old': rec['raw'], 'new': new_raw,
                             'form': rec['form']})
    key = lambda r: (r['file'], r['line'], r['old'], r['new'])
    return sorted(rewrites, key=key), sorted(frozen_cites, key=lambda r: (r['file'], r['line'], r['target']))


def baseline_broken(repo):
    out = []
    for path in repo.markdown:
        if repo.frozen(path):
            continue
        for rec in link_records(repo, path):
            if not exists(rec['target']):
                out.append({'file': path, 'line': rec['line'], 'target': rec['raw']})
    return sorted(out, key=lambda r: (r['file'], r['line'], r['target']))


def frozen_candidates(repo):
    out = []
    for path in repo.markdown:
        if repo.frozen(path):
            continue
        reasons = []
        name = posixpath.basename(path)
        if DATE.search(name):
            reasons.append('date in name')
        elif any(DATE.search(part) for part in path.split('/')[:-1]):
            reasons.append('date in folder name')
        text = repo.text(path) or ''
        for n, line in enumerate(text.split('\n')[:10], 1):
            if line.lstrip().startswith('Recorded:'):
                reasons.append('Recorded: line %d' % n)
                break
        if reasons:
            out.append({'path': path, 'reason': '; '.join(reasons)})
    return out


def _backtick_cites(content, src, moved_path):
    c = content.split('#')[0].rstrip(':.,;')
    if not c or ' ' in c:
        return False
    if c in (moved_path, posixpath.basename(moved_path)):
        return True
    if c.endswith('/' + moved_path):
        return True
    return posixpath.normpath(posixpath.join(posixpath.dirname(src), c)) == moved_path


def cite_forms(repo, moves):
    """Counts, by form, of cites of the moved documents, plus the cites a link rewriter cannot see."""
    counts = dict((k, 0) for k in FORMS)
    unseen = []
    moved = [m['from'] for m in moves]
    names = dict((p, posixpath.basename(p)) for p in moved)
    if not moved:
        return counts, unseen
    for path in repo.tracked:
        text = repo.text(path)
        if text is None:
            continue
        hits = [p for p in moved if p != path and names[p] in text]
        if not hits:
            continue
        frozen = repo.frozen(path)
        is_md = path.lower().endswith(MARKDOWN)
        lines = scan_lines(text) if is_md else ((ln, False) for ln in text.split('\n'))
        for n, (line, fenced) in enumerate(lines, 1):
            for p in hits:
                name = names[p]
                if name not in line:
                    continue
                if frozen:
                    counts['in_frozen_files'] += line.count(name)
                    continue
                if not is_md:
                    counts['non_markdown'] += line.count(name)
                    unseen.append({'file': path, 'line': n, 'form': 'non_markdown', 'cites': p})
                    continue
                if fenced:
                    counts['code_fence'] += line.count(name)
                    unseen.append({'file': path, 'line': n, 'form': 'code_fence', 'cites': p})
                    continue
                masked = list(line)
                for form, a, b, raw in links_in_line(line):
                    tpath, suffix, _ = split_target(raw)
                    if tpath is not None and resolve(path, tpath) == p:
                        counts['anchor' if suffix.startswith('#') else form] += 1
                for a, b, content in _code_spans(line):
                    if _backtick_cites(content, path, p):
                        counts['backtick_path'] += 1
                        unseen.append({'file': path, 'line': n, 'form': 'backtick_path', 'cites': p})
                    masked[a:b] = ' ' * (b - a)
                for rx in (INLINE, HTML, AUTOLINK, REF_DEF):
                    for m in rx.finditer(line):
                        masked[m.start():m.end()] = ' ' * (m.end() - m.start())
                rest = ''.join(masked)
                k = rest.count(name)
                if k:
                    counts['other'] += k
                    unseen.append({'file': path, 'line': n, 'form': 'other', 'cites': p})
    return counts, sorted(unseen, key=lambda r: (r['file'], r['line'], r['form'], r['cites']))


def build_plan(layout_path):
    try:
        layout = parse_layout(layout_path)
    except LayoutError as e:
        sys.exit('reorg_plan: %s' % (e,))
    repo = Repo(layout)
    candidates, placed, moves, unplaced, ambiguities = classify(repo)
    rewrites, frozen_cites = rewrites_for(repo, moves)
    counts, unseen = cite_forms(repo, moves)
    plan = {
        'layout': os.path.relpath(os.path.abspath(layout_path), ROOT),
        'placed': placed,
        'moves': moves,
        'rewrites': rewrites,
        'unplaced': unplaced,
        'frozen_candidates': frozen_candidates(repo),
        'baseline_broken': baseline_broken(repo),
        'cite_forms': counts,
        'unrewritten_cites': unseen,
        'frozen_cites_of_moved': frozen_cites,
        'ambiguities': ambiguities,
    }
    plan['summary'] = {
        'tracked_markdown': len(repo.markdown),
        'candidates': len(candidates),
        'placed': len(placed),
        'misplaced': len(moves) + sum(1 for a in ambiguities if a['kind'] != 'multi_home'),
        'moves': len(moves),
        'unplaced': len(unplaced),
        'ambiguous': len(ambiguities),
        'rewrites': len(rewrites),
        'unrewritten_cites': len(unseen),
        'frozen_candidates': len(plan['frozen_candidates']),
        'baseline_broken': len(plan['baseline_broken']),
    }
    return plan


# ---------------------------------------------------------------- output

def _table(title, headers, rows):
    lines = ['## %s (%d)' % (title, len(rows)), '']
    if not rows:
        return lines + ['(none)', '']
    rows = [[str(c) for c in r] for r in rows]
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    fmt = '  '.join('%%-%ds' % w for w in widths)
    lines.append((fmt % tuple(headers)).rstrip())
    lines.append((fmt % tuple('-' * w for w in widths)).rstrip())
    lines.extend((fmt % tuple(r)).rstrip() for r in rows)
    return lines + ['']


def render_text(plan):
    out = ['# Reorganization plan (read-only, spike T-0161)', '', 'Layout: %s' % plan['layout'], '']
    out += _table('Summary', ['count', 'value'], sorted(plan['summary'].items()))
    out += _table('Moves', ['from', 'to', 'rule'], [(m['from'], m['to'], m['rule']) for m in plan['moves']])
    out += _table('Rewrites', ['file', 'line', 'form', 'old', 'new'],
                  [(r['file'], r['line'], r['form'], r['old'], r['new']) for r in plan['rewrites']])
    out += _table('Unplaced', ['path'], [(p,) for p in plan['unplaced']])
    out += _table('Ambiguities', ['kind', 'paths', 'detail'],
                  [(a['kind'], ', '.join(a['paths']), a['detail']) for a in plan['ambiguities']])
    out += _table('Placed', ['path'], [(p,) for p in plan['placed']])
    out += _table('Cite forms of moved documents', ['form', 'count'], sorted(plan['cite_forms'].items()))
    out += _table('Cites a link rewriter does not see', ['file', 'line', 'form', 'cites'],
                  [(r['file'], r['line'], r['form'], r['cites']) for r in plan['unrewritten_cites']])
    out += _table('Frozen files citing a moved document (not rewritten)', ['file', 'line', 'target'],
                  [(r['file'], r['line'], r['target']) for r in plan['frozen_cites_of_moved']])
    out += _table('Frozen candidates', ['path', 'reason'],
                  [(r['path'], r['reason']) for r in plan['frozen_candidates']])
    out += _table('Links broken before any move', ['file', 'line', 'target'],
                  [(r['file'], r['line'], r['target']) for r in plan['baseline_broken']])
    return '\n'.join(out).rstrip('\n') + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='Read-only document reorganization plan (spike T-0161).')
    ap.add_argument('--layout', required=True, help='layout file to plan against')
    ap.add_argument('--json', action='store_true', help='print one JSON object instead of tables')
    args = ap.parse_args(argv)
    plan = build_plan(args.layout)
    if args.json:
        sys.stdout.write(json.dumps(plan, indent=2, sort_keys=True) + '\n')
    else:
        sys.stdout.write(render_text(plan))
    return 0


if __name__ == '__main__':
    sys.exit(main())
