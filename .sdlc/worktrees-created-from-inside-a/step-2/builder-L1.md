<!-- role=builder level=L1 model=sonnet effort=low -->
All five criteria pass, no em dashes introduced.

## Status
done

## Changes
CLAUDE.md: extended the `scripts/run.sh` bullet with the run-end stray report sentence, extended the `hooks/block-stray-worktree.sh` bullet with the bypass/run-end note.
.claude/agents/sdlc-lite-author.md: extended the existing block-stray-worktree hazard line with the run-end report note.

## Checks
- `grep -qF 'stray worktree appeared during this run' CLAUDE.md` — pass
- `grep -F 'hooks/block-stray-worktree.sh' CLAUDE.md | grep -qF 'run end'` — pass
- `grep -qF 'stray worktree appeared during this run' .claude/agents/sdlc-lite-author.md` — pass
- `grep -F 'block-stray-worktree.sh' .claude/agents/sdlc-lite-author.md | grep -qF 'run end'` — pass
- `grep -qF 'stray_branches' CLAUDE.md` — pass

## Notes
None
