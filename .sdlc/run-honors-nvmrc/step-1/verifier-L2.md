<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- AC1, `.nvmrc` `20` picks v20.11.0 (dry run): pass. Evidence: I ran the command as written. It printed `run.sh: .nvmrc 20: prepended <t>/nvm/versions/node/v20.11.0/bin to PATH` and exited 0. The installed v20.9.0 and v200.1.0 were not chosen. At HEAD, in a throwaway worktree, the same check found nothing and returned rc=1, so it can go red.
- AC2, `.nvmrc` `  v20.11.0` with whitespace: pass. Evidence: it printed `.nvmrc v20.11.0: prepended .../v20.11.0/bin to PATH` and exited 0.
- AC3, v20.11.0 not installed: pass. Evidence: it printed `.nvmrc v20.11.0: not found under <t>/nvm/versions/node, PATH unchanged`, with no `prepended` line, and exited 0.
- AC4, `lts/*` alias: pass. Evidence: it printed `.nvmrc lts/*: alias not resolved, PATH unchanged`, with no `prepended` line, and exited 0.
- AC5 (guard), no `.nvmrc`: pass. Evidence: no `.nvmrc` text in the output, rc=0. Extra probes show an empty `.nvmrc` also prints nothing, and a nonexistent NVM_DIR or HOME still exits 0.
- `grep -q NVM_DIR plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: rc=0.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: `run selftest: PASS`, rc=0. The old cases are kept and the diff only adds to the file. The new cases cover exact, prefix picking highest, `v20.1` vs `v20.11.0`, alias, missing version, no `.nvmrc`, and a real run recording `${PATH%%:*}`.
- Negative control: pass. Evidence: in a `git worktree add --detach HEAD` copy with the built files copied in, the selftest first passed (rc=0). I then deleted the `export PATH="$nvm_bin:$PATH"` line and the selftest printed `run selftest: FAIL: .nvmrc real run: claude saw PATH head '<t>/bin', want '<t>/nvm/versions/node/v20.11.0/bin'` and exited 1. The biting conjunct is the real-run PATH-head assertion. The dry-run stderr assertions cannot catch this mutation, because the echo line stays. With the HEAD run.sh and the new selftest, the selftest also failed (rc=1). The worktree was removed.
- (guard) `shellcheck --severity=warning` on both scripts: pass. Evidence: rc=0.
- Handoff behaviors not covered by a listed criterion: pass. Evidence: I observed in dry runs that `v20.1` and `v2` print `not found`, and `v20.11` and `20.11.0` prepend v20.11.0. `node` and `stable` print the alias line. The resolution sits after the git preflight and before the `SDLC_DRY_RUN` exit. The run.sh header comment is updated. The code runs under `set -euo pipefail` and uses only bash 3.2 constructs.

## Out of scope changes
- `.sdlc/run-honors-nvmrc/handoff.md` has a modified Intent section (`## Intent`). This is the clarify output, not builder work.
- There are untracked `.sdlc` artifacts (`planner-L2.md`, `runs.jsonl`, `step-1/`, `step-2/`).
- The plugin diff touches only `run.sh` and `run-selftest.sh`, as the step specified.

## For the next attempt
None
