# Sub-agent mode live evidence (T-0287), 2026-10-07

Plugin under test: this worktree (`.worktrees/fanout-w5/integration`, branch `subagent-w5`, base 9d8eb162 plus fix 08bf3599), loaded with `claude -p --plugin-dir <worktree>/plugins/sdlc-lite --agent sdlc-lite:conductor --dangerously-skip-permissions --output-format stream-json --verbose`, `SDLC_HEADLESS=1`. Host: Claude Code 2.1.292. Throwaway project `/tmp/sdlcprobe/proj` (a tiny `kit` Python package, one test, `onboard.py setup`, five tickets). Raw records are copied to [subagent-mode-live-2026-10-07/](subagent-mode-live-2026-10-07/); the stream logs and transcripts stay in `/tmp/sdlcprobe/logs` and `~/.claude/projects/-private-tmp-sdlcprobe-proj` (too large to copy). Headless runs spawn foreground sub-agents (`run_in_background: false`, as the conductor text says); the interactive background path was not exercised.

## Result

| Run | What ran | transport | Builder family | Verifier family | Outcome |
|---|---|---|---|---|---|
| L1 | One solo size S ticket (T-0003 chunk), conductor, `solo_run.py run` dispatch JSON, `Agent sdlc-lite:solo-S` | subagent | sonnet (`claude-sonnet-5-5`) | none (tier S has no verifier, per `agents/solo.md`) | Pass after fix 08bf3599; the first attempt (T-0001) was refused by the spawn gate, see What failed |
| L2 | Chain of T-0002 clamp: planner L1, builder L1, verifier L1, each prepare, Agent, record | subagent | sonnet (`claude-sonnet-5-5`) | opus (`claude-opus-5-5`) | Pass, closed with `tickets.py close --reason`; 11 tests green |
| L3 | Two-lane fanout, a=T-0004 (size M, solo-M) and b=T-0005 (size S, solo-S), isolation worktree, verifier L3 on the M ticket, `fanout.py land` | subagent | sonnet (`claude-sonnet-5-5`) | fable (`claude-fable-5-1`) for T-0004 | Both merged into `fanout/live` behind the gate (22 tests); close refused for both, see What failed |

Times (PDT, from [times.txt](subagent-mode-live-2026-10-07/times.txt)): L1 20:14:07 to 20:14:48, L1b 20:19:16 to 20:19:59, L2 20:20:10 to 20:22:05, L3 20:22:23 to 20:28:35. Session ids: L1 `8d8f7319`, L1b `3a31a3a3-f331-4357-b89d-0550d0b373d7`, L2 `b02ffe93-2d33-4cec-872b-a02eac331144`, L3 `a1ae7e48-c24a-41ae-940d-62c65af5f22b`. The row labelled L1 is the passing rerun (L1b in the files); the table's three rows are the runs the ticket counts.

## Raw records

L1b solo run, [L1b-runs.jsonl](subagent-mode-live-2026-10-07/L1b-runs.jsonl) (written by `solo_run.py` at dispatch; the sub-agent usage is not recorded afterwards):

```
{"ts":"2026-10-07T03:19:27Z","role":"solo","level":"L1","model":"sonnet","effort":"low",...,"backend":"claude","transport":"subagent","usage":null,"cost_usd":null,...,"cost_reason":"subagent usage not priced"}
```

Dispatch ([L1b-solo.dispatch.json](subagent-mode-live-2026-10-07/L1b-solo.dispatch.json)): `subagent_type sdlc-lite:solo-S`, `name solo-S-0003-chunk`, `model sonnet`, `effort low`, prompt beginning `Handoff: /private/tmp/sdlcprobe/proj/.sdlc/0003-chunk/handoff.md`. Host stats of the session: `spawned 1, by_type {"sdlc-lite:solo-S": 1}, refused 0`. Transcript `agent-a014d89b352cdf2ef` (`agentType sdlc-lite:solo-S`): model `claude-sonnet-5-5` on all 3 assistant messages.

L2 runs, [L2-runs.jsonl](subagent-mode-live-2026-10-07/L2-runs.jsonl), one line per role, all `transport: subagent`, with `agent_id`, `cost_estimated: true`, `cost_basis: "tokens x blended"`:

```
planner  L1 sonnet medium agent_id ade7c74b789457e65 usage {"subagent_tokens":42697,"tool_uses":3} cost_usd 0.034585 duration_ms 18484
builder  L1 sonnet low    agent_id ad2cbba0f10f2d506 usage {"subagent_tokens":35429,"tool_uses":3} cost_usd 0.028697 duration_ms 9830
verifier L1 opus   medium agent_id a5052b8461b479050 usage {"subagent_tokens":42835,"tool_uses":6} cost_usd 0.042407 duration_ms 41294
```

