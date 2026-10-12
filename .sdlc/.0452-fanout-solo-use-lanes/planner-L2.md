<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `fanout.py` and `solo_run.py` open and close their lanes through `lanes.py`, so a merged lane's tree is gone after a run and a stopped lane stays with a `lane still open` report line. Also make the `lanes.py selftest` isolation check compare only its own temporary repository.

guard timeout: 2700

## Step 1: lanes.py caller API, sentinel isolation, and solo_run through lanes
level: L3
### Do
Depends on: none.

Targets are `plugins/sdlc-lite/scripts/lanes.py` and `plugins/sdlc-lite/scripts/solo_run.py`.

1. Flake fix. The T-0451 isolation check was never a `lanes.py` case. It was the shell criterion at `.sdlc/.0451-lanes-core/step-1/handoff.md` line 212. That criterion compared the real repository's `git worktree list --porcelain` and `git for-each-ref refs/heads refs/archive`, so other sessions writing refs made it red (see `.sdlc/.0451-lanes-core/handoff.md`, `## Closed`). Fix it inside the selftest:
   - In `selftest()`, before `run_selftest`, create a sentinel repo under the selftest's temp `base` (`git init`, one commit) and `os.chdir` into it for the whole run. Restore the old cwd in the `finally`. Any cwd-relative leak now lands in the sentinel.
   - Snapshot the sentinel's `git worktree list --porcelain` plus `git for-each-ref` before the cases and compare after them. A difference prints `FAIL: isolation: <diff>` and exits 1.
   - Observed-red control, inside the selftest: plant `refs/heads/leak` in the sentinel and require the compare to report a difference. Then plant a `git worktree add --detach` tree in the sentinel and require it to be caught too.
   - Only then print exactly `ok: isolation: the sentinel repo is unchanged; a planted ref and a planted worktree are both caught`.
   - The selftest never reads the real repository.
2. `open_lane` gains keyword-only `path=None`, `branch=None` and `check_claim=True`.
   - `path` sets the tree; the leaf is its basename. `branch` is used verbatim. `git check-ref-format --branch`, the clash test and the existing-tree refusal still run. The `.lane.json` record, the `info/exclude` line, the description, the port and `lane_setup` are unchanged.
   - With `check_claim=False`, `claim()` is skipped for local ids. The ids are still recorded, and the title for the description comes from the ticket when it is readable.
   - Why: fanout keeps its layout (`<lanes-dir>/<lane>` on `<integration>-<lane>`). Its selftest stubs read `../alpha/shared.txt` and `../logs/fanout.log` (`OVERLAP_STUB` in fanout.py), and `land_lane_name`, `docs/references/sdlc-internals.md`, `skills/fanout/SKILL.md` and selftest case 22 all name `<integration>-<lane>`.
   - Why the claim bypass: fanout and solo_run lanes hold `ready`, unclaimed tickets. Setting `claimed_by:` from fanout is ticket T-0455 (`.sdlc/.0455-fanout-claimed-status/handoff.md`), so these callers pass `check_claim=False` until it lands.
   - The CLI `open` gains matching `--path DIR`, `--branch NAME` and `--no-claim`. Add them to the docstring usage.
   - The default CLI and API path still refuses an unclaimed ticket, so `case_claim_unclaimed` stays green.
3. New `host_record(name, branch, into, tickets, base=None, cwd='.')`. It writes `<lanes root>/host/<name>.lane.json` with every key of `FIELDS`:
   - `kind host` and `lane <name>`.
   - `base` (default main) and `base_sha`.
   - `opened`, and `run_id` from `$SDLC_RUN_ID`.
   - A port picked under the `lanes.lock` flock when `lane_ports` is set.

   It overwrites a record of the same name and returns the dict.
4. In `sweep(apply=True)`, a lane whose parent dir holds `merge.lock` (a fanout lanes dir) closes only while sweep holds a non-blocking `fcntl` exclusive lock on that file. If the lock is busy, the result is `kept <lane>: merging (merge.lock held)`. This is the section 8 rule that sweep never closes a lane a `land` is merging.
5. New selftest cases, each printing one `ok:` line:
   - `ok: open path: ...`: through the CLI with `--path --branch --no-claim`, an unclaimed ticket opens at the given path and branch with a record. The same call without `--no-claim` refuses.
   - `ok: host record: ...`: the record file has every field, and `discover` reads it.
   - `ok: sweep merge.lock: ...`: the test process holds the flock on a legacy lanes dir's `merge.lock`. `sweep --apply` then keeps a landed lane there with `merging`, and closes it once the lock is released.
   - The `MUTANTS` table requires each marked line (`# NAME-FIRST`, `# DIRTY-CHECK`, the REALPATH line) to appear exactly once. Do not duplicate them.
