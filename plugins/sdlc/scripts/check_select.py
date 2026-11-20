#!/usr/bin/env python3
"""Pick the check.sh jobs that cover a set of changed paths (T-0858).

Usage:
  check_select.py select <path>...        print the selected job names, one per line, in check.sh order
  check_select.py changed [<base>]        the same for `git diff --name-only <base>` plus untracked files
  check_select.py prune <list dir> [<base>]
                                          check.sh --changed: delete the queued job files the changed paths
                                          do not select; exit 3 with `nothing to check` when none is left
  check_select.py selftest

Paths are relative to the repository top. The job map comes from check.sh itself (each `job <tier> <name>
<command...>` line), so a new job needs no second edit here. Rules, first match per path:
  - outside plugins/sdlc/ and docs/: nothing
  - docs/: check.py and docs-repo
  - scripts/check.sh, scripts/check_pool.py: every job
  - a file a job command names (scripts/<name>.py, skills/<s>/scripts/<name>.py, a .sh): that job, check.py,
    the jobs of the scripts that import it (any `import <name>` line, direct importers only), and shellcheck
    for a .sh; a scripts/ file no job names and no job-bearing script imports: every job
  - agents/, adapters/: the generated-definition jobs, prompt_lint and check.py
  - hooks/: the hook jobs, shellcheck for a .sh, and check.py
  - skills/ (not a skill script), the plugin's own *.md: check.py and prompt_lint
  - any other plugins/sdlc/ path: every job
"""
import fnmatch
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
PREFIX = 'plugins/sdlc/'
ALL = '*'
NOTHING_EXIT = 3

JOB_RE = re.compile(r'\bjob\s+(fast|full)\s+(\S+)\s+(.*)$')
IMPORT_RE = re.compile(r'^\s*(?:from\s+(\w+)\s+import\b|import\s+([\w\s,.]+))')
ROOT_TOKEN = re.compile(r'\$root/(\S+)')


def parse_jobs(check_sh):
    """[(name, [relative path or glob named by the command])] in check.sh order."""
    jobs = []
    with open(check_sh, encoding='utf-8') as fh:
        for line in fh:
            if line.lstrip().startswith('#') or line.lstrip().startswith('job()'):
                continue
            m = JOB_RE.search(line)
            if not m:
                continue
            cmd = m.group(3).replace('"', '').replace("'", '')
            cmd = re.split(r';\s*(?:fi|done)\b', cmd)[0]
            jobs.append((m.group(2), ROOT_TOKEN.findall(cmd)))
    return jobs


def script_files(plugin):
    out = []
    for d in ['scripts'] + ['skills/%s/scripts' % s for s in sorted(os.listdir(os.path.join(plugin, 'skills')))]:
        full = os.path.join(plugin, d)
        if os.path.isdir(full):
            out += ['%s/%s' % (d, f) for f in sorted(os.listdir(full)) if f.endswith('.py')]
    return out


def imported_names(path):
    names = set()
    try:
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                m = IMPORT_RE.match(line)
                if not m:
                    continue
                if m.group(1):
                    names.add(m.group(1))
                else:
                    for part in m.group(2).split('#')[0].split(','):
                        part = part.strip().split(' ')[0]
                        if part:
                            names.add(part.split('.')[0])
    except OSError:
        pass
    return names


class Selector:
    def __init__(self, plugin=PLUGIN):
        self.plugin = plugin
        self.jobs = parse_jobs(os.path.join(plugin, 'scripts', 'check.sh'))
        self.names = [n for n, _ in self.jobs]
        self.importers = {}  # module name -> [relative script path that imports it]
        for rel in script_files(plugin):
            for mod in imported_names(os.path.join(plugin, rel)):
                self.importers.setdefault(mod, []).append(rel)

    def owners(self, rel):
        """Jobs whose command names rel exactly."""
        return [n for n, paths in self.jobs if rel in paths]

    def globbed(self, rel):
        """Jobs whose command names rel through a glob (shellcheck's scripts/*.sh)."""
        return [n for n, paths in self.jobs if any('*' in p and fnmatch.fnmatch(rel, p) for p in paths)]

    def one(self, path):
        """The job names one repository-relative path selects; ALL for every job."""
        path = path.replace(os.sep, '/')
        if path.startswith('./'):
            path = path[2:]
        if path.startswith('docs/'):
            return {'check.py', 'docs-repo'}
        if not path.startswith(PREFIX):
            return set()
        rel = path[len(PREFIX):]
        if rel in ('scripts/check.sh', 'scripts/check_pool.py'):
            return ALL
        own = self.owners(rel)
        base, ext = os.path.splitext(os.path.basename(rel))
        if rel.startswith('scripts/') or '/scripts/' in rel:
            sel = set(own)
            if ext == '.py':
                for imp in self.importers.get(base, []):
                    if imp != rel:
                        sel.update(self.owners(imp))
            if not sel:
                return ALL
            return sel | {'check.py'} | set(self.globbed(rel))
        if rel.startswith(('agents/', 'adapters/')):
            return {'codex_roles-generate', 'claude_roles', 'claude_roles-generate', 'codex-selftest',
                    'prompt_lint', 'check.py'}
        if rel.startswith('hooks/'):
            return {'hook-selftest', 'hook-live-probe', 'check.py'} | set(self.globbed(rel))
        if rel.startswith('skills/') or ('/' not in rel and ext == '.md'):
            return {'check.py', 'prompt_lint'}
        return ALL

    def select(self, paths):
        """Selected job names in check.sh order."""
        want = set()
        for p in paths:
            got = self.one(p)
            if got is ALL:
                return list(self.names)
            want |= got
        return [n for n in self.names if n in want]


