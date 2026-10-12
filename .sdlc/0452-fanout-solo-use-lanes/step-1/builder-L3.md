<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout38/n/plugins/sdlc-lite/scripts/lanes.py: five changes.
  - `open_lane` gains keyword-only `path=`, `branch=` and `check_claim=`. A new `ticket_title` helper reads the title when the claim check is skipped.
  - New `host_record`.
  - `sweep --apply` keeps a lane as `merging` while another process holds `merge.lock` in the lane's parent dir. The docstring gains a `merging` row.
  - The CLI `open` gains `--path`, `--branch` and `--no-claim`, and the docstring usage and API list name them.
  - The selftest gains the sentinel repo isolation check with its two planted controls, plus three new cases: `open path`, `host record` and `sweep merge.lock`. The final `ok: lanes.py selftest` line now prints after the isolation check.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout38/n/plugins/sdlc-lite/scripts/solo_run.py: four changes.
  - `ensure_worktree(name, base=None, task_dir=None)`: when the task's front matter has an `id:` (read with `tickets.parse`), it opens the tree through `lanes.open_lane(kind='solo', check_claim=False)` at `<lanes root>/<id>-<slug>` on branch `lane/<id>-<slug>`.
  - An existing tree at that path is reused, and an open refusal raises `Refuse`.
  - Both callers in `main` now pass `task_dir`.
  - Selftest: the old `--worktree:` fixture now has no id, and new `--worktree lanes:` expects were added.

## Checks
- `redck.py record <handoff>` before any edit: exit 0, 4 controls recorded red.
- Criterion 1 (`lanes.py selftest`, isolation line): exit 0.
- Criterion 2 (`lanes.py selftest`, `ok: open path:`, `ok: host record:` and `ok: sweep merge.lock:` lines): exit 0.
- Criterion 3 (signature has `path`, `branch` and `check_claim`, and `host_record` is callable): exit 0.
- Criterion 4 (grep `--worktree lanes:` and `solo_run.py selftest`): exit 0, `solo_run selftest: PASS`.
- Criterion 5 (scope against `$SDLC_BASE_SHA`, `.sdlc` excluded): exit 0. Only the two target files changed.
- Criterion 6 (`git diff --check` against `$SDLC_BASE_SHA`): exit 0.
- Negative control, not a named criterion: I ran `solo_run.py selftest` on a throwaway copy with the lanes branch turned off (`if tid:` changed to `if False:`).
  - All three new `--worktree lanes:` expects that check the tree, branch, record and session cwd failed, so they catch the missing change.
  - The run-succeeds and reuse expects passed in that copy, so they do not catch it on their own.
  - The copy also failed the existing group-kill negative-control expect. That came from rewriting `SCRIPTS` in the copy, not from this change.
  - The copy was deleted afterwards.

## Notes
- `sweep` takes the `merge.lock` flock only after `evaluate` has decided to close a lane, and only with `--apply`. A dry run never touches the lock.
- `host_record` leaves out the record of the same name when it picks a port, so overwriting a record can reuse that record's port.
- `open_lane(path=...)` resolves a relative path against the `cwd` argument. With `check_claim=False`, external ids still print the "claim in its tracker" line.
- The isolation compare is a set difference of the sentinel's `git worktree list --porcelain` and `git for-each-ref` lines. The planted ref is deleted before the worktree is planted, so each control is caught on its own.
- `solo_run.py` imports `lanes` and `tickets` inside `ensure_worktree`, the same lazy import `new_task` already uses.
