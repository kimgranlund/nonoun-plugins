<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Both selftests exit 0: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/steps.py selftest` and `python3 plugins/sdlc-lite/scripts/tickets.py selftest` in the worktree. Both exited 0 ("steps 0", "tickets 0").
- `grep -n "st_mtime"` shows only steps.py's snapshot helper: pass. Evidence: the only hit is `steps.py:198`, `snap[...] = (p.stat().st_mtime_ns, p.read_bytes())`, in the snapshot helper. tickets.py has no hits. Inspection of the diff also shows `find_plan` and the filers line use `order.newest` and `order.ordered` (`run_order.ordered` in tickets.py).
- Negative control: pass. Evidence: I ran it in throwaway copies in a temp dir, not in the worktree, with the mtime key restored.
  - steps.py: restoring the mtime-based `max` made the selftest fail. All three rewritten (c) cases fell in the failure list: equal mtimes, inverse mtimes, and no runs.jsonl.
  - tickets.py: restoring the mtime `sorted` in a full plugin copy made the selftest fail. The baseline copy passed (rc 0) before the edit. All three rewritten (h) cases then failed: equal mtimes, inverse mtimes, and no runs.jsonl.
  - The biting variable is the sort key. The rewritten cases build either equal mtimes, inverse mtimes, or the wrong-name-order file with the newest mtime, so a mtime key selects the wrong file.
- Required content (docstring and argparse help, "no planner-*.md" message, the (c) and (h) cases): pass. Evidence: the `git diff` shows each of these in place.

## Out of scope changes
None from this step. The git status also lists board.py, check.sh, run-selftest.sh, run.sh and order.py as changed. These are consistent with other steps of the same task, and I did not review them here.

## For the next attempt
None
