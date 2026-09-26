<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0088: board.py shows stop for consecutive no-verdict verifier results

## PR body
### Summary
`/board` said "rerun verify" for a step whose last two or more verifier results had no pass/fail verdict. `steps.py next` returns `stop` for that case. The board row now says the step is stopped and asks the user, so the two agree. A single no-verdict result still says "rerun verify".

### Changes
- `plugins/sdlc-lite/scripts/board.py`: the no-verdict branch of `step_row` counts consecutive no-verdict verifier results after the newest build. It stops counting at the first result with a pass or fail verdict.
  - Two or more give a 🟡 row: `stop · no verdict xN · builder … · verifier …, ask the user`.
  - One keeps the existing `no verdict … rerun verify` row.
- The `board.py` docstring describes the new rendering.
- The selftest has three new cases:
  - (a) one no-verdict result;
  - (b) two in a row;
  - (c) a fail, then a rebuild, then no-verdict results. Only the results after the newest build count.
- `steps.py` is untouched. CLAUDE.md and `skills/board/SKILL.md` don't describe the board's no-verdict rendering, so neither changed.

### Verification
The verifier (L1) passed every criterion:
- `grep -q "ask the user"` on `board.py`.
- `board.py selftest` printed `board selftest: PASS`, with `ok:` lines for the one-result, two-result and fail-then-rebuild cases.
- `steps.py selftest` exited 0.
- `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/steps.py` exited 0.
- `plugins/sdlc-lite/scripts/check.sh` exited 0.
- The verifier changed `n >= 2` to `n >= 99` in a throwaway worktree. The two-in-a-row and after-rebuild cases then failed, and the single-result case stayed ok. So the new cases can go red.

## Changelog entry
- `/board` now shows a step as stopped ("ask the user") when its last two or more verifier results have no verdict, matching `steps.py next`. A single no-verdict result still reads "rerun verify".

## Follow-ups
None
