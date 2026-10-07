# Verifier L2 replay of the T-0333 verification (T-0356)

Question: does verifier L2 (sonnet, high) catch the failures verifier L3 (fable, xhigh) caught when T-0333 verified 12 sub-agent tickets (9 pass, 3 fail)?

Result in one line: L2 caught 3 of the 4 failing criteria (all of T-0328 and T-0331, but not T-0280-2), and produced 1 new false fail (T-0275). Safe to route L1/L2 tickets to L2: partly.

## Method

- Tree: `git archive f0ba4f94` extracted to `/tmp/replay-t0356/tree`. `dispatch.py prepare` needs a git work tree with a commit, so I ran `git init` and one commit in the extract (`75156e1`). Consequence: the tree is one squashed commit with no history. The original run had the real repo history, so history-based checks (for example `git show` on an old commit) were not available inside the tree. Two L2 verifiers read the source repo's history read-only to compensate (dispatch-supervisor T0286-3, solo-record T0284-4).
- Handoffs: the six `handoff.md` files were copied unchanged (none contained an absolute tree path). `prepare` pointed the Tree line at the archive tree by itself, so no handoff adaptation was needed.
- Flow per batch: `dispatch.py prepare verifier L2 <handoff>` (all six exit 0, JSON `sdlc-lite:verifier-L2`, sonnet, high), Agent spawn with the printed fields (the six ran as background sub-agents in one block; the printed `run_in_background: true` could not be passed explicitly because the Agent tool schema here has no such parameter), then `dispatch.py record --agent-id <id> --transcript <transcript>` (all six accepted, report validated). No gate refused at any step.
- The L2 verifiers had no access to the L3 verdicts: the archive tree holds no `.sdlc/verify-subagent` folder.
- Artifacts: `/tmp/replay-t0356/<batch>/verifier-L2.md` (verdict), `runs.jsonl`, `verifier-L2.dispatch.json`.

## Per-criterion comparison

L3 verdicts are from `.sdlc/verify-subagent/T-*.md`. Criteria that both passed are grouped.

| Ticket | Criterion | L3 | L2 | Agreement |
|---|---|---|---|---|
| T-0275 | T0275-1, -2, -4, -5, -6 | pass | pass | yes |
| T-0275 | T0275-3 (every probe answered) | pass (with a recorded-evidence-only note) | fail | NO, new false fail |
| T-0279 | T0279-1 to -4 | pass | pass | yes |
| T-0286 | T0286-1 to -4 | pass | pass | yes |
| T-0280 | T0280-1, -3, -4 | pass | pass | yes |
| T-0280 | T0280-2 (cost_basis label) | fail | pass | NO, missed true fail |
| T-0328 | T0328-1 (within 35 percent band) | fail | fail | yes, different evidence |
| T-0328 | T0328-2, -3, -4 | pass | pass | yes |
| T-0331 | T0331-1 (launcher skills lack --transcript) | fail | fail | yes, same 12 skills found |
| T-0331 | T0331-3 (L3 row 0.570 of host) | fail | fail | yes, same 0.57 |
| T-0331 | T0331-2, -4 | pass | pass | yes |
| T-0332 | T0332-1 to -4 | pass | pass | yes |
| T-0284, T-0330 | all (7 criteria) | pass | pass | yes |
| T-0326, T-0327, T-0329 | all (9 criteria) | pass | pass | yes |

Ticket verdicts: 10 of 12 agree. T-0275 (L3 pass, L2 fail) and T-0280 (L3 fail, L2 pass) disagree. Criteria: 41 of 43 agree. Batch verdicts: 5 of 6 match; probes does not (cost-a still ends `fail` through T0328-1, though its T-0280 ticket verdict differs).

## Were the true fails caught

