<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- Criterion 1 (`dispatch.py selftest` exits 0; row and family-fixture parity with `SDLC_DRY_RUN=1 run.sh` on model, effort, result name): pass. Evidence:
  - `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` in the built tree: exit 0, 151 `ok:` lines, 0 `FAIL`, last line `dispatch selftest: PASS`.
  - Rows: 19 `ok: parity row:` lines. An independent read of `adapters/claude/levels.json` gives 19 pipeline rows plus solo S, M, L.
  - Family fixtures: 9 `parity verifier after builder L5|L1|L3` lines (newest build in a step dir by `runs.jsonl` order), 16 `parity task dir, ...` lines (verifier at a task dir), and `parity opus planner: plan-reviewer L1 -> fable high plan-reviewer-L1.md`.
  - Red at base: the same command at `$SDLC_BASE_SHA` in the throwaway worktree exits 2 (`can't open file .../dispatch.py`).
  - Bites, using mutated copies in the throwaway worktree, each exit 1:
    - M1, verifier family returns sonnet: 11 FAIL.
    - M4, plan-reviewer family returns opus: 4 FAIL.
    - M5, result name never bumps: 8 FAIL.
    - M13, worktree `run.sh` `builder:L1` set to opus with `dispatch.py` untouched: `FAIL: parity row: builder L1`. This shows the comparison reaches the real `run.sh`.
    - M14, worktree `levels.json` planner L2 effort set to high: `FAIL: parity row: planner L2`.
    - Unmutated control copy: exit 0.
  - CLI leg: verifier L1 at a task dir after a sonnet build in `step-3` gave `opus medium verifier-L1` from `prepare --dry-run`, and `--model opus --effort medium` from the `run.sh` dry run.

