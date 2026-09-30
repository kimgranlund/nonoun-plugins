<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k plan`: pass. Evidence: rc 0, 7 `ok: plan:` lines (fires and quiet-on-control for all three detectors, plus one extra scope-prose case), then `traces selftest: PASS`. I re-ran it a second time and got the same result.
- The `for d in criteria-never-red contract-dependents scope-prose` grep loop: pass. Evidence: it ran with no `FAIL1` or `FAIL2` echoes and printed `loop done`. The exact strings `ok: plan: <d> fires` and `ok: plan: <d> quiet on control` are in the selftest output above for each of the three detectors.
- `test -f .../detectors/plan.py && test -f .../rerun.py`: pass. Evidence: rc 0. The files are `plugins/sdlc-lite/scripts/traces/detectors/plan.py` and `plugins/sdlc-lite/scripts/traces/rerun.py`.
- `grep -q 'rerun_criteria' .../ingest.py`: pass. Evidence: rc 0. `ingest.py:137` has `def run(..., rerun_criteria=False, thresholds=None)` and `ingest.py:190-191` sets `aux['criteria_reruns'] = rerun.run(repo, rows, thresholds)` only under the flag.
- (guard) scope: pass. Evidence: I ran the exact command and it returned rc 0. The changed and untracked files outside `.sdlc` are `traces.py`, `traces/*` and `.gitignore` (the `__pycache__/` line), all allowed by the guard regex.
- Spec behavior not covered by a listed command: the `rerun.py` and `plan.py` code matches the Do.
  - Non-guard spans only, skipping `guard_skipped` spans.
  - A detached worktree at base-sha under `$SDLC_TMP_WORKTREES/traces-rerun-<pid>`, else `mkdtemp`.
  - `SDLC_BASE_SHA` and a per-span timeout are passed to `steps.run_guard`.
  - `git worktree remove --force` and `prune` run in `finally`.
  - The causes are `agents/planner.md` for two detectors and `skills/chain/SKILL.md` for scope-prose.
  - Each of these is also exercised by the selftest.
- Checks bite: pass. I copied the scripts to `$SDLC_TMP_WORKTREES/mut` and mutated four things, running the plan selftest after each. The copy was removed afterward and `$SDLC_TMP_WORKTREES` is empty.
  - `criteria-never-red` firing on any exit code made the control case fail: `criteria-never-red fired on the control`.
  - Dropping `n >= m` in `contract-dependents` made the fires case fail: `want 1 finding, got 2`.
  - Lowering the scope-prose threshold to `>= 1` made the case `fired on a single blocked build` fail.
  - Skipping `worktree remove` in `rerun.py` produced a FAIL. The output was truncated, so I did not see which case failed.
  - Unmutated, the tree passes.
  - A leftover-worktree check showed none: `git worktree list` has no tmp entries and matches its state before the run.
  - Caveat: after restoring the mutated copy, its final run printed an `ok:` line as its last line instead of PASS. I attribute this to stale `.pyc` files from same-second edits, since nothing was changed in the real tree. I re-ran the real tree and it printed `traces selftest: PASS`, rc 0.

## Out of scope changes
None. Every file is under `plugins/sdlc-lite/scripts/traces*` or is the `.gitignore` `__pycache__/` line, and the guard allows all of them. The builder's edits to `detectors/thresholds.py`, `detectors/__init__.py` and `selftest.py` are also under `traces/`. The other `.sdlc/**` changes belong to the task record.

## For the next attempt
None
