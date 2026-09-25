## Task goal
No two tickets ever get the same id when worktrees file tickets in parallel.

## Step 2: Sync docs with cross-worktree id allocation
level: L1
### Do
- In `CLAUDE.md` (repo root), `scripts/tickets.py` bullet: after "stamps a ticket with the next id", state that `new` and `close` follow-ups take the next id above the max across the same-relative ticket root in every `git worktree list` tree (local root only outside git). Also state that `check` fails on two tickets sharing an id and names both folders. Branches not checked out in any worktree are caught by that `check` after merge.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: add one Rules bullet with the same behavior.
- `.claude/agents/sdlc-lite-author.md`: add to the sync line (line 16) that cross-worktree id allocation stays in sync across tickets.py, the /ticket skill, and CLAUDE.md.
- No em dashes.
### Acceptance criteria
- `grep -n "worktree" CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md .claude/agents/sdlc-lite-author.md` shows a hit in each of the three files describing id allocation.
- `grep -c "—" CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md .claude/agents/sdlc-lite-author.md` reports no more em dashes than before the step (`git diff` adds none).
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The only warning allowed is the expected CLAUDE.md validate warning.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` still exits 0 in this repo.
