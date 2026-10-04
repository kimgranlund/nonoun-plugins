## Task goal
Independently verify branch t0215 (T-0215) against main before it merges. The ticket is .sdlc/.0215-solo-operator-tiers/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification, proportionate. Run every criterion plus python3 plugins/sdlc-lite/scripts/evals.py check. Read the ticket Intent and Constraints. Check: agents/solo.md exists, is short, names tiers S M L with Sonnet low, Sonnet xhigh, Opus xhigh, pins no model, and ends M and L with one independent batched verifier on a different family; models.json holds solo L1 L2 L3 = gpt-6.1-sol low, high, xhigh; the three generated Codex agents match generate --check; steps.py lane gives solo for size S and M and full for L and XL before planning, and the selftest covers it. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: (a) remove the solo tier table, (b) change the Codex solo L2 effort, (c) remove solo from the check.py exclusion so the run.sh agreement check trips, (d) make lane return lean for size M. Confirm no existing model or effort default changed (git diff of run.sh and the other models.json entries) and the evals lock cites a real eval. No live run exists: that is a recorded known limit, do NOT fail for it. Fail only on a real defect or unsupported claim.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
