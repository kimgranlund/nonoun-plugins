<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: line 15 now says `new --numbered` or `close --numbered` appends the config line. It also says plain `check` warns, without failing, when every folder has an NNNN- prefix but the config lacks the line.
- `CLAUDE.md`: the `tickets.py` bullet on line 25 gets the same two changes.
- `.claude/agents/sdlc-lite-author.md`: added one line to Invariants (line 16) on numbered-mode persistence, the `check` warning, and keeping tickets.py, the /ticket skill and CLAUDE.md in sync.

## Checks
- `grep -c "close --numbered"` on SKILL.md and CLAUDE.md: 1 match in each. I did not run the separate `warn` grep, but the added text contains "warns".
- `grep -n -i numbered .claude/agents/sdlc-lite-author.md`: matches line 16.
- `plugins/sdlc-lite/scripts/check.sh`: the output ended with the tickets, board and decompose selftests passing, shellcheck ok and plugin validate ok. The `rc=0` I saw is the exit code of `tail`, not `check.sh`, so I did not observe `check.sh`'s own exit status.

## Notes
- The new line in `sdlc-lite-author.md` sits between the last invariant and `## After every change`. It is worth a glance to confirm it reads as part of the Invariants list, not after a blank line.