- T-0328 T0328-1: caught. L2 priced the stored rows (they hold only `subagent_tokens`) and reported ratios 0.12 and 0.07 of host, not L3's 0.570. Same verdict, different mechanism; both are real, since the stored rows and the transcript-based row are separate readings of the same criterion. L2 also noted the L3 fable figure is 1.44x when priced from transcript-summary usage.
- T-0331 T0331-1: caught, with the full list of launcher skills (build, verify, scout, plan, fix, architect, dig, research, file, fleet-retro, review-traces, agent) and the `git grep` proof.
- T-0331 T0331-3: caught, 0.57 of host (1.4112 vs 2.4762), plus a bonus finding that the report's T-0331 calibration paragraph disagrees with `prices.json`.
- T-0280 T0280-2: MISSED. L2 observed that the transcript basis string is `usage fields x rates`, not the criterion's literal `transcript usage x price`, and passed it by reasoning that the ticket text made the string conditional on a probe. L3 failed it on the literal mismatch plus a stale docstring. Debatable on the merits, but it is the recorded true fail and L2 did not file it.

## False fails and false passes

- New false fail (T0275-3): L2 failed the probes batch because the P1 row omits the resolved haiku id and has a truncated `"level":"xhi..."` quote, both unrecoverable from the surviving hook.log. L3 treated the same gap as recorded evidence only and passed. This is stricter, not wrong in substance: L2 re-observed the raw logs and found a real documentation gap. It would have blocked a ticket that L3 let through.
- Missed true fail: T0280-2 (above).
- No other disagreements across the remaining 41 criteria.

## Cost and duration

| Batch | L2 cost USD | L3 cost USD | L2 minutes | L3 minutes | L2 tool calls | L3 tool calls |
|---|---|---|---|---|---|---|
| probes | 0.90 | 6.04 | 4.2 | 16.5 | 25 | 41 |
| dispatch-supervisor | 0.89 | 5.89 | 11.6 | 16.5 | 28 | 47 |
| cost-a | 1.48 | 7.75 | 22.5 | 25.1 | 33 | 43 |
| cost-b | 1.17 | 4.81 | 16.6 | 15.0 | 30 | 28 |
| solo-record | 0.96 | 6.05 | 8.9 | 17.2 | 31 | 48 |
| fanout | 0.79 | 6.02 | 20.8 | 19.1 | 21 | 44 |
| Total | 6.19 | 36.56 | 84.6 | 109.4 | 168 | 251 |

L2 cost is the `cost_usd` that `dispatch.py record` wrote (`cost_estimated`, basis `usage fields x rates`, Sonnet rates from `prices.json`), the same method as the L3 figures, so the two are comparable. Per run L2 costs 0.79 to 1.48 USD against L3's 4.8 to 7.7, about 17 percent of the L3 total. Duration is first to last transcript timestamp (the L2 sub-agent notification usage was not available to me; `duration_ms` is null in the recorded rows). Six runs ran concurrently on one machine, so durations carry contention noise.

## Limits

- Six batches, one run each, no variance estimate. T0280-2 and T0275-3 are each a single borderline call that could flip on a rerun.
- The replay tree has no git history; L3 had it. Two L2 verifiers reached into the source repo to make up for it.
- The L2 verifiers saw the same handoff text as L3 but a differently pathed tree, and the criteria for T-0328 depend on tree-stored report files, which were identical.
- L3 and L2 ran in different sessions, with different host load; durations are indicative only.
- The L2 verifier family (sonnet) matches the original builder family (solo sonnet low). The role rules ask a verifier to differ from the builder family; `dispatch.py prepare` for a real ticket would move L2 to opus. This replay used `sonnet` as printed because no builder `runs.jsonl` sat beside the handoffs.

## Recommendation

Safe to route L1/L2 tickets to L2: partly. L2 matched L3 on 41 of 43 criteria, caught three of four true failing criteria with sound evidence, and costs about one sixth as much. Keep L3 (or add a second look) where a criterion hinges on a literal string or label match, as T0280-2 did, and expect L2 to be stricter than L3 on evidence gaps (T0275-3). Re-run with more batches before making L2 the unconditional default.
