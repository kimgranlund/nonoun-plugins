# Verify T-0291

Base commit 24ef333 (SDLC_BASE_SHA); the change is HEAD. Read the ticket .sdlc/0291-hook-quadratic-long-command/handoff.md and docs/reports/hook-perf.md. Four PreToolUse hooks (plugins/sdlc-lite/hooks/block-disk-scan.sh, block-pattern-kill.sh, block-stray-worktree.sh, block-repo-format.sh) replaced `pf=${cmd//[\\\'\"]/}` (quadratic on bash 3.2) with `tr -d`; plugins/sdlc-lite/scripts/hook-selftest.sh gained a 20 KB perf case.

Acceptance criteria:
1. The diff base..HEAD under plugins/sdlc-lite/hooks changes only those four `pf=` lines, and the replacement strips exactly backslash, single quote and double quote (verify with a one-line run on a string holding all three).
2. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` prints PASS on HEAD.
3. The new selftest bites: in a temp copy of the repo outside this worktree (not here), restore the base versions of the four hooks and confirm the selftest fails there with timeouts.
4. Run each of the five Bash hooks (block-disk-scan, block-pattern-kill, block-stray-worktree, block-publish, block-repo-format) on a 20 KB heredoc command (SDLC_ROLE=solo; builder for block-repo-format.sh) with a harmless tail and a deny tail: each finishes under 2 s with exit 0 and 2 respectively.
5. The timings and claims in docs/reports/hook-perf.md match what you observe within an order of magnitude.