6. In solo_run, `ensure_worktree(name, base=None, task_dir=None)` works like this:
   - When the task's `handoff.md` front matter has an `id:` (read through `tickets.py`, the only front matter parser), it opens through `lanes.open_lane(name, kind='solo', tickets=[id], check_claim=False, cwd=base)`. The tree is `<lanes root>/<id>-<slug>` on branch `lane/<id>-<slug>` (spec section 17.9 B: the ticket-known form).
   - An existing tree at that path is reused, and an open refusal raises `Refuse(<message>)`.
   - With no id, today's `.worktrees/<name>` on branch `<name>` is kept unchanged.
   - Update both callers (the dispatch path and the `--exec` path in `main`, today lines 1130 and 1135) to pass the task dir.
   - Add selftest expects whose labels start with `--worktree lanes:`. A ticketed task with `--worktree lane-x` runs in `.worktrees/T-0001-lane-x` on `lane/T-0001-lane-x`, with a `.lane.json` of kind `solo` listing the ticket, and the session cwd is that tree. Keep the existing `--worktree:` expects for the no-id fixture.

Validation scope is `lanes.py selftest` (about 50 s at base) and `solo_run.py selftest` (about 26 s). No other caller uses `ensure_worktree`; `git grep -n ensure_worktree` finds only solo_run.py. `open_lane`'s new parameters are keyword-only and default to today's behavior, so the T-0453 callers are unaffected.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/lanes.py selftest) && printf "%s\n" "$out" | grep -qF "ok: isolation: the sentinel repo is unchanged; a planted ref and a planted worktree are both caught"`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/lanes.py selftest) && for l in "ok: open path:" "ok: host record:" "ok: sweep merge.lock:"; do printf "%s\n" "$out" | grep -qF "$l" || exit 1; done`
- (red) `python3 -c "import sys; sys.path.insert(0, \"plugins/sdlc-lite/scripts\"); import inspect, lanes; ps = inspect.signature(lanes.open_lane).parameters; sys.exit(0 if all(k in ps for k in (\"path\", \"branch\", \"check_claim\")) and callable(getattr(lanes, \"host_record\", None)) else 1)"`
- (red) `grep -qF -- "--worktree lanes:" plugins/sdlc-lite/scripts/solo_run.py && python3 plugins/sdlc-lite/scripts/solo_run.py selftest`
- `out=$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc") && test -z "$(printf "%s\n" "$out" | grep -vxF -e plugins/sdlc-lite/scripts/lanes.py -e plugins/sdlc-lite/scripts/solo_run.py -e "")"`
- `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/lanes.py plugins/sdlc-lite/scripts/solo_run.py`

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

## Step 3: prep, land, roll and settle use lanes; skill and reference text; gates green
level: L3
### Do
Depends on: step 2 (the sweep helper and the lane record in fanout).

Targets are `plugins/sdlc-lite/scripts/fanout.py` (`cmd_prep`, `print_prep`, `cmd_land` and `land_ticket`, `cmd_roll`, `cmd_settle`, the docstring and the selftest), `plugins/sdlc-lite/skills/fanout/SKILL.md` and `docs/references/sdlc-internals.md`.

1. prep:
   - Run the step 2 sweep helper after `refuse_overlap`, so a refusal still changes nothing.
   - For each solo dispatch, call `lanes.host_record(<id>-solo, branch=d['branch'], into=integration, tickets=[id], base=start, cwd=top)` and print `    host record: <path>`.
   - For a `full` lane's first ticket, replace the `tree: git worktree add -b ...` line with `tree: python3 <scripts>/lanes.py open <lane> --kind fanout --ticket <id>... --base <start> --into <integration> --path <tree> --branch <integration>-<lane> --no-claim`, listing all of the lane's ids.
   - Update prep's header line ("creates only ...") to name the host record.
2. land:
   - Host lane rebind (on `merged`): the host names the tree `agent-<agent_id>`, not `<id>-solo` (SKILL.md step 2, observed 2026-10-07). When the landed branch is checked out in a worktree under `<top>/.claude/worktrees/` whose leaf differs from `<id>-solo`, write `host_record(<leaf>, branch=<branch>, ...)` and remove the provisional `<lanes root>/host/<id>-solo.lane.json`. The host lane stays open; `dispatch.py prune --done` closes it (ticket C, T-0453).
   - Full lane close: when the branch's tree has a `.lane.json` of kind `fanout` and this ticket is the record's last ticket, close it after the merge lock is released with `lanes.close_lane(<tree>, into=<integration>, cwd=top)`. Print the close message, or `lane still open: <path> (<outcome>)`.
