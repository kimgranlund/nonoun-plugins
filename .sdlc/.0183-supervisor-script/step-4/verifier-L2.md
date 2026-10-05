<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Selftest prints every `ok:` label and `probe selftest: PASS` last: pass. I ran the AC1 command verbatim and it exited 0. The standalone run printed all 12 `ok:` lines, then `probe selftest: PASS`. Mutations of a copy under `$SDLC_TMP_WORKTREES/m` made it go red:
  - Removing the `wakes != 1` check gave `FAIL: fail: two wakes ... gave result=pass`.
  - Removing the body-sha check gave `FAIL: fail: dry-run body differs`.
  - Removing the stamp-order check gave `FAIL: fail: stamps out of order`.
  - Making the dry-run arm send no message gave `FAIL: pass: dry-run arm ... body_sha256=None`.
  - The fifth mutation (dropping the remote-moved check in the push branch) stayed green. It is an equivalent mutant: the `succeeded` push attempt still falls through to a fail line, which probe.py:462 produces.
- AGENTS.md is non-empty, CLAUDE.md is `@AGENTS.md`, and AGENTS.md names `probe.py`: pass. AC2 verbatim, exit 0. I read AGENTS.md and CLAUDE.md: `CLAUDE.md` is `@AGENTS.md`, and AGENTS.md says what the folder holds and how to rerun each arm and the selftest.
- No `run.sh`, has `probe-remote` and `--driver`, and the BODY regex matches: pass. AC3 verbatim, exit 0. probe.py:60 holds `BODY = "What is 2 + 3? ... git push probe-remote HEAD:refs/heads/wake-probe"`.
- The selftest leaves the main checkout's `.sdlc/supervisor` listing unchanged and creates none in the worktree: pass. AC4 verbatim, exit 0, with `p=/Users/kimgranlund/Projects/nonoun/sdlc-lite/.sdlc/supervisor`. I found no leftover `supervisor-live-*` dirs under `$TMPDIR`.
- No em dash in the three files: pass. AC5 verbatim, exit 0.
- (guard) Only the allowed paths changed or were added: pass. The guard command exited 0. `git status` shows only the three allowed modified files, the new `supervisor-live-run/` folder, and `supervisor.py`. `git diff --check` is clean and there is no `__pycache__`.
- Item 8/9 spot check by code read of probe.py: pass.
  - Evidence lines: `arm=` is first, and `remote=`, `message=`, `body_sha256`, `wakes`, the stamps line, `message_state`, `reply`, `remote_commits_added`, `push_attempt` and `cost` follow in order.
  - Oracle: it is a pure function with the unverified, wake, push and dry-run branches the Do requires.
  - Runtime: the selftest runs the wake, push and dry-run arms end to end against a stub.
  - Steelman: I considered failing for `unclassified` as a fourth `push_attempt` value and for the extra evidence lines. The builder's notes disclose both, and the Do does not forbid them. The oracle fails `unclassified`, which is stricter, so I dropped the finding.

## Out of scope changes
None. The modified files `docs/ticket-stages/watcher-design.md`, `docs/reports/idle-host-watcher-design-review.md` and `plugins/sdlc-lite/scripts/check.sh` are on the guard's allowlist, and `supervisor.py` is an earlier step's untracked file. The guard command exited 0.

## For the next attempt
None
