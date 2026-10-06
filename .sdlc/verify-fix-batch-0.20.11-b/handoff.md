## Task goal
Independently verify four fixes on this branch, built after base 3482207 (HEAD 0e85edb). Tickets (read each handoff.md and its acceptance criteria): .sdlc/.0293-solo-run-kill-group, .sdlc/.0298-limit-marker-reset-time, .sdlc/.0299-fanout-bare-ticket-ids, .sdlc/.0300-board-solo-merged-done. Code is in plugins/sdlc-lite/scripts: solo_run.py, run.sh with run-selftest.sh, fanout.py, board.py. Each regression test must fail without its fix and pass with it.

## Step 1: Verify the four fixes
level: L3

### Do
- Work in a throwaway worktree under $SDLC_TMP_WORKTREES at HEAD to show red: revert only the non-test hunks of each fix (the group kill and the lock in solo_run.py; the reset parse in run.sh and solo_run.py; the id normalization in fanout.py; the board.py change), run the matching selftest, and say what you did. Do not edit the real tree. For 0293 use a real child process: confirm no `sleep` child survives a wrapper timeout and a SIGTERM, and that a second run in a worktree with a live solo run is refused.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/solo_run.py selftest`
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `python3 plugins/sdlc-lite/scripts/board.py selftest`
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `python3 plugins/sdlc-lite/scripts/check.py`
- Each of the four regression tests goes red with its fix reverted (observed, not read).
