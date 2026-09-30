<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criteria 1 to 13 (the `review` routing cases: routine plan → `split`, planner L3 / step L4 / Merge step / two planner results / `## Plan review` → `review L1`, pass → `split`, replan → `replan`, two replans → `stop`, blocked → `stop`, pass before a newer plan → `review L1`, `unresolved:` → `stop`, and the split refusal): pass. Evidence: I ran each command span verbatim from the handoff with `SDLC_BASE_SHA` set, and all exited 0. Criterion 13 leaves no `step-1`.
- `steps.py selftest 2>&1 | grep -q 'ok: (r'`: pass, but the predicate is weak. Evidence: exit 0 here, but the base worktree at 0d15d3f already prints 3 `ok: (r` lines, so this grep cannot go red on its own. I counted the new cases in the built tree: 22 `ok: (r) ...` lines matching review or split refusal, 28 `(r` lines in total, against 3 at base. The new cases cover each rule, and the diff shows a negative form for each (steps.py selftest section `(r)`).
- `grep -qF 'steps.py review'` in chain, conductor, plan: pass. Evidence: exit 0. Diff lines are present in chain section 3, the conductor bullet, and plan step 5.
- `plan-reviewer-L1.md` and `plan review:` in handoff-format: pass. Evidence: exit 0. The diff shows the layout line and the `## Plan review` paragraph entries.
- `review <task dir>` in `docs/maintenance/sdlc-internals.md`: pass. Evidence: exit 0. The diff shows both the `steps.py` entry and the `run.sh` plan-reviewer family rule.
- `grep -qF "'steps.py review'" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exit 0. The diff shows the route dict entries and docstring item 11.
- (guard) `steps.py selftest`: pass. Evidence: rc 0. Bite check: at base, `steps.py review` fails with "invalid choice", and `split` of a replan-rejected plan writes `step-1`. So the new cases have something to catch.
- (guard) `check.py plugins/sdlc-lite`: pass. Evidence: rc 0.
- (guard) scope diff against `$SDLC_BASE_SHA`: pass. Evidence: rc 0. `git status` shows only the 7 allowed files modified, and no untracked files outside `.sdlc`.
- The chain section 4 resume paragraph addition: pass. Evidence: line 43 of chain/SKILL.md reads "plan but no `step-<n>/` dir returns to section 3 (`steps.py review`)".
- `RESULT_LEVEL_RE` widened, `review` in the docstring and argparse, `import json`: pass. Evidence: steps.py diff. `steps.py review <dir>` runs through argparse in the criterion runs.
- `git diff --check`: pass. Evidence: clean, no output.
- Builder claim of a pre-existing codex_roles drift: not checked and not a criterion here. Not part of this step.

## Out of scope changes
None. All 7 modified files are in the handoff's Files list. The temp worktree I created is removed, and `git worktree list` shows none under tmp.

## For the next attempt
None