def git(top, *args):
    return subprocess.run(['git', '-C', top] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=True).stdout


def changed_paths(start, base='HEAD'):
    """Repository-relative paths changed since base, plus untracked files."""
    top = git(start, 'rev-parse', '--show-toplevel').strip()
    out = git(top, 'diff', '--name-only', base, '--').splitlines()
    out += git(top, 'ls-files', '--others', '--exclude-standard', '--full-name').splitlines()
    return sorted(set(p for p in out if p)), top


def prefix_of(top, plugin):
    rel = os.path.relpath(os.path.realpath(plugin), os.path.realpath(top)).replace(os.sep, '/')
    return '' if rel == '.' else rel + '/'


def selected_for(base, plugin=PLUGIN):
    paths, top = changed_paths(plugin, base)
    pre = prefix_of(top, plugin)
    # The rules are written for this repository's layout; map another install's plugin folder onto it.
    if pre != PREFIX:
        paths = [PREFIX + p[len(pre):] if p.startswith(pre) else p for p in paths]
    return Selector(plugin).select(paths), paths


def prune(list_dir, base, plugin=PLUGIN, out=sys.stdout):
    sel, _ = selected_for(base, plugin)
    keep = set(sel)
    files = sorted(f for f in os.listdir(list_dir))
    kept, skipped = [], 0
    for f in files:
        with open(os.path.join(list_dir, f), 'rb') as fh:
            name = fh.read().split(b'\0')[0].decode()
        if name in keep:
            kept.append(name)
        else:
            os.remove(os.path.join(list_dir, f))
            skipped += 1
    if not kept:
        print('nothing to check (base %s)' % base, file=out)
        return NOTHING_EXIT
    print('changed: %s' % ' '.join(kept), file=out)
    print('skipped: %d jobs' % skipped, file=out)
    return 0


