<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/docs/reports/2026-10-12-plan-merge-replay.md`: added `## Independent replay` before `## Follow-up` (who ran it, the table with the `Run` column, the four first-return blocks with their lint output, one comparison line), and a pointer sentence after "It is unverified: not an independent run."

## Checks
- Criterion 1 (heading, table header with `Run`, four `independent` rows): exit 0.
- Criterion 2 (guard: original sentence and first table header kept, no trailing whitespace): exit 0.
- Criterion 3 (guard: scope against `a3e2cd9b`): exit 0.
- `git diff --check`: exit 0.
- `plan_check.py goal`, old-skill block on first return: exit 0, 0 FAIL, last line `ok: goal plan passes`.
- `plan_check.py goal`, new-skill block on first return: exit 0, 0 FAIL, last line `ok: goal plan passes`.
- `plan_check.py fanout`, old-skill block on first return: exit 1, 1 FAIL (`overlap`), last line `warn no-budget: T-0499 has no budget_usd; set one with budget.py set`.
- `plan_check.py fanout`, new-skill block on first return: exit 1, 1 FAIL (`overlap`), last line the same.
- `fanout.py run --dry-run a=T-0498 b=T-0499 --lane auto --max-lanes 2 --gate "python3 plugins/sdlc-lite/scripts/check.py"`: exit 0 on both runs.

## Notes
- The independent counts match the first table on every row: goal 3 warn lines and 0 refusals, fanout 1 warn line and 1 refusal, old and new.
- The new-skill runs are not independent of the old-skill runs. One reader did both, and the new references carry the same goal field list and lane rules, so the new blocks are the same as the old ones (the goal block differs in one phrase naming the cap source).
- The new fanout block was written from the skill text without using the overlap refusal the old run had already shown me. The equal refusal count is therefore not a second discovery; the report says so.
- Order was kept: both old blocks were linted and written into the report before `plugins/sdlc-lite/skills/plan/SKILL.md` or its references were opened, and the first Result table was read only after all four runs were written.
- The Questions cells count the `warn` lines I returned in place of questions under `SDLC_HEADLESS=1`. That count is my reading of each skill's missing inputs, not script output.
- `steps.py lane` and the dry runs wrote `skips.md` in the T-0498 and T-0499 folders; both were removed. No plan artifact was written to the tree, and nothing was committed.
