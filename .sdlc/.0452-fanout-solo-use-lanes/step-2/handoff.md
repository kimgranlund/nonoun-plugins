## Task goal
fanout and solo_run open and close their lanes through `lanes.py`, so a merged lane's tree is gone after a run and a stopped lane stays with a report line.

## Step 2: fanout run opens, sweeps, closes, and reports lanes
level: L3
### Do
Depends on: step 1 (`open_lane(path=, branch=, check_claim=)`, the sweep `merge.lock` rule).

Target is `plugins/sdlc-lite/scripts/fanout.py`: `cmd_run`, `setup`, `run_ticket` and the gate env, `report`, the run docstring and the selftest.

1. Sweep at start. After `preflight` and `refuse_overlap` succeed, and before `setup`, run `lanes.sweep(apply=True, cwd=<toplevel>)`. Skip it when `lanes.config(top)['lane_sweep'] == 'off'`.
   - Print each result message line as `lanes sweep: <line>`.
   - A `LaneError` prints `lanes sweep: <error>` and the run goes on. Sweep never blocks a run.
   - A refusal (exit 2) still creates and removes nothing.
   - Put this in one helper, because step 3's `prep` calls it too.
2. Open in setup. Each regular lane opens through `lanes.open_lane(lane.name, kind='fanout', tickets=[ids], base=integration, into=integration, path=lane.dir, branch=lane.branch, check_claim=False, cwd=ctx['cwd'])`. This replaces the `git worktree add -b`.
   - A non-zero `rc` raises `Refuse(message)`, which goes through the existing rollback. The rollback may still `git worktree remove` and `branch -D` what this run just made; spec 17.7 C14 says fanout's undo of a failed start is not a close.
   - Keep the result's `port` on the `Lane`.
   - The integration tree keeps its plain `git worktree add`, because the branch may be reused and `open_lane` creates a new one. Also create `<lanes-dir>/merge.lock` (touch) beside `logs/` in setup, so `lanes.py` reads the integration tree as a legacy fanout integration lane before the first merge.
   - Do not lock lanes: the worktree lock is ticket A2 (spec 17.9), which has not landed (`open_lane` runs no `git worktree lock`).
3. `SDLC_LANE_PORT`. When the lane has a port, set it in the driver env (`run_ticket`) and in each gate's env for that lane's tickets. Otherwise remove any inherited value.
4. Close after the run. After every lane thread has joined, and before `report`, handle each regular lane:
   - If every result is `merged`, close it through one call on a line ending `# LANE-CLOSE`: `lanes.close_lane(str(lane.dir), cwd=str(ctx['top']))`. That marker must appear exactly once in fanout.py; the mutant criterion edits that line.
   - Otherwise the lane stays: its tree and WIP commit are kept.

   Sweep runs before any thread starts and close runs after `join`, so no lane thread races a close. Keep it that way: never close inside `run_lane`.
5. Report lines, after the Overlap lines:
   - Each closed lane: `- <close message first line>`, for example `- closed alpha (ancestor)`.
   - Each stopped lane, or a close that refused: `- lane still open: <path> (<outcome>)`. The outcome is the lane's first non-`merged` outcome, or the close outcome.
   - The integration tree: `- lane still open: <integ_dir> (integration: stays until main contains <integration>)`.

   Each is also printed with the report.
6. Docstring `run` section. Replace "the worktrees stay for inspection" with the lifecycle (open through lanes, close of merged lanes with an archive ref first, stopped lanes kept with their line, sweep at start, `lane_sweep: off`, `SDLC_LANE_PORT`), and describe case 29 under `selftest`.
7. New selftest case 29. Fixture `.sdlc/config` has `lane_ports: 47400-47499` and `lane_min_age_hours: 0`. Run `alpha=T-0001 beta=T-0002`, with a driver that exits 3 for T-0002 and writes `$SDLC_LANE_PORT` to a file, plus a gate that logs it. The case's expect messages carry these labels:
   - `case 29 lifecycle: merged lane gone`: alpha's tree and `refs/heads/<integration>-alpha` are gone, and a `refs/archive/<UTC date>/<integration>-alpha` ref resolves to its tip.
   - `case 29 lifecycle: stopped lane kept`: beta's tree and branch remain, and report.md has `lane still open: <beta path> (driver failed rc=3)`.
   - `case 29 lifecycle: SDLC_LANE_PORT`: the driver and gate saw the port in the lane record, inside the range.
   - `case 29 lifecycle: sweep at start`: a landed plugin lane, made before the run with `lanes.py open` and merged into main, is closed by the run's start and logged as `lanes sweep: closed`.
   - `case 29 lifecycle: sweep off keeps`: the same with `lane_sweep: off` leaves it open.
8. Existing cases that read a merged lane's tree or branch after a run must change to expect them closed. They include the first case's `board.py --lanes` expects that pin `fanout/test-alpha` and `fanout/test-beta` (found with `git grep -n "fanout/test-" -- plugins/sdlc-lite/scripts/fanout.py`), case 6, case 12's beta and case 13. Keep each case's intent and note in its message that the lane was closed. Cases 9 and 10 remove a stopped lane themselves and stay as they are.

Validation scope is `fanout.py selftest` (108 s at base) and the mutant run.
### Acceptance criteria
- (red) `for l in "case 29 lifecycle: merged lane gone" "case 29 lifecycle: stopped lane kept" "case 29 lifecycle: SDLC_LANE_PORT" "case 29 lifecycle: sweep at start"; do grep -qF "$l" plugins/sdlc-lite/scripts/fanout.py || exit 1; done && python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (red) `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/fo-mut.XXXXXX") && cp -R plugins/sdlc-lite "$d/p" && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); assert s.count(\"# LANE-CLOSE\") == 1; open(p, \"w\").write(chr(10).join(l.replace(\"lanes.close_lane(\", \"(lambda *a, **k: dict(rc=1, message=chr(109), path=None))(\", 1) if \"# LANE-CLOSE\" in l else l for l in s.split(chr(10))))" "$d/p/scripts/fanout.py" && ! python3 "$d/p/scripts/fanout.py" selftest >/dev/null 2>"$d/err" && grep -qF "case 29 lifecycle: merged lane gone" "$d/err"`
- (red) `grep -qF "case 29 lifecycle: sweep off keeps" plugins/sdlc-lite/scripts/fanout.py`
- (red) `grep -qF "lanes.open_lane(" plugins/sdlc-lite/scripts/fanout.py`
- (red) `grep -qF "lanes.sweep(" plugins/sdlc-lite/scripts/fanout.py`
- (red) `grep -qF "SDLC_LANE_PORT" plugins/sdlc-lite/scripts/fanout.py`
- `out=$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc") && test -z "$(printf "%s\n" "$out" | grep -vxF -e plugins/sdlc-lite/scripts/lanes.py -e plugins/sdlc-lite/scripts/solo_run.py -e plugins/sdlc-lite/scripts/fanout.py -e "")"`
- `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/fanout.py`
