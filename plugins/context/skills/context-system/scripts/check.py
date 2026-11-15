#!/usr/bin/env python3
"""Run every check a corpus has the artifacts for, and say which layers are not present.

Usage: check.py [--root CORPUS] [--strict] [--require LAYER[,LAYER...]]

It looks under --root (default: the current directory) for the files each layer's tool reads, runs only the tools
whose files exist, and prints one summary line per layer:

  vocabulary   vocabulary.json                       validate_kos.py, with the corpus scanned for retired labels
  statements   rules.json (needs vocabulary.json)    lint_cnl.py over the corpus
  manifests    registry.json and *.manifest.json     check_registry.py
  routing      profile.json                          validate.py; with suite.json, replay.py as well
  links        always                                check_links.py

A corpus that keeps these files elsewhere names them in `context-system.json` at the root, any of:
  {"vocabulary": "docs/vocabulary.json", "rules": "docs/rules.json", "registry": "dist/registry.json",
   "manifests": "components/*/manifest.json", "keep": "kind,family", "profile": "ctx/profile.json",
   "suite": "ctx/suite.json", "docs": ["docs", "README.md"]}
`docs` is what the vocabulary and statements checks scan (default: the root).

A layer with no file is reported as "not present", which is not a failure: a corpus adds a layer only when it has the
evidence for one. A gate names the layers its corpus must have with --require; a required layer that is not present
fails. A profile with no suite is reported as "no suite, replay not run" and fails under --strict, because the route
replay did not run. A failed replay names the cases that failed. Exit 0 when every layer that is present passes, 1 when
one fails, 2 when --root cannot be read or --require names no layer.
Standard library only; runs on Python 3.9.
"""
import argparse
import glob
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYERS = ('vocabulary', 'statements', 'manifests', 'routing', 'links')


def run(script, *args, cwd=None):
    r = subprocess.run([sys.executable, '-B', str(HERE / script), *map(str, args)], capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr).rstrip('\n')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', default='.')
    ap.add_argument('--strict', action='store_true', help='warnings fail too')
    ap.add_argument('--require', default='', help='comma-separated layers that must be present: ' + ', '.join(LAYERS))
    args = ap.parse_args(argv)
    required = [x.strip() for x in args.require.split(',') if x.strip()]
    unknown = [x for x in required if x not in LAYERS]
    if unknown:
        print(f"--require: no layer named {', '.join(unknown)}; the layers are {', '.join(LAYERS)}", file=sys.stderr)
        return 2
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f'{args.root}: not a directory', file=sys.stderr)
        return 2
    cfg = {}
    if (root / 'context-system.json').is_file():
        try:
            cfg = json.loads((root / 'context-system.json').read_text(encoding='utf-8'))
        except ValueError as exc:
            print(f'context-system.json: not valid JSON: {exc}', file=sys.stderr)
            return 2
    at = lambda key, default: root / cfg.get(key, default)  # noqa: E731
    vocabulary, rules, registry = at('vocabulary', 'vocabulary.json'), at('rules', 'rules.json'), at('registry', 'registry.json')
    profile, suite = at('profile', 'profile.json'), at('suite', 'suite.json')
    docs = [str(root / d) for d in cfg.get('docs', ['.'])]
    strict = ['--strict'] if args.strict else []
    results = []  # (layer, state, last line, full output)

    def record(layer, code, output):
        results.append((layer, 'PASS' if code == 0 else 'FAIL', output.split('\n')[-1] if output else '', output))

    def absent(layer, what):
        if layer in required:
            results.append((layer, 'FAIL', f'{what}; required by --require', f'{what}; required by --require'))
        else:
            results.append((layer, 'not present', what, ''))

    if vocabulary.is_file():
        corpus = [x for d in docs for x in ('--corpus', d)]
        record('vocabulary', *run('validate_kos.py', vocabulary, *corpus, *strict))
    else:
        absent('vocabulary', f'no {vocabulary.relative_to(root)}')
    if rules.is_file() and vocabulary.is_file():
        record('statements', *run('lint_cnl.py', rules, vocabulary, *docs, *strict))
    else:
        absent('statements', f'no {rules.relative_to(root)}' if not rules.is_file() else 'rules without a vocabulary')
    pattern = str(root / cfg.get('manifests', '**/*.manifest.json'))
    if registry.is_file() and glob.glob(pattern, recursive=True):
        keep = ['--keep', cfg['keep']] if cfg.get('keep') else []
        record('manifests', *run('check_registry.py', '--registry', registry, '--manifests', pattern, *keep, *strict))
    else:
        absent('manifests', f'no {registry.relative_to(root)}' if not registry.is_file() else f'no manifests match {cfg.get("manifests", "**/*.manifest.json")}')
    if profile.is_file():
        code, out = run('validate.py', '--root', root, '--profile', profile)
        if code == 0:
            out = 'profile valid'
            if suite.is_file():
                failing = []
                with tempfile.TemporaryDirectory() as tmp:
                    record_path = Path(tmp) / 'run.json'
                    code, replay = run('replay.py', '--root', root, '--profile', profile, '--suite', suite, '--out', record_path)
                    try:
                        failing = [str(c.get('id', '?')) for c in json.loads(record_path.read_text(encoding='utf-8'))['cases'] if not c.get('passed')]
                    except (OSError, ValueError, KeyError, TypeError, AttributeError):
                        pass
                try:
                    r = json.loads(replay)
                    out = f"profile valid; route replay {r['passed']} of {r['total']} passed"
                    if failing:
                        out += '; failed: ' + ', '.join(failing)
                except (ValueError, KeyError):
                    out = replay
            else:
                out = f'profile valid; no {suite.relative_to(root)}, replay not run'
                if args.strict:
                    code, out = 1, out + ' (a failure under --strict)'
        record('routing', code, out)
    else:
        absent('routing', f'no {profile.relative_to(root)}')
    record('links', *run('check_links.py', '--root', root, *strict))

    for layer, state, last, output in results:
        if state == 'FAIL':
            print(f'--- {layer}\n{output}')
    for layer, state, last, _ in results:
        print(f'{layer:<11} {state:<12} {last}')
    failed = [layer for layer, state, _, _ in results if state == 'FAIL']
    print(f"check: {len(failed)} layer(s) failed{': ' + ', '.join(failed) if failed else ''}; "
          f"{sum(s == 'not present' for _, s, _, _ in results)} not present")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
