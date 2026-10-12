## Task goal
fanout and solo_run open and close their lanes through `lanes.py`, so a merged lane's tree is gone after a run and a stopped lane stays with a report line.

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
   - Why the claim bypass: fanout and solo_run lanes hold `ready`, unclaimed tickets. Setting `claimed_by:` from fanout is ticket T-0455 (`.sdlc/0455-fanout-claimed-status/handoff.md`), so these callers pass `check_claim=False` until it lands.
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
