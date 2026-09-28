#!/usr/bin/env python3
"""Read-only readiness checks. Configuration success is not proof of authentication or host capacity."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def inspect(project, backend, transport='exec', agents=True):
    errors, notes = [], []
    project = Path(project).resolve()
    for tool in ('git', 'python3', 'jq') + ((backend,) if transport == 'exec' else ()):
        if not shutil.which(tool):
            errors.append('Install or expose on PATH: ' + tool)
    if backend == 'claude' and transport != 'exec':
        errors.append('Claude supports exec transport; use --transport exec.')
    if shutil.which('git'):
        p = subprocess.run(['git', '-C', str(project), 'rev-parse', '--verify', 'HEAD'], capture_output=True)
        if p.returncode:
            errors.append('Use an existing Git project with an initial commit: ' + str(project))
    manifest = ROOT / ('.codex-plugin' if backend == 'codex' else '.claude-plugin') / 'plugin.json'
    try:
        data = json.loads(manifest.read_text())
        if data.get('name') != 'sdlc-lite':
            errors.append('Plugin manifest identity must be sdlc-lite: ' + str(manifest))
        if backend == 'claude':
            hooks = ROOT / data['hooks']
            hook_data = json.loads(hooks.read_text())
            if not hook_data.get('hooks', {}).get('PreToolUse'):
                errors.append('Claude PreToolUse hook registration is missing: ' + str(hooks))
        else:
            import codex_roles
            for name, definition in codex_roles.definitions():
                target = ROOT / 'adapters/codex/agents' / (name + '.toml')
                if not target.exists() or target.read_text() != codex_roles.dumps(definition):
                    errors.append('Regenerate stale source agents: python3 ' + str(ROOT/'scripts/codex_roles.py') + ' generate')
                    break
            if transport == 'subagent' and agents:
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        codex_roles.install(project, check=True)
                except (OSError, ValueError, KeyError) as exc:
                    errors.append(str(exc) + '; run python3 "' + str(ROOT/'scripts/codex_roles.py') + '" install "' + str(project) + '" and start a fresh Codex chat.')
    except (OSError, ValueError, KeyError) as exc:
        errors.append('Repair plugin configuration: ' + str(exc))
    if backend == 'codex' and transport == 'subagent':
        notes.append('The calling Codex chat must expose the named agents and have delegation capacity; a shell check cannot verify that they are loaded.')
    else:
        notes.append('Authentication, model access, and host permission behavior require a live run; no model call was made.')
    return dict(ready=not errors, scope='local configuration', backend=backend, transport=transport, project=str(project), errors=errors, notes=notes)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path.cwd())
    p.add_argument('--backend', choices=['claude', 'codex'], required=True)
    p.add_argument('--transport', choices=['exec', 'subagent'], default='exec')
    a = p.parse_args()
    result = inspect(a.project, a.backend, a.transport)
    print(json.dumps(result, indent=2))
    return 0 if result['ready'] else 2


if __name__ == '__main__':
    sys.exit(main())
