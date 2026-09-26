<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
No plan, builder, or verifier files exist in the artifacts dir, so there is no verifier verdict for this change. It was a conductor trivial edit, and `handoff.md` is the only record. Its claim that `scripts/check.sh` exited 0 and its negative-control result were not independently verified.

## PR title
T-0108: Remove the run.sh skill temp file on dry-run exit

## PR body
### Summary
A dry run (`SDLC_DRY_RUN=1`) of a role whose agent declares skills (planner, architect, verifier) left its `mktemp` skill file behind. It is now removed on exit. This is a follow-up from T-0095.

### Changes
- `plugins/sdlc-lite/scripts/run.sh`: right after `skill_file=$(mktemp)`, add `trap 'rm -f "$skill_file"' EXIT`. The dry-run `exit 0` and the missing-skill `exit 2` now remove the file. The later `on_exit` trap replaces this one and still removes the file.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: a dry run of verifier L1 must print an `--append-system-prompt-file` path that no longer exists.

### Verification
- Per the handoff, the negative control passes: with the trap removed, the selftest fails with `dry run left its skill file behind`.
- Per the handoff, `scripts/check.sh` exits 0.
- Both results are reported by the conductor only. No independent verifier ran.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: a dry run of a role that declares skills (planner, architect, verifier) no longer leaves its temporary skill file behind.

## Follow-ups
None