Dispatch files: [planner](subagent-mode-live-2026-10-07/L2-planner-L1.dispatch.json), [builder](subagent-mode-live-2026-10-07/L2-builder-L1.dispatch.json), [verifier](subagent-mode-live-2026-10-07/L2-verifier-L1.dispatch.json) (`"model": "opus"` after a sonnet build, `lane_override` carried). Transcripts: planner and builder `claude-sonnet-5-5`, verifier `claude-opus-5-5` (9 of 9 assistant messages; [transcript-summary.txt](subagent-mode-live-2026-10-07/transcript-summary.txt)). Host stats: `spawned 3, by_type planner-L1, builder-L1, verifier-L1`.

L3 records, [L3-runs.jsonl](subagent-mode-live-2026-10-07/L3-runs.jsonl):

```
solo     L2 sonnet xhigh  transport subagent usage null cost_usd null "subagent usage not priced"   (T-0004)
solo     L1 sonnet low    transport subagent usage null cost_usd null "subagent usage not priced"   (T-0005)
verifier L3 fable  xhigh  transport subagent agent_id a904ad1cad883ca4b usage {"subagent_tokens":51955,"tool_uses":9} cost_usd 0.170412 duration_ms 275217
```

Dispatch of the verifier: `"model": "fable"` ([L3-verifier-L3.dispatch.json](subagent-mode-live-2026-10-07/L3-verifier-L3.dispatch.json)); transcript model `claude-fable-5-1` on 23 of 23 messages; the solos were `claude-sonnet-5-5`. The two solo sub-agents ran side by side: solo-M 03:22:52 to 03:23:30, solo-S 03:22:54 to 03:23:02 (transcript timestamps), in isolated worktrees `.claude/worktrees/agent-acf61a22dc619fd24` and `agent-ab4b159bcba10b564`. Fanout report ([L3-fanout-report.md](subagent-mode-live-2026-10-07/L3-fanout-report.md)): both branches merged, gate `python3 -m unittest discover -s tests -t .` green (22 tests on `fanout/live` at 3475f30).

## Verifier independence

Shown from the dispatch record and from the transcript model field (probe P5 holds): L2 builder sonnet, verifier opus; L3 solo sonnet, verifier fable. Different families in both runs, and the transcript model equals the dispatched `model`. L1 has no verifier by design.

## Cost against the host

The host figure is the session `modelUsage` `costUSD` in the stream-json result ([host-cost.txt](subagent-mode-live-2026-10-07/host-cost.txt)); it covers the conductor session and its sub-agents. A verifier is the only opus or fable use in its run (the conductor runs sonnet), so its host cost is read per model.

| Run | Estimate (`runs.jsonl`) | Host, same scope | Gap |
|---|---|---|---|
| L2 verifier (opus) | $0.0424 | $0.3538 | estimate is 12 percent of host |
| L3 verifier (fable) | $0.1704 | $2.4762 | estimate is 7 percent of host |
| L2 whole run | $0.1057 for three roles | $1.0058 total (sonnet $0.652 incl. conductor, opus $0.3538) | conductor not estimated, role scopes not separable on sonnet |
| L1, L3 solos | null (unpriced) | L1 $0.3667 incl. conductor; L3 sonnet $0.7548 incl. conductor and both solos | unmeterable from records |

The estimate is outside the 35 percent band by about 8x to 14x. Cause, from the transcripts: the notification `subagent_tokens` (opus verifier 42,835) counts roughly the new tokens, while the transcript holds 344,304 tokens including 288,063 cache reads (fable verifier: 51,955 against 1,045,299). `adapters/claude/prices.json` multiplies the small count by a blended rate fitted to `run.sh` runs, so the budget gate under-meters sub-agent roles. Criterion not met; the gap is stated.

## Account switch

Not driven by this run, and I did not run `/login`. The coordinator's session switched accounts between L1 and L1b, so it is observable but not a run that spanned the switch.

- When: after L1 ended (20:14:48) and before L1b started (20:19:16); the coordinator reported the `/login` at about 20:18 PDT. The exact instant is not recorded in my logs.
- Evidence of the switch in my stream logs: `rate_limit_event` of L1 shows `five_hour` `resetsAt 1791348000`, `utilization 0.95`; L1b, L2 and L3 show `resetsAt 1791360600`, `utilization 0.01` to `0.04`, `overageDisabledReason org_level_disabled`. Different window and utilization, so a different account's limits.
- In flight at the switch: none of mine (no run was running; L2 and L3 started after). The `claude -p` processes the coordinator saw alive (pids 519, 9745, 59720, 70552 in `ps`) belong to other sessions, not these runs, so nothing is claimed about them.
- Errors: `grep` for 401, 403, `authentication_error`, `not logged in` and `OAuth` over every stream log and stderr finds nothing; every `result` has `is_error false`, `api_error_status null`.
- What survived, observed: the L1 run records and ticket state written under the old account (T-0001 closed, `runs.jsonl`, `skips.md`) stayed valid and were read by later runs; later `dispatch.py prepare`, Agent spawns, `record` and `fanout.py land` ran on the new account with the same plugin and handoffs; `fable` (L3 verifier) and `opus` (L2 verifier) were available on the new account.
- What needed `dispatch.py resume`: nothing, so no resume rung was used. The ticket's criterion that a run spans a switch and shows the rung is therefore not met: unverified. What the design predicts (section 6, 7): in-session sub-agents survive, a `claude -p` owner is marked interrupted, `SendMessage` by name is rung 1, a new `-k` attempt is rung 3, and a model missing on the new account fails the spawn and is reported instead of moving a verifier onto the builder's family. None of that was exercised here.

