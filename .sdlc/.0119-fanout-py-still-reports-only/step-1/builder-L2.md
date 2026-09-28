<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/fanout.py: `run_ticket` now calls `inherited_red` before it handles a non-zero driver `rc`. If it finds an inherited-red step, the outcome is `<inherited> (driver rc=<n>)`; if not, the outcome is still `driver failed rc=<n>`. The zero-exit path behaves as before. The module docstring (step 2) describes the new rule. Selftest case 5b is new: it asserts the rc=7 inherited outcome, run exit 1, no merges, ticket still `ready`, a clean lane tree, and T-0002 `skipped`, plus a negative control where a plain `exit 7` gives `driver failed rc=7`.
- CLAUDE.md: the fanout.py Layout entry now says the inherited-red outcome is also reported after a non-zero driver exit, with the ` (driver rc=<n>)` suffix.
- .claude/agents/sdlc-lite-author.md: the inherited-red route line now says the same.

## Checks
- Criterion 1, the new-behavior command from the handoff: exit 0, and the report row is `inherited red: step-1: test_a (driver rc=7)`.
- Criterion 2 (guard), the plain `exit 7` driver command: exit 0, and the report row is `driver failed rc=7`.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. It runs the fanout selftest, which now includes case 5b.

## Notes
I left `plugins/sdlc-lite/skills/fanout/SKILL.md` unchanged. Its line 25 says what an outcome starting with `inherited red: step-<n>: <tests>` means, and that stays correct with the added suffix.
