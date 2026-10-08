# Solo L2 (Sonnet) effort sweep 2: high versus xhigh (T-0357)

Date: 2026-10-07. Status: experiment record, uncommitted. `adapters/claude/levels.json` and every tracked file were not touched. Working files: `/tmp/sweep2-t0357`.

## Question

Does solo L2 (Sonnet) at effort high pass everything it passes at xhigh, at lower cost? Sweep 1 ([first sweep](2026-10-07-solo-l2-effort-sweep.md)) was 8 of 8 on small L1-sized fixes with weak judging. This sweep uses real L2 tickets, an independent behavior probe per ticket, and a blind reviewer.

## Method

- Tickets: six closed tickets with handoff `size: L2`, each touching several files and real behavior, none from T-0343 to T-0350. Each pre-change tree is the parent of the ticket's implementation commit, recreated with `git archive`, one fresh `git init` and commit per checkout (`base`, `high`, `xhigh`, plus a `ref` tree at the real implementation commit for validating the probes). Parents: T-0229 a771bd40, T-0271 0b58bd23, T-0274 8d45cb62, T-0304 7353252f, T-0314 d960ddb0, T-0323 b37cc340. T-0153 was dropped first (its parent predates the `solo` agent) and replaced by T-0229.
- Arms: `SDLC_ROLE=solo claude -p --plugin-dir <checkout>/plugins/sdlc-lite --agent sdlc-lite:solo --model sonnet --effort high|xhigh --dangerously-skip-permissions --output-format json -- <prompt>` in the arm's own checkout, 8 sessions at most at once. The prompt is `Handoff: <path>`, `Artifacts dir: <dir>`, then one line telling the agent to deliver per Goal and Done when and not commit. I did not use `solo_run.py run` to produce the prompt (see Limits). The ticket handoff (status set to ready, `## Closed` removed) was copied into the checkout.
- Independent behavior probe per ticket (`/tmp/sweep2-t0357/probes/p<NNNN>.py`), written by me from the Done-when text and not from any arm. Each probe was validated both ways: it fails on the pre-change tree and passes on the real implementation commit (T-0271 4 of 6 pass at base, 6 of 6 at ref; T-0274 6 of 11, 11 of 11; T-0304 6 of 8, 8 of 8; T-0314 5 of 9, 9 of 9; T-0323 5 of 10, 10 of 10; T-0229 4 of 7, 7 of 7). So these are checks that exist independent of the builder.
- Own checks per arm, observed output (`<ticket>/<arm>.judge.txt`): `check.py`, `tickets.py check` (run on a copy with the ticket size normalised, because the pre-change `tickets.py` only knows S|M|L|XL and the ticket text says L2), the touched script's selftest (steps, run-selftest, gate_lock, specgate, fleet_status, solo_run, budget), and the probe.
- Blind reviewer: one `claude -p --model opus --tools ""` call per arm, prompt on stdin, containing the ticket Goal and criteria and the arm's diff (excluding `.sdlc`), asked for PASS or FAIL per criterion and overall. Arms were labelled A and B at random per ticket (`labels.json`); the prompt does not mention effort. The reviewer cannot run code, so it judges reading only.
- Cost and duration: `total_cost_usd` and `duration_ms` from each arm's session result JSON.

## Results (five valid tickets)

T-0229 is excluded from the comparison, see Invalid ticket below. All five valid tickets are size L2.

| Ticket | High own checks | xhigh own checks | High reviewer | xhigh reviewer | High cost | xhigh cost | High time | xhigh time |
|---|---|---|---|---|---|---|---|---|
| T-0271 lint plan-defect dependents | pass (6 of 6 probe) | pass (6 of 6) | pass | pass | $0.68 | $2.83 | 15.5 min | 33.9 min |
| T-0274 run.sh lane gate | pass, probe 10 of 11 (note 1) | pass, probe 9 of 11 (notes 1, 2) | pass | pass | $1.77 | $7.03 | 33.5 min | 54.9 min |
| T-0304 gate_lock reap | pass (8 of 8) | pass (8 of 8) | pass | pass | $0.61 | $2.22 | 13.6 min | 20.0 min |
| T-0314 red-first control | pass (9 of 9) | pass (9 of 9) | pass | pass | $1.99 | $5.83 | 30.5 min | 42.3 min |
| T-0323 fleet_status render | pass (10 of 10) | pass (10 of 10) | fail (note 3) | fail (note 3) | $1.10 | $3.57 | 5.8 min | 20.2 min |
| Total | 5 of 5 | 5 of 5 | 4 of 5 | 4 of 5 | $6.15 | $21.48 | 98.9 min | 171.3 min |

Turns: 165 at high, 254 at xhigh. Session cost at high is 29 percent of xhigh, wall time 58 percent.

Notes:

1. T-0274 probe case "override reason recorded in skips.md" fails in both arms. Both arms deliberately write nothing in a dry run (each arm's own run-selftest asserts that), and my probe ran `run.sh` dry. The reference writes it even in a dry run. The Done-when does not say which, so I count this as a probe artifact, not a defect. I did not run a stub-claude real run to close it.
2. T-0274 xhigh also gates a task handoff that has no ticket `id:` (exit 5), where high and the reference do not. This is outside the listed criteria; `steps.py lane --check` returns full for a no-id handoff with no size, so the effect is limited to a size S or M handoff without an id. A real but minor behavior difference at xhigh.
3. T-0323 reviewer fail is the same in both arms and comes from the ticket text, not the code: the criteria name `docs/references/sdlc-internals.md`, the pre-change tree keeps that file at `docs/maintenance/sdlc-internals.md`, and the scope criterion lists only the former. Both arms edited the file that exists. The reviewer found the render, marks, collapse and skill text correct. Treat as an artifact of a later docs rename, equal on both sides.

## Cost the session JSON does not show

Most arms launched a nested batched verifier (`run.sh verifier L3`, Fable xhigh) as the solo flow does at tier M. That is a separate `claude -p` process, so its cost is not in the arm's `total_cost_usd`. Recorded in each arm's `runs.jsonl`:

| Ticket | High nested verifier | xhigh nested verifier |
|---|---|---|
| T-0271 | none | $4.56 |
| T-0274 | none | $3.15 |
| T-0304 | $6.12 | $5.60 |
| T-0314 | $4.86 | $4.85 |
| T-0323 | none | $4.28 |
| Total | $10.98 | $22.44 |

With the verifier included, the five tickets cost $17.13 at high and $43.92 at xhigh (39 percent). The xhigh arms always ran the verifier; the high arms ran it on 2 of 5. That difference is part of the xhigh cost and I cannot separate it from effort with one run each. I did not read the nested verifier verdicts as evidence (they are the arm's own flow, not a blind judge).

## Where high and xhigh disagree

No disagreement on any verdict: all three judges (own checks, probe, blind reviewer) gave the same result for high and xhigh on all five tickets. Differences below are not verdict differences.

- Size: xhigh diffs are larger on every ticket (outside `.sdlc`): T-0271 +182 versus +125, T-0274 +342 versus +221, T-0304 +218 versus +163, T-0314 +505 versus +362 over 14 files versus 8, T-0323 +225 versus +178. Larger was not better on these probes.
- T-0274: xhigh gates a no-id handoff (note 2). High matches the reference there.
- T-0271: the reviewer noted a gap in the high arm (a backticked path with `:line` keeps a trailing backtick after stripping and is dropped as nonexistent) and still passed it. The probe (plain path in a verifier result) passes at both.
- T-0314: the first probe version used `(guard) (red)` on one line, which `specgate.py` itself flags as invalid, and it made xhigh look like it failed swap tag parity. After correcting the fixture to the valid `(red)` only form, high, xhigh and the reference all refuse a swap that drops the tag. This was my probe error, found by running the reference.

## Invalid ticket: T-0229

Excluded from the totals. Its handoff carried post-delivery `## Result`, `## Verification` and `## Limits` sections describing the finished implementation, and both arms saw them; the blind reviewers then judged against a Result that cited a different implementation. The xhigh arm completed ($4.40 session plus an $8.26 nested verifier, probe 7 of 7, selftests and own checks pass, reviewer fail for the citation mismatch). The high arm was still running after 42 minutes in a nested verifier when I stopped it, so it has no result. The other five handoffs carry an `## Acceptance criteria` section that was written at delivery time and names exact selftest labels (for example `ok: (s) lint accepts a plan whose step names...`); arms saw it equally. It narrows the build, so these runs are easier than a fresh ticket. My probes do not depend on those labels.

## Spend and stop rule

The stop line was about $45. By session JSON alone the sweep was at $32 (plus $8 of reviewers) and looked safe; the nested verifier sessions, which I did not meter until late, bring the total to about $82: arms $32.03, nested verifiers $41.68, reviewers $7.92, one test call $0.56, plus an unmetered partial T-0229 high nested session and about two minutes of two sessions on T-0304 started and killed by a mistaken first launch. I overshot the stop line without noticing and stopped further work once I saw it: no T-0229 rerun, no rerun of the T-0323 reviewers with the path rename explained, no stub-claude real-run probe for T-0274.

## Limits

- One run per arm per ticket, no variance. Five ties cannot exclude a high failure rate of tens of percent, and a hard ticket could split the efforts where these did not.
- Five tickets on one codebase and one author's style of ticket, all scripts, hooks and renderers. Nothing ambiguous or under-specified; the criteria were detailed and partly leaked into the handoff.
- The reviewer reads diffs only, did not see a run, and failed T-0323 on both arms for a reason outside the code. Its "pass" on four tickets is plausible-from-diff, not observed.
- The probes check the listed behaviors, not every Done-when line (for example full `check.sh`, live Codex runs and the verifier step were not run by me).
- Prompt differs from `solo_run.py run`: I did not run it to avoid its worktree and marker side effects, so the dispatch record, brief wording and the `solo_run.py` cost record were not exercised. The first launch attempt did run it on T-0304 for about two minutes before I killed it; the checkouts were reset.
- The nested-verifier asymmetry (xhigh 5 of 5, high 2 of 5) confounds cost.
- The arms used each ticket's pre-change plugin, not current main.

## Recommendation

Drop solo L2 to high: partly. Yes for builds of this class, supported by: all five valid tickets passed own checks, an independent probe validated against the real implementation, and a blind reviewer at both efforts with zero verdict disagreement (5 of 5 and 4 of 5 with the same T-0323 reviewer artifact on both), at 29 percent of the session cost ($6.15 versus $21.48) and 58 percent of the wall time (98.9 versus 171.3 minutes), or 39 percent of cost with nested verifiers ($17.13 versus $43.92). Not yet a decision: n=5 with one run each, no ambiguous or hard ticket, the T-0229 ticket invalid, and the overspend means no rerun. If the user wants more confidence before editing `levels.json`, the cheapest next step is two or three repeat runs of T-0274 and T-0314 at high only (the two largest diffs), with the handoff reduced to Goal and Done when and the verifier step off for both arms.
