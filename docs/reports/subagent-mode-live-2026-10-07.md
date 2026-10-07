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

## Rerun after T-0326 to T-0328

Plugin under test: this worktree (`.worktrees/fanout-w6/integration`, branch `subagent-w6`, commit 995632ed, which holds T-0326, T-0327 and T-0328), `claude -p --plugin-dir <worktree>/plugins/sdlc-lite --agent sdlc-lite:conductor --dangerously-skip-permissions --output-format stream-json --verbose`, `SDLC_HEADLESS=1`, Claude Code 2.1.292, no `/login`. Two throwaway projects, `/tmp/sdlcrerun/proj` (R1) and `/tmp/sdlcrerun3/proj` (R2), each a tiny `kit` package, `onboard.py setup`, two ready tickets. Raw records: files prefixed `R1-`, `R2-` and [rerun-host-cost.txt](subagent-mode-live-2026-10-07/rerun-host-cost.txt) in [subagent-mode-live-2026-10-07/](subagent-mode-live-2026-10-07/). Stream logs and transcripts stay in `/tmp/sdlcrerun*/logs` and `~/.claude/projects/-private-tmp-sdlcrerun-proj`. Headless runs spawn foreground sub-agents.

R1 ran the one two-lane fanout asked for: a=T-0001 (size M, solo-M) and b=T-0002 (size S, solo-S), verifier L3 on T-0001 (family fable, solos sonnet), `fanout.py land` per branch (20:45:25 to 20:50:17 PDT). It exposed one still-failing fix, so I fixed that in this branch and ran R2, two size S lanes with `land` on its default `--lane auto` (20:56:15 to 20:57:10 PDT).

| Fix | Verdict | Evidence |
|---|---|---|
| T-0326 prep lane spawns pass the gate | fixed (observed) | R1 and R2: every lane spawn (`T-0001-solo`, `T-0002-solo`) went through the Agent gate; host `subagent_stats` `spawned 3 ... refused 0` (R1), `spawned 2 ... refused 0`, `permission_denials 0` (R2). |
| T-0327 land recognizes host branches | still failing at 995632ed, fixed by the commit that carries this section (observed in R2) | R1 below, then R2. |
| T-0328 cost within 35 percent, solo rows priced | still failing | Cost below. |

### T-0326, fixed (observed)

The spawn prompt began `Handoff: .sdlc/0001-slugify/handoff.md` ([R1-T-0001-solo.dispatch.json](subagent-mode-live-2026-10-07/R1-T-0001-solo.dispatch.json), [R1-T-0002-solo.dispatch.json](subagent-mode-live-2026-10-07/R1-T-0002-solo.dispatch.json)), and `fanout.py prep` wrote `T-0001-solo.dispatch.json` and `T-0002-solo.dispatch.json` beside each handoff before the spawn. The conductor spawned both from the prep JSON with no fallback to `solo_run.py run`; both solos ran in isolated worktrees (`.claude/worktrees/agent-ac24d8dfc4ddda2ad`, `agent-aca0f892eefaa7b91`) and committed `WIP` plus `T-000N: <title>`. The verifier spawn (`verifier-L3-0001-slugify`, `model fable`, transcript `claude-fable-5-1`) also passed.

### T-0327, still failing at 995632ed, then fixed

R1: the host again named the branches `worktree-agent-<agent_id>` (`worktree-agent-ac24d8dfc4ddda2ad`, `worktree-agent-aca0f892eefaa7b91`; the agent id is the `task_started` `task_id`). `land ... --ticket T-0001` printed `(lane full)` and `merged, close refused: no filer-L*.md`, the same symptom as finding 3; the conductor then closed both by hand with `tickets.py close --reason`, after a `--lane solo` re-land that returned `no changes`.

Root cause: `host_branch_ticket` finds the lane through an `agent_id` in a `runs.jsonl` line on the branch, and a `kind` of solo needs that line to say `role: solo`. A real solo sub-agent writes no `runs.jsonl` line in its lane (the fanout prep path writes only the dispatch JSON, untracked in the main tree), and T-0001's branch held only the verifier line (the verifier's own agent id, `a63896d71b9e6437b`). The T-0327 selftest fixture hand-wrote a solo `agent_id` line, so it passed against a record nothing produces.

Fix (this branch, `fanout.py land_preflight`): fanout spawns only solo lanes as sub-agents, so a host-form branch with no record naming another role is a solo lane, and a record that names another role or another ticket still routes `full`. The selftest gains the real shape (a host branch with no record and `--ticket`), with its negative control observed: with the old condition restored, `fanout.py selftest` fails on exactly that case; with the fix it passes. `SKILL.md` step 2 and design section 5 now say the host names the branch and the conductor reads it from the Agent result.

