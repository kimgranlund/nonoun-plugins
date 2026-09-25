<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`:
  - Added `git_toplevel`, `tree_state` and `tree_changes`. `guard_cwd` now calls `git_toplevel` and behaves as before.
  - `run_guards` takes a work tree snapshot before the first runnable guard and another after the last, and refuses if they differ. The refusal prints one line per changed path, then a single `plan defect:` last line that also names any red guards.
  - Extended the `--only N` docstring with the phrase `changed the work tree`.
  - Added 7 `(o)` selftest cases. The existing `(n)` cases are unchanged.

## Checks
- Criterion 1 (a guard creates an untracked file, refuses): rc=0. The last line is `plan defect: step 1 (guard) criteria changed the work tree: sdlc-guard-made; replan this step (/chain 3)`.
- Criterion 2 (a guard modifies a tracked file, refuses): rc=0. The last line names `tracked.txt` and no handoff is written.
- Criterion 3 (guard, a guard that changes nothing passes): rc=0 and the handoff is written.
- Criterion 4 (guard, a tree dirty before the guards passes): rc=0 and the handoff is written.
- Criterion 5 (`grep -c '^ok: (o)'` is at least 3): rc=0. The count is 7.
- Criterion 6 (`grep -q "changed the work tree" steps.py`): rc=0.
- Criterion 7 (guard, the selftest's last line is `steps selftest: PASS`): rc=0.
- Criterion 8 (guard, `(n)` ok count is at least 7): rc=0. All 7 `(n)` cases pass.
- Criterion 9 (no edits to the `(n)` bodies): `git diff HEAD -- plugins/sdlc-lite/scripts/steps.py | grep -E '^[-+].*\(n\)'` finds no lines, so no `(n)` line changed.
- Negative control: I made `tree_changes` return `[]` in a temp copy. The selftest then FAILs on the 4 `(o)` refusal cases (untracked file, tracked file, changed already-dirty file, red guard plus changed tree), so the new tests do catch a missing check.
- `plugins/sdlc-lite/scripts/check.sh`: rc=0. All selftests PASS, shellcheck ok, plugin validate ok.

## Notes
- The snapshot records each path's porcelain XY status plus its lstat size and mtime_ns. This goes slightly past the handoff's status-only wording: a guard that appends to a file that was already dirty is caught even though its status letter stays ` M`, and one `(o)` case proves this. Ignored files are not seen, because git status leaves them out.
- The snapshot runs `git --no-optional-locks status`, so taking it does not refresh `.git/index`.
- When `--only` names several steps, the per-path lines and the `plan defect:` line say `steps 1, 2` rather than one step, because the snapshot covers all the chosen steps' guards together.
- Anything else writing into the work tree while the guards run (another session or process) would also trigger the refusal. I did not handle this because the step does not ask for it.
- Nothing was committed.
