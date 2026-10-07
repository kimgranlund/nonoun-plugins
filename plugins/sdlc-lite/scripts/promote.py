#!/usr/bin/env python3
"""Copy a .sdlc artifact into a docs/ home as a promoted document (docs/docs-schema/design.md, Promotion).

Usage:
  promote.py [--root DIR] <artifact path> <home> [--slug S] [--ticket T-NNNN] [--note]
  promote.py selftest

The copy goes to docs/<home>/<slug>.md with front matter: `source: T-NNNN`, `source-file: <original name>`,
and the home's mandatory key (`status: proposed` for planning and decisions, `date: <today>` for reports).
Reports also get a YYYY-MM-DD- file name prefix. Refuses an unknown home, an existing target, a non-Markdown
artifact, and a decisions slug with no four-digit number prefix. Never edits the ticket's handoff.md and never
removes the .sdlc copy. --note appends one line to .sdlc/notes.md (or .sdlc/notes/notes.md under topics layout).
--root is the repository root (default: the current directory). Calls no model.
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docs_check  # noqa: E402

HOMES = docs_check.DEFAULT_HOMES


class Refuse(Exception):
    pass


def kebab(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def ticket_of(path, given):
    if given:
        if not re.fullmatch(r'T-\d{4}', given):
            raise Refuse('--ticket must look like T-NNNN, got %r' % given)
        return given
    for part in reversed(os.path.abspath(path).split(os.sep)[:-1]):
        m = re.match(r'^\.?(\d{4})-', part)
        if m:
            return 'T-' + m.group(1)
    raise Refuse('cannot infer the ticket id from the path; pass --ticket T-NNNN')


def with_front_matter(text, keys):
    """Add keys (ordered pairs) to a leading front matter block, or create one. Existing keys win."""
    lines = text.split('\n')
    if lines and lines[0].strip() == '---' and any(l.strip() == '---' for l in lines[1:]):
        have = docs_check.front_matter(text)
        add = ['%s: %s' % (k, v) for k, v in keys if k not in have]
        if 'source' in have:
            raise Refuse('the artifact already has a source: key; it looks promoted already')
        return '\n'.join([lines[0]] + add + lines[1:])
    return '---\n' + ''.join('%s: %s\n' % kv for kv in keys) + '---\n\n' + text


def notes_path(root):
    topics = os.path.join(root, '.sdlc', 'notes', 'notes.md')
    return topics if os.path.isfile(topics) else os.path.join(root, '.sdlc', 'notes.md')


def promote(root, artifact, home, slug=None, ticket=None, note=False, today=None):
    today = today or datetime.date.today().isoformat()
    if home not in HOMES:
        raise Refuse('unknown home %r; one of %s' % (home, ', '.join(HOMES)))
    if home == 'assets':
        raise Refuse('assets holds non-Markdown files and takes no front matter; copy those by hand')
    if not os.path.isfile(artifact):
        raise Refuse('no such artifact: %s' % artifact)
    if not artifact.endswith('.md'):
        raise Refuse('only a Markdown artifact can be promoted')
    tid = ticket_of(artifact, ticket)
    orig = os.path.basename(artifact)
    name = kebab(slug) if slug else kebab(os.path.splitext(orig)[0])
    if not name:
        raise Refuse('empty slug')
    if home == 'decisions' and not re.match(r'^\d{4}-', name):
        raise Refuse('a decisions file name needs a four-digit number prefix; pass --slug NNNN-name')
    keys = [('source', tid), ('source-file', orig)]
    if home in ('planning', 'decisions'):
        keys.append(('status', 'proposed'))
    if home == 'reports':
        keys.append(('date', today))
        if not docs_check.DATE_IN_NAME.match(name):
            name = '%s-%s' % (today, name)
    target = os.path.join(root, 'docs', home, name + '.md')
    if os.path.exists(target):
        raise Refuse('target exists, not overwriting: %s' % os.path.relpath(target, root))
    with open(artifact, encoding='utf-8') as f:
        body = f.read()
    out = with_front_matter(body, keys)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'x', encoding='utf-8') as f:
        f.write(out)
    rel = os.path.relpath(target, root)
    if note:
        npath = notes_path(root)
        os.makedirs(os.path.dirname(npath), exist_ok=True)
        with open(npath, 'a', encoding='utf-8') as f:
            f.write('- %s: promoted %s to %s\n' % (today, orig, rel))
    return rel


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', default='.')
    ap.add_argument('artifact')
    ap.add_argument('home')
    ap.add_argument('--slug')
    ap.add_argument('--ticket')
    ap.add_argument('--note', action='store_true')
    a = ap.parse_args(argv)
    try:
        print(promote(a.root, a.artifact, a.home, a.slug, a.ticket, a.note))
    except Refuse as e:
        print('refused: %s' % e, file=sys.stderr)
        return 1
    return 0


def selftest():
    tmp = tempfile.mkdtemp(prefix='promote-')
    fails = []

    def expect(ok, msg):
        if not ok:
            fails.append(msg)

    def refused(*args, **kw):
        try:
            promote(*args, **kw)
        except Refuse:
            return True
        return False

    try:
        subprocess.run(['git', 'init', '-q', tmp], check=True)
        tdir = os.path.join(tmp, '.sdlc', '0099-demo')
        os.makedirs(tdir)
        handoff = os.path.join(tdir, 'handoff.md')
        review = os.path.join(tdir, 'verifier-L3.md')
        with open(handoff, 'w') as f:
            f.write('---\nid: T-0099\n---\n# H\n')
        with open(review, 'w') as f:
            f.write('# Review\n\nbody\n')
        before = open(handoff).read()
        r = promote(tmp, review, 'reports', today='2026-10-06', note=True)
        expect(r == 'docs/reports/2026-10-06-verifier-l3.md', 'report path %s' % r)
        text = open(os.path.join(tmp, r)).read()
        expect('source: T-0099' in text and 'source-file: verifier-L3.md' in text and 'date: 2026-10-06' in text, 'report front matter')
        expect(open(handoff).read() == before, 'handoff changed')
        expect(os.path.isfile(review), 'source copy removed')
        expect('promoted verifier-L3.md to docs/reports/' in open(os.path.join(tmp, '.sdlc', 'notes.md')).read(), 'note line')
        p = promote(tmp, review, 'planning', slug='My Plan', ticket='T-0100')
        expect(p == 'docs/planning/my-plan.md' and 'status: proposed' in open(os.path.join(tmp, p)).read(), 'planning copy')
        for h, kw in (('nonsense', {}), ('decisions', {}), ('assets', {}), ('reports', {'ticket': 'x'})):
            expect(refused(tmp, review, h, **kw), 'accepted bad input for %s %s' % (h, kw))
        expect(refused(tmp, review, 'planning', slug='my-plan'), 'overwrote an existing target')
        expect(refused(tmp, review, 'reports', today='2026-10-06'), 'overwrote an existing report')
        expect(open(handoff).read() == before, 'handoff changed after refusals')
        expect(refused(tmp, os.path.join(tdir, 'missing.md'), 'specs'), 'accepted a missing artifact')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        for m in fails:
            print('FAIL promote selftest: %s' % m)
        return 1
    print('promote.py selftest: ok')
    return 0


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'selftest':
        sys.exit(selftest())
    sys.exit(main())
