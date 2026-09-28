<!-- role=filer level=L1 model=sonnet effort=medium -->
All steps passed: single-step plan (L2), builder done, verifier pass on all three criteria.

## Warnings
None

## PR title
T-0119: fanout.py surfaces inherited-red cause after a non-zero driver exit

## PR body
Summary: When a lane's driver (conductor) exits non-zero, `fanout.py` previously reported only `driver failed rc=<n>`, hiding the inherited-red cause when the lane's ticket dir held a step whose `steps.py next` action was `inherited`. This follow-up from T-0115 makes `fanout.py` check for an inherited-red step on a non-zero exit too, not just on exit 0.

Changes:
- `plugins/sdlc-lite/scripts/fanout.py`: `run_ticket` now calls `inherited_red` before returning on a non-zero driver `rc`. When an inherited-red step is found, the outcome is `<inherited red: step-<n>: <tests>> (driver rc=<n>)`; when none is found, the outcome stays exactly `driver failed rc=<n>` as before. The zero-exit inherited-red path is unchanged. The module docstring (step 2/3) documents the new rule. A new selftest case (5b) covers the rc=7 inherited outcome (exit 1, no merge, ticket stays `ready`, clean WIP-committed lane tree, next ticket `skipped`) plus its negative control (plain `exit 7` with no inherited step still gives `driver failed rc=7`).
- `CLAUDE.md` (Layout, fanout.py entry) and `.claude/agents/sdlc-lite-author.md` (inherited-red route line): updated to state the inherited-red outcome is also reported after a non-zero driver exit, with the driver rc visible.
- `plugins/sdlc-lite/skills/fanout/SKILL.md` left unchanged: its description of the outcome string's meaning stays correct with the added suffix.

How verified: the verifier (L1) independently ran the plan's two acceptance-criteria commands against the built tree and got the exact expected report rows (`inherited red: step-1: test_a (driver rc=7)` and `driver failed rc=7`), and confirmed the first criterion actually discriminates by re-running it against pre-build HEAD in a throwaway worktree, where it correctly failed (`driver failed rc=7`, not yet showing the inherited cause). It also ran `bash plugins/sdlc-lite/scripts/check.sh`, which exited 0 and included `fanout selftest: PASS` (covering the new case 5b and its negative control). No out-of-scope changes were found.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
fanout.py now reports the inherited-red cause (with the driver's exit code) instead of only `driver failed rc=<n>` when a lane's driver exits non-zero after an inherited-red stop.

## Follow-ups
None
