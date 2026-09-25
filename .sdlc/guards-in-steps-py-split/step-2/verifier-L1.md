<!-- role=verifier level=L1 model=sonnet effort=medium -->
No diff — handoff-format untouched, confirmed by empty diff (guard's own check already passed above; this confirms via git diff directly rather than just git status).

## Verdict
pass

## Criteria
- `grep -q "changed the work tree" CLAUDE.md`: pass. Evidence: ran the exact command in the tree, exit 0.
- `grep -q "changed the work tree" .claude/agents/sdlc-lite-author.md`: pass. Evidence: ran the exact command, exit 0.
- `grep -q "changed the work tree" plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: ran the exact command, exit 0.
- `grep -q "changed the work tree" plugins/sdlc-lite/agents/planner.md`: pass. Evidence: ran the exact command, exit 0.
- `grep -q "'changed the work tree'" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: ran the exact command, exit 0; `git diff plugins/sdlc-lite/scripts/check.py` shows exactly the one-line `PLAN_DEFECT_DOCS` entry the handoff specified, byte for byte.
- `(guard) plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: ran `bash plugins/sdlc-lite/scripts/check.sh`, all sections `ok`/`PASS`, exit 0. Bites: copied the new `check.py` (with the `'changed the work tree'` PLAN_DEFECT_DOCS entry) into a throwaway `git worktree add --detach /tmp/vwt/check-red HEAD` (pre-step docs), ran it, got `FAIL agents/planner.md / skills/chain/SKILL.md / scripts/steps.py: plan-defect route missing "changed the work tree"`, exit 1 — confirmed red, then removed the worktree.
- `(guard) python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -n1 | grep -qx 'steps selftest: PASS'`: pass. Evidence: ran it, printed `steps selftest: PASS`, grep matched.
- `(guard) test -z "$(git status --porcelain --untracked-files=all -- plugins/sdlc-lite/skills/handoff-format)"`: pass. Evidence: ran the command (empty output, test succeeded) and independently confirmed with `git diff --stat plugins/sdlc-lite/skills/handoff-format` (no output) — the merge-step template copy in handoff-format was not touched, matching the criterion's stated intent.

## Out of scope changes
`.sdlc/guards-in-steps-py-split/handoff.md` (Goal/Context/Constraints filled in) and the untracked `planner-L2.md`, `runs.jsonl`, `step-1/`, `step-2/` under the same task dir. Checked: `builder-L1.md`'s "Clarify (unattended)" note plus the file's content match a task-level clarify step that predates step-2 (fills the task Goal/Constraints from the ticket's Context, notes "conductor filled it from the Context"), and `step-1/builder-L3.md` shows the `steps.py` 127-line diff belongs to step 1's already-built guard-refusal code, not this step's builder. Neither is part of step 2's Do (docs + check.py only), and the step-2 builder's own Changes list matches exactly what git diff shows for the 5 in-scope files. Not out of scope for this step's build; pre-existing task/step-1 state.

## For the next attempt
None.
