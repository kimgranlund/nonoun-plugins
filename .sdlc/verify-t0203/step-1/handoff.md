## Task goal
Independently verify branch t0203 (T-0203) against main before it merges. The ticket is .sdlc/.0203-fanout-overlap/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification. Run every criterion and python3 plugins/sdlc-lite/scripts/fanout.py selftest. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught by the selftest: (a) report no overlap when two lanes touch one file, (b) report overlap for disjoint lanes, (c) merge an overlapping lane before the lane it overlaps, (d) drop the dry-run scope allow-list overlap report. Confirm report.md carries the overlap lines, and that lanes still plan inside the lane (no Files: line was added). Check the docs/references/sdlc-internals.md fanout entry matches the behavior.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
