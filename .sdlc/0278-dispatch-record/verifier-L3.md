<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
No `builder-*.md` or `runs.jsonl` existed in the artifacts dir, so the working tree diff against `c727e8d` (`$SDLC_BASE_SHA`, equal to HEAD) was the claim under review. Red runs used a throwaway worktree at the base sha, then the same worktree with the built diff applied and one mutation per run (M-numbers below). Both worktrees are removed.

- (guard) `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` prints `dispatch selftest: PASS` and no `FAIL:` line: pass. Evidence: built tree exit 0, 215 lines, last line `dispatch selftest: PASS`, `grep -c '^FAIL:'` printed 0, stderr empty. The prose half is at `dispatch.py:1018` (`via_runsh` runs the real `run.sh` with a stub `claude`), `:1059` (loop over builder, verifier, planner, plan-reviewer), `:1067` (`set(b_line) == set(a_line) | {'agent_id', 'cost_reason'}`). Source leg: `run.sh:577-584` writes 19 keys and `record` writes those plus `agent_id` and `cost_reason`. It bites: every mutation below ended `dispatch selftest: FAIL` with exit 1, and mutating `run.sh`'s header turned `record parity builder: valid result exits 0 like run.sh` red, so the real `run.sh` is in the loop.
- `... | grep -c '^ok: \(record parity\|steps.py next reads\|order.py reads\)'` at least 20: pass. Evidence: built 28, base 0. Red under mutation:
  - M1 (extra key in the line): 4 `key set` FAILs.
  - M2 (`transport='claude'`): 4 `transport subagent` FAILs.
  - M3 (no header written): 26 FAILs, including both `steps.py next reads` cases and all four header cases.
  - The count alone tolerates up to 8 failed cases (M1 leaves 24); the first criterion's no-`FAIL:` rule covers that gap.
  - The `order.py reads` predicate bites only on the result file's presence and name, not on line content, in a one-result dir.
- `... | grep -c '^ok: \(invalid result\|negative control\)'` at least 9: pass. Evidence: built 13, which is 12 record cases plus the pre-existing line `ok: negative control: without the lock gate a second running attempt starts`; base 1, that line only. Red under mutation:
  - M4 (validator result ignored): 9 FAILs, count drops to 4.
  - M4b (message shape changed): 3 `prints dispatch.py: <role> result <reason>; see <file>` FAILs.
  - M4c (return 1 instead of 3): 3 `exits 3` FAILs.
  - Independent CLI leg in a fixture repo, for missing key section, disallowed first value, and section order: each exited 3 with empty stdout and a stderr line such as `dispatch.py: builder result lacks ## Status (done|blocked|inherited red: <tests>); see <fx>/.sdlc/b1/builder-L1.md`; the file was kept with its header, `runs.jsonl` had 1 line, and the attempt was `failed` with `exit_code` 3.
- `... | grep -c '^ok: \(a failed sub-agent\|a 429\|no result file\|a later success\|CLI record\)'` at least 7: pass. Evidence: built 8, base 0. Red under mutation:
  - M5 (failed path closes completed with 0): 4 FAILs.
  - M5b (limit regex never matches): 2 FAILs.
  - M5c (marker not removed on success): 1 FAIL.
  - CLI leg, stdin `API Error: 429 Too Many Requests` with no result file: exit 1, attempt `failed` with the text, no `runs.jsonl`, `verifier-L1.log` written, and `verifier-L1.limit` holding `"resume":"python3 <abs>/dispatch.py prepare verifier L1 <handoff>"`.
  - CLI leg, plain error text: exit 1 and no `.limit` file.
  - CLI leg, a valid result on stdin with no file: exit 0 and the file written with its header.
