<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 seven reference/eval files exist, five ask/expected pairs with `Kind: <kind>` on line 1: pass. Evidence: ran the command with `SDLC_BASE_SHA` exported, exit 0. Line counts read with `wc -l`: all files present; `evals/0*.expected.md` hold `Kind: goal|fanout|doc|steps|campaign` (read 01 and 04).
- #2 SKILL.md kind list, `Dry run (<kind>)`, `Reserved first word:`, at most 90 lines and 7168 bytes: pass. Evidence: exit 0; `wc -lc` gives 68 lines, 5886 bytes; read SKILL.md lines 16, 18, 56 to 62.
- #3 nineteen required phrases in SKILL.md: pass. Evidence: exit 0, no `MISSING` line printed.
- #4 description at most 1024 characters with the eight trigger phrases: pass. Evidence: exit 0, `${#d}` = 806.
- #5 `goal.md` and `doc.md` are byte copies: pass. Evidence: `cmp -s` pair, exit 0.
- #6 plan-rules at most 60 lines with eight phrases, steps/campaign/fanout at most 70 lines, both headings: pass. Evidence: exit 0; line counts 60, 15, 70, 29.
- #7 steps.md carries the dispatch procedure phrases: pass. Evidence: exit 0; read `references/steps.md`: step 3 holds `dispatch.py prepare planner`, `--transcript`, `SDLC_BACKEND=codex`, and step 5 holds the `steps.py review` routes. Diffed against the old SKILL.md lines in `git diff a3e2cd9b`: the old text is moved whole.
- #8 entry row: pass. Evidence: exit 0; `git diff` shows the single added row after the "Plan a goal, loop, or fanout run" row, with no other row touched.
- #9 check.py item 57: pass. Evidence: exit 0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`. The item's inline controls (each phrase removed, each kind reference removed, harness reference added, entry route removed, each file missing) run on every `check.py` run and would print "plan kinds negative control not flagged" when vacuous; none printed. An external mutant in a throwaway worktree could not be run: the stray-worktree hook blocked `git worktree add` because `SDLC_TMP_WORKTREES` is unset in this session. The in-run controls are the red observation for the gate.
- #10 prompt_lint on the named files, check-packaging, `plan_check.py selftest`, no summary flag under the folder: pass. Evidence: exit 0, `plan_check selftest: PASS (252 checks)`. Extra: `prompt_lint.py` default set `73 files, 0 errors`.
- #11 (guard) plan-reviewer, steps.py review, entry-skill path in plan SKILL.md and the old entry rows kept: pass. Evidence: exit 0.
- #12 (guard) scope diff against `$SDLC_BASE_SHA`: pass. Evidence: exit 0, empty output. Tracked changes outside the exclusions: none; untracked outside `.sdlc` and `skills/plan`: none. `git status` shows only `check.py`, `skills/plan/SKILL.md`, `skills/sdlc-lite/SKILL.md` modified.

## Out of scope changes
None. `git status --short` and the criterion 12 guard show only the three allowed tracked files plus `skills/plan/references` and `skills/plan/evals` (untracked, in scope) and `.sdlc` records. `plan-goal`, `plan-campaign`, `plan-doc`, `plan-fanout`, `plan-loop`, `plan-verification` and `plan_check.py` are untouched. The builder's extra "Goal and doc lines" in `plan-rules.md` stays within the 60-line cap and sits in the folder the step owns. Dismissed as harmless: `git grep -n "skills/plan/"` outside `check.py` found no other pinning dependent. `claude_roles.py generate --check` and `codex_roles.py generate --check` both pass. `git diff --check` is clean.

## For the next attempt
None
