<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/messages.py`: added the `selftest` subcommand with 18 cases. Added the `SDLC_MESSAGES_TEST_CLAIM=copy-delete` and `SDLC_MESSAGES_TEST_BARRIER=<dir>` hooks in `claim()` and a new `barrier()`; the `claim()` docstring and the module docstring (`--help`) both name them as selftest only. Added `selftest` to the usage line, the subparser list and `COMMANDS`, plus the imports `shutil`, `tempfile` and `time`. No step 1 CLI behavior changed: no case exposed a defect in it.

## Checks
- AC1 (selftest prints `messages selftest: PASS` and all 18 `ok:` labels): exit 0.
- AC2 (the main checkout's `.sdlc/messages` listing and untracked files are the same before and after): exit 0.
- AC4 (file exists and has no em dash): exit 0.
- Guard (only `messages.py` changed since `$SDLC_BASE_SHA`, outside `.sdlc`): exit 0.
- `git diff --check`: exit 0.
- Runtime: three sequential runs took 9.37 s, 9.34 s and 9.01 s, all PASS. Four concurrent runs all PASS. No `messages-selftest-*` temp dirs left behind.
- Observable criterion, run on temp copies with each defect injected alone:
  - (a1) `compose` writes `read_time: stamp(now)`: exit 1, `FAIL: create` (send refused: read_time is set in new/).
  - (a2) `deliver` writes `read_time` after validation: exit 1, `FAIL: create` (read_time is '…', expected '').
  - (b1) default claim becomes the copy-delete hook: exit 1, `FAIL: race: one winner`.
  - (b2) default claim becomes copy, barrier, plain `os.unlink`: exit 1, `FAIL: race: one winner`.
- 15 more single-defect injections each fail the named case: read_time early, ack_time early, ack ignores follow-up, expire sends no notice, expire outcome, read by any receiver, reply rule ignores topic, `--send-time` flag added, count skips validation, body cap 4001, no marker check, uppercase names, protocol not required, mailbox via show-toplevel, read path anywhere.
- Step 1's 13 acceptance criteria, rerun as a regression check after the `claim()` change: all exit 0. I removed `$SDLC_TMP_WORKTREES/mbox-wt` afterwards.

## Notes
- **Race check goes beyond the spec, on purpose.** Besides the two-reader race the handoff describes, the race verdict function first runs a probe on a separate message. One reader is held at the barrier while the harness checks that the message still sits only in `new/`. The harness then adds the second barrier entry itself to release it.
  - Without the probe, a copy-then-delete claim whose delete does not ignore FileNotFoundError (b2) passes, because the failing unlink picks a single winner.
  - The two-reader race itself is unchanged: two readers started back to back on one message.
- **Case 17 accepts two outcomes.** It requires a failing verdict, a probe that saw the copy in both folders, and either two winners or a racer refused with "in more than one folder".
  - Two winners happened in 30 of 30 measured rounds.
  - The second outcome is a fallback for when scheduling delays the second racer past the first one's copy. Requiring two winners outright could then fail by chance.
- **One injection cannot be caught (b3).** If the copy then delete runs after the barrier, the non-atomic window is outside anything the barrier can hold open, and the selftest passes. To inject defect (b), the verifier should put the barrier between the copy and the delete, as the hook does.
- **Extra isolation.** The selftest's environment drops every `GIT_*` variable as well as `SDLC_MESSAGES_TEST_*`, so nothing it runs can reach the caller's repo. Negative controls also compare the mailbox's directories, not just its files, which is stricter than the spec.
- **Where output goes.** The `ok:`, `PASS` and `FAIL` lines all go to stdout.
