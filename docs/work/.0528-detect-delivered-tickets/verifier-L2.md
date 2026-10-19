<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 `tickets.py selftest` exits 0 with the new cases: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` printed `tickets selftest: PASS` (run on the built tree). The T-0528 block is at plugins/sdlc-lite/scripts/tickets.py (selftest, "T-0528: delivered and superseded open tickets").
- #2 A `T-0002: x` commit on main makes `check` list T-0002; the same commit on an unmerged branch lists nothing: pass. Evidence: the selftest cases cover both (control first on branch `side`, then on `main`: one `warning: beta: T-0002 is open but commit <sha> on main ... close beta --reason "delivered in <sha>"` row). Negative control observed: in a throwaway worktree I changed `git log <branch>` to `git log --all`; selftest then failed with "these did not bite: (T-0528) control: a T-0002: commit on an unmerged branch lists nothing" and the output showed the warning appearing.
- #3 `successor: T-0003` with T-0003 done prints the close line; with T-0003 open prints nothing: pass. Evidence: selftest cases "successor T-0003 done prints the ready-to-run close line" and "control: still open prints no close line". Negative control observed: replacing the `== 'done'` test with `False` in a throwaway worktree made selftest fail on "successor T-0003 done prints the ready-to-run close line".
- #4 `successor: maison:T-0158` accepted and `successor: banana` rejected: pass. Evidence: selftest cases (cross-repo prints `note: alpha: successor maison:T-0158 is in another repository; check it there`, exit 0, no close line; banana gives rc=1 with `alpha: successor 'banana' is not T-NNNN or <repo>:T-NNNN`). Negative control observed: making the validation accept any value in a throwaway worktree made selftest fail on "successor banana is rejected".
- #5 Constraints (reference-safe closure, id uniqueness, follow-up selection preserved): pass. Evidence: the diff to plugins/sdlc-lite/scripts/tickets.py only adds the two regexes, the `successor` field validation in `problems`, `default_branch`, `delivered_warnings`, `successor_lines`, the roadmap status cell and the two `cmd_check` calls; no change to close, new or archive. The full selftest (which covers those paths) passes. `python3 scripts/check-packaging.py` passed. `git diff --check` is clean. Running `tickets.py --root .sdlc check` on this tree does not crash and shows no spurious delivered or successor lines.

## Out of scope changes
None. The diff against 3509ed11 touches tickets.py, skills/ticket/SKILL.md and skills/handoff-format/SKILL.md (all named in the handoff), plus the task folder's own run records (runs.jsonl, skips.md, solo-L2-f14f0d97.md).

## For the next attempt
None.

## Notes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout67/b/.sdlc/0528-detect-delivered-tickets/solo-L2-f14f0d97.md holds only the usage-limit message, not a builder report; the build was checked from the diff and observed runs, not from builder claims.
- docs/specs/doc-standards/work-items.md and docs/specs/sdlc-lite/lane-lifecycle.md mention front matter fields (grep for paused_reason) but were not in the handoff's file list; not checked or changed.
