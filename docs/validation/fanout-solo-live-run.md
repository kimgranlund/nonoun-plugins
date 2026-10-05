# Fanout solo-first live run

Recorded: 2026-10-05. Live run for ticket T-0221: `fanout.py run` with four tickets in four lanes, started on the `fanout-solo` branch (commits 09134ad and adb9789 on top of main 9bc9fb8). One run, one machine.

## What ran

A throwaway Git project (a tiny `kit` package, four disjoint tickets): three size S (T-0001 clamp, T-0002 chunk, T-0003 title_case) and one size M (T-0004 parse_duration, which also edits README.md). Command: `fanout.py run a=T-0001 b=T-0002 c=T-0003 d=T-0004 --integration fanout/live --gate "python3 -m unittest discover -s tests -t ." --stagger 3`. No `--driver` and no `--lane`, so the default solo-first driver ran. Wall time 5 minutes 43 seconds (16:31:17 to 16:37:00, [`start.txt`](fanout-solo-live-run/start.txt) and [`end.txt`](fanout-solo-live-run/end.txt)), exit 0 (`rc=0` at the end of [`run-output.txt`](fanout-solo-live-run/run-output.txt)).

## Result

- Lane per ticket (from `steps.py lane`, recorded in each ticket's `skips.md`): T-0001, T-0002 and T-0003 solo tier S; T-0004 solo tier M. The report lists them ([`report.md`](fanout-solo-live-run/report.md)).
- All four tickets merged and closed (`close T-000N` commits on `fanout/live`, [`integration-log.txt`](fanout-solo-live-run/integration-log.txt)), each behind the gate. The four lanes started 3 seconds apart, as `--stagger 3` says: the driver logs were created at 16:31:17, 16:31:20, 16:31:23 and 16:31:26 ([`lane-start-times.txt`](fanout-solo-live-run/lane-start-times.txt), file creation times; `fanout-log.txt` itself carries no timestamps).
- Hidden check on the integration worktree: `hidden_check: 24/24 passed` ([`hidden-check.txt`](fanout-solo-live-run/hidden-check.txt), output of [`hidden.py`](fanout-solo-live-run/hidden.py), which sat outside every lane and was never named in a prompt).
- The size M ticket's independent batched verifier ran inside the solo session through `run.sh verifier L3`, verdict pass ([`verifier-L3-T-0004.md`](fanout-solo-live-run/verifier-L3-T-0004.md)). Fanout did not have to run a verifier itself, and the three S tickets had none, as `agents/solo.md` says.

## Models, from the session transcripts

The transcripts stay in `~/.claude/projects` and are too large to copy; [`transcript-summary.json`](fanout-solo-live-run/transcript-summary.json) holds the `agentSetting`, model counts and output tokens read from them.

- Solo, all four lanes: `agentSetting` `sdlc-lite:solo`, every assistant event `claude-sonnet-5-5`. Effort is a launch flag (`--effort low` for S, `xhigh` for M); the stream does not record it.
- Verifier: `agentSetting` `sdlc-lite:verifier`, model `claude-fable-5-1`; the run record and result header say `fable xhigh`. A different family from the Sonnet solo.
- Cost: only the verifier has a record, $3.13 (`cost_usd` 3.1298 in [`lane-d-runs.jsonl`](fanout-solo-live-run/lane-d-runs.jsonl)). The solo sessions printed no cost (`claude -p` text output), so their cost is not measured here; their transcripts show 743 to 6,044 output tokens each.

## Limits

- One run of four tiny tickets on one machine: it shows the path works, not the real lane limit. No more than four lanes were tried. The recommended count for this plan is 4, then raise it only after watching limit use and merge conflicts.
- No Codex lane was run (`codex_exec.py solo` is built and selftested, not exercised live). No size L ticket, and the full-chain branch was exercised only by the selftest.
- The fixtures were disjoint by construction, so merge-time overlap handling was not tested live (the selftest covers it).
- The solo sessions' own cost was not captured.
- The plugin under test was the `fanout-solo` worktree (0.20.5 manifests) at commit 8e6d835, before T-0218 to T-0220 were merged in.

## Addendum, 2026-10-05: rerun after the skips-guard fix (T-0222)

The run above predates the T-0219 skips guard. On main with that guard, `steps.py lane` wrote `lane: solo` to a task's `skips.md`, fanout closed the solo ticket with `tickets.py close --reason`, and the guard demanded `## Skipped` entries for the planner and filer that nothing wrote, so the close was refused (`merged, close refused`). The 0.20.6 release fact-check reproduced it, and the first run's selftest passed `--driver` everywhere, so nothing caught it.

Fix (T-0222): when a solo lane starts, `fanout.py` writes `- skip: planner; step: all; reason: solo lane: size <tier> runs end to end in one session; decided: lane` and the same line for the filer under `## Skipped`, before the close. The guard is unchanged. Selftest case 16 runs two solo tickets through a lane with the real `steps.py lane`, the real driver choice and the real `tickets.py close`, with only a `claude` shim on PATH for the model session; its negative control turns the write off and the close is refused with `no ## Skipped entry`.

Rerun, same fixture and command (four lanes, three size S and one size M, `--stagger 3`, a gate of `python3 -m unittest discover`), with the fixed `fanout.py` and the guard live: 18:01:11 to 18:05:38 (4 minutes 27 seconds), exit 0, all four tickets merged and closed (four `close T-000N` commits), `hidden_check: 24/24 passed`. Lane starts 3 seconds apart (18:01:12, :15, :18, :21). `skips.md` of a closed ticket shows the lane line and both Skipped entries ([`skips-T-0001.md`](fanout-solo-live-run/rerun-t0222/skips-T-0001.md)). Solo sessions on `claude-sonnet-5-5` (753 to 6,153 output tokens), the size M verifier on `claude-fable-5-1` at $2.20 (the verifier's `cost_usd`; solo cost not captured, as before). Evidence, all committed: [`report.md`](fanout-solo-live-run/rerun-t0222/report.md), [`run-output.txt`](fanout-solo-live-run/rerun-t0222/run-output.txt), [`hidden-check.txt`](fanout-solo-live-run/rerun-t0222/hidden-check.txt), [`integration-log.txt`](fanout-solo-live-run/rerun-t0222/integration-log.txt), [`lane-start-times.txt`](fanout-solo-live-run/rerun-t0222/lane-start-times.txt), [`lane-d-runs.jsonl`](fanout-solo-live-run/rerun-t0222/lane-d-runs.jsonl), [`transcript-summary.json`](fanout-solo-live-run/rerun-t0222/transcript-summary.json), [`start.txt`](fanout-solo-live-run/rerun-t0222/start.txt), [`end.txt`](fanout-solo-live-run/rerun-t0222/end.txt).

Limits as before: one run, one machine, four disjoint single-ticket lanes (the multi-ticket case is covered by selftest case 16, not live), no Codex lane. The overlap refusal reads only `step-<n>/` handoffs, so it cannot fire for solo tickets; merge-time overlap handling still serializes them.