3. roll: at the end of every roll, after `roll_setup` succeeded and whatever the outcome, run `git worktree remove --force <lanes-dir>/rolling` and `git worktree prune`. The scratch tree is detached and holds no branch. `roll_setup` still creates it when absent.
4. settle: after the fast-forward, or when the branch is already merged, close the integration branch's worktree through `lanes.close_lane(<worktree path>, into=<current branch>, cwd)`. This writes the archive ref before any removal (a handoff constraint), and the `--force` removal no longer stops on an untracked copied `.sdlc/config`. Print its message. Any refusal (not a plugin lane, row 4 lanes still open, no worktree) prints `lane still open: <path or branch> (<outcome>)`, keeps the branch and exits 1. The diverged refusal (exit 2) is unchanged.
5. Selftest:
   - Case 28 gets label `case 28 settle archive`. Its integration trees live at `<lanes dir>/<n>/integration` with `merge.lock` and `logs/`, as fanout makes them. After settle, `refs/archive/<UTC date>/fanout/ff` and `.../fanout/hand` exist. A tree outside a lanes dir is kept with `lane still open` and exit 1.
   - Case 30 (`case 30 host record`): prep writes `<lanes root>/host/T-0001-solo.lane.json` with kind `host` and ticket T-0001. A land from a worktree under `.claude/worktrees/agent-x` rebinds it to `agent-x.lane.json`.
   - Case 31 (`case 31 roll scratch`): after a merged roll and after a refused roll, `<lanes-dir>/rolling` is absent and `git worktree list --porcelain` names no rolling tree.
   - Case 32 (`case 32 full lane close`): a tree opened with prep's printed `lanes.py open` line, landed for its last ticket, is gone with an archive ref, and its branch is deleted.
   - Update case 22's `worktree add -b fanout/p-alpha` expect (found with `git grep -n "worktree add -b fanout/p-alpha"`) to the `lanes.py open` line, and its "creates no file" expect to allow the host record.
6. `skills/fanout/SKILL.md`:
   - Replace "Lane worktrees stay after the run so they can be inspected." with a lifecycle paragraph. It covers: lanes open through `lanes.py`; each lane whose tickets all merged is closed after an archive ref `refs/archive/<date>/<branch>`; a stopped lane stays with `lane still open: <path> (<outcome>)`; the integration tree stays until main contains it; `run` and `prep` start with `lanes.py sweep --apply` unless `lane_sweep: off`; roll removes its scratch; `$SDLC_LANE_PORT` is set under `lane_ports:`.
   - Sub-agent step 5 says the full-lane tree is made with the `lanes.py open` command prep prints.
   - `## 5. Main`: after the user-approved `git merge --ff-only <integration>`, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py settle <integration>`, which closes the integration tree now. Then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lanes.py sweep --apply`, which closes every other landed lane; a lane younger than `lane_min_age_hours` waits for a later sweep. Settle comes first because sweep's `recent` row keeps a tip made minutes ago (lanes.py docstring, the truth table).
   - Add `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lanes.py:*)` to `allowed-tools`.
   - Keep every phrase `check.py` pins: `FANOUT_SKILL_PHRASES` (`Solo first`, `--max-lanes`, `--stagger`, `fanout.py prep`, `fanout.py land`, `` `Tree: <path>` ``, `.claude/worktrees/`), the long-run words (`interactive`, `run_in_background`, `notification`, `sleep`, `SDLC_HEADLESS`), and the inherited-red route text.
7. `docs/references/sdlc-internals.md`:
   - Line 147: replace "the worktrees stay for inspection" with the lifecycle sentence.
   - Line 141: prep "creates nothing and writes nothing" now writes the host record; settle "removes its worktree and deletes the branch" now closes through `lanes.close` with the archive ref first; land rebinds the host record and closes a full lane after its last ticket.
