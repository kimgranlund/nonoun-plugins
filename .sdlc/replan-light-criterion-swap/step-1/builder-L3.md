<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: new `swap <step dir> [--timeout SECONDS]` subcommand, plus `swap_pair`, `earlier_swap`, `section_lines_start` and `list_item` helpers and `swap`/`cmd_swap`. `criteria_lines` now delegates to a new `criteria_indexed`, so swap uses the same region rule with line indices. `next_action` routes a plan-defect fail with one pair and no earlier swap to `swap L<build level>` (the reason names `steps.py swap`), and every other plan defect still goes to `replan`. The module docstring has a new `swap` paragraph and the updated `next` rules. Added 23 selftest cases: 18 `ok: swap: ` and 5 `ok: next swap: `.
- `plugins/sdlc-lite/agents/verifier.md`: new swap-rule paragraph right after the `plan defect:` sentence.
- `plugins/sdlc-lite/scripts/check.py`: `swap old:` and `swap new:` entries added to `PLAN_DEFECT_DOCS` (verifier.md, steps.py), and docstring item 5 now names the swap.

## Checks
- All 14 acceptance criteria, each run verbatim with `bash -c` from the repo root (extracted from the handoff by a small python loop): 14 of 14 PASS.
  - The swap applies and the sibling guard line stays.
  - `next` prints `swap L2`.
  - A replacement that is red now refuses, writes nothing, and ends with a `plan defect:` line.
  - A replacement that drops `(guard)` refuses.
  - A second swap on the same step goes to `replan` (guard).
  - The selftest prints `^ok: swap: ` and `^ok: next swap: ` lines, and the full selftest passes.
  - The four greps find their text.
  - The check.py negative control prints `agents/verifier.md: plan-defect route missing "swap old:"`.
  - `check.py plugins/sdlc-lite` passes (guard).
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: `steps selftest: PASS`.
- Mutation test on a temp copy of steps.py, with the `(guard)` tag check and the swap tree-change check both disabled: the selftest went red on both tag-mismatch cases and on the tree-change case, so the new cases can fail.
- `plugins/sdlc-lite/scripts/check.sh`: rc=0 (all selftests, shellcheck, and plugin validate ok).

## Notes
- The handoff did not name `plugins/sdlc-lite/scripts/check.sh`; I ran it only because CLAUDE.md asks for it after a script change.
- `next` can now print a new action, `swap L<n>`. /chain, the conductor, and any board rendering do not route it yet; the planner scoped that to step 2 ("Route `swap` in /chain and the conductor").
- Refusal last line format: `plan defect: steps swap refused: <why>; replan this step (/chain 4.2)`.
- Refusals for a missing dir or handoff use the same format.
- An invalid `--timeout` gets a plain argument error, like `--guard-timeout`.
- For an extra hint, the `replan` reason in `next` now says why a proposed swap was not routed (an earlier swap exists, or the swap lines are malformed). The action itself is still `replan`.
- A stray first shell command in my criteria run tried to redirect into a file under `$SDLC_TMP_WORKTREES`. It failed ("no such file or directory") and created nothing.
- Nothing is committed (this is not a merge step).
