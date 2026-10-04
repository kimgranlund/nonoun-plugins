## Task goal
Independently verify branch t0204 (T-0204) against main before it merges. The ticket is .sdlc/.0204-fanout-resolver/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification, proportionate. A previous branch verification failed because the branch was cut before T-0203 merged; main has since been merged in and a step 2 was built to route planned_scope through the ticket root. Run every criterion plus python3 plugins/sdlc-lite/scripts/fanout.py selftest. Confirm: planned_scope reads the configured ticket root, the ticket_root lane selftest has two lanes with planned step-1 scopes sharing a file and asserts the pair line, and the internals sentence covers the planned-scope check. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: (a) hardcode .sdlc in planned_scope, (b) drop the planned-scope pair line, (c) make the resolver ignore ticket_root. Fail only on a real defect or unsupported claim.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