def selftest():
    misses = []

    def check(name, cond, got=None):
        if cond:
            print('ok: %s' % name)
        else:
            misses.append(name)
            print('FAIL: %s%s' % (name, '' if got is None else ' (got %s)' % got))

    s = Selector()
    n_all = len(s.names)
    check('job map parsed from check.sh', n_all > 20 and 'check.py' in s.names and 'wtroot' in s.names, n_all)
    check('check_select has its own job', 'check_select' in s.names)
    check('shellcheck globs a .sh', 'shellcheck' in s.globbed('scripts/run.sh'))

    leaf = s.select([PREFIX + 'scripts/cite_check.py'])
    check('leaf script: its job and check.py', leaf == ['check.py', 'cite_check'], leaf)
    shared = s.select([PREFIX + 'scripts/roots.py'])
    check('shared module: its importers\' jobs', {'roots', 'check.py', 'tickets', 'steps'} <= set(shared)
          and len(shared) < n_all, shared)
    skill_script = s.select([PREFIX + 'skills/decompose/scripts/coverage_check.py'])
    check('skill script: its job before the skills/ rule', skill_script == ['check.py', 'coverage_check'], skill_script)
    docs = s.select(['docs/references/sdlc-internals.md'])
    check('docs-only path: check.py and docs-repo', set(docs) == {'check.py', 'docs-repo'}, docs)
    check('outside the plugin: nothing', s.select(['README.md', '.sdlc/tickets/x.md', 'plugins/design/x.md']) == [])
    check('check.sh itself: all', s.select([PREFIX + 'scripts/check.sh']) == s.names)
    check('check_pool.py: all', s.select([PREFIX + 'scripts/check_pool.py']) == s.names)
    check('unmapped plugin path: all', s.select([PREFIX + 'output-styles/x.md']) == s.names)
    check('script no job names: all', s.select([PREFIX + 'scripts/run.sh']) == s.names)
    hook = s.select([PREFIX + 'hooks/block-publish.sh'])
    check('hook: hook jobs', {'hook-selftest', 'check.py'} <= set(hook) and len(hook) < n_all, hook)
    agent = s.select([PREFIX + 'agents/solo.md'])
    check('agent: generated definitions', {'claude_roles-generate', 'codex_roles-generate', 'check.py'} <= set(agent)
          and len(agent) < n_all, agent)
    skill = s.select([PREFIX + 'skills/chain/SKILL.md'])
    check('skill doc: check.py and prompt_lint', skill == ['check.py', 'prompt_lint'], skill)
    check('union keeps check.sh order', s.select([PREFIX + 'scripts/wtroot.py', 'docs/x.md'])
          == [n for n in s.names if n in set(s.select([PREFIX + 'scripts/wtroot.py'])) | {'check.py', 'docs-repo'}])

    # changed / prune on a throwaway repository: a copy of check.sh as the plugin, one edit, one untracked file.
    tmp = tempfile.mkdtemp(prefix='check-select-')
    try:
        plug = os.path.join(tmp, PREFIX)
        os.makedirs(os.path.join(plug, 'scripts'))
        os.makedirs(os.path.join(plug, 'skills'))
        for f in ('check.sh', 'cite_check.py', 'roots.py', 'tickets.py'):
            shutil.copy(os.path.join(HERE, f), os.path.join(plug, 'scripts', f))
        env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t',
                   GIT_COMMITTER_EMAIL='t@t')
        for args in (['init', '-q'], ['add', '-A'], ['commit', '-qm', 'base', '--no-gpg-sign']):
            subprocess.run(['git', '-C', tmp] + args, check=True, env=env, stdout=subprocess.DEVNULL)
        sel, _ = selected_for('HEAD', plug)
        check('changed: a clean tree selects nothing', sel == [], sel)
        with open(os.path.join(plug, 'scripts', 'cite_check.py'), 'a') as fh:
            fh.write('\n')
        os.makedirs(os.path.join(tmp, 'docs'))
        open(os.path.join(tmp, 'docs', 'new.md'), 'w').close()
        sel, paths = selected_for('HEAD', plug)
        check('changed: an edit plus an untracked file', paths == ['docs/new.md', PREFIX + 'scripts/cite_check.py']
              and sel == [n for n in Selector(plug).names if n in ('check.py', 'cite_check', 'docs-repo')], (paths, sel))
        lst = os.path.join(tmp, 'list')
        os.makedirs(lst)
        for i, name in enumerate(['fanout', 'cite_check', 'check.py']):
            with open(os.path.join(lst, '%03d' % i), 'wb') as fh:
                fh.write(b'\0'.join(x.encode() for x in (name, 'true')) + b'\0')
        buf = io.StringIO()
        rc = prune(lst, 'HEAD', plug, buf)
        check('prune: keeps the selected jobs, counts the skipped', rc == 0 and len(os.listdir(lst)) == 2
              and 'skipped: 1 jobs' in buf.getvalue(), buf.getvalue())
        subprocess.run(['git', '-C', tmp, 'checkout', '-q', '--', '.'], check=True)
        os.remove(os.path.join(tmp, 'docs', 'new.md'))
        buf = io.StringIO()
        rc = prune(lst, 'HEAD', plug, buf)
        check('prune: nothing to check exits %d' % NOTHING_EXIT, rc == NOTHING_EXIT
              and 'nothing to check' in buf.getvalue() and os.listdir(lst) == [], buf.getvalue())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print('check_select selftest: %s' % ('FAIL: ' + ', '.join(misses) if misses else 'PASS'))
    return 1 if misses else 0


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0 if argv else 2
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == 'selftest':
            return selftest()
        if cmd == 'select' and rest:
            print('\n'.join(Selector().select(rest)))
            return 0
        if cmd == 'changed' and len(rest) <= 1:
            sel, _ = selected_for(rest[0] if rest else 'HEAD')
            print('\n'.join(sel) if sel else 'nothing to check')
            return 0
        if cmd == 'prune' and 1 <= len(rest) <= 2:
            return prune(rest[0], rest[1] if len(rest) > 1 else 'HEAD')
    except subprocess.CalledProcessError as e:
        print('check_select.py: git failed: %s' % (e.stderr or e).strip(), file=sys.stderr)
        return 2
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
