<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1 (`specgate.py selftest`, 11 labels, last line PASS): pass. Evidence: ran the span verbatim under `bash -c` with `SDLC_BASE_SHA=b77b49b`, rc 0. The span is vacuous only if the script is missing, and `specgate.py` is absent at the base commit, so the check can go red.
- Criterion 2 (`check` on 0195 `planner-L3-2.md`: rc 1, `step 4: slow guard:`): pass. Evidence: span run verbatim, rc 0.
- Criterion 3 (0184 `planner-L2.md` step 7 only, and 0197 `planner-L3.md` step 3 slow guard with no step 2 finding): pass. Evidence: span run verbatim, rc 0.
- Criterion 4 (plan `guard timeout: 1` makes `steps.py split --only` time out after 1s): pass. Evidence: span rc 0. Negative control: the same plan run with the base-commit `steps.py` in a detached worktree under `$SDLC_TMP_WORKTREES` gives `split` rc 0 and writes `step-1/handoff.md`, so the criterion goes red at base.
- Criterion 5 (step line 1 beats plan line 10): pass. Evidence: span run verbatim, rc 0. The step line (1s) overrides the plan line (10s), and `sleep 3` times out.
- Criterion 6 (three `(guard timeout)` labels in the `steps.py` selftest): pass. Evidence: span rc 0. Also ran `steps.py selftest | tail -1`, which prints `steps selftest: PASS`.
- Criterion 7 (`run.sh` plan-reviewer dry run refused: exit 2, `step 1: slow guard:`): pass. Evidence: span rc 0. The base `run.sh` has no gate, so the dry run would exit 0 there and the criterion is red at base.
- Criterion 8 (real run refused: exit 2, stub never called, no `runs.jsonl`, no `*.running`): pass. Evidence: span rc 0.
- Criterion 9 (`SDLC_SPECGATE=off`: exit 0, stub called, run line has `.specgate == "off"`): pass. Evidence: span rc 0.
- Criterion 10 (`import steps` line, no re-defined parser functions, `check.sh` selftest line): pass. Evidence: span rc 0. `git diff` of `check.sh` shows `python3 "$root/scripts/specgate.py" selftest || fail=1` after the footprint line, and `specgate.py` is listed in the header comment.
- Criterion 11 (scope guard): pass. Evidence: span rc 0. Tracked changes outside `.sdlc` are only `steps.py`, `run.sh`, `run-selftest.sh` and `check.sh`. The only untracked file is `specgate.py`.
- Criterion 12 (`run-selftest.sh` and `codex-selftest.py`): pass. Evidence: `bash plugins/sdlc-lite/scripts/run-selftest.sh` rc 0 with `run selftest: PASS`, and `python3 plugins/sdlc-lite/scripts/codex-selftest.py` rc 0. I did not run the pre-build gate comparison because both are green on the built tree.

Extra checks I ran:
- `bash plugins/sdlc-lite/scripts/check.sh` rc 0.
- `git diff --check` clean.
- `steps.py lint .sdlc/0210-spec-gate-check` prints `steps lint: ok`.
- Dry run of a plan-reviewer on this ticket (clean plan) rc 0 with only the `claude -p ...` command line printed, so a pass is silent.
- The same dry run with `SDLC_SPECGATE=off` prints the one `run.sh: SDLC_SPECGATE=off: spec gate skipped` line.
- `git diff` of `run.sh` matches the Do: the gate sits before the lifecycle exec, skips when `SDLC_LIFECYCLE_CHILD=1`, and adds the `specgate` key to the run line only for plan-reviewer with the gate off.

I drafted a fail on the builder's note that docs still say the split guard default is 300 (`docs/maintenance/sdlc-internals.md:47`, `docs/lean-sdlc/cost-control.md:41`). The builder's rebuttal would hold: criterion 11's scope guard forbids docs edits in this step. I dropped it.

## Out of scope changes
None. The diff touches only the four allowed scripts plus the new `specgate.py`, confirmed by the scope guard and `git status`.

## For the next attempt
None. Optional follow-up for a later step: the two docs above still describe the split guard default as 300 with no mention of the `guard timeout:` line.
