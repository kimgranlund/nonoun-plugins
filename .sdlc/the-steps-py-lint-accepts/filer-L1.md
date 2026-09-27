<!-- role=filer level=L1 model=sonnet effort=medium -->
All checks pass: builder done, verifier pass with independent evidence on both new criteria plus a negative control on the selftest guard. Single step, no plan review issues.

## Warnings
None

## PR title
T-0137: Stop the steps.py `||` lint from accepting a piped fail-fast exit

## PR body
Summary: The `steps.py` `||` lint's fail-fast check treated `exit N` followed by a pipe (e.g. `test -f a || exit 1 | cat`) as a valid fallback. That's actually `a || (exit 1 | cat)`, which returns cat's exit status (0), so a criterion using this form passed even when the left-hand check failed.

Changes:
- `plugins/sdlc-lite/scripts/steps.py`: dropped the lone `'|'` from `ends_command`'s fail-fast operator tuple, so `exit N` (or a `{ ...; exit N; }` group) followed by a pipe no longer counts as fail-fast. Updated `ends_command`'s docstring and added a clause to `or_fallback`'s docstring explaining that a piped exit stays a finding.
- Added two refuse controls to the `(k2)` selftest block: `test -f a || exit 1 | cat` and `test -f a || { echo x; exit 1; } | cat`. Existing pass controls (bare `exit 1`, loop/brace forms, `&&` after exit) are unchanged and still pass.

How verified: Builder (L1) ran the two new lint acceptance criteria and the full `steps.py selftest`, all green. Verifier (L1, independent) reran both criteria against the built tree (rc=0, "plan defect" emitted) and confirmed each fails at pre-change HEAD (rc=1, no defect caught) in a throwaway worktree — proving the fix actually changes behavior rather than being vacuously true. The verifier also ran a negative control on the selftest guard: reintroducing the lone `'|'` into `ends_command` in a throwaway worktree made the new refuse controls fail, confirming they detect the old behavior. Verdict: pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Fixed: `steps.py`'s `||` acceptance-criterion lint no longer accepts a piped fail-fast exit (`... || exit 1 | cat`), which previously let such a criterion pass even when its left-hand check failed.

## Follow-ups
None
