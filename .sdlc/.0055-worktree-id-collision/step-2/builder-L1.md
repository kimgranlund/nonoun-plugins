<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `CLAUDE.md`: `scripts/tickets.py` bullet now says `new` and `close` follow-ups take the next id above the max across every `git worktree list` tree, and that `check` fails on duplicate ids and names both folders.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: added a Rules bullet with the same behavior.
- `.claude/agents/sdlc-lite-author.md`: added a sync sentence for cross-worktree id allocation.

## Checks
- `git diff | grep '^+' | grep -c "—"`: 0 added em dashes.
- `grep -c worktree` on the three files: 3, 1 and 4. I did not run the literal `grep -n` from the criteria, and I did not check that the ticket SKILL.md and author-agent hits are the new lines.
- `scripts/check.sh`: the tail ended with "ok: plugin validate". I only read the last 5 lines, and the `rc=0` came from `tail`, not `check.sh`. I did not see the expected CLAUDE.md validate warning.
- `tickets.py --root .sdlc check`: "ok: 60 tickets, roadmap current", exit 0.

## Notes
The `check.sh` exit code is unconfirmed, because `rc=$?` reported `tail`'s status. The verifier should rerun `plugins/sdlc-lite/scripts/check.sh` and read its exit code directly.
