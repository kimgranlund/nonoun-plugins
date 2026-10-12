<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/docs/reports/2026-10-12-plan-merge-replay.md` created (the replay report).
- `steps.py lane` wrote `.sdlc/0498-planner-run-each-criterion/skips.md` and `.sdlc/0499-close-skips-for-ran-roles/skips.md` during the replay; I removed both, so there is no net change outside the report.

## Checks
All commands ran from the tree root with `SDLC_BASE_SHA=a3e2cd9b273ade52a66978f8e1938ad8e7fae948`.

Replay:
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0, `ok: 493 tickets, roadmap current`; the roadmap holds 0 ready tickets.
- `python3 plugins/sdlc-lite/scripts/steps.py lane <task dir>` for T-0498 and T-0499: exit 0, both print `solo`.
- `plan_check.py goal`, old-skill block, first return: exit 0, last line `ok: goal plan passes`, 0 FAIL lines, 1 warn (`no-measure`).
- `plan_check.py goal`, new-skill block, first return: exit 0, same output.
- `plan_check.py fanout`, old-skill block, first return: exit 1, 1 FAIL (`overlap`), last line `warn no-budget: T-0499 has no budget_usd; set one with budget.py set`.
- `plan_check.py fanout`, new-skill block, first return: exit 1, same output.
- `plan_check.py fanout` after adding `--allow-overlap`: exit 0, `ok: fanout plan passes`.
- `fanout.py run --dry-run a=T-0498 b=T-0499 --lane auto --max-lanes 2` (and again with `--allow-overlap --gate ...`): exit 0, no refusal.

Acceptance criteria:
- Criterion 1 (report exists with T-0467, the table header, the unverified line, both `Dry run` strings): exit 0.
- Criterion 2 (the four `| <ask> | <skill> |` rows): exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: exit 0.
- (guard) `python3 scripts/check-packaging.py`: exit 0, PASS.
- (guard) `python3 plugins/sdlc-lite/scripts/plan_check.py selftest`: exit 0, PASS (252 checks).
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs scripts`: exit 0.
- (guard) scope test (tracked diff plus untracked files outside the allowed paths): exit 0.
- `grep -nE '[[:space:]]+$|—'` over the report and the untracked `plan/evals/*` and `plan/references/*`: no matches.

## Notes
- The replay shows no difference between old and new: goal is 3 warn-questions and 0 refusals for both; fanout is 1 warn-question and 1 refusal for both.
- The same builder wrote the old and the new blocks, so the identical rows are by construction. The report states "unverified: not an independent run" and carries a follow-up line for an independent replay (the T-0495 pattern).
- No ticket was ready, so the handoff's fallback applied: proposed tickets T-0498 and T-0499 (both L1) filled the placeholders. `fanout.py run --dry-run` did not refuse the pair, so the `lanes:` line is its output, not a refusal.
- The goal Questions cell counts 3 warn lines: money cap, authorization, and the measure gap from plan-verification. `01-goal.expected.md` expects 2 because it counts only the skill's own.
- The fanout refusal is `FAIL overlap`: both tickets cite `docs/reports/2026-10-12-fleet-retro-12.md` as evidence and neither edits it. `fanout.py run --dry-run` prints `overlap (planned scope): none` for the same pair. The report lists this mismatch as a second follow-up.
- The "First-return lint" cell for fanout is a `warn no-budget` line, because that is the lint's last line; the FAIL text is in the report's row notes.
- The `Dry run (fanout)` block in the report is the post-fix one (with `--allow-overlap`). Its `lanes:` text is verbatim up to the `gate 1:` line; the five driver, close and logs lines after it are left out, and the report says so.
- The `cost:` line reads `$10 of $unknown ... ; warn: no cap given`. The plan rules define `unknown` for a missing ticket size, not a missing cap, so this form is my choice.
- The kinds steps, doc and campaign were not run, as the handoff allows; the report lists them as not run.
- No `(red)` criterion in the handoff, so `redck.py record` was not run. Nothing was committed.
