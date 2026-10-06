# Re-verify T-0291 (failed criteria only)

Base commit 24ef333 (SDLC_BASE_SHA); the change is HEAD. Read the ticket .sdlc/0291-hook-quadratic-long-command/handoff.md and docs/reports/hook-perf.md, and your previous result verifier-L3.md in this dir. The builder replaced, in plugins/sdlc-lite/hooks/block-disk-scan.sh, block-pattern-kill.sh, block-stray-worktree.sh and block-repo-format.sh, both the `pf=` line and the `raw=` line with `tr -d` forms, and the selftest body now holds backslashes.

Criteria (only the ones that failed or were widened):
1. The hooks diff base..HEAD changes only the `pf=` and `raw=` lines of those four hooks, and the new `raw=` line yields the same text as the old one (backslashes removed, newlines to spaces) on a string holding backslashes and newlines.
2. Run each of the five Bash hooks (disk-scan, pattern-kill, stray-worktree, publish, repo-format) on a 20 KB heredoc command with backslashes in the body (as in your earlier 604-backslash prose body, and the selftest body), harmless tail and deny tail: each under 2 s, exit 0 and 2 respectively.
3. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` prints PASS on HEAD, and fails on the version of the hooks with only the `pf=` lines fixed (HEAD~1 hooks).
4. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.
