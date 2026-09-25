<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/planner.md`: the brief now reads `step-*/builder-*.md` and `step-*/verifier-*.md` and names every replan trigger. Added a `## Criteria that can pass` section before the output format with the 5 rules: red now or `(guard)` green now, criteria must hold together, "no new findings versus the base commit", no broken command in a span, and the replan reads `## Plan review`.
- `plugins/sdlc-lite/agents/builder.md`: rule 3 now covers a defective criterion. Status is blocked, Notes starts with `plan defect: <criterion> <why>`, the work stays in the tree, and the builder never reports done.
- `plugins/sdlc-lite/agents/verifier.md`: new paragraph after "A criterion with no evidence fails". A criterion that cannot pass gives a fail, and `## For the next attempt` starts with `plan defect:`. The verifier never passes a criterion on its intent.
- `plugins/sdlc-lite/agents/conductor.md`: line 21 now says a `plan defect:` note from the builder, the verifier, or a split refusal means a planner L3 replan, never a rebuild or a bump.
- `plugins/sdlc-lite/skills/chain/SKILL.md`:
  - Step 3: a split refusal is appended under `## Plan review`, then planner L3 runs and the split runs again. After the second refusal it stops and asks the user. The same applies to the split in 4.2.
  - 4.2: a blocked builder is never rerun and never gets `## Previous attempt`.
  - 4.4: a fail tagged `plan defect:` takes the 4.2 replan path, with no rebuild and no bump, and it does not count as a fail.
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: line 25 says a tagged fail or block goes to replan and never counts toward a bump. The Planner L3 "Fits when" cell lists the replan triggers. No model or effort cell changed.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the task handoff template has an optional `## Plan review` section. The step handoff section says `## Previous attempt` is added only after a verifier fail that is not a plan defect.
- `plugins/sdlc-lite/scripts/check.py`: new `PLAN_DEFECT_DOCS` guard for the three phrases (`plan defect`, `Plan review`, `no new findings`) in the named files. The docstring list gains item 4 (the existing long-run check, which was not listed) and item 5 (this guard).
- `CLAUDE.md`: new Decisions bullet for the plan-defect route. The "Escalation is enforced by `/chain` instructions, not by code" sentence now names the `steps.py split` lint as the exception.
- `.claude/agents/sdlc-lite-author.md`: one new invariant to keep the plan-defect route in sync across its files.

## Checks
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. All selftests, shellcheck, and plugin validate were ok.
- Negative control, copy without the perl edit: `check.py` exit 0.
- Same copy after the perl edit: exit 1, with `FAIL agents/verifier.md: plan-defect route missing "plan defect"`.
- `grep -c "plan defect"`:
  - chain SKILL.md: 3.
  - builder, verifier, conductor, and the author agent: 1 each.
  - planner: 3. level-rubric, handoff-format, and CLAUDE.md: 2 each.
  - No `:0` line.
- `grep -n "no new findings" plugins/sdlc-lite/agents/planner.md`: matched line 17. `grep -cF` counts for `(guard)`, `## Plan review`, and `step-*/builder-*.md` in planner.md: 1, 2, 2.
- `grep -n "Plan review"` in handoff-format: line 89. That is between `## Task handoff` (line 71) and `## Step handoff` (line 93), so it sits inside the task handoff template.
- `git diff HEAD --stat -- plugins/sdlc-lite/scripts/run.sh`: empty. `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 18 role levels, 8 agents checked`, exit 0.
- Live run:
  1. `git worktree add --detach /var/folders/.../tmp.hUS5twxQGs/wt HEAD`.
  2. Wrote `.sdlc/t/step-1/handoff.md` there: `level: L1`, Do creates `marker.txt` with the line `marker`, and two criteria that contradict each other (`grep -c '^marker$' marker.txt` prints `1`; `test -e marker.txt` exits 1).
  3. From inside that tree ran `/Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets11/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/t/step-1/handoff.md`: exit 0.
  4. `builder-L1.md` began:
     ```
     <!-- role=builder level=L1 model=sonnet effort=low -->
     ## Status
     blocked
     ...
     ## Notes
     plan defect: criteria 1 and 2 contradict each other. ...
     ```
  5. Then `git worktree remove --force <tmp>`. `git worktree list` shows only the two repo worktrees; a grep for `/tmp` or `/var/folders` matched nothing.

## Notes
- **Live run used this tree's `run.sh`.** The Do's own reason for "this tree's run.sh" is that the edited builder.md must be the one used. A throwaway at `HEAD` does not contain the uncommitted edits, so its copy of `run.sh` would load the old builder.md. I therefore ran this worktree's `run.sh` by absolute path from inside the throwaway tree. `run.sh` resolves `plugin_root` from its own path, so the edited agents were loaded. The verifier should repeat the run the same way unless these changes are committed first.
- **Extra docstring item.** The check.py docstring gains an item 4 for the existing long-run check, so the new guard's item 5 fits into a complete list. That is a docstring-only addition.
- **Step 1 changes are also in the diff.** The uncommitted changes to `steps.py`, `skills/plan/SKILL.md`, the CLAUDE.md `steps.py` bullet, and the task handoff's `## Plan review` come from step 1, not this step.
