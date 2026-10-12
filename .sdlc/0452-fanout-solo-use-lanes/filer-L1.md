<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: step 2, red-checkpoint: retrospective. Attempt 2dc26decede7462a97e461b1965d99f8 (handoff sha256 1cfc260d88cf) had 5 of 5 `(red)` criteria without a pre-edit red control. They were the fo-mut mutant command, the `case 29 lifecycle: sweep off keeps` grep, and the greps for `lanes.open_lane(`, `lanes.sweep(` and `SDLC_LANE_PORT`. The builder also reported that criterion C1 (label greps plus selftest) had no recorded control, and that the C1 selftest ran twice, against rule 10. The verifier ran the mutant itself, saw the red, and passed the step. A passing verdict does not clear the deviation.
- process deviation: step 3, red-checkpoint: retrospective. Attempt 056df778d68a4a3ebfcb722d6ba962f5 (handoff sha256 847b5012ba49) had 5 of 5 `(red)` criteria without a pre-edit red control. They were the absence of "Lane worktrees stay after the run" in SKILL.md, the presence of `lanes.py sweep --apply`, `lanes.py open` and the `allowed-tools` entry in SKILL.md, and the absence of "the worktrees stay for inspection". The builder said only 5 of the 6 `(red)` criteria were recorded because steps 1 and 2 were already uncommitted when `record` ran. The verifier read the pre-state from the base diff and passed the step.
- Step 1 recorded its red controls before any edit (4 controls). It has no process deviation.
- Step 3 check.sh: the first run exited 1 on `gate_lock selftest ... isolation: the real state root was not touched`. `gate_lock.py` is unchanged from base and passes alone, and a full rerun exited 0. The verifier judged it contention, not a regression. This is the same kind of flake T-0452 set out to fix in `lanes.py`.
- All three steps got a verifier verdict of pass. The Loose ends step has no artifact.

## PR title
T-0452: fanout.py and solo_run.py open and close lanes through lanes.py

## PR body
### Summary
`fanout.py` and `solo_run.py` now open and close their lanes through `lanes.py` (lane lifecycle B, section 13 of `docs/specs/sdlc-lite/lane-lifecycle.md`).
- A merged lane's tree is gone after a run.
- A stopped lane stays, with a `lane still open: <path> (<outcome>)` report line.
- The `lanes.py selftest` isolation flake from T-0451 is fixed.

### Changes
- `plugins/sdlc-lite/scripts/lanes.py`:
  - `open_lane` takes keyword-only `path=`, `branch=` and `check_claim=`.
  - New `host_record` helper.
  - `sweep --apply` keeps a lane as `merging` while another process holds `merge.lock`.
  - The CLI `open` gains `--path`, `--branch` and `--no-claim`.
  - The selftest isolation check now compares only a sentinel repo inside the selftest's temp dir, not the real repository. It keeps observed-red controls: a planted ref and a planted worktree are both caught.
  - New selftest cases: `open path`, `host record`, `sweep merge.lock`.
- `plugins/sdlc-lite/scripts/solo_run.py`: `ensure_worktree` opens the tree through `lanes.open_lane(kind='solo', check_claim=False)` when the task has a ticket id. It reuses an existing tree and raises `Refuse` on an open refusal. The selftest has new `--worktree lanes:` expects.
- `plugins/sdlc-lite/scripts/fanout.py`:
  - `setup` opens lanes via `lanes.open_lane`, with `SDLC_LANE_PORT` for the driver and gate env.
  - `sweep_lanes` runs at the start of a run and is skipped when `lane_sweep` is `off`.
  - `close_lanes` closes merged lanes after the joins and before the report.
  - `prep` writes dispatch and host records and prints `lanes.py open` for a `full` lane.
  - `land` rebinds the host record.
  - `roll` removes its scratch tree.
  - `settle` removes the integration branch and worktree after a non-fast-forward merge, through `close_lane` with an archive ref.
  - The docstring and selftest are updated, with new cases 28 to 32.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: a "Lane lifecycle" paragraph replaces "Lane worktrees stay after the run". Step 5 runs `lanes.py sweep --apply`. `allowed-tools` gains `lanes.py`. The `.claude/worktrees/` phrase `check.py` pins is kept. The sub-agent step 1 wording "creates nothing" now names the dispatch and host records.
- `docs/references/sdlc-internals.md`: "the worktrees stay for inspection" replaced.

### Verification
- Step 1, verifier pass:
  - `lanes.py selftest` exits 0 with the isolation line. A leaked ref added after the cases made the selftest print `FAIL: isolation` and exit 1.
  - Disabling the merge.lock branch turned that case red.
  - `solo_run.py selftest`: PASS.
- Step 2, verifier pass:
  - `fanout.py selftest`: PASS, with case 29 value-pinned.
  - A mutant that stubs the close (`# LANE-CLOSE`) made `case 29 lifecycle: merged lane gone` fail.
  - The four label greps and the `SDLC_LANE_PORT` grep hit.
- Step 3, verifier pass:
  - Mutants for roll cleanup, `land_lanes`, host rebind and settle each failed only their own case (31, 32, 30, 28).
  - The SKILL.md and docs greps pass.
  - `check.py plugins/sdlc-lite`, `check-packaging.py` and `git diff --check` pass.
  - `check.sh` exited 0 on a rerun. Its first run failed on a `gate_lock` isolation flake that is unrelated to this change.
- Scope: only the five allowed files differ from base outside `.sdlc`.
- Process deviations: two retrospective red checkpoints (steps 2 and 3), listed under Warnings.

### Limitations
- In the prep and land flow, `fanout.py settle` will usually refuse and exit 1 with `lane still open: ... (lanes still open into <integration>: <host lanes>)`. Prep's host records stay open until T-0453's `dispatch.py prune --done`. This is the expected row 4 refusal. Case 28 has no row 4 control.
- `settle` now keeps an integration branch that has no worktree (`lane still open: <branch> (no worktree)`, exit 1). The old code deleted it. The fast-forward still runs before the close, so main can move even when the close refuses.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- fanout and solo now open and close lane worktrees through `lanes.py`. A merged lane's tree is removed after a run, a stopped lane stays with a `lane still open` line, and `fanout.py settle` removes the integration branch. The `lanes.py selftest` isolation check no longer reads the real repository.

## Follow-ups
- decide: `fanout.py settle` refuses in the prep and land flow because host records into the integration branch stay open until T-0453's `dispatch.py prune --done`; confirm T-0453 covers this, or relax row 4 for that case.
- fix-now: a run with an outside `--lanes-dir` now creates `.worktrees/lanes.lock` in the main tree, and preflight does not check that `.worktrees/` is gitignored. Add a preflight check or a docstring-pinned refusal.
- note: `sweep_lanes` catches only `lanes.LaneError`, so an `OSError` from `lanes.py` would still stop a run.
- note: two `roll` runs sharing one lanes dir at once could remove each other's scratch tree.
- note: the Loose ends step has no artifact, so no loose-end verdict exists for this task.
