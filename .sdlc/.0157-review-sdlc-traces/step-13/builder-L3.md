<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/rerun.py` (new): `run(repo, rows, thresholds)` picks each step dir the rows name where the newest verifier passed and a `base-sha` file exists. It takes the non-guard, non-skipped criterion spans of that step's `handoff.md` and runs each through `steps.run_guard` in a detached throwaway worktree at base-sha, with `SDLC_BASE_SHA` set and a per-span timeout. The worktree goes under `$SDLC_TMP_WORKTREES/traces-rerun-<pid>`, or a `mkdtemp` dir when that variable is unset. `finally` runs `git worktree remove --force` and `git worktree prune`, then deletes the root dir.
- `plugins/sdlc-lite/scripts/traces/detectors/plan.py` (new): `detect(rows, aux, thresholds)` with three detectors:
  - `criteria-never-red`: fires on reruns that exited 0 at base; cause `agents/planner.md`.
  - `contract-dependents`: cause `agents/planner.md`.
  - `scope-prose`: cause `skills/chain/SKILL.md`.
- `plugins/sdlc-lite/scripts/traces/ingest.py`: `run(..., rerun_criteria=False, thresholds=None)`. Only with the flag does aux get `criteria_reruns`. Docstring updated.
- `plugins/sdlc-lite/scripts/traces/detectors/thresholds.py`: added `rerun_timeout_secs: 60` and severities for the three new detectors.
- `plugins/sdlc-lite/scripts/traces/detectors/__init__.py`: docstring now lists the `plan` family.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: added the `plan` cases: fires and quiet-on-control for all three detectors, plus one extra case for scope-prose (a step `## Scope widened` section, or a single blocked build, stays quiet).

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k plan`: rc 0, 7 ok lines, PASS.
- The for-loop grep criterion over `ok: plan: $d fires` and `ok: plan: $d quiet on control` for all three detectors: rc 0.
- `test -f .../detectors/plan.py && test -f .../rerun.py`: rc 0.
- `grep -q 'rerun_criteria' .../ingest.py`: rc 0.
- (guard) scope criterion: rc 0 (empty output).
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (all families): PASS, rc 0.
- `git diff --check`: clean.
- Mutation controls (in-process monkeypatch, files not changed): each one made its case fail.
  - Guard spans not excluded: the criteria-never-red control failed.
  - Worktree remove/prune skipped: the fires case failed on the `git worktree list` comparison.
  - Changes forced to match the note path: the contract-dependents control failed.
  - Plan-review `scope widened:` ignored: the scope-prose control failed.
- `$SDLC_TMP_WORKTREES` was empty after all runs.
- pyflakes is not installed, so no lint ran.

## Notes
- The criteria-never-red fires case also checks two more things:
  - `git worktree list --porcelain` is the same before and after the ingest.
  - With the flag off, aux has no `criteria_reruns` and the detector is quiet.
- The control case uses `test -f added.txt` (the file is added after base) plus a `(guard) test -f README.md` that exits 0 at base. It asserts that only the non-guard span ran.
- `rerun.run` considers every step dir the rows name, superseded dirs included, as long as the newest verifier passed.
- `contract-dependents` and `scope-prose` look only at live (non-superseded) step rows.
- Both detectors read each note from the result files, because rows carry no `next_note` or `changes` fields.
- Reruns are not cached: they run on every ingest where the flag is set.
- Nothing was committed.