- `... | grep -c '^ok: \(a changed handoff\|strays are reported\|the dispatch tmp prefix\|the outside worktrees\)'` prints 4: pass. Evidence: built 4, base 0. Red under mutation:
  - M6 (stale never detected): 1 FAIL.
  - M6b (stale returns 4): 2 FAILs.
  - M6c (strays never found): 1 FAIL.
  - M6d (prefix not removed): 1 FAIL.
  - M6e (cleanup removes every new worktree): 2 FAILs, including `the outside worktrees are only reported, never removed`.
  - CLI leg with a changed handoff, a stray detached worktree, a stray branch, and a worktree under the tmp prefix: exit 0; the three stderr lines appeared (`stale input: ... changed while builder ran`, `stray worktree appeared during this run: .../fx-stray`, `stray branch appeared during this run: stray-br`); the line had `stale_input: True` and both strays; the prefix was gone and the stray worktree was still registered.
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py` exits 0: pass. Evidence: exit 0 on the built tree. Negative control (the `run.sh` header line broken in the throwaway copy): exit 1, `FAILED (failures=6)`.
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` exits 0: pass. Evidence: exit 0 on the built tree. Same negative control: exit 1, `FAILED (failures=2)`.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`: pass. Evidence: exit 0, one `run selftest: PASS` line. Same negative control: exit 1, no PASS line, `run selftest: FAIL: run 1: run.sh exited non-zero`.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: exit 0, 928 output lines, no `FAIL` line, `dispatch selftest: PASS` at line 253, ending `ok: shellcheck` and `ok: plugin validate`. Same negative control: exit 1. `check.sh:15` runs the dispatch selftest with `|| fail=1` and the script ends `exit $fail`.
- `git diff HEAD --name-only -- plugins/sdlc-lite/scripts/results.py plugins/sdlc-lite/scripts/run.sh` prints nothing: pass. Evidence: empty output with both paths present (`test -f`). Bite: the same command on `dispatch.py` printed its path.
- `git diff HEAD -- docs plugins .sdlc/0278-dispatch-record | grep '^+' | grep -c "$(printf '\xe2\x80\x94')"` prints 0, and `git diff HEAD --check` exits 0: pass. Evidence: printed 0 over 462 added lines; a fixture line with an em dash through the same pipe printed 1; `git diff HEAD --check` exit 0. The two untracked files also have 0 em dashes.

Contract dependents traced, each cleared by a read or a run:
- `cost_usd: null` in `runs.jsonl`: counted as unmetered at `budget.py:93-97`, skipped at `footprint.py:87-89`, `or 0` at `board.py:101`, `// 0` at `bench-summary.sh:22`. The budget, board, steps, order, and traces selftests all print PASS in the `check.sh` output.
- `results.HEADER`, used by `record`: present at HEAD, `results.py:62`.
- `<role>-<level>.running`: `prepare` never writes it (`git grep '\.running'` shows `dispatch.py` only unlinks, at `:275` and `:536`), so the unlink in `close()` is a no-op that matches `run.sh`.
- `worktrees_before` and `branches_before` in the attempt record: read only at `dispatch.py:485-487`. `run_lifecycle.py` reads attempt records with `.get` and asserts no key set.
- `python3 scripts/check-packaging.py`: exit 0, `PASS: catalog parity, identity, skill routes, hook isolation and context links`.

## Out of scope changes
None. Each changed file outside `dispatch.py` was checked:
- `.sdlc/0278-dispatch-record/handoff.md`: the diff adds only the `## Acceptance criteria` block. `plugins/sdlc-lite/agents/solo.md:43` has the solo lane write it before the batched verifier. Its sha256 (`5f331aef...`) equals the one in my attempt record, so it did not change during this run.
- `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/AGENTS.md`, `plugins/sdlc-lite/scripts/check.sh`: the diff is prose and one comment line describing `record`; no executable line changed. The docs claims I tested (stdin rule, exit codes 0, 1, 2, 3, the tmp-prefix guard, the `usage` flags) matched the CLI runs above.
- `.sdlc/0278-dispatch-record/base-sha`, `verifier-L3.attempt.json` (untracked): this run's own records; the attempt's `process_pid` 87856 and handoff path match this run.

Steelman: draft finding "`check.sh`, `AGENTS.md`, and `sdlc-internals.md` are outside the Do". Rebuttal: they are the records for the subcommand the Do adds, they change no behavior, and the repo rule is that a change repairs its records in the same change. Dropped.

## For the next attempt
None
