# Hook perf on long Bash commands (T-0291)

Date 2026-10-06. Machine: macOS, `/bin/bash` 3.2. Input: a heredoc command (`cat > /tmp/x.txt <<'EOF2'` plus `echo line N 'quoted text' "dq" done` lines, then `git status`) wrapped as a PreToolUse Bash payload, run as `SDLC_ROLE=solo bash <hook>` under a Python subprocess timeout.

## Cause

`pf=${cmd//[\\\'\"]/}` (the cheap-exit line in block-disk-scan.sh, block-pattern-kill.sh, block-stray-worktree.sh and block-repo-format.sh). A 9.4 KB string took 56.5 s for that one substitution; the literal-pattern `${cmd//\\/}` on the same string took under 0.01 s. Replaced with `tr -d`. block-publish.sh, block-background.sh, block-role-spawn.sh and warn-handoff-edit.sh have no such substitution; the same bench showed at most 0.11 s at 8 KB.

## Timings, wall seconds

| Hook | Size | Before | After |
|---|---|---|---|
| block-disk-scan.sh | 1 KB / 2 KB / 4 KB / 8 KB | 0.23 / 1.34 / 8.78 / over 20 (timeout) | 0.02 / 0.02 / 0.02 / 0.02 |
| block-pattern-kill.sh | 1 / 2 / 4 / 8 KB | 0.27 / 1.32 / 8.84 / over 20 | 0.02 / 0.02 / 0.02 / 0.02 |
| block-stray-worktree.sh | 1 / 2 / 4 / 8 KB | 0.25 / 1.40 / 9.32 / over 20 | 0.02 / 0.03 / 0.03 / 0.03 |
| block-repo-format.sh (builder) | 20 KB | over 2 (selftest timeout) | 0.01 |

At 20 KB after the fix: disk-scan 0.03, pattern-kill 0.02, stray-worktree 0.03, publish 0.02, repo-format 0.01. The 20 KB before-fix case was not timed past the 2 s selftest timeout (the 8 KB case already exceeded 20 s). With a trigger word in the tail (`pkill`, `find /`, `git worktree add -b`, `git push`, `npm run format`) the 20 KB runs took 0.07 to 0.09 s and still exited 2.

## Test

`bash plugins/sdlc-lite/scripts/hook-selftest.sh` now runs five hooks on a 20 KB heredoc under a 2 s timeout, each with a pass tail (exit 0) and a deny tail (exit 2). On the pre-fix hooks it failed with `timeout>2s` for the four affected hooks (8 of 10 cases); on the fixed hooks it prints `hook selftest: PASS`.
