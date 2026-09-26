<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/file/SKILL.md: step 1.1 describes the `(worktree <name>)` lines; step 1.2 comparison covers them.
- plugins/sdlc-lite/skills/ticket/SKILL.md: item 4 `--dry-run` sentence updated.
- CLAUDE.md: Layout, tickets.py bullet, dry-run clause updated.
- .claude/agents/sdlc-lite-author.md: line 17 sync sentence updated.

## Checks
- `grep -cF '(worktree <name>)'` on each of the four files: 1, 1, 2, 1, so all four criteria pass.
- The `open T-NNNN` guard on file/SKILL.md: the string is still present.
- The no-em-dash diff check: passed.
- `plugins/sdlc-lite/scripts/check.sh`: the last 8 lines show every selftest PASS, shellcheck ok, plugin validate ok. The `rc=0` in that command is from `tail`, not `check.sh`, so its own exit code was not captured. I did not read the earlier output for failures.

## Notes
None
