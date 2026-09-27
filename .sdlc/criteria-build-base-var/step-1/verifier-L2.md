<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1 (first builder run: stub sees HEAD, `base-sha` written = HEAD): pass. Evidence: ran the exact criterion command from git toplevel, printed `CRIT1_PASS`, exit 0. Confirmed it bites: same command run against a throwaway worktree (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`, pre-build tree) exits 1 (no pass marker), then worktree removed.
- Criterion 2 (plain commit keeps base; `--no-ff` resync merge moves base and rewrites file): pass. Evidence: ran the exact criterion command, printed `CRIT2_PASS`, exit 0.
- Criterion 3, `(guard)` (planner sees `unset`, writes no `base-sha`): pass. Evidence: ran the exact command, printed `CRIT3_PASS`, exit 0. Ran the same command against the pre-build worktree: also passes (trivially true — no base-sha concept existed), which is the expected shape for a guard that must hold both before and after. To confirm this guard actually discriminates (not vacuous), mutated a copy of `run.sh` (`sed 's/if \[\[ "$role" == builder || "$role" == verifier \]\]; then/if true; then/'`) so every role gets `SDLC_BASE_SHA`; the criterion then fails (stub file never written, `test` on it errors, exit 1) — confirms it bites.
- Criterion 4 (`grep -q SDLC_BASE_SHA run-selftest.sh`): pass. Evidence: `grep -q SDLC_BASE_SHA plugins/sdlc-lite/scripts/run-selftest.sh` exits 0 in the built tree; exits 1 against the pre-build worktree copy — confirms it bites.
- Criterion 5, `(guard)` (`bash run-selftest.sh`): pass. Evidence: `bash plugins/sdlc-lite/scripts/run-selftest.sh` → `run selftest: PASS`, exit 0. This guard's new section itself red-then-green tests all six required cases (dry run writes nothing, planner sees unset even with `SDLC_BASE_SHA=leak` exported by the caller, first builder run = HEAD, plain commit keeps old base, `--no-ff` resync merge moves base, junk/non-ancestor stored value replaced by HEAD) — read at `plugins/sdlc-lite/scripts/run-selftest.sh:301-366`.
- Criterion 6, `(guard)` (`shellcheck --severity=warning run.sh run-selftest.sh`): pass. Evidence: ran the exact command, exit 0, no output.

## Out of scope changes
None. `git status --porcelain` shows only `plugins/sdlc-lite/scripts/run.sh` and `plugins/sdlc-lite/scripts/run-selftest.sh` modified; the untracked `.sdlc/criteria-build-base-var/*` entries are this task's own planner/step artifacts, not code changes. Doc updates (planner.md, builder.md, verifier.md, CLAUDE.md, check.py) are explicitly scoped to step-3, and gate-suite fixes to step-4 (read from those steps' handoffs) — step-1's Do correctly touches only run.sh and run-selftest.sh.

## For the next attempt
None.
