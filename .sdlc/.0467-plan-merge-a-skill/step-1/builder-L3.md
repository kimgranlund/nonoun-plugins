<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/plan/SKILL.md`: rewritten as the kind router plus shared procedure (68 lines, 5886 bytes).
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/plan/references/plan-rules.md`: new, 60 lines; shared rules, the kind-to-lint map, and the goal and doc kind lines.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/plan/references/steps.md`: new, 15 lines; the dispatch procedure moved whole from the old SKILL.md lines 12 to 20.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/plan/references/goal.md`: new, byte copy of `plan-goal/references/goal-rules.md`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/plan/references/doc.md`: new, byte copy of `plan-doc/references/plan-doc-format.md`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/plan/references/campaign.md`: new, 70 lines; `campaign-rules.md` plus four kind-only lines.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/plan/references/fanout.md`: new, 29 lines; `fanout-rules.md` plus Gather, Group the lanes, Check and return.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/plan/evals/README.md`: new, plus the five pairs `01-goal`, `02-fanout`, `03-doc`, `04-steps`, `05-campaign` (`.ask.md` and `.expected.md` each).
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: one row added after the "Plan a goal, loop, or fanout run" row; existing rows unchanged.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/plugins/sdlc-lite/scripts/check.py`: docstring item 57 "Plan kinds (T-0467)" and its block `plan_kinds_bad` with inline controls, placed after item 56.

## Checks
- `python3 plugins/sdlc-lite/scripts/check.py`, first run: exit 1, six `broken links: unlisted broken link plugins/sdlc-lite/skills/plan/SKILL.md -> references/<file>.md` findings from item 32. Fixed by writing the six reference paths in SKILL.md as code spans instead of Markdown links; second run exit 0.
- `prompt_lint.py` over the named files, first run: exit 1, `P-2 skills/plan/references/fanout.md: line 7: fanout.py has no flag "--help"`. Fixed by rewording that label; the rerun is criterion 10.
- Criterion 1 (`F=plugins/sdlc-lite/skills/plan; for f in references/plan-rules.md ...`, seven files and five eval pairs): exit 0.
- Criterion 2 (`grep -qF "steps|doc|goal|campaign|fanout" ...`, dry-run line, Reserved first word, 90 lines, 7168 bytes): exit 0.
- Criterion 3 (`for p in "## 1. Gather" "plan_check.py" ...`, 19 phrases in SKILL.md): exit 0.
- Criterion 4 (`d=$(grep -m1 "^description:" ...)`, length and eight trigger phrases): exit 0.
- Criterion 5 (`cmp -s` for `goal.md` and `doc.md`): exit 0.
- Criterion 6 (`plan-rules.md` at most 60 lines with eight phrases; steps, campaign, fanout at most 70 lines; both headings): exit 0.
- Criterion 7 (`steps.md` six phrases): exit 0.
- Criterion 8 (`grep -qF "| Plan by kind: ... | plan <kind> |"`): exit 0.
- Criterion 9 (`grep -qF "T-0467" "$C" && ... && python3 "$C"`): exit 0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
- Criterion 10 (`prompt_lint.py` on the named files, `python3 scripts/check-packaging.py`, `plan_check.py selftest`, no summary flag under the folder): exit 0, `plan_check selftest: PASS (252 checks)`.
- Criterion 11 (guard, `grep -qF "plan-reviewer" ...` and the kept entry rows): exit 0.
- Criterion 12 (guard, scope diff against `$SDLC_BASE_SHA`): exit 0, run with `SDLC_BASE_SHA` exported from `step-1/base-sha` (a3e2cd9b273ade52a66978f8e1938ad8e7fae948) because the variable was empty in the shell.
- `git diff --check`: exit 0.

## Notes
- SKILL.md names its six reference files as code-span paths, not Markdown links. `check.py` item 32 (broken-link baseline) reads `git ls-files`, so a link from the tracked SKILL.md to an untracked `references/*.md` counts as broken until the files are tracked. The verifier and step 2 run `check.py` in this same untracked state, and the code-span form keeps it green there. `campaign.md` holds one in-folder link, `[the goal rules](goal.md)`, and `plan-rules.md` links the five kind files; both resolve once tracked.
- `references/fanout.md` is not byte-identical to `fanout-rules.md` in its first 17 lines: the Spec row label changed from `fanout.py --help` to "the `fanout.py` usage text", because `prompt_lint.py` P-2 rejects that flag. Only `goal.md` and `doc.md` are pinned by `cmp`.
- `goal.md` and `doc.md` are byte copies, so the goal and doc kind-only Gather and Write lines of the old skill bodies had no reference home. They sit in `plan-rules.md` under "Goal and doc lines", which is a small extension of handoff item 2.
- The handoff says the cost line uses "the ticket sizes `tickets.py check` lists". `tickets.py --root .sdlc check` prints no sizes, so the skill text says to compute the cost from `TIERS` in `budget.py` and each ticket's `size:` after `tickets.py check` passes.
- The dry run's `lanes:` line for campaign follows the design (`fanout.py run --dry-run`); the old campaign skill never ran that command.
- The five-ask replay in the ticket's Done when is not a criterion of this step and has not run. The question counts in the `.expected.md` files are expectations from the skill text, as the evals README states.
- No `(red)` criterion, so no `redck.py` record was owed. Nothing is committed or staged; the new files are untracked. `check.sh` was left to step 2.
