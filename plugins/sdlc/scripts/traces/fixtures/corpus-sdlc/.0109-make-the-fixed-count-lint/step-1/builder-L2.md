<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc/scripts/steps.py: in `COMPARE_RE`, a lone `=` now counts as a comparison only when whitespace comes before it (`(?<=\s)=`). Added one sentence to the `lint` docstring naming `n=26`. Added the `(k6)` selftest group: one pass case and four refusal forms.
- CLAUDE.md: the `scripts/steps.py` Layout bullet now has the bare `=` / `n=26` clause.

## Checks
- c1 `fixed_set_count("n=26; ls x* | wc -l")` is false: exit 0
- c2 `export N=26; find ... | grep -c x` is false: exit 0
- c3 (guard) `-eq 26` still flagged: exit 0
- c4 (guard) ` = 26` still flagged: exit 0
- c5 (guard) `[ $n == 26 ]` still flagged: exit 0
- `steps.py selftest | grep -q "^ok: (k6)"`: exit 0. The pass case and all four refusal cases each printed `ok: (k6) ...`.
- (guard) `(k4) lint refuses ...` line present: exit 0
- `"n=26" in steps.__doc__`: exit 0
- `grep -q 'n=26' CLAUDE.md`: exit 0
- `bash plugins/sdlc/scripts/check.sh`: exit 0 (all selftests, shellcheck, plugin validate PASS)
- (guard) no other tracked files changed under plugins/CLAUDE.md/.claude: exit 0
- (guard) no untracked files under plugins/CLAUDE.md/.claude: exit 0

## Notes
None
