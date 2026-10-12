<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) selftest, rc 0 and the load-cap control line: pass. Evidence: `gate_lock.py selftest` gave rc=0, with `gate_lock selftest: negative control observed (load cap): the waiter ran over the load cap` and `gate_lock selftest: PASS`. The grep for `negative control observed (load cap)` exited 0. The control bites on the `# LOAD-CAP` line (`M_LOAD`), whose mutant makes the waiter run over the cap. No `process-deviations.md` exists in the artifacts dir, so there is no red-checkpoint deviation to name.
- #2 (red) over the cap the run exits 3, under it the run is admitted: pass. Evidence: the criterion's command exited 0. The over-cap run printed `gate_lock: timeout after 2s waiting for a grant of compute_units=3 (no holders)` and exited 3. The run after `echo 10` was admitted. Red control: the base `gate_lock.py` (from `git show $SDLC_BASE_SHA:...`, run in a plain temp dir because the worktree hook was blocked) admitted `run --timeout 2 -- true` at load 36.5 with rc=0, so the criterion's expected exit 3 cannot hold there.
- #3 (red) a held grant survives a load rise, status prints the reason, the waiter runs once the load drops: pass. Evidence: the criterion's command exited 0. Status printed `admitted  name HOLD ...`, then `queued    name WAIT ...`, then `waiting: load 36.5 over cap 24`. `$d/ran` did not exist before the drop and did exist after it.
- #4 (red) `max_load` is top-level, never a capacity, and 0 turns it off: pass. Evidence: the command exited 0. `policy show` printed `{'capacity': {...no max_load}, 'max_load': 24, ...}` and, after `max_load=0`, no `max_load` key. Red control: the base script's `policy set max_load=24` put `max_load` inside `capacity` (`capacity browser_jobs=3,compute_units=6,max_load=24`), so the check fails there.
- #5 (red) `max_load` appears in both docs: pass. Evidence: the grep loop exited 0 (rc=0). The diff shows the sdlc-internals.md "Load cap (T-0497)" paragraph and a new section 14 in gate-lock-admission.md; section 5 is untouched.
- #6 (red) `SDLC_GATE_LOAD_FILE` in sdlc-internals.md: pass. Evidence: the grep exited 0. It sits in the Load cap paragraph, marked tests only.
- #7 (guard) default policy unchanged: pass. Evidence: `policy show` on a fresh root equals the exact builtin dict (rc=0).
- #8 (guard) only the three target files change: pass. Evidence: the command with `SDLC_BASE_SHA=1f6e5ea2...` exited 0. `git status` shows only gate_lock.py, sdlc-internals.md and gate-lock-admission.md outside `.sdlc`. `git diff --check` was clean.
- #9 (guard) `check.py`: pass. Evidence: rc=0 and `ok: 19 role levels, 9 agents, 22 generated definitions checked`. It was not run at the base because it is green.
- #10 (guard) `check.sh`: pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` exited 0, and the log ends with `run selftest: PASS`, `hook selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.

Steelman: I drafted a fail for the code and the docs claim that "a nested run takes no turn". The handoff's criteria do not test that claim, and `schedule` is untouched for nested runs. I dropped the finding.

## Out of scope changes
None. Only the three target files differ from `$SDLC_BASE_SHA` outside `.sdlc` (criterion #8).

## For the next attempt
None
