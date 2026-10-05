## Task goal
Independently verify branch t0183 (T-0183: `scripts/supervisor.py`, a deterministic watcher that resumes an idle host on new mail) against main before it merges.

## Step 1: Verify the branch
level: L3

### Do
Read-only. Run every criterion. Then, in a throwaway copy under $SDLC_TMP_WORKTREES, confirm these defects are caught by the selftest: (a) the watcher claims or moves a message, (b) the wake prompt includes the topic or a body, (c) the lock allows a second watcher, (d) the STOP file is ignored, (e) dry-run still calls the host. Confirm the watcher makes no model call and never reads a message body. Read `docs/reports/supervisor-live-run.md` and its evidence files and check each claim (arm results, `Codex wake arm after the fix: 3 of 3 passed.`, no push in the push arms, the pre-push hook basis). No em dashes in new text. Report only real defects; do not ask for extra tests.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/supervisor.py selftest`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