- Criterion 2 (a refusal per gate with `run.sh`'s exit code, a negative control per gate, a refusal writes no file): pass. Evidence:
  - Selftest lines `... prepare exits N like run.sh (got N, run.sh N)` for goal precheck planner and plan-reviewer (2), spec gate (2), lane gate planner, builder, plan-reviewer and on a step (5), budget gate (4). Each has a `a refusal wrote nothing` line and a `negative control, without the <gate> gate the bad input goes through` line.
  - Preflight in the selftest: missing handoff, unknown row, non-git dir and no-commit repo each `exits 2 like run.sh`, plus `preflight: negative control, without the gate a repo with no commit goes through`.
  - Lane override in the selftest: `SDLC_LANE_OVERRIDE proceeds and is carried`.
  - Bites, each exit 1:
    - M2, lane exit 5 to 2: 5 FAIL, `got 2, run.sh 5`.
    - M3, budget exit 4 to 2: 1 FAIL.
    - M11, goal exit 2 to 3: 2 FAIL.
    - M12, spec gate exit 2 to 3: 2 FAIL.
    - M6, lane refusal writes a file first: `FAIL: lane gate planner: a refusal wrote nothing`.
    - M15, budget gate ignores `skip`: `FAIL: budget gate: negative control ...`.
  - CLI leg in the throwaway worktree, with a file-hash snapshot of `.sdlc` before and after each refusal, all unchanged and stdout 0 bytes:

    | Case | prepare | run.sh dry run |
    |---|---|---|
    | goal precheck, planner | 2 | 2 |
    | goal precheck, plan-reviewer | 2 | 2 |
    | spec gate | 2 | 2 |
    | missing handoff | 2 | 2 |
    | unknown row `builder L9` | 2 | 2 |
    | outside a git work tree | 2 | 2 |
    | budget, 90 percent of `budget_usd: 10` | 4 | 4 |
    | lane, size S fixture, builder and planner | 5 | 5 |
    | lane, the real T-0277 handoff (size M), builder | 5 | 5 |

  - Overrides by CLI: `SDLC_LANE_OVERRIDE` gives 0 with `lane_override` carried (`run.sh` 0); `SDLC_SPECGATE=off` gives 0 with `specgate: off` (`run.sh` 0); a budget ack gives 0 (`run.sh` 0).
  - Coverage note: the selftest's `refused()` helper checks "wrote nothing" for goal, spec, lane and budget only. For preflight that property rests on my CLI hash comparison.
  - My first budget fixture had broken front matter (my error): both tools exited 0. The corrected fixture gave the row above.

- Criterion 3 (a real `prepare` writes both records with the named keys; a builder or verifier gets `base-sha`): pass. Evidence, from the CLI in the throwaway worktree:
  - `prepare verifier L1 .sdlc/0277-dispatch-prepare/handoff.md` exits 0 and the dir gains `verifier-L1.attempt.json`, `verifier-L1.dispatch.json`, `base-sha`, `.run.lock`.
  - Attempt record: `status: running`, `transport: subagent`, `parent_pid: 65606`, the calling shell passed through `SDLC_DISPATCH_PARENT_PID`.
  - Dispatch record: `subagent_type: sdlc-lite:verifier-L1`, `model: sonnet`, `effort: medium`, `name: verifier-L1-0277-dispatch-prepare`, `result`, `tmp_prefix`, `base_sha`, `prompt` all non-null. stdout is byte-identical to the file (`cmp`).
  - Verifier base sha: `base-sha` equals `git rev-parse HEAD` (21d3e25), and the prompt holds `Base sha: 21d3e25...`.
  - Builder: `prepare builder L3 .sdlc/vfix/step-3/handoff.md` exits 0, name `builder-L3-vfix-s3`, `base_sha` equals HEAD in the dispatch, the `base-sha` file and the prompt.
  - With no forced pid the attempt holds `parent_pid: 33803`, `parent_pid_source: claude`; `ps` names that pid `claude`, the session process and not the tool shell.
  - A planner dry run has `base_sha: None` and no `Base sha` line.
  - Selftest lines: `attempt record: running, subagent transport, parent pid`, eight `dispatch JSON has <key>` lines, `a builder gets its base sha, in the dispatch, base-sha, and the brief`.
  - Bites: M7, transport set to `exec`, fails the attempt-record line. M10, no `base-sha` write, exits 1 through an uncaught `FileNotFoundError` instead of a labeled FAIL.
  - Non-blocking: the label at `dispatch.py:749`, `a verifier or planner dispatch has no base sha`, is wrong for the verifier. The case tests a planner only. Verifier base sha is covered by my CLI run, not by the selftest.

- Criterion 4 (second `prepare` with a live parent exits 2; a dead-parent attempt is marked `interrupted` first and the new attempt takes the next name): pass. Evidence, all in one shell so the parent pid stayed alive:
  - Second `prepare verifier L1`: exit 2, stdout 0 bytes, stderr `an attempt is still running in ...: verifier-L1.attempt.json (pid 65606)`, still one `*.attempt.json`. `scout L1` on the same dir also exits 2.
  - After rewriting `parent_pid` to a pid that `kill -0` reports dead: exit 0, stderr `recovered stale attempt(s) before this dispatch: verifier-L1.attempt.json`. The old record is `interrupted` with `finished_at` and the same `attempt_id`. The new attempt is `verifier-L1-2`, result `verifier-L1-2.md`, Agent name `verifier-L1-0277-dispatch-prepare-2`.
  - A later Bash call, a new shell, still got exit 2 against the builder attempt whose parent is the live `claude` pid.
  - Selftest lines: `a second prepare with a running attempt and a live parent refuses`, `a dead-parent attempt is recovered first`, `the new attempt gets the next result name and Agent name`, `the interrupted attempt was not overwritten`.
  - Bites: M9, live attempt never refuses, 3 FAIL. M8, dead parent never recovered, fails `a dead-parent attempt is recovered first` and then exits 1 on an uncaught `TypeError`.

- Criterion 5 (`run-selftest.sh` exits 0, `run.sh` unchanged, no em dash in changed files): pass. Evidence:
  - `bash plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0, `run selftest: PASS`. It can go red: with the worktree `run.sh` timeout floor changed to 1000 it exits 1, `run selftest: FAIL: timeouts 'unset': claude saw '1000 1000'`. An earlier mutation (`k=2` to `k=3`) stayed green because real runs take the name from `run_lifecycle.py`, so that variable does not bite.
  - `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh` exits 0. `git hash-object` of the file and the base blob are both `c33934b1`. The same check exits 1 on the mutated worktree copy.
  - Em dash: `LC_ALL=C grep -c` for the UTF-8 bytes of U+2014 gives 0 in each of the 7 changed or untracked files, and a Python count of the code point also gives 0 in each. The grep returns 1 on a fixture line holding one.

- Dependents of the changed `check.sh` (no criterion, traced because the diff touches the regression suite): green. Evidence:
  - `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 in 9 min 5 s; output line 190 is `dispatch selftest: PASS`, so the new line ran. `git status` was identical afterwards.
  - `check.py` exit 0 (`19 role levels, 9 agents, 22 generated definitions checked`).
  - `claude_roles.py generate --check`, `codex_roles.py generate --check` and `scripts/check-packaging.py` all exit 0.
  - `git diff --check` exits 0.

- Considered and dropped (steelman):
  - Draft fail: `readiness.py` is named in the ticket Context and `dispatch.py` does not use it. Rebuttal: `readiness.py:21` adds an error for `backend == 'claude' and transport != 'exec'`, so calling it unchanged would refuse every sub-agent dispatch, and no criterion names it. Dropped.
  - Draft fail: the docs say "A refusal writes nothing", but with one dead-parent and one live-parent running attempt in the same dir, `prepare` exits 2 and rewrites the dead record to `interrupted` (observed). Rebuttal: no new file is written, the record becomes true, and `prepare` alone cannot produce that state because it recovers or refuses before adding a second running attempt. Dropped; the sentence is slightly too broad.
  - Draft fail: `next_stem` counts any `<stem>.*` file while the `run.sh` dry run counts only `.md` and `.request.json`. Rebuttal: `run_lifecycle.py:83` uses the same `glob(name + '.*')` on the real path, and the parity fixtures use `.md`. Dropped.
  - Not exercised: a running-attempt refusal in a dir with no `.run.lock` would create that empty git-ignored file before refusing. The lock is not one of criterion 2's listed gates.
  - The selftest conjunct `source in ('claude', 'ancestor', 'ppid')` at `dispatch.py:751` cannot fail, since those are the only return values; `pid_alive(pid)` is the part that bites.

## Out of scope changes
None. Each changed file was checked:
- No `builder-*.md` exists in the artifacts dir, so there was no builder claim to check; everything above comes from the tree.
- `.sdlc/0277-dispatch-prepare/handoff.md`: `git diff` shows only the appended `## Acceptance criteria` section, which is the contract verified here.
- `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/AGENTS.md`, `plugins/sdlc-lite/scripts/check.sh`: `git grep dispatch.py` shows these are the only references outside the design doc. They document and wire in the new script, which the repo rule on repairing records in the same change calls for.
- `.sdlc/0277-dispatch-prepare/base-sha` and `verifier-L3.attempt.json`: written by `run.sh` and `run_lifecycle.py` for this verifier run. The record shows role verifier, level L3, `transport: exec`, `process_pid: 33740`, which matches the `$SDLC_TMP_WORKTREES` suffix.
- Codex paths: `git status` lists no Codex file.
- The throwaway worktree is removed: `git worktree list` has no `verifier-33740` entry and `git status` matches the start.

## For the next attempt
None
