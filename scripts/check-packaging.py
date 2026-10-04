#!/usr/bin/env python3
"""Check both host catalogs and packaged entry points without installing anything."""
import argparse
import json
from pathlib import Path
import re
import sys


def check(root):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)
    catalogs = []
    for host, rel in [('codex', '.agents/plugins/marketplace.json'),
                      ('claude', '.claude-plugin/marketplace.json')]:
        catalog = json.loads((root / rel).read_text())
        entries = catalog['plugins']
        names = [entry['name'] for entry in entries]
        require(len(names) == len(set(names)), f'{host}: duplicate plugin names')
        catalogs.append(set(names))
        for entry in entries:
            name = entry['name']
            source = entry['source']['path'] if host == 'codex' else entry['source']
            require(source == f'./plugins/{name}', f'{host}: wrong source for {name}')
            require((root / source).is_dir(), f'{host}: missing source for {name}')
    require(catalogs[0] == catalogs[1] == {'sdlc-lite', 'progressive-context'},
            'catalogs must contain both peer plugins')
    for name in sorted(catalogs[0]):
        plugin = root / 'plugins' / name
        codex = json.loads((plugin / '.codex-plugin/plugin.json').read_text())
        claude = json.loads((plugin / '.claude-plugin/plugin.json').read_text())
        for key in ('name', 'version', 'description', 'author'):
            require(codex.get(key) == claude.get(key), f'{name}: {key} differs by host')
        require(codex['name'] == name, f'{name}: identity mismatch')
        require(codex['skills'] == './skills/', f'{name}: nonstandard skill location')
        for skill in (plugin / 'skills').glob('*/SKILL.md'):
            require(skill.read_text().startswith('---\n'), f'{skill}: missing frontmatter')
        require((plugin / 'skills' / name / 'SKILL.md').is_file(), f'{name}: missing entry point')
    sdlc = root / 'plugins/sdlc-lite'
    require(not (sdlc / 'hooks/hooks.json').exists(), 'Claude hooks leak into Codex discovery')
    manifest = json.loads((sdlc / '.claude-plugin/plugin.json').read_text())
    hooks = sdlc / manifest['hooks']
    require(hooks.is_file(), 'Claude hook configuration missing')
    hook_data = json.loads(hooks.read_text())
    pre = hook_data['hooks']['PreToolUse']
    require(len(pre) == 4, 'Claude hook routes lost')
    require(any(r.get('matcher') == 'Edit|Write|NotebookEdit' and 'warn-handoff-edit.sh' in json.dumps(r) for r in pre),
            'Claude handoff-freeze hook route lost')
    for skill in (sdlc / 'skills').glob('*/SKILL.md'):
        if skill.parent.name != 'sdlc-lite':
            require('../sdlc-lite/SKILL.md' in skill.read_text(), f'{skill}: missing Codex route')
    for path in (root / 'plugins/progressive-context/skills').rglob('*.md'):
        # Contract templates use illustrative paths inside fenced examples.
        text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in target and not target.startswith('#'):
                require((path.parent / target.split('#')[0]).exists(), f'{path}: broken link {target}')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        errors = check(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors = [str(exc)]
    for error in errors:
        print('FAIL:', error, file=sys.stderr)
    if errors:
        sys.exit(1)
    print('PASS: catalog parity, identity, skill routes, hook isolation and context links')
