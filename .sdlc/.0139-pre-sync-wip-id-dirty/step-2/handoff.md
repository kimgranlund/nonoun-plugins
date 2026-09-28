## Task goal
A `wip(<id>): dirty before sync` commit that `fanout.py` `run_ticket` makes on a lane branch can never reach the integration branch, matching the documented contract that a `wip(<id>)` commit is never merged.

Conductor decision (unattended, derived from that contract, no user choice needed): guard. When the pre-sync `wip_commit` finds a dirty lane tree, `run_ticket` stops that ticket with an outcome other than `merged` (for example `dirty before sync: wip <sha>`), so no sync, driver, lane commit, or merge happens for it, and the lane stops as for any other non-merged outcome (remaining tickets `skipped`). The wip sha shows in the report. The planner may pick an equivalent guard if it finds a reason, but must not merge that commit.

## Step 2: Gates green
level: L1
### Do
Reason for the level: this step only runs the gate and makes small fixes to what step 1 changed.

Run `plugins/sdlc-lite/scripts/check.sh` from the git toplevel. It covers the fanout selftest, shellcheck, `claude plugin validate`, and the doc and table guards in check.py. Fix any red that step 1 introduced, and only in the files step 1 changed. If the gate was already red at the build-start HEAD, report Status `inherited red: <tests>`.
### Acceptance criteria
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and prints `fanout selftest: PASS`