8. Fanout docstring: update the prep, land, roll and settle sections. The phrase "the worktrees stay for inspection" must be gone.
9. Gates: run every gate below and fix any red an earlier step introduced.
### Acceptance criteria
- (red) `for l in "case 28 settle archive" "case 30 host record" "case 31 roll scratch" "case 32 full lane close"; do grep -qF "$l" plugins/sdlc-lite/scripts/fanout.py || exit 1; done && python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (red) `! grep -qF "Lane worktrees stay after the run" plugins/sdlc-lite/skills/fanout/SKILL.md`
- (red) `grep -qF "lanes.py sweep --apply" plugins/sdlc-lite/skills/fanout/SKILL.md`
- (red) `grep -qF "lanes.py open" plugins/sdlc-lite/skills/fanout/SKILL.md`
- (red) `sed -n "/^allowed-tools:/p" plugins/sdlc-lite/skills/fanout/SKILL.md | grep -qF "scripts/lanes.py"`
- (red) `! grep -qF "the worktrees stay for inspection" plugins/sdlc-lite/scripts/fanout.py docs/references/sdlc-internals.md`
- (guard) `grep -qF ".claude/worktrees/" plugins/sdlc-lite/skills/fanout/SKILL.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
- `out=$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc") && test -z "$(printf "%s\n" "$out" | grep -vxF -e plugins/sdlc-lite/scripts/lanes.py -e plugins/sdlc-lite/scripts/solo_run.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/skills/fanout/SKILL.md -e docs/references/sdlc-internals.md -e "")"`

## Assumptions
- The T-0451 isolation check was a plan criterion, not a `lanes.py` case. Verified by `.sdlc/.0451-lanes-core/step-1/handoff.md:212`, by `.sdlc/.0451-lanes-core/handoff.md` (`## Closed`), and by `grep -n "isolation" plugins/sdlc-lite/scripts/lanes.py`, which finds only the kinds-table text.
- Ticket A2 (worktree lock and worktree config) has not landed, so B does not lock lanes. Verified by reading `open_lane` (lanes.py:815-885): it has no `git worktree lock`, and the selftest has no C11 or C12 case.
- The 17.9 amendments to B are left out of this ticket: the `wave/<N>` default, `lane/<ticket>-<slug>` names for fanout lanes, the lock at open, and `lane_names: legacy`. Fanout keeps `<integration>-<lane>` through `open_lane(path=, branch=)`; only solo_run's ticketed `--worktree` takes `lane/<id>-<slug>`. Verified by the handoff's Do, which lists exactly the section 13 items, and by the dependents of the old names: `docs/references/sdlc-internals.md:141,147`, `skills/fanout/SKILL.md:20,30`, `land_lane_name`, case 22, and the board expects in fanout.py's selftest.
- Fanout and solo_run open with `check_claim=False`, because claiming tickets from fanout is T-0455's scope. Verified by `.sdlc/AGENTS.md:22` and by the existence of `.sdlc/.0455-fanout-claimed-status/`. Fanout's preflight already refuses done, dropped, unknown and uncommitted tickets.
- Settle's non-fast-forward retirement already exists (T-0438, case 28 `fanout/hand`). This ticket routes its removal through `lanes.close_lane` so the archive ref comes first. Verified by `cmd_settle` (fanout.py:2048-2074) and case 28 (fanout.py:3775-3815).
- `lanes.config` and fanout's config copy both read the main worktree's `.sdlc/config`. Verified by `config()` (lanes.py:209) and `setup()` (fanout.py:938-993).
- Run times at base: `lanes.py selftest` exit 0 in 47 to 51 s, `solo_run.py selftest` PASS in 26 s, `fanout.py selftest` PASS in 108 s. Each step's red criteria exited 1 for the missing behavior, and the step 3 guards other than `check.sh` exited 0.
- `guard timeout: 2700` is about three times the 897 s `check.sh` run recorded in `.sdlc/.0441-overlay-mechanism-builder-ends/planner-L2.md`.

## Risks
- `check.sh` was not run at plan time. Its green state at base rests on T-0451's closing record, where it passed on rerun after one flake. Any fanout or lanes selftest flake under parallel load shows up on the step 3 guard.
- Closing merged lanes after a run changes several existing fanout selftest cases (the board case, case 6, case 12, case 13). Step 2 may run long while those are adjusted.
- The host lane's real tree name (`agent-<agent_id>`) is known only at land, so a provisional `<id>-solo` record stays until land rebinds it. A solo that never lands leaves a provisional record whose tree never exists. `discover` lists it with `exists` false, and sweep skips it.
- The maintainer may want the 17.9 naming (`wave/<N>`, `lane/<ticket>-<slug>` for fanout lanes) in this ticket. If so, it is a follow-up ticket that touches the dependents named in Assumptions.
- `lane_min_age_hours` (default 2) means sweep at the start of a run, and the step 5 sweep, close only lanes whose tip is at least that old. The skill text says so; settle closes the integration tree right away.
