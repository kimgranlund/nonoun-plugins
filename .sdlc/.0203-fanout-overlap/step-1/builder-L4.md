<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: changed the module docstring (step 5 overlap wait and the `waiting for lane` event, the external-lane pointer to step 5, the report's `- Overlap:` lines, a case 13 paragraph) and `Lane` (`files` and `done` fields). Added `lane_pending` and `wait_for_overlap`. In `merge_gate_close`, the wait now runs before the lock, and inside the lock `HEAD...<ref>` paths are recorded into `lane.files`. `run_lane` gained `try/finally` with `done` and notify. `report` writes the Overlap lines, `cmd_run` sets `ctx['cond']`, and the selftest has `OVERLAP_STUB` plus case 13 and its disjoint negative control.

## Checks
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: `fanout selftest: PASS`, rc 0 (about 46 s). Run twice, the second time after the last docstring rewrap.
- `grep -qF 'waiting for lane alpha (overlap: shared.txt)' plugins/sdlc-lite/scripts/fanout.py`: rc 0
- `grep -qE -- '- Overlap: .alpha. and .beta.: .shared\.txt.' plugins/sdlc-lite/scripts/fanout.py`: rc 0
- `grep -qF -- '- Overlap: none' plugins/sdlc-lite/scripts/fanout.py`: rc 0
- `grep -qF 'overlap order: alpha merges before beta' plugins/sdlc-lite/scripts/fanout.py`: rc 0
- `grep -qF -- '--no-optional-locks' plugins/sdlc-lite/scripts/fanout.py`: rc 0
- (guard) scope `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" ...; git ls-files --others ...; } | grep -vxF -e plugins/sdlc-lite/scripts/fanout.py)"`: rc 0
- `git diff --check`: rc 0. The diff contains no em dash (count 0).
- Negative control: I copied `plugins/sdlc-lite` to a `mktemp -d` dir outside the repo. In the copy I replaced the two-line block `    wait_for_overlap(ctx, lane, t, ref)\n    with lock:` once (asserted unique) with `    pass\n    with lock:`, then ran that copy's selftest. Result: `fanout selftest: FAIL`, rc 1, with these case 13 misses:
  - `overlap: exit 0, both rows merged` got 1 with `T-0001: driver failed rc=1` and `T-0002: merged`
  - `overlap order: alpha merges before beta` got `['Merge fanout/ov-beta: T-0002']`
  - `overlap: fanout.log contains waiting for lane alpha (overlap: shared.txt)`
  - `overlap: report.md has the line - Overlap: ...` (it showed `- Overlap: none`)
  - `overlap: the integration shared.txt holds both top alpha and bottom beta` (only `bottom beta`)

  The temp dir was removed and the real tree was not edited.

## Notes
- Negative control anchor for the verifier: replace only the call line in `merge_gate_close`. A blind `sed 's/wait_for_overlap(ctx, lane, t, ref)/pass/'` also hits the `def wait_for_overlap(ctx, lane, t, ref):` line, which gives a SyntaxError instead of a case 13 miss. I anchored on the call line plus the following `    with lock:` line. Expect about 60 s of extra runtime, because alpha's stub uses its full 600 x 0.1 s timeout.
- No base-SHA pre-build run was needed. No gate failed, and case 13 does not exist at the base; the negative control above shows it red without the wait.
- Lock order: `wait_for_overlap` holds `ctx['cond']` (never the merge lock) while it runs `lane_pending` git reads and `say`. `run_lane` notifies with no other lock held, so no lock-order inversion is possible.
- `lane_pending` drops the result unless `merge-base` returns exactly one sha, and it turns any git failure or exception into an empty set. If the waiting lane's own-paths read fails, that also counts as no paths, so the lane never blocks.
- `docs/maintenance/sdlc-internals.md` is left alone here; step 3 updates its fanout entry.
- The untracked `.sdlc/0203-fanout-overlap/step-1/base-sha` and `builder-L4.attempt.json` were created by the runner, not by this step.
