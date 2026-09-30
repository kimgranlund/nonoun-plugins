<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1, grep for `Temporary worktree recipe` and `clone --bare`, then `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: I ran the command and it printed `run selftest: PASS` with rc=0. The header paragraph is at run-selftest.sh:34 and the case uses `git clone -q --bare`. The case makes no model call, because it uses the shared stub `claude`.
- Criterion 2, last line of the selftest output is `run selftest: PASS`: pass. Evidence: I ran the command as written and it returned rc2=0.
- Criterion 3, builder report shows the negative control, its `FAIL` line and the restore: pass. Evidence: `builder-L3.md` lines 12-14 record two controls (run from the primary, and handoff copied into the temporary worktree), each with a `run selftest: FAIL: temporary worktree recipe: ...` line, plus the restore. I reran both in a scratch copy of the plugin under `$SDLC_TMP_WORKTREES`.
  - Run from the primary: `FAIL: temporary worktree recipe: the role ran in '.../proj/main', want the temporary worktree .../recipe.fb2y9P/wt`.
  - Handoff inside the temporary worktree: `FAIL: temporary worktree recipe: .../proj/main/.sdlc/t/scout-L1.md is missing`.
  - Two more mutations also went red. Dirtying the primary's tracked file gave `the primary's tracked file bytes changed`. Creating a primary `.worktrees` dir gave `the primary has a .worktrees dir`.
  - The unmodified copy of the script is green, so the assertions can go red and are not vacuous.
- (guard) `command -v shellcheck >/dev/null && shellcheck --severity=warning plugins/sdlc-lite/scripts/run-selftest.sh`: pass, with the tool supplied. As written on this host it exits non-zero, because `command -v shellcheck` finds nothing (sc=1). That is host setup, not the change. I put a temporary shim on PATH that ran pipx `shellcheck-py`, and the same guard command gave rc=0 with no findings. The builder reported the same result for the base file.

## Out of scope changes
None for this step. `git status` shows `plugins/sdlc-lite/skills/chain/SKILL.md` and `plugins/sdlc-lite/skills/handoff-format/run-operations.md` modified. They are uncommitted step 1 work, and the handoff and builder report both name step 1 as their source. The only step 2 change is `run-selftest.sh`: the header paragraph, one added `pwd -P >"$tmp/cwd"` line in the stub, and the recipe case.

The extra stub line and the added cwd assertion go beyond the handoff's list. I checked that they are needed: without them the "run from primary" control would not fail. It failed exactly on that assertion.

## For the next attempt
None
