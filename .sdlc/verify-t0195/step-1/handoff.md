## Task goal
Independently verify branch t0195 (T-0195) against main before it merges. The ticket is .sdlc/.0195-runner-family-task-dir/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification. Run every criterion plus bash plugins/sdlc-lite/scripts/run-selftest.sh and python3 plugins/sdlc-lite/scripts/codex-selftest.py. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: (a) revert the run.sh task-dir fallback so a task-dir verifier finds no builder, (b) let the fallback read a step-N.superseded-K dir, (c) pick the lowest-numbered step instead of the highest that holds a builder result, (d) revert codex_roles.py resolve so a task-dir argument returns shared false with no builder. Confirm existing step-dir behavior is unchanged (run-selftest.sh step fixture cases still pass). Read docs/validation/runner-family-task-dir-live-run.md and its evidence: check each claim (builder on Sonnet, verifier on Opus, base dry run from commit 171e13b printing the pre-fix model and the fixed run printing opus), and that the report's Environment is accurate. Confirm no model or effort default changed (git diff of the table lines in run.sh).

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`
