<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `CLAUDE.md`: added the `hooks/block-stray-worktree.sh` bullet after the pattern-kill bullet, and added the hook to the "Check everything" hook-selftest list.
- `.claude/agents/sdlc-lite-author.md`: added the hook to the check.sh hook-selftest list and added a learned-hazard bullet after the pattern-kill entry.
- `plugins/sdlc-lite/agents/builder.md`: added a clause to rule 5.
- `plugins/sdlc-lite/agents/verifier.md`: added a clause to rule 3.

## Checks
- The four `grep -q` criteria all passed.
- The em-dash diff check passed.
- `bash plugins/sdlc-lite/scripts/check.sh` printed PASS for every selftest, shellcheck and plugin validate. I piped it through `tail`, so I did not capture its exit code. The tail showed no failure.

## Notes
The new hook blocked my first attempt, a python heredoc that quoted the worktree-add phrase. That attempt wrote nothing. I made every edit with the Edit tool instead.
