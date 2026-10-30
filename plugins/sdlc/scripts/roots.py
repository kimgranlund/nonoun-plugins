#!/usr/bin/env python3
"""One resolver for every root path of an SDLC repo: state, config, runtime, messages, router, templates,
work, tickets, roadmap, notes, tasks, archive, evals, proposals and the fleet registry (T-0621).

Usage: roots.py paths [--root DIR]   print `key<TAB>path` for each Roots field (default --root .sdlc)
       roots.py selftest             prove the resolver on throwaway fixtures

The state root (<top>/.sdlc) holds `config`. Its opt-in `work_root: <path>` line moves the tracked work records
(ticket and task folders, ROADMAP.md, NOTES.md, archive/, evals/, proposals/, fleet.json) to <top>/<path>;
config, _templates, runtime, messages and the router stay in the state root. Blank and # comment lines are
ignored and a missing config is no line. With no work_root line every path is the one tickets.layout_paths
gave before T-0621 (flat, `ticket_root: tickets`, and `layout: topics`), plus evals/, proposals/ and
fleet.json under the state root.

Fail refuses, before anything is read or written: an empty work_root, `.`, an absolute path, any `..`, a path
under the state root, two different values, work_root beside `ticket_root: tickets` or `layout: topics`, and
the ticket_root and layout values tickets.py always refused. The singleton names are Roots.roadmap.name and
Roots.notes.name; compare against those, never a literal.

Stdlib only, Python 3.9, no import side effects.
"""
import collections
import os
import pathlib
import posixpath
import re
import sys
import tempfile

TICKET_ROOT_RE = re.compile(r'\s*ticket_root\s*:\s*(\S+)\s*(?:#.*)?')
LAYOUT_RE = re.compile(r'\s*layout\s*:\s*(\S+)\s*(?:#.*)?')
WORK_ROOT_RE = re.compile(r'\s*work_root\s*:\s*([^#]*?)\s*(?:#.*)?')
ROADMAP = 'ROADMAP.md'  # the work-root singletons (T-0620): UPPERCASE, ticket folders are the children
NOTES = 'NOTES.md'

Config = collections.namedtuple('Config', 'work_root ticket_root layout')  # each a tuple of (value, line)
Roots = collections.namedtuple('Roots', 'top state config templates runtime messages router work layout tickets '
                                        'nested roadmap notes tasks archive evals proposals fleet')


class Fail(Exception):
    """A refusal: the message goes to stderr and the command exits 1. Never a traceback. tickets.Fail is this."""


def parse(config_text):
    """Config(work_root, ticket_root, layout) from a config file's text (None is no file): each field is the
    tuple of (value, stripped line) for its lines, in file order. Blank and # comment lines are ignored."""
    work, troot, layout = [], [], []
    for line in (config_text or '').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        for regex, out in ((WORK_ROOT_RE, work), (TICKET_ROOT_RE, troot), (LAYOUT_RE, layout)):
            m = regex.fullmatch(line)
            if m:
                out.append((m.group(1), line.strip()))
    return Config(tuple(work), tuple(troot), tuple(layout))


def read_config(state):
    """<state>/config's text, or None when there is no such file."""
    path = pathlib.Path(state) / 'config'
    return path.read_text(encoding='utf-8') if path.is_file() else None


def _ticket_root(cfg, label):
    """True when cfg sets `ticket_root: tickets`; any other value raises Fail."""
    for v, _ in cfg.ticket_root:
        if v != 'tickets':
            raise Fail(f'{label}: ticket_root: {v} is not supported; the only supported value is '
                       f'ticket_root: tickets; nothing written')
    return bool(cfg.ticket_root)


