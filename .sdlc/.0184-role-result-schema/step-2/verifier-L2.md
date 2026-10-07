<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `grep -qF 'results.py" validate' plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: ran it, exit 0.
- `grep -qF 'results.py" key' plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: ran it, exit 0. The diff shows `sect=$(python3 "$plugin_root/scripts/results.py" key "$role")` just before the `events=` pick.
- `! grep -qE "allowed='|sect=[A-Z]" plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: ran it, exit 0. The diff shows the per-role case table deleted.
- `grep -qF 'comes before' plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: exit 0. The check bites: I ran the new run-selftest.sh against the pre-build run.sh in a detached worktree at $SDLC_BASE_SHA and it failed with `exit 0, want 3` and rc=1. On the built tree it passes.
- `! grep -qF 'PR_SECT = "plan-reviewer) sect=' plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exit 0, and `grep -n PR_SECT` finds nothing, so the constant is removed. The diff shows the new guard reads `results.SCHEMA`.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: rc=0, "run selftest: PASS".
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: pass. Evidence: rc=0, ends with "OK".
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: pass. Evidence: rc=0.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: rc=0, "ok: 19 role levels, 9 agents checked". The negative control bites: in a temp copy with the validate call replaced by `schema`, check.py printed `FAIL scripts/run.sh: plan-reviewer role: no result check "results.py" validate"` and exited nonzero.
- (guard) `grep -qF 'inherited red' plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: exit 0. The header comment keeps the words.
- (guard) scope diff against `$SDLC_BASE_SHA`: pass. Evidence: the command exited 0. Only run.sh, run-selftest.sh, check.py, check.sh and results.py changed.

Steelman pass: I drafted a fail on the check.sh edit (the `results.py selftest` line) as outside this step's code. The allowed-files list in the scope guard names check.sh, so I dropped the finding.

## Out of scope changes
None. check.sh gained a `results.py selftest` line, which the scope guard allows. I checked it with `git diff` and the exit-0 scope guard. `git diff --check` is clean.

## For the next attempt
None. The builder's note about stale "lacks its section" prose in `docs/references/sdlc-internals.md`, `agents/conductor.md` and the run-selftest header comments is outside this step's allowed files. Later steps should pick it up.
