<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- AC1 (selftest: every one of the 35 step 3 labels printed as `ok: <label>`, `supervisor selftest: PASS` as the last line, the main checkout's `.sdlc/supervisor` unchanged, no `./.sdlc/supervisor`): pass. Evidence:
  - Verbatim command in the built tree: `AC1 rc=0`, 70.66 s wall clock (under the 150 s target). The saved output has 67 `ok:` lines plus `supervisor selftest: PASS`; all 35 step 3 labels and all 32 step 2 labels are present (`missing=0` from a grep loop over the step 2 handoff's list). `ps` after every run showed no leftover `stub.py` or `sleep 60` process.
  - Red at the pre-build HEAD: in `git worktree add --detach "$SDLC_TMP_WORKTREES/base" "$SDLC_BASE_SHA"` the same command gives `rc=2` (`can't open file .../supervisor.py`). Worktree removed afterwards (`git worktree list` shows none).
  - The selftest bites, shown on five mutated copies of `supervisor.py` with `messages.py` beside them under `$SDLC_TMP_WORKTREES`:
    - `os.killpg` changed to `os.kill` (pid only, no group): `FAIL: failure: a timed-out wake is killed and counts: a late wake was not killed: the stub grandchild 31626 still runs`, rc=1. The group signal is the biting conjunct.
    - `KILL_GRACE` 5 to 1000 (no KILL inside the deadline): `FAIL: failure: a timed-out wake is killed and counts: a late wake was not killed: watch --run --once outlived the 20 s limit`, rc=1.
    - depth rule `>=` to `>`: `FAIL: depth: a reply chain of three records needs a human: a reply chain at the depth limit woke the host: ... the stub was called 1 times, expected 0`, rc=1.
    - `receiver_state(view, _hc=hourly_cap)` holding the rule in a default argument: `FAIL: control: a copy without the hourly cap wakes past it: the case passed on the patched copy`, rc=1, so the call-time lookup rule (D20) is enforced by the controls.
    - `count_failure` excluding `lost`: `FAIL: active: a stale pid record is dropped: status field: the status the stub saw: failures is 0, expected 2`, rc=1, so "lost counts as a failure" is checked.
    - After the group-signal mutation left a grandchild alive, `ps` showed no `sleep 60` process once the run ended: the selftest's SIGKILL cleanup (`st_kill_recorded`, supervisor.py:1757-1766, called at 1806 and 2817) was observed working.
  - Code read against the Do: D8 order in `receiver_state` (supervisor.py:704-738: no pending, failed, depth, running, transcript, debounce, cooldown/backoff, hourly, daily, STOP, dry-run, notify/wake); one module-level function per rule, each looked up by name at call time (`receiver_failed` :512, `re_hops` :517, `wake_lineage` :541, `pid_matches` :562, `wake_running` :575, `stale_result` :585, `transcript_active` :591, `cooldown_end` :603, `backoff_end` :610, `hourly_cap` :639, `daily_cap` :644, `wake_result` :663, `wake_timed_out` :674, `count_failure` :679, `failure_stop` :684, `stranded_ids` :689, `reset_receiver` :699); re depth 1 for no/missing parent, +1 per parent, stops at the limit (:523-538); lineage W.depth + 1 (:553); TERM to the group then KILL after `KILL_GRACE = 5` (:880-894); `load_state` is the only reader of `state.json` (:836-853, used by `cmd_watch` :1258 and `cmd_reset` :1301); `reset_receiver` clears both fields (:701); stub records pid and lstart per call (:1413-1414), grandchild `sleep` in the stub's group when `sleep` is set (:1415-1419), `ignore_term` via `trap '' TERM` and `SIG_IGN` (:1376, :1393-1394); every status case asserts the eight fields through `st_state` (:2343-2346); the lineage case runs without `--now` (:2462-2475); the timeout case uses a 20 s subprocess limit, `wake_timeout_seconds` 1, `sleep=60, ignore_term=True`, and asserts exit 0, `timeout`, failures 1, stub and grandchild gone (:2576-2597).
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" ...)" && test -z "$(git ls-files --others ...)"`: pass. Evidence: verbatim command `guard rc=0`. The tracked diff lists only `docs/planning/ticket-stages/watcher-design.md`, `docs/reports/idle-host-watcher-design-review.md`, `plugins/sdlc-lite/scripts/check.sh`; the only untracked file outside `.sdlc` is `plugins/sdlc-lite/scripts/supervisor.py`. It bites: in the throwaway base worktree it was rc=0 clean, rc=1 with a stray `plugins/sdlc-lite/scripts/stray.py`, and rc=1 with `messages.py` modified.

Neighbor and dependent checks:
- `git grep supervisor.py` outside its own file finds only `check.sh` (the selftest line I ran) and the design doc; `messages.py` is unchanged against `$SDLC_BASE_SHA` (0 diff lines). T-0187, the future `status.json` reader, is not built. The full `check.sh` suite was not run: its only dependent on this step is the `supervisor.py selftest` line, run above, and step 7 owns that gate.
- Step 2's static criteria still hold on the built tree: AC2 (imports, no forbidden `def`) rc=0, AC3 (one main guard) rc=0, AC4 (no `shell=True`/`os.system`/`os.popen`/em dash) rc=0, AC5 (help metavar and options) rc=0. `python3 -m py_compile` ok under Python 3.9.6; 0 trailing-whitespace lines.

Builder claims checked against the tree (not restated): the 71 s timing (my run 70.66 s), the 18 controls failing for their own reason (enforced by `st_control` :2681-2707, whose prefix check is seen biting in the default-argument mutation), and the kill-code mutations (two of three reproduced above, same failure text).

Steelman pass, three drafts dropped:
- "D8 says no pending is `idle`, but `receiver_state` returns `cooling` or `waking` with no pending." Handoff item 3 requires `cooling` after a wake until the cooldown ends, and the cooldown case label pins "status cooling" with pending 0. Dropped.
- "The grandchild is in the stub's group, not a group of its own." The handoff says the timeout case proves "the group signal", which a grandchild in a separate group could not demonstrate; the group-only mutation confirms the grandchild check is what proves it. Dropped.
- "`cap_reached` is shared by both caps, so the zero-cap control rebinds more than one rule." The zero-cap rule is exactly `count >= cap`; rebinding it removes that one rule and leaves `hourly_cap` and `daily_cap` intact. Dropped.

## Out of scope changes
None. `supervisor.py` is the step's only target. The three tracked diffs (`watcher-design.md`, `idle-host-watcher-design-review.md`, `check.sh`) are the guard's listed exclusions; their mtimes are Oct 1 14:30 to 14:52 (steps 1 and 2), before this builder ran on Oct 3 17:15, and the `check.sh` diff is exactly step 2's two required edits. Entries under `.sdlc/0183-supervisor-script/` are run records.

## For the next attempt
None
