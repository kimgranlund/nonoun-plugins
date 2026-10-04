## Task goal
Independently verify branch t0214 (T-0214, per-ticket cost budget) against main before it merges. The ticket is .sdlc/.0214-ticket-budget/handoff.md; the design is docs/lean-sdlc/cost-control.md section D. Main has already been merged into the branch (conflicts in check.py, check.sh, run.sh and run-selftest.sh were resolved by keeping both sides: the spec gate and the budget gate in run.sh, check.py docstring item 19 for the budget guard).

## Step 1: Verify the branch
level: L3

### Do
Read-only verification, proportionate to a size-M change that adds a run.sh exit code. Inspect `git diff main...HEAD` and the merged run.sh gates. Check, with your own commands and not by reading: (a) `budget.py status` exits 0 under 80 percent, 3 at 80 and over, 2 with no budget, counts a duplicated attempt_id once, treats null cost as unmetered, counts a `step-<n>.superseded-<k>` run; (b) `run.sh` exits 4 with `run.sh: budget <pct>%: ask the user; budget.py ack` before any model call or runs.jsonl line for a ticket at 85 percent of budget_usd 10 with no ack, and launches with an ack and for a ticket with no budget; use a stub claude on PATH, no model call; (c) the spec gate still refuses a plan-reviewer run as before (both gates coexist in run.sh and neither shadows the other); (d) board output is byte-identical when no ticket has budget_usd; (e) inject one defect of your own in a throwaway worktree, for example make the gate fire at 90 percent instead of 80, and confirm the selftest or a check fails. Report any real defect with file and line; do not fail on style.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/budget.py selftest`
