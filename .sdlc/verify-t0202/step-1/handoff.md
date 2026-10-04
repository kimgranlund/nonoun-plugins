## Task goal
Independently verify branch t0202 (T-0202) against main before it merges. The ticket is .sdlc/0202-carry-forward/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification, proportionate. Run every criterion. Check the Carry forward section is declared last for scout, researcher, architect and archaeologist in results.SCHEMA and their agent bodies, planner.md and builder.md say to read it first, cite the result path and search only what it does not answer, and the regenerated Codex agents match generate --check. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: (a) remove the Carry forward heading from scout.md, (b) remove 'search only what it does not answer' from planner.md, (c) reorder the section in results.SCHEMA. The live run (docs/validation/carry-forward-live-run.md) is a known limit: read it and confirm its report states the real outcome and the metric miss honestly (the planner read the scout result through a glob so read_scout_result recorded no, while it cited the path and ran no symbol search); do NOT fail the branch for that metric miss alone. Fail only on a real defect or an unsupported claim.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/results.py selftest`
