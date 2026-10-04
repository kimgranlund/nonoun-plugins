## Task goal
Independently verify branch t0204 (T-0204) against main before it merges. The ticket is .sdlc/0204-fanout-resolver/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification, proportionate. Run every criterion and python3 plugins/sdlc-lite/scripts/fanout.py selftest. Read the ticket Intent. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: break the resolver the ticket adds in fanout.py (return the wrong ticket dir, ignore the configured root, hardcode .sdlc). Confirm existing fanout behavior is unchanged (selftest). Fail only on a real defect or an unsupported claim.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