## What worked

- Conductor, `dispatch.py prepare`, the Agent spawn gate, sub-agent and `dispatch.py record` end to end for planner, builder and verifier (L2): header, validation, `runs.jsonl` row with `transport: subagent`, `agent_id` and an estimated cost, attempt files, `steps.py next`, close.
- Verifier family remap by `prepare` (sonnet to opus, sonnet to fable), enforced by the gate, confirmed in transcripts.
- Solo S as a sub-agent through the generated `solo-S` definition with `skills` and `effort` honored (P1), and fanout lanes as isolated worktree sub-agents running concurrently, a gate-checked merge in `land`, and the verifier committed on the branch.
- Hooks fire for sub-agent calls with `agent_type` (P2): `block-stray-worktree.sh` denied a verifier's `git worktree add "$B"` with an unresolved path and the verifier retried with a literal path under its tmp prefix (L2 and L3 `permission_denials` list it).
- Host reports `subagent_stats` per session (spawned, by_type, refused 0).

## What failed

1. Spawn gate refused solo sub-agents (fixed, commit 08bf3599). The first L1 (T-0001) ended with `PreToolUse:Agent hook error ... only sdlc-lite:<role>-L<n> agents are dispatched` for `sdlc-lite:solo-S`, so the conductor fell back to `solo_run.py --exec` (a headless `claude -p`, `transport: claude`, [L1a-runs.jsonl](subagent-mode-live-2026-10-07/L1a-runs.jsonl)). Root cause: `hooks/block-role-spawn.sh` accepted only the `<role>-L<n>` form and `solo_run.py` wrote no `<name>.dispatch.json` and no `Handoff:` prompt line, so conditions 1 and 3 of the gate could not hold for solo. Fix: the gate accepts `sdlc-lite:solo-S|M|L` on its dispatch record and model alone; `solo_run.py` writes the record and prefixes the prompt with `Handoff:` and `Artifacts dir:`; `hook-selftest.sh` gains a positive case and two negative controls (wrong model, no record); `solo_run.py selftest`, `dispatch.py selftest`, `fanout.py selftest` and `hook-selftest.sh` pass. L1a's first row also shows a smaller flaw: `solo_run.py` writes a `transport: subagent` row at dispatch time, before any spawn, so the refused T-0001 spawn left a row claiming a sub-agent run that never happened.
2. `fanout.py prep` lane dispatch is refused by the same gate (open). Its prompt has no `Handoff:` line and `prep` writes no record (it "creates nothing"), so both lane spawns (`T-0004-solo`, `T-0005-solo`) were denied. The conductor recovered by running `solo_run.py run` per ticket in the main tree (names `solo-M-0004-slugify`, `solo-S-0005-titlecase`), leaving untracked dispatch records there instead of in the lane. Proposed ticket: `prep` prints a `Handoff:` line and the dispatch record is written at spawn (or the gate accepts `<id>-solo` against a prep manifest).
3. Host branch name differs from the design (open). The host named the worktree branches `worktree-agent-<agent_id>`, not `worktree-<name>`, under `.claude/worktrees/agent-<agent_id>`; `fanout.py land` therefore treated each as an external lane `full`, merged them, then refused to close: `no filer-L*.md in .sdlc/0004-slugify`. Both tickets stay open although merged and green. Proposed ticket: `land` decides the lane from `--ticket` and `steps.py lane`, not from the branch name, and the conductor reads the branch from the Agent result; correct design section 5, `fanout/SKILL.md` and `SUBAGENT_BRANCH`.
4. Cost estimate far below the host (open): 7 to 12 percent of host on the verifier rows, and null for every solo row (see Cost). Proposed ticket: price from the transcript usage (P5) or refit the rate against `subagent_tokens`, and have the solo path record usage at completion.

## Unverified

- Account switch spanning a run, the resume ladder and its rung: not exercised (see above).
- Interactive background sub-agents (`run_in_background: true`) and the completion notification path: the headless runs used foreground spawns.
- Behavior at a session limit (utilization reached 0.95 on the old account but no limit was hit), parent exit with sub-agents running, nested lane conductors (P8), and a lane whose spawn fails on a missing model.
- Whether lane sub-agents were started in one assistant message or two (their transcripts overlap, so concurrent, but the spawn order was the conductor's).
- Estimated cost within the 35 percent band: failed (see Cost), so unmet.
