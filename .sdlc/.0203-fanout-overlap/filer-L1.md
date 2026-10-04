<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0203: fanout.py merge-time file-overlap check

## PR body
### Summary
`fanout.py` now checks for file overlap between lanes when they reach the merge. A lane that overlaps an earlier lane waits and merges after it. Lanes plan inside the lane, so no plan exists at launch. This is why the check runs at merge time and not at launch. `--dry-run` also reports scope allow-list overlap for tickets that are already planned.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - Lanes rank by their position in the spec list. A lane waits only for an earlier lane that has not finished and has pending files overlapping its own, so no wait cycle can form.
  - The wait happens outside the merge lock. The locked merge and the integration-dirty refusal are unchanged.
  - A waiting lane logs `waiting for lane <name> (overlap: <files>)` in `fanout.log`.
  - `report.md` gets `- Overlap: '<lane>' and '<lane>': '<file>'` lines, or `- Overlap: none`.
  - `--dry-run` prints `overlap (planned scope)` lines. They cover pairs, `none`, and `not planned, checked at merge time: <tickets>`.
  - The module docstring covers the new behavior, including its limit.
- `docs/maintenance/sdlc-internals.md`: the `fanout.py` entry describes the wait, the event, the report lines, the dry-run lines and the limit.
- Selftest: case 13 (two lanes touching `shared.txt`, plus a disjoint negative control) and case 14 (the planned-scope dry run, plus a negative control).

### How each was verified
Each step had an independent verifier, and all three returned pass.
- Step 1 (merge-time wait, record, report), verifier L3:
  - The five greps and the selftest passed. The greps failed at the base SHA, so they bite.
  - Negative control: in a temp copy, the `wait_for_overlap(...)` call was replaced by `pass`. The selftest then failed with five case 13 misses.
  - The verifier traced the contract dependents. `traces/sources/fanout.py` parsed the new report line and log event with no problems. The traces and board selftests passed.
  - The diff touched only `fanout.py`.
- Step 2 (planned-scope dry run), verifier L1:
  - The three greps and the selftest passed.
  - Negative control: in a temp copy, `planned_scope` was made to return `None`. Case 14 failed.
  - The verifier did not capture that failing run's exit code; it relied on the FAIL output.
- Step 3 (docs), verifier L1: the doc greps and `git diff --check` passed, and these gates were green:
  - `bash plugins/sdlc-lite/scripts/check.sh`
  - `python3 scripts/check-packaging.py`
  - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
  - `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`

Limits: `shellcheck` is not installed, so `check.sh` skipped it. No live host run is recorded in the artifacts; verification is the selftest with a stub driver.

## Changelog entry
- fanout: lanes that touch the same files now merge in spec order. A later lane waits, outside the merge lock, for an earlier overlapping lane. `report.md` lists overlaps (`- Overlap:`), and `--dry-run` reports scope allow-list overlap for planned tickets.

## Follow-ups
- note: An overlap first visible after a later lane has started its merge is not reordered. The docstring and `sdlc-internals.md` state this limit.
- note: `check.sh` skipped `shellcheck` (not installed), so shell lint did not run for this change.
- note: Planned-scope overlap in `--dry-run` always lists an external lane's tickets as not planned, because their step folders live on the external branch.
