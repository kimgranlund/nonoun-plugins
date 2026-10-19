<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 dispatch.py selftest exits 0 with the T-0537 cases: pass. Evidence: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` printed `dispatch selftest: PASS`, rc=0. Output lines 360-366 are the T-0537 cases: `resume --limit marks a running attempt limit-stopped, clears its running marker, and writes the .limit marker with SendMessage by name`; `status shows limit-stopped and resume prints the ladder for it`; `a limit-stopped attempt resumed by SendMessage records as usual ...`; `negative control: resume --limit refuses a completed attempt`; `negative control: resume --limit refuses a running attempt that has a result, writes no marker, and keeps it running`; `negative control: prepare is silent when the row matches the previous attempt`; `prepare prints one row-changed line when the model or effort differs from the previous attempt`. The cases can go red: in a throwaway worktree at HEAD I disabled the has-a-result refusal and the row-changed condition in dispatch.py (`if False:`). The selftest then exited rc=1 with `FAIL: negative control: resume --limit refuses a running attempt that has a result, writes no marker, and keeps it running` and `FAIL: prepare prints one row-changed line when the model or effort differs from the previous attempt`. The throwaway worktree is removed.
- #2 lifecycle-selftest.py exits 0: pass. Evidence: `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` printed `OK`, rc=0.
- #3 check.sh exits 0 (generated Codex conductor TOML fresh): pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` ran to its last stage: `supervisor selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`. The command exited 0. The diff updates `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml` together with `agents/conductor.md`, and check.sh's generated-agent parity stage did not fail.
- #4 conductor.md tells the conductor to run `dispatch.py resume --limit <name>` and resume with a SendMessage by name: pass. Evidence: `plugins/sdlc-lite/agents/conductor.md` (line 42 in the diff hunk) now reads "run `dispatch.py resume --limit <name>`, which marks it `limit-stopped` and writes `<role>-<level>.limit`; once the limit resets, a `SendMessage` to the agent by name resumes it with its context", and describes the `prepare` `row changed:` line.

## Out of scope changes
None in plugins/. Housekeeping under `.sdlc/0537-dispatch-limit-stop-and-row-change/` (base-sha, handoff, runs.jsonl, skips.md, solo and verifier attempt/dispatch records) is the run's own bookkeeping. The HEAD commit is the driver's `wip(T-0537): driver failed rc=1` snapshot. The solo result `solo-L2-dc546fac.md` holds only the "weekly limit" message, so the build landed in the tree without a solo report. The criteria were judged on the tree, not on that report.

## For the next attempt
None

## Notes
- `dispatch.py` `limit_stop` writes the `.limit` marker with `time.strftime` but the attempt's `limit_stopped_at` with `run_lifecycle.now()`. Two timestamp formats, harmless.
- `dispatch.py selftest` and `lifecycle-selftest.py` ran under load average about 40; both completed and passed.
