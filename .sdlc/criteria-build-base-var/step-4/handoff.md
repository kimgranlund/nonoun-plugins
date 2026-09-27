## Task goal
A step's scope criteria compare against the tree the build started from, and that works whether or not anything gets committed later.

## Step 4: gates green
level: L2
### Do
Run `bash plugins/sdlc-lite/scripts/check.sh` and every gate below, and fix any red the earlier steps introduced. `scripts/hook-selftest.sh` is left out of the guards on purpose. At plan time it failed 2 of 3 runs with exit 141 (SIGPIPE) on block-repo-format "verifier allows" fixtures, and this ticket does not touch hooks. Run it once, and report its outcome and any 141 in Notes as a pre-existing flake. Do not fix it here.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/skills/decompose/scripts/coverage_check.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/order.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh plugins/sdlc-lite/scripts/check.sh`
- (guard) `claude plugin validate plugins/sdlc-lite`
