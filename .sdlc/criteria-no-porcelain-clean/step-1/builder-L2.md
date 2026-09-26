<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: four changes.
  - Added `requires_clean_status()` and the regexes it uses (`STATUS_RE`, `PORCELAIN_RE`, `PATHSPEC_RE`, `EMPTY_TEST_RE`).
  - Added a new finding in `lint_steps`, with a second line pointing the planner to `git diff --quiet HEAD -- <path>` plus `git ls-files --others --exclude-standard -- <path>`.
  - Extended the `lint` paragraph of the module docstring.
  - Added selftest case `(k6)` after `(k5)`.

## Checks
- Criterion 1 (the three bad spans each get a "clean porcelain status" finding): exit 0
- Criterion 2 (guard: the four allowed spans get no finding): exit 0
- `grep -q "(k6)" plugins/sdlc-lite/scripts/steps.py`: exit 0
- `grep -qF "clean porcelain status" plugins/sdlc-lite/scripts/steps.py`: exit 0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0, PASS, all 7 `(k6)` lines ok
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0

## Notes
- The `(k6)` ok-spans case runs `lint` only. It does not also run `split` as `(k5)` does, because the handoff asked for `lint` with `steps lint: ok`.
- A span counts as path-scoped only when a standalone `--` sits in the same `git status` command segment, meaning before any `|`, `;`, `&`, `)` or backtick.
