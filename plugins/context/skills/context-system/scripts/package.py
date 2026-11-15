#!/usr/bin/env python3
"""Write the consumer's copy of this skill and check that nothing in it points at what was left out.

Usage: package.py --out DIR

Left out: tests/, fixtures/, evals/, README.md (maintenance), this script, the skill's own vocabulary.json,
profile.json and suite.json, and the performance contract among the earlier routing references. DIR must not exist. After copying, check_links.py
runs on DIR with --strict; a consumer file that still names an author-only path fails the packaging (exit 1) and DIR is
kept for inspection. Standard library only; runs on Python 3.9.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_ONLY = ('tests', 'fixtures', 'evals', 'README.md', 'vocabulary.json', 'profile.json', 'suite.json', 'scripts/package.py',
               '/'.join(('references', 'routing', 'earlier', 'performance-contract.json')))
NOISE = ('__pycache__', '.DS_Store', '.git')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    if args.out.exists():
        print(f'{args.out}: already exists', file=sys.stderr)
        return 2
    skip = {ROOT / p for p in AUTHOR_ONLY}

    def ignore(folder, names):
        return [n for n in names if n in NOISE or Path(folder) / n in skip]
    shutil.copytree(ROOT, args.out, ignore=ignore)
    files = sum(1 for p in args.out.rglob('*') if p.is_file())
    check = subprocess.run([sys.executable, '-B', str(args.out / 'scripts' / 'check_links.py'), '--root', str(args.out), '--strict',
                            '--orphans', 'references,templates,schemas,examples,scripts', '--also', 'tests,fixtures,evals'],
                           capture_output=True, text=True)
    sys.stdout.write(check.stdout)
    print(f'package: {files} file(s) in {args.out}; {"ok" if check.returncode == 0 else "the copy points at something it does not carry"}')
    return check.returncode


if __name__ == '__main__':
    sys.exit(main())
