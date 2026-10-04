## Task goal
Independently verify branch t0197 (T-0197) against main before it merges. The ticket is .sdlc/.0197-lane/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification. Run every criterion plus python3 plugins/sdlc-lite/scripts/steps.py selftest. Read the ticket Intent and the design section it cites, then in a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught by the selftest or a criterion: (a) make steps lane ignore size, (b) make steps lane ignore a mandatory full-chain trigger (planner L3, L4 or L5 step, merge step, replan, Plan review line, unresolved: assumption), (c) make the tickets lane read crash on a handoff with no front matter, (d) drop the skips.md write. Check the handoff-format layout record mentions skips.md. Keep it proportionate: fail only on a real defect or an unsupported claim.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
