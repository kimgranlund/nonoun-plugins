# Builder overlay retest on blocking tasks (T-0458)

Ticket question: do the builder L1 and L5 overlays still earn their place when replayed on tasks that make builders block, with at least one priced L5 pair?

Verdict: drop
L1 overlay: drop
L5 overlay: unverified
Null at this sample size: yes
Spend: 10.04 USD
Ticket spend: 19.30 USD (planners, the blocked L3 builder and the replay, before this report's builder, verifier and filer), under the 20 USD cap
Outcome metric: builder blocked rate, arm A versus arm B: L1 0 of 1 versus 0 of 1, L5 1 of 1 versus not run (before: 0 of 5 versus 0 of 5 on the first A/B tasks)

The drop comes from the T-0442 blocked-rate rule, the same rule that dropped L1 in the first A/B. It could not bite here either. So the retest adds no evidence beyond the first A/B's outcome, which the maintainer saw and overruled on 2026-10-11. The only L1 task that ran replayed the fixed handoff, sha256 `8974d49f`. The blocked version, `fceea3cc`, was never committed in agent-ui and is gone. So no L1 run tested blocking, and the retest did not reach the ticket's question. The L5 pair is half run. The replay stopped at the cap.

## Per-run results

Cost provenance: `dispatch.py record --transcript`, `cost_estimated`, basis `usage fields x rates`.

| task | source | level | arm | rep | cost_usd | builder_min | blocked | block_tag | hidden_check | verifier | verifier_cost_usd | verifier_min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rts-step10 | blocked note | L1 | A | 1 | 0.34 | 1.2 | no | none | n/a | pass | 0.51 | 1.5 |
| rts-step10 | blocked note | L1 | B | 1 | 0.28 | 1.2 | no | none | n/a | pass | 0.37 | 1.1 |
| ndc-step2 | blocked note | L5 | A | 1 | 8.54 | 22.8 | yes | plan defect | n/a | n/a | 0.00 | 0 |
`hidden_check` is `n/a` on all three, because both tasks are `blocked note` tasks (the plan's rule: a step with a real plan defect has no correct build to grade).

## Rule outcomes

| measure | arm A (no overlay) | arm B (overlay) | change |
|---|---|---|---|
| L1 builder cost, `rts-step10` rep 1 | 0.34 | 0.28 | -17.5 percent |
| L1 verifier cost | 0.51 | 0.37 | -27.3 percent |
| L1 builder minutes | 1.2 | 1.2 | none |
| L1 verifier minutes | 1.5 | 1.1 | -0.4 min |
| L1 blocked | 0 of 1 | 0 of 1 | none |
| L1 first pass, `rts-step10` | 1 of 1 | 1 of 1 | none |
| L5 builder cost, `ndc-step2` rep 1 | 8.54 | not run | n/a |
| L5 blocked | 1 of 1 | not run | n/a |
| Blocks that name the same defect as the original note | 1 of 1 (L5) | 0 runs | n/a |

| rule | rep 1 | rep 2 |
|---|---|---|
| blocked rate below arm A's | no (0/1 vs 0/1), drop | not run |
| any task's first-pass rate falls | no | not run |
| cost rises more than 10 percent | no (-17.5) | not run |
| hidden-check regression | none (n/a in both arms) | not run |
| measured-block: arm B blocked rate above arm A's | no (0/1 vs 0/1) | not run |
| measured-block: lower on the blocked-note tasks | no (0 vs 0 on `rts-step10`; `ndc-step2` L1 not run) | not run |

- Null: only rep 1 ran, so no rule outcome was shown in both reps, and the null line is `yes`.
- The measured-block rule (the ticket's added rule) is not raised, and lowering could not be measured.
- L5 rules: not applied, because arm B never ran, so `L5 overlay: unverified`.
- Same defect: the L5 arm A block names the original note's defect. The scope guard omits `scripts/bundle.mjs`, which the mandated chart imports require. That makes 1 of 1 arm A blocks the same defect, with no arm B run. The original L3 builder cost $3.41 to block on it. The L5 builder cost $8.54.
- Overall: the only overlay that ran is dropped, so `Verdict: drop` (T-0442 derivation). This records the verdict only. Deleting or keeping the overlay is the maintainer's call, and T-0443 stays gated on it.

## Stop at the cap

`budget.txt`:

```
start pair rts-step10 L1 rep 1: spend 0.00 + estimate 2.00 <= 14.00
start pair ndc-step2 L5 rep 1: spend 1.50 + estimate 8.00 <= 14.00 (plan estimate)
stop after half pair ndc-step2 L5 rep 1: spend 10.04; arm B estimate 8.54 -> 18.58 > 14.00; three more L1 rep-1 pairs (2 x (0.34 + 0.51) = 1.70 each) cannot follow under the 20 USD cap; blocked as plan defec
```

- Replay Spend was 10.04 after half the L5 pair.
- Arm B at the arm A cost would have made it 18.58, against the 14.00 replay target.
- The planners ($3.85) plus the blocked L3 builder ($2.14) put the ticket at about $16.03.
- So no further cell ran, per the conductor's direction and the ticket Constraint "stop at it and report what was run".

## Method

- Arms: `git clone --shared` copies under the tmp prefix. armB is this repo at `ebac4973`. armA is the same with `builder-L1.md` and `builder-L5.md` from `00735e20^`. `diff -rq` of the two plugin folders lists only those two files, with one hunk each (`34a35,55` for L1, `34a35,52` for L5), and each hunk starts `## At this level`.
- Preflight: the Haiku `--plugin-dir` init events in `preflight.txt` show exactly one `sdlc-lite` plugin, at the arm root, in agent-ui@0e18b708, ultimate-tokens@7f05eb50 and sdlc-lite@6a14c165 cells, for both arms.
- Hash checks: the `rts-step10` cell handoff is `8974d49f6a3f`, the done row, not the blocked row `fceea3cca477` (mismatch). The `ndc-step2` handoff is `6c2cd3e60200`, which matches the blocked row.
- The t0378 hidden check is red at base `b599114e` and green at `a8b39893` and `e1fa6e04`. The earlier plan's claim "red at wip a8b39893" was false. t0378 did not run.
- Base trees were checked with `git ls-tree`; no task was dropped.
- Each cell was priced with `dispatch.py record --transcript`. `steps.py lint` was ok and `prepare` passed every time.
- The driver is `cell.py` in the evidence folder.
- Repository paths outside this repo are written as absolute paths or plain words, never as bare repo-relative `.sdlc/` paths.

## Not run

- `ndc-step2` L5 arm B rep 1: unverified, skipped for budget.
- L1 rep 1 pairs `ndc-step2`, `t0368`, `t0373`, `t0378`: unverified, skipped for budget.
- L1 rep 2 pairs for `rts-step10`, `ndc-step2`, `t0368`, `t0373`, `t0378`: unverified, skipped for budget (no rep 2 ran).
- `match-peer-lightness`: unverified, its L5 original cost $39.24 and fits no budget.
- `button-geometry-model`, `svelte-icon-component`: unverified, their repos and base shas are missing on this machine.
- 0356, 0398: unverified, T-0450 criterion defects that can never pass.
- 0372, 0426: unverified, no separable hidden check.

## First A/B verifier miss

`figma-stale-skip-report` failed its hidden check `staleskipnotice` in all four first A/B runs, while both verifier levels passed it each time. It is a verifier miss, the same in both arms. It is recorded for the verifier prompt work and not fixed here.

## Raw rows

```jsonl
{"ts":"2026-10-12T13:05:31Z","role":"builder","level":"L5","model":"fable","effort":"xhigh","file":"builder-L5.md","shared_with_builder":false,"attempt_id":"8f2b965169854813a2cd83ce2d15bb49","handoff_sha256":"6c2cd3e60200db0f8a79411e76b9163c7d8f35eb39c6ce25f2cf19816ab688cd","result_sha256":"b8c9f3d250f93b3b2aa3b9a22481c19920a89ede7fba539f8f244ceb540b3ed7","stale_input":false,"routing_reason":"T-0458 overlay retest arm A","backend":"claude","transport":"subagent","agent_id":null,"usage":{"input_tokens":998,"cache_creation_input_tokens":166729,"cache_read_input_tokens":3586347,"output_tokens":61422},"cost_usd":8.543153,"cost_reason":null,"duration_ms":1364519,"turns":null,"stray_worktrees":[],"stray_branches":[],"loaded_context":{"status":"log absent"},"cost_estimated":true,"cost_basis":"usage fields x rates","resolved_model":"claude-fable-5-1"}
{"ts":"2026-10-12T12:38:16Z","role":"builder","level":"L1","model":"sonnet","effort":"low","file":"builder-L1.md","shared_with_builder":false,"attempt_id":"d9932392e40f49769360eeed8d4345b1","handoff_sha256":"8974d49f6a3f2ab5f982eeec6f3f7f5ee0748cc942ffcd1615798c72732e1b64","result_sha256":"d9ba282cbae36f76d2b821c8822aa64f6f9a323f94fb46bfda55c7072b3b09cb","stale_input":false,"routing_reason":"T-0458 overlay retest arm A","backend":"claude","transport":"subagent","agent_id":null,"usage":{"input_tokens":16,"cache_creation_input_tokens":55975,"cache_read_input_tokens":410079,"output_tokens":5579},"cost_usd":0.337507,"cost_reason":null,"duration_ms":64765,"turns":null,"stray_worktrees":[],"stray_branches":[],"loaded_context":{"status":"log absent"},"cost_estimated":true,"cost_basis":"usage fields x rates","resolved_model":"claude-sonnet-5-5"}
{"ts":"2026-10-12T12:39:46Z","role":"verifier","level":"L1","model":"opus","effort":"medium","file":"verifier-L1.md","shared_with_builder":false,"attempt_id":"0f9889ae392748f58ee016009a7bddbb","handoff_sha256":"8974d49f6a3f2ab5f982eeec6f3f7f5ee0748cc942ffcd1615798c72732e1b64","result_sha256":"8a53cf9c2a95fe093f99c6a659030952c35b6a1def01ed0396f13c8f53df1aa4","stale_input":false,"routing_reason":"T-0458 overlay retest arm A verifier","backend":"claude","transport":"subagent","agent_id":null,"usage":{"input_tokens":16,"cache_creation_input_tokens":66341,"cache_read_input_tokens":409173,"output_tokens":6816},"cost_usd":0.512175,"cost_reason":null,"duration_ms":83647,"turns":null,"stray_worktrees":[],"stray_branches":[],"loaded_context":{"status":"log absent"},"cost_estimated":true,"cost_basis":"usage fields x rates","resolved_model":"claude-opus-5-5"}
{"ts":"2026-10-12T12:41:12Z","role":"builder","level":"L1","model":"sonnet","effort":"low","file":"builder-L1.md","shared_with_builder":false,"attempt_id":"70f57c701a2a4f0f978b0574ce22ddcc","handoff_sha256":"8974d49f6a3f2ab5f982eeec6f3f7f5ee0748cc942ffcd1615798c72732e1b64","result_sha256":"eb84454894c78ec174a2680de401fbe2711b7a6ac5e0e8c720a4347dacac20ef","stale_input":false,"routing_reason":"T-0458 overlay retest arm B","backend":"claude","transport":"subagent","agent_id":null,"usage":{"input_tokens":14,"cache_creation_input_tokens":47902,"cache_read_input_tokens":327052,"output_tokens":4409},"cost_usd":0.278392,"cost_reason":null,"duration_ms":67244,"turns":null,"stray_worktrees":[],"stray_branches":[],"loaded_context":{"status":"log absent"},"cost_estimated":true,"cost_basis":"usage fields x rates","resolved_model":"claude-sonnet-5-5"}
{"ts":"2026-10-12T12:42:21Z","role":"verifier","level":"L1","model":"opus","effort":"medium","file":"verifier-L1.md","shared_with_builder":false,"attempt_id":"b75216cea1ff4dc097cd97604d9d4076","handoff_sha256":"8974d49f6a3f2ab5f982eeec6f3f7f5ee0748cc942ffcd1615798c72732e1b64","result_sha256":"5cec712cbe3540a45d37fd4e2c39add370d68eeea40823d91ebdd9a44c561a8a","stale_input":false,"routing_reason":"T-0458 overlay retest arm B verifier","backend":"claude","transport":"subagent","agent_id":null,"usage":{"input_tokens":12,"cache_creation_input_tokens":47550,"cache_read_input_tokens":282448,"output_tokens":5305},"cost_usd":0.372207,"cost_reason":null,"duration_ms":64891,"turns":null,"stray_worktrees":[],"stray_branches":[],"loaded_context":{"status":"log absent"},"cost_estimated":true,"cost_basis":"usage fields x rates","resolved_model":"claude-opus-5-5"}
```
