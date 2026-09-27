<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: I ran it from the git toplevel on the built tree and got `check exit 0`. The tail of its output reads `fanout selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`. To confirm the check can go red, I made a throwaway worktree under `$SDLC_TMP_WORKTREES/base` at HEAD, copied in the built fanout.py, and deleted the new `return 'dirty before sync', f'wip {sha}'` line (grep count 0 afterwards). check.sh then printed `mutated check.sh exit 1` with `fanout selftest: FAIL`. The biting variable is the early return in `run_ticket`.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and prints `fanout selftest: PASS`: pass. Evidence: on the built tree it exited 0 and printed `fanout selftest: PASS`. With the same mutation in the throwaway worktree it printed `mutated selftest exit 1`. The failures listed were `dirty-sync case: run exits 1, got 0`, `lane tip subject is wip(T-0002): dirty before sync, got 'T-0002: Ticket b'`, `the lane tip is not an ancestor of the integration branch`, `the integration branch does not hold dirty.txt`, and a status of `done` where `ready` was expected. So without the guard, the wip commit really does get merged, and the check catches it. I removed the worktree afterwards (`git worktree remove --force`, rc 0), and `git status --short` was the same as before.

Builder claim that no changes were needed: `git diff --stat` shows only the step-1 files (fanout.py, SKILL.md, CLAUDE.md) and the task handoff. Both gates are green on that tree, so no fix was needed. Accepted on those two runs.

Steelman: I considered filing that the builder made no changes. Its likely rebuttal is that the Do asks for fixes only when the gate is red, and I saw the gate green myself, so that finding was dropped.

## Out of scope changes
None from step 2, which changed no files. The dirty tree holds step 1's scoped files (`plugins/sdlc-lite/scripts/fanout.py`, `plugins/sdlc-lite/skills/fanout/SKILL.md`, `CLAUDE.md`), all named in the task Constraints. It also holds `.sdlc/pre-sync-wip-id-dirty/handoff.md`: I read its diff, and it only fills in the conductor's Goal, Constraints, and Done-when text, which is task bookkeeping rather than project code. Dismissed on that reading.

## For the next attempt
None
