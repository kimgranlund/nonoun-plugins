<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/solo_run.py selftest`: pass. Evidence: real tree, rc=0, `solo_run selftest: PASS`, three runs (HEAD c461bc6 at 09:01, 832bb36 at 09:22, 2cd5342 at 09:28). It can go red: five separate reverts in the throwaway worktree each gave rc=1 (lines quoted under the last criterion).
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. Evidence: real tree, rc=0, `fanout selftest: PASS` on the same three HEADs (about 71 s each). Red on revert of `fanout.py:458`, rc=1.
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: pass. Evidence: real tree, rc=0, `board selftest: PASS` on the same three HEADs. Red on revert of `board.py:206-209`, rc=1.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: real tree, rc=0, `run selftest: PASS` on the same three HEADs (86 to 93 s). Red on revert of `run.sh:496`, rc=1.
- `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: real tree, rc=0, `ok: 19 role levels, 9 agents checked` on the same three HEADs. It can go red: in a throwaway worktree at 2cd5342 the baseline was rc=0, and with the `S` tier effort in that copy's `solo_run.py:54` changed it was rc=1 with `FAIL solo_run.py TIERS does not list S, M, and L` and `FAIL solo_run.py TIERS differ from fanout.py SOLO_TIERS`.
- Each of the four regression tests goes red with its fix reverted (observed, not read): pass. Evidence: all reverts were made in `$SDLC_TMP_WORKTREES/base` (detached at c461bc6), one at a time, and each file was restored by `cp` from the real tree (`git status --short` there: 0 lines after each).
  - **T-0300 board.** Deleted the early `closed` return in `task_rows` (`board.py:206-209`). Selftest rc=1: `solo lane done ticket reads ['closed'], got ['built · builder L2, awaiting verify']`. The `ready` control did not fail. Restored copy: PASS.
    - CLI leg on a temp `.sdlc` fixture: fixed `board.py --root` prints `| T-0001 | soloed | done | task | 🟢 closed | 100 |`; the pre-fix script (worktree at 3482207) prints `| 1. do it | 🟡 built · builder L2, awaiting verify`.
    - Controls (status `ready`, last lane `full`, a `.running` marker) render the same on both. `board.py --summary` prints `soloed closed`, rc=0.
  - **T-0299 fanout.** Changed `norm_tid(x.strip())` to `x.strip()` at `fanout.py:458`. Selftest rc=1 with two lines:
    - `bare 0001, 1 and T-0001 resolve the same ticket in a dry run: [(0, ''), (2, "fanout: alpha: '0001' is not a ticket id like T-0001\n"), ...]`
    - `alpha=0001 beta=T-0001 refuses as twice listed, got 2 "fanout: alpha: '0001' is not a ticket id like T-0001\n"`
    - Note: the label case `the same id bare and prefixed` stayed green on revert, because an unknown bare id also exits 2. The two lines above are the ones that bite.
  - **T-0298 run.sh.** Replaced the parse at `run.sh:496` with `reset=""`. `run-selftest.sh` rc=1: `run selftest: FAIL: session limit reset: marker has no reset 1:40pm`. Removing only the hint append line gave `FAIL: session limit reset: hint has no resets 1:40pm`, so both assertions bite.
  - **T-0298 solo_run.py.** Changed `solo_run.py:150` to `rm = None`. Selftest rc=1: `solo_run selftest FAIL: limit stop with a reset: marker reset is 1:40pm and the hint says so`. Removing only the hint suffix at `:158` fails the same line.
    - CLI leg: fixed script writes `reset` `1:40pm` and the hint ends `(resets 1:40pm)`; the 3482207 script writes no `reset` and no suffix; a no-reset message writes no `reset`.
  - **T-0293 group kill.** Two reverts, both rc=1:
    - Pre-fix `subprocess.run(..., timeout=)` restored in `_run_locked` and the handler install at `solo_run.py:302` removed: `group kill after timeout: wrapper exits nonzero and the child is gone`, `group kill after sigterm: wrapper exits nonzero and the child is gone`, `group kill after sigterm: lock removed`.
    - Only `start_new_session=True` flipped to `False` at `:326`: the two `child is gone` lines fail. The biting variable is the child's own process group.
  - **T-0293 lock.** Changed `solo_run.py:293` to `lock = None`. Selftest rc=1 after 82 s, as a `subprocess.TimeoutExpired` traceback at the second-run call (`solo_run.py:688`), not an expect line: the second run was not refused, started a session, and hung to the 60 s timeout. It left a stub and a `sleep 300` (pids 55952, 55953), which I killed. Disclosure: I found them with `pgrep` on my own scratch path `/tmp/vfb-b-scratch/t-solo-lock`.
  - **T-0293 real child (the Do item).** Stub `claude` that spawns `sleep 300`, a fresh `git init` repo in `/tmp`, signals sent to the wrapper pid. Real tree script:
    - `timeout: wrapper rc=124 (2s) sleep=gone stub=gone lock=absent`
    - SIGTERM rc=143, SIGINT rc=130, SIGHUP rc=129: each `sleep=gone stub=gone lock=absent`, stderr `solo_run.py: stopped by signal N; process group ended`
    - Child that ignores TERM, `--timeout 1`: rc=124 at 3 s, sleep and stub gone (the KILL path)
    - Second run while the first is live: `B: exited rc=2`, one stderr line `solo_run.py: another solo run is live (pid 71924)`, stub sessions 1 to 1, `runs.jsonl` 5 to 5, lock still holds the first pid. After SIGTERM to the first: rc=143, lock absent, stub and sleep gone.
    - Stale lock with a dead pid: rc=0, one record added, lock absent.
  - **Before picture, 3482207 script, same harness.** `timeout: sleep=ALIVE`; SIGTERM and SIGHUP: `sleep=ALIVE stub=ALIVE`; second run `STILL RUNNING after 8s (not refused)`, sessions 1 to 2. SIGINT is not a clean comparison there: a background launch ignores INT. My first harness pass signalled a bash subshell instead of the wrapper (visible as a pid mismatch); I discarded it and reran.
  - **Note, not a fail.** Two SIGTERMs 0.5 s apart with a child that ignores TERM: `wrapper rc=1 sleep=ALIVE stub=ALIVE lock=absent`, stderr ends `__main__.Stopped: 15`. `on_signal` (`solo_run.py:298-299`) raises again while `kill_group` (`:222`) runs inside `except Stopped` (`:335`), so KILL is never sent. Steelman: the handoff and ticket name one signal, and the single-signal case passed even with a TERM-ignoring child. Follow-up candidate.
  - **Ticket doc lines** in `docs/maintenance/sdlc-internals.md`: 11 (run.sh `reset`), 31 (`## Feed`, the T-0300 rule), 67 (bare ids), 106 (process group, lock, `solo.limit` reset). Each still greps 1 at 2cd5342.
  - **Dependents.**
    - `.limit` marker: `git grep` for `resume with`, `session limit`, `.limit`, `solo.limit` outside `run.sh`, `solo_run.py`, and `run-selftest.sh` returned nothing in `plugins/` and `scripts/`, so the added `reset` key has no reader.
    - `plan_check.py selftest`: `PASS (46 checks)`. `plan_check.py:253` still requires the `T-` prefix, stricter than fanout; nothing breaks.
    - `fanout.py` has no `killpg` or signal sends (grep), so the child's new session escapes no group kill there.
  - No `builder-*.md` exists in the artifacts dir. The claims checked were the four tickets' `## Closed` lines and acceptance checkboxes, each against the runs above.

