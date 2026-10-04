## Task goal
Independently verify branch t0198 (T-0198) against main before it merges. The ticket is .sdlc/0198-skips-guard/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification, proportionate. Run every criterion plus python3 plugins/sdlc-lite/scripts/tickets.py selftest. Read the ticket Intent. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: (a) a lean ticket missing a required skips.md entry passes check, (b) a pre-feature closed ticket without skips.md fails check, (c) the guard lives in check.py instead of tickets.py, (d) remove the introduction marker so existing closed tickets go red. Run python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check on this repo and confirm it stays green. Fail only on a real defect or unsupported claim.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
