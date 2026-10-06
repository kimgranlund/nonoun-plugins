# Hook perf on long Bash commands (T-0291)

Date 2026-10-06. Machine: macOS, `/bin/bash` 3.2. Input: a heredoc command (`cat > /tmp/x.txt <<'EOF2'` plus `echo line N 'quoted text' "dq" done C:\tmp\rowN` lines, then `ls -la`) wrapped as a PreToolUse Bash payload, run as `SDLC_ROLE=solo bash <hook>` (`builder` for block-repo-format.sh) under a Python subprocess timeout of 25 s.

## Cause

Two lines in each of block-disk-scan.sh, block-pattern-kill.sh, block-stray-worktree.sh and block-repo-format.sh:

- `pf=${cmd//[\\\'\"]/}` (cheap exit). A 9.4 KB string took 56.5 s for that one substitution.
- `raw=$(tr '\n' ' ' <<<"${cmd//\\/}")` (raw fallback, reached by every heredoc command). A literal pattern, but quadratic when the text holds many backslashes: 0.002 s at 9.4 KB with none, 1.97 s with 386 (verifier measurement).

Both became `tr -d`. block-publish.sh, block-background.sh, block-role-spawn.sh and warn-handoff-edit.sh have no such substitution; they stayed at or under 0.11 s at 8 KB before the fix.

## Timings, wall seconds, body with backslashes

| Hook | Version | 1 KB | 2 KB | 4 KB | 8 KB | 20 KB |
|---|---|---|---|---|---|---|
| block-disk-scan.sh | before | 0.35 | 1.60 | 8.93 | over 25 | over 25 |
| block-disk-scan.sh | after | 0.14 | 0.18 | 0.13 | 0.18 | 0.21 |
| block-pattern-kill.sh | before | 0.20 | 1.15 | 8.01 | over 25 | over 25 |
| block-pattern-kill.sh | after | 0.03 | 0.04 | 0.06 | 0.05 | 0.04 |
| block-stray-worktree.sh | before | 0.20 | 1.19 | 7.87 | over 25 | over 25 |
| block-stray-worktree.sh | after | 0.04 | 0.08 | 0.04 | 0.04 | 0.04 |
| block-repo-format.sh | before | 0.19 | 1.15 | 7.63 | over 25 | over 25 |
| block-repo-format.sh | after | 0.02 | 0.02 | 0.06 | 0.05 | 0.08 |

Before is commit 24ef333; after is the T-0291 change. Intermediate state (only the `pf=` line fixed, same body): pattern-kill, stray-worktree and repo-format were already 0.02 to 0.05 s at 20 KB, but disk-scan took 4.09 s at 8 KB and over 25 s at 20 KB, so the first fix alone was not enough. A body with no backslashes after the `pf=` fix alone: 0.01 to 0.03 s at 20 KB for all five hooks. A trigger word in the tail (`pkill`, `find /`, `git worktree add -b`, `git push`, `npm run format`) still exits 2 at 20 KB in 0.07 to 0.09 s on that body.

## Test

`bash plugins/sdlc-lite/scripts/hook-selftest.sh` runs the five Bash hooks that scan the command (disk-scan, pattern-kill, stray-worktree, publish, repo-format) on a 20 KB heredoc with backslashes under a 2 s timeout, each with a pass tail (exit 0) and a deny tail (exit 2). On the `pf=`-only intermediate state it failed with `timeout>2s` for five cases; on the fixed hooks it prints `hook selftest: PASS`. block-background.sh, block-role-spawn.sh and warn-handoff-edit.sh are not in the test.

## Verifier

First independent verifier run (Fable L3) failed criterion 4 on the backslash body and found the `raw=` line; both fixes above and the backslash test body came from that finding.