## Out of scope changes
- At start, `git diff --name-only "$SDLC_BASE_SHA"` was empty: `SDLC_BASE_SHA` equals the start HEAD c461bc6. The handoff names 0e85edb; `git diff --stat 0e85edb c461bc6` shows only the two verify handoffs. No gate went red, so the inherited-red rule was not used.
- Another session committed 832bb36, b1b3c74, and 2cd5342 (all T-0294) during this run. They touch `scripts/steps.py`, `agents/planner.md`, `skills/handoff-format/SKILL.md`, `skills/level-rubric/SKILL.md`, five codex planner and plan-reviewer TOMLs, and `sdlc-internals.md` line 57. Judged harmless here by three checks:
  - `git diff --stat c461bc6 2cd5342` over `solo_run.py`, `run.sh`, `run-selftest.sh`, `fanout.py`, `board.py`, `check.py` is empty.
  - The internals diff is `@@ -57 +57 @@` only.
  - All five commands are green on 2cd5342 (HEAD the same before and after the run, 09:28:50 to 09:31:54, no tracked modifications).
- Between 3482207 and c461bc6 the branch also carries T-0294 to T-0297, T-0303, and T-0304 (`steps.py`, `gate_lock.py`, `check.py`, `check.sh`, agents, skills, codex TOMLs, `docs/lean-sdlc/design.md`). Other tickets, not verified here.
- Untracked: `.sdlc/verify-fix-batch-0.20.11-a/`, `-a2/`, `-a3/`, and `-b/` run artifacts.
- Mine: nothing in the tree. Both throwaway worktrees (`base`, `prefix`) are removed (`git worktree list | grep -c verifier-98921` is 0). Scratch files are in `/tmp/vfb-b-scratch`.

## For the next attempt
None
