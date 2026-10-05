## Task goal
Independently verify branch idle-host (T-0180 idle-host limit docs and T-0181 `messages.py wait`) against main (2a428cc) before it merges.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification. Run every criterion, then inject defects in a throwaway copy under $SDLC_TMP_WORKTREES and show each is caught: (a) make `wait` claim the message (move it to read/), (b) make `wait` print a body, (c) remove the timeout cap, (d) remove the exit 3 on timeout. Read `docs/reports/messages-wait-live-run.md` and its evidence files, and check each claim against the evidence (one wait call, no polling calls, send_time <= read_time <= ack_time, host versions). Check the sentence `cannot wake an idle host` in the five T-0180 files and that `wait` does not claim to wake an idle host. No em dashes in new text.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `test "$(grep -l 'cannot wake an idle host' plugins/sdlc-lite/scripts/messages.py plugins/sdlc-lite/agents/messenger.md docs/ticket-stages/design.md docs/codex-role-execution.md docs/reports/messages-idle-host-limit-2026-10-01.md | wc -l)" -eq 5`
