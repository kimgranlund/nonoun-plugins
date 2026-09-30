<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: ran on the built tree, `run selftest: PASS`, rc 0 (35 s). Seen red three ways: the new selftest against the base plugin (criterion 6 below) gives `FAIL: stale prefix: dead-owner prefix builder-81703 is still on disk`; the same base copy with the stale-prefix block (lines 337..359) deleted gives `FAIL: term cleanup: a worktree under .worktrees/tmp is still registered: .../wrepo/.worktrees/tmp/builder-86812/w`; a copy of the built plugin with the `stop_role` call (run.sh:386) deleted gives `FAIL: term cleanup: the stub claude (pid 92479) is still alive`. Each new case bites on its own, and the liveness assertion bites independently of the worktree assertions.
- `test -x plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh`: pass. Evidence: rc 0 on the built tree (mode `-rwxr-xr-x`); rc 1 in the throwaway worktree at `$SDLC_BASE_SHA` (e399089), where the file does not exist.
- `grep -qF reap-tmp-worktrees.sh plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: rc 0 built; rc 1 at base. The reference is a real call: run.sh:292-294 `reap_tmp()` runs `scripts/reap-tmp-worktrees.sh "$toplevel" "$wt_tmp"`, called at :313 (before `snap_wt=` at :315) and at :307 inside `cleanup_worktrees` after `rm -rf "$wt_tmp"` at :306; both sit after the dry-run `exit 0` at :260, so a dry run never reaps.
- `grep -qF 'fail "stale prefix:' plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: rc 0 built; rc 1 at base. `grep -c 'reap-tmp' run-selftest.sh` is 0, so the case drives run.sh only, as the Do requires.
- `grep -qF 'fail "term cleanup:' plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: rc 0 built; rc 1 at base.
- The new selftest fails on the base run.sh (verbatim command): pass. Evidence: ran the exact command with `$SDLC_BASE_SHA`=e399089c…; `criterion rc=0`; captured output `run selftest: FAIL: stale prefix: dead-owner prefix builder-81703 is still on disk`. Archive dir removed afterwards.
- `grep -qF reap-tmp-worktrees.sh docs/maintenance/sdlc-internals.md`: pass. Evidence: rc 0 built; rc 1 at base. The diff shows the run.sh paragraph now describes the background role + TERM/KILL-after-2 s handler and the reaper at start and exit, dead-owner prefixes, never deletes a branch.
- `bash -n plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh`: pass. Evidence: rc 0; the check goes red on a bad snippet (`bash -n <<<'if [ ; then'` rc 2, "syntax error").

Do-item checks beyond the criteria, all observed:
- Reaper contract (direct probe on a scratch `git init` repo under `$SDLC_TMP_WORKTREES`, plain dirs): with own=`verifier-<dead>`, `builder-<dead>` was removed while `builder-$$` (live), `foo`, `Builder-1` (case mismatch) and the own prefix stayed; a second call without own removed `verifier-<dead>`; with the rest cleared, `.worktrees/tmp` and `.worktrees` were rmdir'd; missing toplevel rc 0, no args rc 0; with no `ps` on PATH (PATH holding only git/rm/rmdir/sed) the dead-owner dir was kept and rc 0, then removed once `ps` was back. This confirms the builder's "no ps means no reaping" note by a run, not by its summary.
- run.sh launches the role with `&`, records `role_pid=$!`, `wait`s, keeps `</dev/null >"$log" 2>&1` and the "exited non-zero; see $log" / `exit 1` path (diff); `want_wt fail 1` in the guard exercises the non-zero path. `on_exit` order is `stop_role` (:386) then `cleanup_worktrees` (:388); traps 130/143/129 at :397-399 unchanged; the body is still one `{` (:84) … `exit 0` (:451) `}` (:452) group, and the guard's `self-edit` case passed. Term-cleanup asserts exit 143 and passed with the fix.
- Neighbors: `lifecycle-selftest.py` OK; `check.py` "ok: 18 role levels, 8 agents checked"; `scripts/check-packaging.py` PASS; `git diff --check` rc 0.
- Throwaway worktree `$SDLC_TMP_WORKTREES/base` removed; `git worktree list` shows 0 entries under my prefix and the prefix dir is empty. `git status` after all runs matches the pre-verification state (3 modified, 1 new script).

## Out of scope changes
None. Diff touches only the four files the step names. One note for the next step, not a fail: `reap-tmp-worktrees.sh` header line 5 says "fanout calls it for a lane after each driver", but `grep -c reap plugins/sdlc-lite/scripts/fanout.py` is 0. Steelman: planner-L2.md step 2 adds exactly that call, and the step's Do asks the header to state the script's contract, which it does; no criterion covers callers. Dropped as a fail reason; step 2 should make the sentence true or trim it.

## For the next attempt
None.