def _work_root(cfg, label, state_rel):
    """The normalized work_root value (posix, relative to top), or None with no line. Unsafe values raise Fail."""
    if not cfg.work_root:
        return None
    first = cfg.work_root[0]
    for v, line in cfg.work_root:
        if v != first[0]:
            raise Fail(f'{label}: {line} conflicts with {first[1]}; keep one work_root value; nothing written')
    v, line = first
    if not v:
        raise Fail(f'{label}: {line} has no path; use a relative path such as work_root: docs/work; nothing written')
    if v.startswith(('/', '\\')) or re.match(r'[A-Za-z]:', v) or os.path.isabs(v):
        raise Fail(f'{label}: {line} is absolute; work_root is relative to the repo top, such as docs/work; '
                   f'nothing written')
    if '..' in re.split(r'[\\/]', v):
        raise Fail(f'{label}: {line} leaves the repo through ..; use a path inside the repo, such as docs/work; '
                   f'nothing written')
    norm = posixpath.normpath(v.replace('\\', '/'))
    if norm == '.':
        raise Fail(f'{label}: {line} is the repo top; use a subdir such as docs/work; nothing written')
    srel = posixpath.normpath(str(state_rel).replace('\\', '/'))
    if norm == srel or norm.startswith(srel + '/'):
        raise Fail(f'{label}: {line} is under {srel}, which keeps config, runtime and messages; use a path outside '
                   f'it, such as docs/work; nothing written')
    if _ticket_root_set(cfg):
        raise Fail(f'{label}: {line} cannot sit beside ticket_root: tickets; the work root holds the ticket folders '
                   f'itself, so drop the ticket_root line; nothing written')
    return norm


def _ticket_root_set(cfg):
    return any(v == 'tickets' for v, _ in cfg.ticket_root)


def _layout(cfg, label):
    """'flat' or 'topics' from cfg's layout lines; unsupported or conflicting values raise Fail."""
    for v, line in cfg.layout:
        if v not in ('flat', 'topics'):
            raise Fail(f'{label}: {line} is not supported; the supported values are layout: flat and layout: topics; '
                       f'nothing written')
    for v, line in cfg.layout:
        if v != cfg.layout[0][0]:
            raise Fail(f'{label}: {line} conflicts with {cfg.layout[0][1]}; keep one layout value; nothing written')
    return cfg.layout[0][0] if cfg.layout else 'flat'


def ticket_dir(state, config_text=None):
    """The dir holding the ticket folders: <top>/<work_root> with a work_root line, <state>/tickets with
    `ticket_root: tickets`, else state. Reads only the ticket_root and work_root lines, never `layout`, so a bad
    layout line in another tree never breaks that tree's ticket root (tickets.ticket_dir delegates here)."""
    state = pathlib.Path(state)
    if config_text is None:
        config_text = read_config(state)
    cfg = parse(config_text)
    label = state / 'config'
    nested = _ticket_root(cfg, label)
    work = _work_root(cfg, label, state.name)
    if work is not None:
        return state.parent / work
    return state / 'tickets' if nested else state


def resolve(state, config_text=None):
    """Roots for the state root `state` (<top>/.sdlc), reading <state>/config unless config_text is given."""
    state = pathlib.Path(state)
    if config_text is None:
        config_text = read_config(state)
    return _resolve(state.parent, state, config_text)


def resolve_text(top, state_rel, config_text):
    """Roots for another worktree or a git branch: top is its checkout dir (or the path its records are named
    under), state_rel its state root relative to top, config_text that tree's config (None: no file)."""
    return _resolve(pathlib.Path(top), pathlib.Path(top) / state_rel, config_text)


def _resolve(top, state, config_text):
    cfg = parse(config_text)
    label = state / 'config'
    layout = _layout(cfg, label)  # layout before ticket_root: the order tickets.layout_paths refused in
    nested = _ticket_root(cfg, label)
    work = _work_root(cfg, label, os.path.relpath(state, top) if state.is_absolute() == top.is_absolute()
                      else state.name)
    common = dict(top=top, state=state, config=label, templates=state / '_templates', runtime=state / 'runtime',
                  messages=state / 'messages', router=state / 'AGENTS.md')
    if work is not None:
        if layout == 'topics':
            raise Fail(f'{label}: work_root: {work} cannot sit beside layout: topics; the work root is flat, so '
                       f'drop the layout line; nothing written')
        w = top / work
        return Roots(work=w, layout='flat', tickets=w, nested=True, roadmap=w / ROADMAP, notes=w / NOTES, tasks=w,
                     archive=w / 'archive', evals=w / 'evals', proposals=w / 'proposals', fleet=w / 'fleet.json',
                     **common)
    tdir = state / 'tickets' if nested else state
    if layout == 'topics':
        if not nested:
            raise Fail(f'{label}: layout: topics needs a ticket_root: tickets line too (other worktrees, branches, '
                       f'board.py and traces find the ticket root from ticket_root alone); add ticket_root: tickets; '
                       f'nothing written')
        work_dir, roadmap, notes = state / 'work', tdir / 'roadmap.md', state / 'notes' / 'notes.md'
    else:
        work_dir, roadmap, notes = state, state / 'roadmap.md', state / 'notes.md'
    return Roots(work=work_dir, layout=layout, tickets=tdir, nested=nested, roadmap=roadmap, notes=notes,
                 tasks=work_dir, archive=work_dir / 'archive', evals=state / 'evals', proposals=state / 'proposals',
                 fleet=state / 'fleet.json', **common)


