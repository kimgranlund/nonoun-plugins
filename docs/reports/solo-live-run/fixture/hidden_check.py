#!/usr/bin/env python3
"""Hidden check for the slugify max_length ticket. Usage: hidden_check.py <project dir>. Exit 0 pass, 1 fail."""
import subprocess
import sys

project = sys.argv[1]
sys.path.insert(0, project)
results = []


def case(name, fn):
    try:
        ok = fn()
    except Exception as e:  # noqa: BLE001
        ok = False
        name += f' ({type(e).__name__}: {e})'
    results.append((name, bool(ok)))


def raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


import strkit  # noqa: E402
from strkit import slugify  # noqa: E402

case('default unchanged', lambda: slugify('  Hello,  World! ') == 'hello-world')
case('max_length None unchanged', lambda: slugify('Hello World Again', max_length=None) == 'hello-world-again')
case('fits exactly', lambda: slugify('Hello World', max_length=11) == 'hello-world')
case('cut at boundary 11', lambda: slugify('Hello World Again', max_length=11) == 'hello-world')
case('cut at boundary 12', lambda: slugify('Hello World Again', max_length=12) == 'hello-world')
case('cut mid word 6', lambda: slugify('Hello World', max_length=6) == 'hello')
case('long limit', lambda: slugify('Hello World Again', max_length=100) == 'hello-world-again')
case('first word too long', lambda: slugify('Supercalifragilistic word', max_length=5) == 'super')
case('limit 1', lambda: slugify('a b', max_length=1) == 'a')
case('custom sep', lambda: slugify('Hello World', sep='_', max_length=8) == 'hello')
case('empty text', lambda: slugify('', max_length=5) == '')
case('zero raises', lambda: raises(lambda: slugify('Hello World', max_length=0)))
case('negative raises', lambda: raises(lambda: slugify('Hello World', max_length=-3)))
case('zero raises on empty text', lambda: raises(lambda: slugify('', max_length=0)))
case('helper exported', lambda: 'truncate_at_boundary' in strkit.__all__)
case('helper boundary', lambda: strkit.truncate_at_boundary('hello-world-again', 11, '-') == 'hello-world')
case('helper unchanged', lambda: strkit.truncate_at_boundary('ab-cd', 5, '-') == 'ab-cd')
case('helper hard cut', lambda: strkit.truncate_at_boundary('abcdefgh-ij', 4, '-') == 'abcd')
case('helper raises', lambda: raises(lambda: strkit.truncate_at_boundary('ab', 0, '-')))

r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'], cwd=project,
                   capture_output=True, text=True)
tail = (r.stderr.strip().splitlines() or [''])[-1]
results.append((f'project tests ({tail})', r.returncode == 0))

for name, ok in results:
    print(('PASS ' if ok else 'FAIL ') + name)
failed = sum(1 for _, ok in results if not ok)
print(f'hidden_check: {len(results) - failed}/{len(results)} passed')
sys.exit(1 if failed else 0)
