<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: I ran it on the built tree and got `check rc=0`. The tail of the output shows `steps selftest: PASS`, `fanout selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`. To confirm it can go red, I made a throwaway worktree at HEAD under `$SDLC_TMP_WORKTREES`, copied in the built steps.py and CLAUDE.md, and replaced the new trailing-redirect regex in `is_command` with `return False`. check.sh then returned `mutant check rc=1` with `steps selftest: FAIL`.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0: pass. Evidence: on the built tree it returned `selftest rc=0` and ended with `steps selftest: PASS`. Against the same mutant it returned `mutant selftest rc=1`. Three cases failed: the two new `(k2) lint refuses a || fallback in a compound with a trailing redirect or pipe` cases (`... done < f` and `... done | cat`) and `(k2) a fail-fast loop with a trailing redirect is a command span and lints ok`. The guard therefore goes red on exactly the step 1 mechanism. I removed the worktree afterwards; `git worktree list` shows no tmp entry.
- Builder claim ("both gates already pass, no changes needed"): confirmed by the two runs above. `git diff --stat` shows only step 1's edits (steps.py, CLAUDE.md, the task handoff) and nothing from step 2.

## Out of scope changes
None. I read the full `git diff`:
- `plugins/sdlc-lite/scripts/steps.py`: the `is_command` change, its docstring and usage text, and the new selftest cases. This is step 1 work.
- `CLAUDE.md`: one clause added to the steps.py bullet, "also when they end in a trailing redirect or pipe after the closing keyword". The ticket's Constraints ask for this doc sync.
- `.sdlc/the-steps-py-lint-does/handoff.md`: fills in the Goal and Constraints. This is task bookkeeping.
- The untracked files are all `.sdlc` task artifacts.

Step 2 changed no files.

## For the next attempt
None
