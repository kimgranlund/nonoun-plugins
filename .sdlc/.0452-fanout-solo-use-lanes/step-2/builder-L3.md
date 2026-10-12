<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout38/n/plugins/sdlc-lite/scripts/fanout.py: added `import lanes` and `Lane.port`. `setup` now touches `merge.lock` and opens each regular lane through `lanes.open_lane`. New helpers: `lane_port_env` (used by the driver env and the gate env), `sweep_lanes` (called in `cmd_run` between `refuse_overlap` and `setup`) and `close_lanes` (called after join, before `report`, with the single `# LANE-CLOSE` line). `report` gets the lifecycle lines. Also updated: the docstring (setup, lifecycle, case 29), selftest case 29, an `archived()` helper, and the adjusted cases 1, 6, 8 control, 12 and 15 stagger.

## Checks
- `python3 redck.py record step-2/handoff.md`, run before the first edit: recorded 5 controls, all red, phase `retrospective` (see Notes).
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` after the implementation, before the test updates: FAIL, 14 misses. They were existing cases reading closed lane trees or branches, plus `?? .worktrees/` in cases 1 and 12.
- The same selftest after the case updates and case 29: PASS (2:13). After that I ran C1 again in full as the acceptance run, so the selftest ran twice green. That repeat is a small deviation from rule 10.
- C1 (four label greps, then `fanout.py selftest`): exit 0.
- C2 (the mutant: `close_lane` replaced by a stub returning rc=1): the mutant selftest failed, and its stderr has `case 29 lifecycle: merged lane gone`. Exit 0.
- C3 `grep -qF "case 29 lifecycle: sweep off keeps"`: exit 0.
- C4 `grep -qF "lanes.open_lane("`: exit 0.
- C5 `grep -qF "lanes.sweep("`: exit 0.
- C6 `grep -qF "SDLC_LANE_PORT"`: exit 0.
- C7 scope check (only lanes.py, solo_run.py and fanout.py differ from base outside `.sdlc`): exit 0.
- C8 `git diff --check $SDLC_BASE_SHA -- plugins/sdlc-lite/scripts/fanout.py`: exit 0.
- The temporary edit scripts and the mutant copy under `.worktrees/tmp/0452-s2-builder-L3` are removed. No worktree was created.

## Notes
- The red checkpoint is `retrospective`, not pre-edit. Step 1's `lanes.py` and `solo_run.py` were already uncommitted in this lane when I ran `record`. `fanout.py` was untouched at that point and all 5 recorded controls were red. Only 5 of the 6 `(red)` criteria were recorded. The one missing is C1 (the label greps plus selftest).
- Behavior change outside the handoff text: `lanes.open_lane` takes its flock at `<lanes root>/lanes.lock`, which defaults to `<toplevel>/.worktrees`. So a run with an outside `--lanes-dir` now creates `.worktrees/lanes.lock` in the main tree. Preflight does not check that `.worktrees/` is gitignored in that case. The docstring states the requirement. The planner should decide whether step 3 or a follow-up ticket adds a preflight check.
- Fixture edits the verifier will see:
  - Case 1's repo now commits `.gitignore: .worktrees/`.
  - Case 12's `external` repo gets `.worktrees/` in `.git/info/exclude`. Both changes come from the `lanes.lock` behavior above.
  - Cases 1 (the `T-0004.saw` read, board without beta, beta archived), 6, the case 8 control, 12 and the case 15 stagger now read merged lanes on the integration branch or at their `refs/archive/...` ref. Their messages say the lane was closed.
  - Case 13 was named in the handoff but needed no change: it reads `fanout/ov:shared.txt` after the run, and its stubs read `../alpha` only while the lanes are still running.
- The `open_lane` call also passes `root=str(ctx['root'])`, which is not in the handoff's signature. With it, branch descriptions and the archive tag message get the ticket title under a non-default `--root`.
- `sweep_lanes` catches only `lanes.LaneError`, as the handoff specifies. An `OSError` raised inside lanes.py would still stop the run. Question for the planner: should the catch be wider? I did not change it.
- Sweep prints every result line, including the `kept <lane>: ...` lines.
- The setup line now shows the port, for example `worktree alpha: <dir> (branch <b>, port N)`. Case 29 checks this line.
- The integration report line uses the `integ_dir` path.
