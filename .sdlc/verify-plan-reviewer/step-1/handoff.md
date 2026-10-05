## Task goal
Independent check that branch `plan-reviewer-role` delivers T-0171: a plan-reviewer role that rejects a defective plan before a builder starts, on Claude Code and Codex.

## Step 1: Whole-feature check
level: L3

### Do
Verify the feature as a whole. Beyond the criteria below: read `docs/reports/plan-reviewer-live-run.md` and check each claim in its Results table against the code and the retained evidence. Reproduce, offline, the `run.sh` dry-run command lines for the plan-reviewer on Claude Code for a Fable planner and an Opus planner (`SDLC_DRY_RUN=1`), and `codex_roles.py resolve plan-reviewer L1` for an Astra planner. Build a throwaway repository with a planner result, run `steps.py review` and `steps.py split` before and after a reviewer result that says `replan`, and show that a rejected plan is never split and that a `pass` allows the split. Check that each new check in `check.py` can fail by injecting a defect in a throwaway copy. Check that no existing role, level, model, or effort in `run.sh` or `models.json` changed except the additions the ticket lists. Report any claim the evidence does not support.

### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check main -- . ":(exclude).sdlc"`
