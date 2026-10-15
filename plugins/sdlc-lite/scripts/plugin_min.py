#!/usr/bin/env python3
"""plugin_min.py: the minimum plugin version a repo needs, checked against the running plugin (T-0593).

Usage: plugin_min.py check <dir> [--host claude|codex] [--plugin DIR]   exit 2 with one stderr line when refused

A `plugin_min: X.Y.Z` line in .sdlc/config names the oldest sdlc-lite a repo accepts. Claude Code and Codex install
the plugin separately, so one repo can run two versions with different rules; `dispatch.py prepare`, `run.sh` and
`lanes.py open` refuse with exit 2 when the running plugin is older, naming both versions and the host's update
command, and `tickets.py check` warns. The running version is the `version` of the plugin's own manifest for the
host (.claude-plugin/plugin.json for claude, .codex-plugin/plugin.json for codex); the host defaults to
$SDLC_BACKEND, else claude. The config is the nearest .sdlc/config at or above <dir>, else the main checkout's (a
lane worktree often has no copy, since the config is usually untracked). No `plugin_min:` line means no check. The
comparison is numeric per part, missing parts read as 0 (0.10.0 is above 0.9.0; 1.0 equals 1.0.0). A malformed
value refuses too, so a typo never silently disables the gate.

T-0596: `solo_run.py run` refuses the same way, and on claude the check also reads the installed plugin whose hooks
run in the session: $CLAUDE_PLUGIN_ROOT's manifest when set, else the newest version folder under the plugin cache
($SDLC_PLUGIN_CACHE, default ~/.claude/plugins/cache/sdlc-lite/sdlc-lite). A conductor running a source checkout's
scripts sees the checkout's version while the hooks come from that install, so either one below plugin_min refuses,
and the line names which (the running plugin or the hook plugin). No install found means only the running plugin is
checked.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
LINE_RE = re.compile(r'\s*plugin_min\s*:\s*(\S*)\s*(?:#.*)?')
VERSION_RE = re.compile(r'\d+(\.\d+)*')
MANIFEST = {'claude': '.claude-plugin/plugin.json', 'codex': '.codex-plugin/plugin.json'}
CACHE = Path.home() / '.claude' / 'plugins' / 'cache' / 'sdlc-lite' / 'sdlc-lite'
UPDATE = {'claude': 'claude plugin marketplace update sdlc-lite && claude plugin update sdlc-lite@sdlc-lite, then start a fresh session',
          'codex': 'codex plugin marketplace upgrade sdlc-lite, then start a fresh Codex session'}


def parts(version):
    return tuple(int(p) for p in version.split('.'))


def below(have, need):
    """True when version have is lower than need, numeric per part, missing parts as 0."""
    a, b = parts(have), parts(need)
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)) < b + (0,) * (n - len(b))


def config_path(start):
    """The nearest .sdlc/config at or above start, else the main checkout's, else None."""
    start = Path(os.path.abspath(start))
    for d in [start] + list(start.parents):
        if (d / '.sdlc' / 'config').is_file():
            return d / '.sdlc' / 'config'
    probe = start if start.is_dir() else start.parent
    r = subprocess.run(['git', '-C', str(probe), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        cfg = Path(r.stdout.strip()).parent / '.sdlc' / 'config'
        if cfg.is_file():
            return cfg
    return None


def required(cfg):
    """The plugin_min: value of cfg ('' for a line with no value), or None when there is no line."""
    try:
        lines = Path(cfg).read_text(encoding='utf-8').splitlines()
    except (OSError, ValueError):
        return None
    for ln in lines:
        m = LINE_RE.fullmatch(ln)
        if m:
            return m.group(1)
    return None


def running(plugin=PLUGIN, host='claude'):
    """(version or None, manifest path) of the plugin's own manifest for host."""
    path = Path(plugin) / MANIFEST[host]
    try:
        v = json.loads(path.read_text(encoding='utf-8')).get('version')
    except (OSError, ValueError, AttributeError):
        v = None
    return (v if isinstance(v, str) and VERSION_RE.fullmatch(v) else None), path


def hook_plugin():
    """(dir, how) of the installed Claude plugin whose hooks run in the session, or (None, None) when none is found:
    $CLAUDE_PLUGIN_ROOT, else the newest version folder under the plugin cache."""
    root = os.environ.get('CLAUDE_PLUGIN_ROOT')
    if root:
        return Path(root), 'CLAUDE_PLUGIN_ROOT'
    cache = Path(os.environ.get('SDLC_PLUGIN_CACHE') or CACHE)
    try:
        found = [d for d in cache.iterdir() if VERSION_RE.fullmatch(d.name) and (d / MANIFEST['claude']).is_file()]
    except OSError:
        return None, None
    return (max(found, key=lambda d: parts(d.name)), 'plugin cache') if found else (None, None)


def host_of(host=None):
    h = host or os.environ.get('SDLC_BACKEND') or 'claude'
    return h if h in MANIFEST else 'claude'


def refusal(start, plugin=PLUGIN, host=None):
    """None when the running plugin meets the repo's plugin_min (or there is none); else the one-line refusal."""
    cfg = config_path(start)
    need = required(cfg) if cfg else None
    if need is None:
        return None
    host = host_of(host)
    if not VERSION_RE.fullmatch(need):
        return 'plugin_min: %r in %s is not a version (X.Y.Z); fix the line or remove it' % (need, cfg)
    have, manifest = running(plugin, host)
    if have is None:
        return 'plugin_min: %s needs sdlc-lite %s, but the running %s plugin has no readable version in %s' % (cfg, need, host, manifest)
    if below(have, need):
        return ('plugin_min: %s needs sdlc-lite %s or later; this %s host\'s running plugin is %s (%s). Update: %s'
                % (cfg, need, host, have, manifest, UPDATE[host]))
    if host != 'claude':
        return None
    hooks, how = hook_plugin()
    if hooks is None or os.path.realpath(hooks) == os.path.realpath(plugin):
        return None
    hv, hm = running(hooks, 'claude')
    if hv is None:
        return 'plugin_min: %s needs sdlc-lite %s, but the hook plugin (%s) has no readable version in %s' % (cfg, need, how, hm)
    if below(hv, need):
        return ('plugin_min: %s needs sdlc-lite %s or later; the running plugin is %s but the hook plugin (%s) is %s (%s). Update: %s'
                % (cfg, need, have, how, hv, hm, UPDATE[host]))
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(prog='plugin_min.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check')
    c.add_argument('dir')
    c.add_argument('--host', choices=sorted(MANIFEST))
    c.add_argument('--plugin', default=str(PLUGIN))
    a = ap.parse_args(argv)
    msg = refusal(a.dir, a.plugin, a.host)
    if msg:
        print(msg, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
