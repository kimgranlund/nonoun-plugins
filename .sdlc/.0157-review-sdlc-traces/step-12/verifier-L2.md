<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation`: pass. Evidence: I ran it and it exited 0. It printed 22 `ok:` lines (the 10 `fires` cases, the 10 `quiet on control` cases and 2 extra cases), then `traces selftest: PASS`.
- The `for d in ...` loop over the 10 detector names, grepping for `ok: escalation: $d fires` and `ok: escalation: $d quiet on control`: pass. Evidence: I ran it and it exited 0 (`AC2 0`).
- `test -f .../detectors/thresholds.py && test -f .../detectors/escalation.py`: pass. Evidence: I ran it and it exited 0. Both files exist, at 44 and 526 lines.
- (guard) scope: pass. Evidence: I ran the command with `SDLC_BASE_SHA=7334f49...` and it exited 0. The non-`.sdlc` changes are `.gitignore` (adds `__pycache__/`), `plugins/sdlc-lite/scripts/traces.py` and `plugins/sdlc-lite/scripts/traces/*`. All three match the allowed pattern.

Checks that can go red:
- Fixture strength, read in `selftest.py:1017-1023`. `_esc_one` asserts exactly one finding, an evidence entry with `path` plus `line` or an `attempt_id`, a non-empty `cause_hint.file`, and the family and layer.
- Per-detector `_ck_*` checks pin the evidence values. `_esc_quiet` asserts the control fires nothing.
- Mutation, run by me in a throwaway copy under `$SDLC_TMP_WORKTREES`. I disabled `exit_3_result` and the blocked test in `wrong_resume_order`. `selftest -k escalation` then printed `traces selftest: FAIL`. I did not check which cases failed, because I grepped only the summary line. The copy was removed afterwards.
- The full `traces.py selftest` on the real tree exited 0 with PASS.
- I read `detect()` against every detector bullet in the Do (`escalation.py:231-504`). It matches, including these details:
  - Severities come from `THRESHOLDS` (`thresholds.py`).
  - Every finding goes through `findings.make` via `_make`.
  - Newest-result ordering uses `order.newest` and `order.ordered`.
  - Liveness uses `os.kill(pid, 0)` with errors caught.
  - The `stale-running-marker` fixture's marker path is asserted.

Builder claims checked:
- The scope claim holds. It matches my guard run and `git status`.
- The two extra cases and the whole-suite PASS claim match the outputs above.
- I did not re-run the builder's corpus smoke run and I do not rely on it.

Steelman: I drafted a fail on `stale-running-marker`, on the ground that it reads `owner_pid` from `.attempt.json`, which the Do does not list as a raw read. The Do says "a running record whose owner_pid", and `owner_pid` exists only in the attempt record. The path is one a row's `sources` names, so it is allowed. I dropped the finding.

## Out of scope changes
None. `.gitignore` gains `__pycache__/`, and the scope guard's own allow-list includes `.gitignore`, so it is allowed. The `.sdlc` task files are excluded from the guard.

## For the next attempt
None
