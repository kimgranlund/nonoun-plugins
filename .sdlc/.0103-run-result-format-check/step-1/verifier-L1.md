<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1, builder result with no `## Status` exits 3, stderr names `## Status`, result file and `runs.jsonl` line kept: pass. Evidence: I ran the criterion's setup on the new tree. Output was `builder rc=3` and `run.sh: builder result lacks ## Status (done|blocked); see .../builder-L2.md`. The directory listing held `builder-L2.md` and `runs.jsonl`, and the `runs.jsonl` line names `"file":"builder-L2.md"`. The same setup on a `HEAD` worktree gave `rc=0`, so the check goes red on the old code.
- Criterion 2, verifier `## Verdict` then `maybe` exits 3 and names `## Verdict`: pass. Evidence: on the new tree, `verifier rc=3` and `run.sh: verifier result lacks ## Verdict (pass|fail)`. On `HEAD`, `rc=0`.
- Criterion 3, researcher with no `## Answer` exits 3 and names it: pass. Evidence: on the new tree, `researcher rc=3` and `run.sh: researcher result lacks ## Answer`. On `HEAD`, `rc=0`.
- (guard) builder `## Status` then `done` exits 0: pass. Evidence: `builder rc=0` on the new tree. The old tree gave 0 as well, which is expected for a guard.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: `run selftest: PASS`. The new selftest against the old `run.sh` gave `FAIL: builder result '## Changes\nNone': exit 0, want 3`, so the new cases go red without the change.
- (guard) `shellcheck --severity=warning` on `run.sh` and `run-selftest.sh`: pass. Evidence: no findings, and `SC ok` printed.
- `git diff HEAD -- plugins/sdlc-lite/scripts/run-selftest.sh` shows exit 3 cases for a builder with no `## Status` and a verifier verdict of `maybe`: pass. Evidence: the diff has `want_rc 3 builder L2 $'## Changes\nNone'` and `want_rc 3 verifier L1 $'## Verdict\nmaybe'`. It also has the planner no-`## Goal` case, the builder `maybe` case, and the two exit 0 cases.
- Header comment of `run.sh` documents exit 3: pass. Evidence: the diff adds `# Exit codes: 0 ok, 1 ..., 2 ..., 3 result lacks its section.`
- Stub `claude` and the `.nvmrc` real run: pass. Evidence: the stub cats `STUB_RESULT` when it is set, and the `.nvmrc` real run now passes `res $'## Status\ndone'`. The selftest passes.

## Out of scope changes
None. `git status` shows only `run.sh` and `run-selftest.sh` modified under `plugins/`. The rest is untracked `.sdlc` artifacts.

Not run: `scripts/check.sh`, the full repo check. The builder also did not run it.

## For the next attempt
None
