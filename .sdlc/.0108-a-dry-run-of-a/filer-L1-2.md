<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0108: Remove the run.sh skill temp file on dry-run exit

## PR body
### Summary
A dry run (`SDLC_DRY_RUN=1`) of a role whose agent declares skills (planner, architect, verifier) left its `mktemp` skill file behind in `run.sh`. It is now removed on exit. This is a follow-up from T-0095.

### Changes
- `plugins/sdlc-lite/scripts/run.sh` (+2): right after `skill_file=$(mktemp)`, add `trap 'rm -f "$skill_file"' EXIT`. The dry-run `exit 0` and the missing-skill `exit 2` now remove the file. The later `on_exit` trap replaces this one and still removes the file.
- `plugins/sdlc-lite/scripts/run-selftest.sh` (+7/-1): a dry run of verifier L1 must print an `--append-system-prompt-file` path that no longer exists.
- `.sdlc/0108-a-dry-run-of-a/handoff.md`: the ticket record.

### Verification
A verifier (L1, Sonnet medium) returned pass on all four acceptance criteria:
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` printed `run selftest: PASS`.
- Negative control: in a throwaway worktree at HEAD, with the new selftest copied in and only the trap line removed from `run.sh`, the selftest failed with `dry run left its skill file behind`. The worktree was removed afterwards and the main tree was unchanged.
- `plugins/sdlc-lite/scripts/check.sh` exited 0. The tail showed the run selftest, hook selftest, shellcheck and plugin validate all passing.
- `git diff --stat` lists only the handoff, `run-selftest.sh` and `run.sh`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: a dry run of a role that declares skills (planner, architect, verifier) no longer leaves its temporary skill file behind.

## Follow-ups
None
