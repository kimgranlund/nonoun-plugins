<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `CLAUDE.md`: added the Decisions bullet on the merge step, and named the `merge-step` guard in the `check.sh` Commands line.
- `.claude/agents/sdlc-lite-author.md`: added the Invariants bullet on keeping the `merge-step` template in sync.

## Checks
- `grep -c merge-step` on both files: 2 lines in `CLAUDE.md`, 1 in the author agent.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0.
- I did not run the `grep -n 'git merge --no-ff' CLAUDE.md` criterion itself. The new bullet contains that text, but I did not grep for it.

## Notes
None
