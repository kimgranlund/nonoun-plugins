<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Evidence: it printed `tickets selftest: PASS`, rc 0. The new cases are in the diff: lane full missing results fails, lane solo with no entries fails, solo with planner and filer entries passes, an open solo ticket passes, and lean then full with every result passes.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass. Evidence: it printed `ok: 220 tickets, roadmap current`, rc 0. No real done ticket with a lane record trips the widened guard.
- Mutation copy with solo and full removed from the lane tuple, then `! selftest`: pass. Evidence: the sed changed only line 827 (diff of the `.bak` against the edited file). Selftest on the mutated copy printed `FAIL, these did not bite: (skips) check: lane full missing planner and filer fails: rc=0 ''` and `(skips) check: lane solo with no entries fails: rc=0 ''`. The exact criterion command exited 0, so the `!` was satisfied. An unmutated copy printed `tickets selftest: PASS`. Dropping only `solo` from the tuple went red on the solo case, so each lane value has its own check that fails when the lane is missing.
- `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: the output ends `ok: plugin validate`, rc 0. It also shows `supervisor selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS` and `hook live probe selftest: PASS`. shellcheck was skipped because it is not installed, which does not affect this change.
- Diff read against 244d0af (the Do's behavioral claims): pass. Evidence: `tickets.py:827` now accepts `('solo','lean','fix','full')`.
  - Lanes lean and fix go through the same code path, so they behave as before.
  - The `skip_missing` body (lines 815-851) requires a planner or filer result, or a counting `## Skipped` entry. It requires a verifier per `step-N/` directory. A solo ticket has no step directories, so it needs only planner and filer entries.
  - `skip_problems` checks only `status == 'done'`, and the open-solo selftest case passes.
  - No `skips.md` or no lane record returns None, so those tickets stay exempt.
  - The old lean-then-full case was changed on purpose: it now uses the `fullres` result files, and a new `tofull-miss` case asserts failure.
  - The docs and the handoff-format SKILL.md were updated to match.

## Out of scope changes
`git diff 244d0af` also shows `check.py` (unique guard numbers, commit 1e109ce), the `.sdlc` ticket and handoff files, `.sdlc/AGENTS.md` and `roadmap.md`. These belong to the sibling tickets T-0218 and T-0220 and to ticket bookkeeping, not to the T-0219 code. The T-0219 change touches only `tickets.py` and `handoff-format/SKILL.md`, both named in the handoff. Neither `check.py` nor the `.sdlc` files affect the four criteria, and all four passed on this tree.

## For the next attempt
None
