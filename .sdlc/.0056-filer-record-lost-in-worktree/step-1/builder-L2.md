<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: in `cmd_close`, when this tree has no filer, the refusal now names other worktrees holding `<slug>/filer-L*.md`. It only globs for them, never reads them, and wraps the glob in `try/except OSError`. With no match, the message is byte-identical to before. I added a new worktree selftest case and updated the usage text and the `cmd_close` docstring.
- `CLAUDE.md`: added a clause about the no-filer hint to the tickets.py bullet.
- `plugins/sdlc-lite/skills/file/SKILL.md`: step 3.1 now says that when the refusal names another worktree, the user should commit or copy the record into this tree and rerun the dry run.
- `.claude/agents/sdlc-lite-author.md`: added a keep-in-sync line for the hint.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` with the new case and no fix: FAIL. It reported only the new case (rc=1, old message).
- Same selftest after the fix: PASS, exit 0. The existing (e) case still passes, and the new case asserts `/file` is in the message.
- `grep -n "worktree" plugins/sdlc-lite/scripts/tickets.py`: line 23 of the usage text shows the hint. The docstring also mentions it.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.

## Notes
- The new case runs after the `zeta` case, so it adds no ticket and does not change any ids. It reuses `alpha`: that ticket is in main, but its filer record exists only in `wt`, written by the earlier numbered-close case there.
- The case checks that main's `.sdlc` snapshot is unchanged, which covers the manual-repro criterion.
- I did not run a separate manual repro outside the selftest.
- The hint lists paths as returned by `worktree_roots`, which are resolved paths.