R2 ([R2-fanout-report.md](subagent-mode-live-2026-10-07/R2-fanout-report.md), [R2-land.jsonl](subagent-mode-live-2026-10-07/R2-land.jsonl)): with the fix, `land worktree-agent-aab842b43e18de66e --ticket T-0001` printed `(lane solo tier S)`, `merged`, and the integration branch holds `close T-0001` and `close T-0002` commits made by `land`; the conductor closed nothing by hand (gate green, tickets done and archived on `fanout/rerun`). Both lanes report `Lane for ...: solo (tier S: sonnet low)`.

### T-0328, still failing

Verifier row of R1 ([R1-runs.jsonl](subagent-mode-live-2026-10-07/R1-runs.jsonl)): `usage {"subagent_tokens":59930,"tool_uses":12}`, `cost_usd 0.19657`, `cost_estimated true`, `cost_basis "tokens x blended"`. Host, same scope (the verifier is the only fable use, the conductor runs sonnet): `claude-fable-5-1` `costUSD 2.3025`. The estimate is 8.5 percent of host, outside the 35 percent band by about 12x.

Root causes, two:

1. The new `dispatch.py record --transcript` path (and the field-priced `usage_input` rates) is never reached: the conductor's text and the fanout skill pass `--tokens`, not `--transcript`, so the row is still priced from the notice count. Pricing the same verifier from its transcript with `cost_estimate.transcript_usage` gives $0.8498 (37 percent of host), still outside the band.
2. The transcript undercounts against the host: the verifier transcript sums `output_tokens 1697` and `input_tokens 258` against the host's `modelUsage` `outputTokens 18417` and `inputTokens 51956` (cache fields are close: read 360163 vs 410383, write 58224 vs 60757). The fitted rates in `prices.json` reproduce the host figure from the host's counts (about $1.89, 82 percent), so the remaining gap is the transcript's streamed usage values, which carry early partial counts.

Solo rows: priced rows do not exist on the fanout path. Neither lane has a `runs.jsonl` row for the solo (`git show worktree-agent-aca0f892eefaa7b91:.sdlc/0002-titlecase/runs.jsonl` does not exist; T-0001's branch holds only the verifier row), so `solo_run.py complete`, which prices an existing unpriced solo row in place, has nothing to price. Solo cost from the host side: R1 sonnet $0.6453 for the conductor and both solos; R2 sonnet $0.4820 for the conductor and two size S solos. Estimate for the solos: none recorded. Criterion not met; proposed ticket: record a solo row at `prep`/`land` and make the conductor pass `--transcript`, then recalibrate against the host with the output and input counts the transcript undercounts.

### Other findings in R1

- The verifier prompt printed by `dispatch.py prepare verifier L3 <worktree handoff>` carried `Tree: /private/tmp/sdlcrerun/proj` (the main tree, which has no change); the conductor added a note pointing the verifier at the built worktree. `prepare` should set `Tree` to the worktree when the handoff sits under `.claude/worktrees/`. Open, not fixed here.
- The verifier's final message was not on disk as `verifier-L3.md` when `record` ran, so the conductor passed a condensed verdict on stdin; the record is the conductor's summary, not the verifier's full report. Open.
- Both runs: the conductor's first `land` loop failed on a zsh word-splitting slip in its own shell (`set -- $p`), before any land ran; it reran with explicit arguments. The skill's printed command is a single call, so this is a conductor habit, not a script defect.

### Still unverified

Account switch, resume ladder, interactive background sub-agents and the other items listed under Unverified above are unchanged by this rerun. The R2 fix is observed on size S lanes; a size M lane through `land` with a verifier result on a host-named branch was exercised only in R1 (before the fix, forced `--lane solo`) and by the selftest.

### T-0331 calibration

The conductor text and the chain skill now pass `dispatch.py record --transcript`; `fanout.py prep` writes an unpriced `role solo` row and `fanout.py land --transcript` prices it. The transcript undercounts input and output tokens (R1 verifier: output 1697 vs host 18417, input 258 vs 51956), so `adapters/claude/prices.json` carries `usage_calibration` (input x100, output x2), applied per field in `cost_estimate.estimate`. Fitted band, estimate over host: L2 opus verifier 1.22, L3 fable verifier 1.12, R1 fable verifier 0.48. The L2 and L3 rows are within 35 percent; the R1 row stays under the band (selftest asserts 0.45 to 1.35, with a negative control showing the uncalibrated R1 estimate falls below 0.45). The calibration is fitted on three rows and not observed live after this change.
