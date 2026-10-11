<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/b/plugins/sdlc-lite/scripts/traces/sources/tickets.py`: line 31, the `tickets.problems(...)` call now passes `areas=tickets.config_areas(root)`.

## Checks
- (red) `grep -qF "areas=tickets.config_areas(root)" plugins/sdlc-lite/scripts/traces/sources/tickets.py` passes after the edit.
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest` printed `traces selftest: PASS`.
- (guard) The changed-files check was not run. This step touched only the one named file.

## Notes
- `redck.py record` was retrospective, not a before-edit record. Eleven source paths from steps 1 and 2 already differed from the base, and the tool says so. The grep was red before my edit: the line had no `areas=`.
- The docstring on line 7 still reads `tickets.problems(ts, tickets.config_numbered(root))`. I left it alone because the step said to change nothing else.