def state_of(path):
    """The state root that owns `path`, or None: (1) its nearest ancestor named .sdlc (itself included); else
    (2) the nearest ancestor A whose A/.sdlc/config sets a work_root W with path under A/W, giving A/.sdlc;
    else (3) None, and the caller keeps its own fallback. A refused config in rule 2 is skipped, not raised."""
    p = pathlib.Path(path)
    chain = [p, *p.parents]
    for a in chain:
        if a.name == '.sdlc':
            return a
    for a in chain:
        state = a / '.sdlc'
        text = read_config(state) if state.is_dir() else None
        if text is None:
            continue
        try:
            work = _work_root(parse(text), state / 'config', '.sdlc')
        except Fail:
            continue
        if work is not None and (p == a / work or (a / work) in p.parents):
            return state
    return None


def record_prefixes(top):
    """Repo-relative prefixes of the tracked work records: ('.sdlc/',) plus '<work_root>/' when one is set."""
    work = _work_root(parse(read_config(pathlib.Path(top) / '.sdlc')), pathlib.Path(top) / '.sdlc' / 'config',
                      '.sdlc')
    return ('.sdlc/',) if work is None else ('.sdlc/', work + '/')


# ---------- selftest ----------

def selftest():
    fails = []

    def need(cond, msg):
        if not cond:
            fails.append(msg)

    def refuses(text, msg):
        try:
            resolve(state, text)
        except Fail:
            return
        fails.append(f'{msg}: no Fail for {text!r}')

    with tempfile.TemporaryDirectory() as tmp:
        top = pathlib.Path(tmp).resolve() / 'repo'
        state = top / '.sdlc'
        state.mkdir(parents=True)

        # work_root: docs/work moves the work records, the state root keeps the rest
        r = resolve(state, 'work_root: docs/work\n')
        w = top / 'docs' / 'work'
        need(r.tickets == w, f'work_root tickets {r.tickets}')
        need(r.roadmap == w / 'ROADMAP.md', f'work_root roadmap {r.roadmap}')
        need(r.notes == w / 'NOTES.md', f'work_root notes {r.notes}')
        need(r.runtime == top / '.sdlc' / 'runtime', f'work_root runtime {r.runtime}')
        need((r.tasks, r.archive, r.evals, r.proposals, r.fleet)
             == (w, w / 'archive', w / 'evals', w / 'proposals', w / 'fleet.json'), f'work_root records {r}')
        need((r.config, r.templates, r.messages, r.router)
             == (state / 'config', state / '_templates', state / 'messages', state / 'AGENTS.md'), f'state {r}')
        need(r.layout == 'flat' and r.nested and r.work == w, f'work_root layout {r}')
        need(resolve(state, 'work_root: docs/work/  # moved\nlayout: flat\n') == r, 'trailing slash, comment, flat')
        need(resolve(state, '# work_root: docs/work\n').tickets == state, 'a commented work_root line is no line')

        # no work_root line: every path exactly as tickets.layout_paths gave them before T-0621
        flat = dict(layout='flat', tickets=state, roadmap=state / 'roadmap.md', notes=state / 'notes.md',
                    work=state, nested=False)
        nested = dict(flat, tickets=state / 'tickets', nested=True)
        topics = dict(layout='topics', tickets=state / 'tickets', roadmap=state / 'tickets' / 'roadmap.md',
                      notes=state / 'notes' / 'notes.md', work=state / 'work', nested=True)
        for text, want in ((None, flat), ('', flat), ('layout: flat\n', flat), ('ticket_root: tickets\n', nested),
                           ('ticket_root: tickets\nlayout: flat\n', nested),
                           ('ticket_root: tickets  # nested\nlayout: topics\n', topics)):
            r = resolve(state, text)
            got = {k: getattr(r, k) for k in want}
            need(got == want, f'no work_root {text!r}: {got} != {want}')
            need((r.tasks, r.archive) == (want['work'], want['work'] / 'archive'), f'tasks/archive {text!r}')
            need((r.evals, r.proposals, r.fleet, r.runtime)
                 == (state / 'evals', state / 'proposals', state / 'fleet.json', state / 'runtime'),
                 f'state records {text!r}')

        # refusals, before anything is written
        for text, msg in (('work_root: .sdlc/x\n', 'under .sdlc'), ('work_root: .sdlc\n', 'the state root'),
                          ('work_root: ../x\n', '..'), ('work_root: docs/../../x\n', 'inner ..'),
                          ('work_root: /tmp/x\n', 'absolute'), ('work_root: .\n', 'the top'),
                          ('work_root:\n', 'empty'), ('work_root: docs/work\nwork_root: docs/other\n', 'two values'),
                          ('work_root: docs/work\nticket_root: tickets\n', 'beside ticket_root: tickets'),
                          ('work_root: docs/work\nlayout: topics\n', 'beside layout: topics'),
                          ('ticket_root: other\n', 'bad ticket_root'), ('layout: deep\n', 'bad layout'),
                          ('layout: flat\nlayout: topics\n', 'two layouts'), ('layout: topics\n', 'topics alone')):
            refuses(text, msg)
        need(not any(state.iterdir()), 'a refusal wrote something')

        # tickets.py delegates: same paths, same Fail
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import roots as module  # the imported module, not __main__, is the one tickets.py sees
        import tickets
        need(tickets.Fail is module.Fail, 'tickets.Fail is not roots.Fail')
        (state / 'config').write_text('work_root: docs/work\n', encoding='utf-8')
        need(tickets.ticket_dir(state) == w, f'tickets.ticket_dir {tickets.ticket_dir(state)}')
        need(tuple(tickets.layout_paths(state)) == ('flat', w, w / 'ROADMAP.md', w / 'NOTES.md', w),
             f'tickets.layout_paths {tickets.layout_paths(state)}')
        (state / 'config').write_text('ticket_root: tickets\nlayout: deep\n', encoding='utf-8')
        need(tickets.ticket_dir(state) == state / 'tickets', 'ticket_dir must not read the layout line')

        # another tree or branch from its own config text
        r = resolve_text(top.parent / 'lane', '.sdlc', 'work_root: docs/work\n')
        need(r.tickets == top.parent / 'lane' / 'docs' / 'work' and r.state == top.parent / 'lane' / '.sdlc',
             f'resolve_text {r}')
        need(resolve_text(top, '.sdlc', 'ticket_root: tickets') == resolve(state, 'ticket_root: tickets'),
             'resolve_text matches resolve')
        need(resolve_text(pathlib.Path('.'), '.sdlc', 'work_root: docs/work').tickets == pathlib.Path('docs/work'),
             'resolve_text on a relative top')

        # state_of and record_prefixes
        (state / 'config').write_text('work_root: docs/work\n', encoding='utf-8')
        need(state_of(state / 'runtime' / 'tasks' / 'x') == state, 'state_of rule 1')
        need(state_of(w / '0001-a' / 'handoff.md') == state, 'state_of rule 2')
        need(state_of(w) == state, 'state_of rule 2 on the work root itself')
        need(state_of(top / 'docs' / 'other') is None, 'state_of rule 3 outside the work root')
        need(record_prefixes(top) == ('.sdlc/', 'docs/work/'), f'record_prefixes {record_prefixes(top)}')
        (state / 'config').write_text('layout: flat\n', encoding='utf-8')
        need(state_of(w / '0001-a') is None, 'state_of without work_root')
        need(record_prefixes(top) == ('.sdlc/',), 'record_prefixes without work_root')

    for f in fails:
        print(f'FAIL: {f}', file=sys.stderr)
    print('roots selftest: ' + ('FAIL' if fails else 'ok'))
    return 1 if fails else 0


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    if argv[:1] == ['paths']:
        rest = argv[1:]
        root = '.sdlc'
        if rest[:1] == ['--root'] and len(rest) == 2:
            root = rest[1]
        elif rest:
            print(__doc__.split('\n\n')[1], file=sys.stderr)
            return 2
        try:
            r = resolve(pathlib.Path(root).resolve())
        except Fail as e:
            print(f'roots.py: {e}', file=sys.stderr)
            return 1
        for k, v in r._asdict().items():
            print(f'{k}\t{v}')
        return 0
    print(__doc__.split('\n\n')[1], file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
