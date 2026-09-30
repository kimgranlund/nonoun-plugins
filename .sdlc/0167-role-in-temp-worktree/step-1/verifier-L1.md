<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q '^## Run a role from a temporary worktree' …/run-operations.md`: pass. Evidence: the command exited 0. The heading is at the added diff hunk.
- `grep -qF -- '--detach' …/run-operations.md`: pass. Evidence: exit 0. The string appears in the recipe prose and in the `sh` block.
- `grep -qF 'worktree remove' …/run-operations.md`: pass. Evidence: exit 0. The `sh` block has `git -C <repo> worktree remove "$wt"`.
- `grep -qF 'SDLC_TMP_WORKTREES' …/run-operations.md`: pass. Evidence: exit 0.
- `grep -qi 'bare' …/run-operations.md`: pass. Evidence: exit 0.
- `grep -qi 'fanout' …/run-operations.md`: pass. Evidence: exit 0.
- `grep -qF 'Run a role from a temporary worktree' …/chain/SKILL.md`: pass. Evidence: exit 0. The diff shows the existing sentence extended to "…safe recovery, and `Run a role from a temporary worktree`."
- The new section states the four required facts in findable prose: pass. Evidence, read from the diff:
  - Results and `runs.jsonl` land beside the absolute handoff path in the home `.sdlc/<task>/`: paragraph starting "The result and `runs.jsonl` land next to…".
  - Builder edits must be committed on a named branch before removal or they are lost: "A builder's edits exist only in `$wt`…".
  - Removal uses no `--force`: "Removal uses no `--force`…".
  - Only the recipe's own worktree is removed: "Only the recipe's own worktree is removed…".
  - The section also has the numbered recipe and the `sh` block.
  - The `SDLC_TMP_WORKTREES` claim matches `run.sh`. Line 267 has `wt_tmp="$toplevel/.worktrees/tmp/$role-$$"`, and line 369 sets it only in the role's env.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: printed "Codex agent definitions verified", rc=0.
- Whether the greps can go red: pass. Evidence: at `$SDLC_BASE_SHA`, `git show` on `run-operations.md` piped to `grep -ciE 'bare|SDLC_TMP|--detach'` counts 0, and the same check on `chain/SKILL.md` for "Run a role from" counts 0. So the greps fail on the base and pass on the built tree.

## Out of scope changes
None. The diff touches only `plugins/sdlc-lite/skills/chain/SKILL.md` and `plugins/sdlc-lite/skills/handoff-format/run-operations.md`. The other new files are `.sdlc/` task artifacts. `fanout.py` is unchanged, and the generated agents show no drift.

## For the next attempt
None
