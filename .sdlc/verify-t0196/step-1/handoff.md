## Task goal
Independently verify branch t0196 (T-0196) against main before it merges. The ticket is .sdlc/0196-batch-state/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification, proportionate. Run every criterion plus steps.py selftest and board.py selftest. Read the ticket Intent. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: (a) treat an unlisted step as verified, (b) ignore a builder result newer than the Verified listing, (c) accept a listing for an L4 or L5 step or a merge step, (d) use file mtime instead of order.py. Confirm batching stays within a small steps.py rule (the ticket says report if it grows large) and board renders the batched verification. Fail only on a real defect or unsupported claim.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
