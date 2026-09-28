<!-- role=builder level=L1 model=sonnet effort=low -->
All checks pass. This is a small L1 step, no repo-wide gate needed beyond the selftest which passed.

## Status
done

## Changes
- plugins/sdlc-lite/scripts/steps.py: dropped lone `|` from `ends_command`'s fail-fast operators, updated its docstring and `or_fallback`'s docstring, added two refuse controls in the (k2) selftest block for piped exit forms.

## Checks
- `d=$(mktemp -d) && ... 'test -f a || exit 1 | cat' ... steps.py lint ... | grep -q "plan defect"` → PASS
- `d=$(mktemp -d) && ... 'test -f a || { echo x; exit 1; } | cat' ... steps.py lint ... | grep -q "plan defect"` → PASS
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` → all ok, `steps selftest: PASS`

## Notes
None
