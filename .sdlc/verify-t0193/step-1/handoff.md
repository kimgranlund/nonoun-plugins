## Task goal
Independently verify branch t0193 (t0193) against main before it merges. The ticket is .sdlc/- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`/handoff.md: read its Intent and Constraints, and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification. Run every criterion. Run python3 plugins/sdlc-lite/scripts/footprint.py selftest and then, in a throwaway copy under $SDLC_TMP_WORKTREES, inject defects and show each is caught: (a) count a file twice, (b) drop the .md bytes, (c) make check ignore --max-files, (d) make footprint write under the ticket dir. Reproduce the design's Baseline table for the closed dot folders named in the ticket (T-0188, T-0164, T-0181, T-0175) with footprint.py and compare with the table in docs/lean-sdlc/design.md; state each difference. Check that counts are derived at run time. Fail on any claim not supported by the output.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
