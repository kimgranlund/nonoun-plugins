# Solo close live run

Recorded: 2026-10-05. Live run for ticket T-0224: a conductor-started solo ticket is closed with `tickets.py close --reason` while the T-0219 skips guard is live. One run, one machine. Plugin: the `solo-skips` worktree (`plugins/sdlc-lite`, 0.20.6 plus the T-0224 change).

## Why

`steps.py lane` wrote only `lane: solo` to `skips.md`. The T-0219 guard needs a `## Skipped` entry for the planner and the filer, which nothing wrote for a solo ticket started by a conductor (the T-0217 Bash start path), so the close was refused unless the conductor wrote the two lines itself. Fanout had its own private writer (T-0222); the T-0216 conductor proof predated the guard. T-0224 moves the write into the lane script: `steps.write_solo_skips`, called by `record_lane` when the lane is `solo` (idempotent, only when the last lane record is solo), and fanout calls the same function.

## Method

A throwaway Git project (`kit` package, one size M ticket `duration`: add `parse_duration`, 8 or more tests, a README usage line; fixture and hidden check in [`hidden.py`](solo-close-live-run/hidden.py), kept outside the project). A fresh headless conductor session, with no lane, no solo command, no verifier and no check in the prompt:

`env-wrapper.sh env SDLC_HEADLESS=1 BASH_DEFAULT_TIMEOUT_MS=3600000 BASH_MAX_TIMEOUT_MS=3600000 claude -p --plugin-dir <plugin> --agent sdlc-lite:conductor --model sonnet --effort high --dangerously-skip-permissions --output-format stream-json --verbose "Deliver the size-M ticket at .sdlc/duration/handoff.md, then close it."`

(`env-wrapper.sh` strips every inherited Claude Code and SDLC variable, as in the T-0216 run.) 19:08:15 to 19:13:49 ([`start.txt`](solo-close-live-run/start.txt), [`end.txt`](solo-close-live-run/end.txt)), 5 minutes 34 seconds, exit 0 ([`rc.txt`](solo-close-live-run/rc.txt)).

## Result

- The conductor ran `steps.py lane .sdlc/duration` (call 3 in [`session-trace.txt`](solo-close-live-run/session-trace.txt)), which printed `solo` (size M decides before planning), then started the solo agent from Bash (`claude -p ... --agent sdlc-lite:solo`, call 6). No Agent-tool spawn: the stream holds only Bash calls and `permission_denials` is 0.
- The solo delivered the ticket (12 tests) and ran one independent batched verifier (`run.sh verifier L3`, `fable xhigh`, Verdict pass, [`verifier-L3.md`](solo-close-live-run/verifier-L3.md)).
- The conductor then ran `tickets.py close duration --reason "..."` (call 8): `T-0004 done (closed by reason: ...); no follow-ups filed`, exit 0, with the guard live. The ticket handoff reads `status: done` and a `## Closed` section.
- [`skips.md`](solo-close-live-run/skips.md) holds the lane line (written by `steps.py lane`) and both entries under `## Skipped`: `- skip: planner; step: all; reason: solo lane: runs end to end in one session; decided: lane` and the same for the filer. The conductor wrote none of these itself; its one edit to the file was appending a `Lane: solo because ...` line (call 5, the dispatch line `agents/conductor.md` asks for).
- Hidden check on the final tree: `hidden_check: 9/9 passed` ([`hidden-check.txt`](solo-close-live-run/hidden-check.txt)). `git status` after the run is in [`git-status-after.txt`](solo-close-live-run/git-status-after.txt).

## Models and cost, from the session transcripts

[`transcript-summary.json`](solo-close-live-run/transcript-summary.json): conductor `sdlc-lite:conductor` on `claude-sonnet-5-5` (5,068 output tokens), solo `sdlc-lite:solo` on `claude-sonnet-5-5` (13,594), verifier `sdlc-lite:verifier` on `claude-fable-5-1` (55,798). Effort is a launch flag: conductor `high`; the conductor started the solo with `--model sonnet --effort xhigh` (tier M of `agents/solo.md`, call 6), which the stream does not otherwise record. Cost: the conductor session $0.20 (the result event's `total_cost_usd`, [`session-trace.txt`](solo-close-live-run/session-trace.txt)), the verifier $3.09 ([`runs.jsonl`](solo-close-live-run/runs.jsonl)); the solo session's cost was not captured.

## Limits

- One run on one machine, one tiny size M ticket, Claude Code only (no Codex conductor start).
- The conductor started the solo from Bash itself with the tier M flags it read in `agents/solo.md` (call 4), not through a script.
- The run shows the close is no longer refused on the default path; the selftest negative control (steps selftest, `(lane solo close)`) is what shows the guard still refuses without the entries.
- The evidence was copied from the run directory and trimmed to text files; the transcripts stay in `~/.claude/projects`.
