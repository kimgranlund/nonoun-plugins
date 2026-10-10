# L4 full-chain cost replay on ultimate-tokens T-0040 and T-0044 (T-0418)

Recorded 2026-10-10 from read-only runs against `/Users/kimgranlund/Projects/nonoun/ultimate-tokens`. Spike, no code. Fleet retro 2026-10-09 row 2 and the keep-or-loosen list item 1 asked whether solo-sized chunks would have cut the cost of two L4 tickets. A figure marked [U] is my estimate, not a collector or ticket-record number.

## Verdict

Change the rule, narrowly: let an L3 or L4 ticket run as chunked solo when its plan groups into at most 4 chunks of file-sharing steps and has no step that needs a different model, with one plan review of the whole plan and one ticket verifier. Keep the full chain for L5, merge and cross-component tickets. Estimated saving on these two tickets is 34 to 43 percent of their metered spend, $53 to $68 of $158.69 [U], and 18 to 27 percent even if only per-step verifiers and the L5 builder tier are removed. The follow-up ticket is at the end.

The estimate rests on two things the records do not hold: no solo run is priced, and n is 2. Both tickets were already finished partly by solo chunks after the user chose "big chunks", so the replay moves that choice earlier instead of testing an untried lane.

## Sources and commands

| Figure | Source |
|---|---|
| Fleet totals today: 150 runs, $401.60; by lane full 113 runs $368.19, solo 37 runs $33.42; solo role 21 runs $0.00 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect /Users/kimgranlund/Projects/nonoun/ultimate-tokens --since 2026-10-08` (output kept in `/tmp/t0418-collect.txt`). The ticket quoted full $359.21 from an earlier window; the same command now reports $368.19 because later runs landed |
| The collector gives role and lane totals, not per-ticket dollars | same output, `runs.by_ticket` holds counts only |
| Per-ticket and per-step dollars | `cost_usd` in `.sdlc/match-peer-lightness/runs.jsonl`, `.sdlc/match-peer-lightness/step-*/runs.jsonl`, `.sdlc/ui-standardization/runs.jsonl`, `.sdlc/ui-standardization/step-*/runs.jsonl` (ultimate-tokens, summed by role with a short script over those files) |
| Files per step | `git show --numstat` on each step commit in ultimate-tokens (hashes in the tables) |
| Plan steps and levels | `.sdlc/match-peer-lightness/planner-L3-3.md`, `.sdlc/ui-standardization/planner-L3.md` |
| Lane rule | `plugins/sdlc-lite/scripts/steps.py` `lane` help: before planning L1 and L2 are solo, L3 to L5 are full; after planning any L4 or L5 step adds a plan review |
| Retro text | `.sdlc/fleet-retro-2026-10-09.md` row 1 and `.sdlc/fleet-retro-2026-10-09-12.md` rows for big-chunk solo sessions |
| Price ratio for the tier estimate | `plugins/sdlc-lite/adapters/claude/prices.json`: blended opus 0.99 and fable 3.28 USD per million tokens, usage input opus 3.0 and fable 7.23 |

Every metered row has `cost_estimated: true` with basis `usage fields x rates`, and every `usage.tool_uses` reads 50, so the dollars are estimates and the tool counts are capped. The five T-0040 solo rows and the one T-0044 solo row carry `cost_usd` null (`subagent usage not priced`).

## Ticket totals (metered rows only)

The two tickets are $158.69 of $368.19 full-lane spend (43 percent) and 40 percent of all $401.60 [V, from the sums above].

| Ticket | Architect | Planner | Plan review | Step builders | Step verifiers | Whole-ticket verifier | Metered total | Unmetered |
|---|---|---|---|---|---|---|---|---|
| T-0040 (`match-peer-lightness`) | 5.02 | 20.04 (3 rounds) | 17.60 (3 rounds) | 40.82 | 0.92 | 8.97 | 93.38 | 5 solo runs |
| T-0044 (`ui-standardization`) | 6.46 | 8.28 (1 round) | 6.43 (1 round) | 19.30 | 13.93 | 10.91 | 65.31 | 1 solo run |

Design and review (architect, planner, plan review) are 46 percent of T-0040 ($42.67) and 32 percent of T-0044 ($21.17). Per-step verification is small on T-0040 and 21 percent of T-0044. The T-0040 step 2 L5 builder is $39.24 alone, 42 percent of that ticket.

The chain figures understate true ticket cost: T-0040 steps 3 to 7 and T-0044 steps 9 to 12 were finished by solo runs that no record prices. So "full lane is 77 percent of spend" in the retro compares priced chain rows with unpriced solo rows.

## Per-step table, T-0040

Plan and review cost is ticket level; the per-step share is the planner plus plan-review total ($37.64) split over 7 steps, $5.38 each [U].

| Step | Level | Files touched (commit) | Builder | Verifier | How it finished |
|---|---|---|---|---|---|
| 1 freeze `ramp@1`, register `ramp@2` | L3 | `src/engine/layers.mjs`, `layer-pins.mjs`, `layers/ramp@1.mjs`, `FROZEN.json`, `test/engine/anchor.mjs`, `layers.mjs`, `layer-pins.mjs`, `mode-isolation-gate.mjs`, `test/ui/model.mjs` (2fbb40d1) | 1.58 (L3) | 0.92 (L2) | chain, pass |
| 2 `ramp@2` engine invariants | L5 | `src/engine/tonal.js`, `test/engine/peer-lightness.mjs`, `test/run.mjs`, `scripts/lib/envelope-measure.mjs`, `scripts/report-compute-neutral.mjs`, fixtures (19c6f8a4) | 39.24 (L5, blocked on two plan defects, `step-2.superseded-1/builder-L5.md`) | none | solo continued the uncommitted tree |
| 3 edited kit within 2x of `ramp@1` | L3 | `src/engine/tonal.js` only (1180a2f9) | not in chain | none | solo |
| 4 re-pin npm-test dependents | L3 | `test/engine/anchor.mjs`, `tonal.mjs`, `semantic.mjs`, `exports.mjs`, `chroma-envelope-gate.mjs`, `mode-isolation-gate.mjs`, `peer-lightness.mjs`, `test/ui/headless-boot.mjs`, fixtures (13b96e52) | not in chain | none | solo |
| 5 sweeps read `ramp@2` | L3 | `test/engine/fixtures/mode-isolation.json` (3bc5b924), one report cite (12f1551a); sweep fix later in c2a66824 | not in chain | none | solo |
| 6 opt-in `matchPeerLightness` | L4 | `src/engine/tonal.js`, `layers.mjs`, `src/ui/persist.js`, `model.mjs`, `sections/color.js`, 8 `categories/*.js`, `test/engine/anchor.mjs`, `tonal.mjs`, `peer-lightness.mjs`, `test/ui/persist.mjs`, `headless-boot.mjs`, `test/smoke/smoke.mjs` (a39a472c) | not in chain | none | solo |
| 7 control, ADR, board, gates | L3 | `docs/references/decision-records.md`, `changelog.md`, `knowledge-02-tonal-scale.md`, `docs/reports/2026-10-09-ramp2-extremes.md`, `.claude/skills/color-math/SKILL.md`, `test/smoke/smoke.mjs` (e8c4febf) | not in chain | none | solo |
| Ticket level | | architect 5.02 (fable L1), planner 7.85 + 3.94 + 8.25 (opus L3), plan review 5.67 + 4.76 + 7.18 (fable L1), whole-ticket verifier 8.97 (fable L3, pass) | | | |

Adjacent steps that share files:
- Steps 1, 2, 3: `tonal.js` and the `ramp` layer registry, then the same `peer-lightness.mjs` and generated bundle files. Step 3 is a one-file edit to step 2's file.
- Steps 4, 5: tests and fixtures only, no `src/` edit by the plan's own guard, the same test files as step 2 and step 6.
- Steps 6, 7: `color.js`, `test/smoke/smoke.mjs`, `headless-boot.mjs` and the docs they describe.
- Three chunks: {1, 2, 3}, {4, 5}, {6, 7}. Steps 4 to 7 could be one chunk because step 6 re-edits `anchor.mjs`, `tonal.mjs`, `peer-lightness.mjs` that step 4 re-pinned.

## Per-step table, T-0044

Plan and review share: $14.71 over 12 steps, $1.23 each [U].

| Step | Level | Files touched (commit) | Builder | Verifier | How it finished |
|---|---|---|---|---|---|
| 1 shell roles module | L3 | `src/ui/shell-roles.mjs`, `test/ui/shell-roles.mjs`, `test/run.mjs` (26e6c6be) | 1.22 | 0.49 (L2) | chain |
| 2 role aliases, per-host block | L4 | `src/ui/app.js`, `styles.css`, `scripts/bundle.mjs`, `test/ui/headless-boot.mjs`, `shell-roles.mjs`, `docs/specs/app-shell.md`, inventory (7df5f57d) | 2.76 (L4) | 4.57 (L3) | chain |
| 3 shell text gate | L3 | `test/repo/shell-text.mjs`, `control-text.mjs`, `test/run.mjs`, `.claude/CLAUDE.md`, one skill, inventory (9fdcbacf) | 1.47 | 0.41 | chain |
| 4 frame text | L3 | `src/ui/styles.css`, `test/repo/shell-text.mjs` (5a6bd08e) | 1.84 | 0.43 | chain |
| 5 inspector and story text | L3 | same two files (44102311) | 1.22 | 0.73 | chain, parallel lane |
| 6 dialog text | L3 | same two files (c6b29f12) | 1.66 | 0.47 | chain, parallel lane |
| 7 typography and geometry text | L3 | same two files (77b6011f) | 1.26 | 0.30 | chain, parallel lane |
| 8 control and container anatomy | L4 | `styles.css`, `shell-text.mjs`, `test/repo/ui-polish.mjs`, `test/smoke/smoke.mjs`, inventory (09d58484) | 6.59 (L4, then 1.28 rerun after replan) | 6.53 (L3) | chain stalled twice on a deny-path guard `steps.py widen` could not rewrite (`fleet-retro-2026-10-09.md` row 3); solo finished |
| 9 glyph motion tokens | L3 | `app.js`, `icons.js`, `apply-gate.js`, `sections/color.js`, `typography.js`, `styles.css`, `ui-polish.mjs`, `headless-boot.mjs` (d48f91ce) | not in chain | none | solo |
| 10 product-sm default, smoke matrix | L4 | `app.js`, `overlays/settings.js`, `styles.css`, `test/smoke/smoke.mjs`, `headless-boot.mjs` (9d83b5d5) | not in chain | none | solo |
| 11 ADR, reference page, skills | L2 | `decision-records.md`, `geometry/shell-roles.md`, `component-inventory.md`, two skills (225aa041) | not in chain | none | solo |
| 12 gates green | L3 | no file change (8d83235a) | not in chain | none | solo |
| Ticket level | | architect 6.46 (fable L1), planner 8.28 (opus L3), plan review 6.43 (fable L1, pass), whole-ticket verifier 10.91 (fable L3, pass) | | | |

Adjacent steps that share files:
- Steps 4 to 7 each edit `src/ui/styles.css` and `test/repo/shell-text.mjs`. Running 5, 6, 7 in parallel lanes produced merge conflicts only in the `PENDING` list of `shell-text.mjs` (retro row 7), which one session would not have had.
- Steps 1, 2, 3 share `shell-roles.mjs`, `headless-boot.mjs`, `test/run.mjs`.
- Steps 8, 9, 10 share `styles.css`, `app.js`, `ui-polish.mjs`, `smoke.mjs`, `headless-boot.mjs`.
- Four chunks: {1, 2, 3}, {4, 5, 6, 7}, {8, 9, 10}, {11, 12}.

## What the money was

- An L3 step in the chain costs about $2 (builder $1.2 to $1.8, Sonnet verifier $0.3 to $0.7). Chunking adjacent L3 steps alone saves little.
- The dollars sit in the L4 and L5 handling: the Fable L3 verifier on L4 steps ($4.57 step 2, $6.53 step 8), the three plan reviews and two replans of T-0040 ($17.60 and $12.19), and the L5 builder block ($39.24).
- Blocked runs came from plan defects, not build defects. T-0040 step 2 stopped on a guard that read the value the step changes and a scope list missing two tests; T-0044 step 8 stopped on a guard `widen` could not rewrite. In both cases the plan review had passed or noted the plan (`plan-reviewer-L1-2.md`, `-3.md` pass; `ui-standardization/plan-reviewer-L1.md` pass), so the review did not catch the defect that cost the most. Its first round on T-0040 did return a real replan (`plan-reviewer-L1.md`: step 5 had no scope criterion).

## Saving estimate [U]

Rule: replace the chain's per-step builder and verifier runs with one solo L3 (Opus xhigh) session per chunk and one ticket verifier. A solo session is assumed to cost between 1.0 and 1.5 times the chain builder rows it replaces (premium low and high). The L5 builder is re-priced as Opus at the fitted blended ratio of prices (0.99 over 3.28, usage ratio 3.0 over 7.23): $11.84 to $16.28 instead of $39.24. Solo runs for steps already finished by solo are the same in both worlds and drop out.

| Scenario | What is removed | T-0040 saving | T-0044 saving | Both |
|---|---|---|---|---|
| Low | per-step verifiers, step 8 rerun, L5 builder priced as Opus solo | $23.09 to $28.32 (25 to 30 percent) | $6.21 to $15.21 (9 to 23 percent) | $29.30 to $43.53 (18 to 27 percent of $158.69) |
| Mid | Low plus all plan review (needs: chunks are L3 solo, so no step forces review) | $40.69 to $45.92 (44 to 49 percent) | $12.64 to $21.64 (19 to 33 percent) | $53.32 to $67.55 (34 to 43 percent) |
| High | Mid plus the two T-0040 planner replans (needs: a plan of 3 chunks has fewer guards to get wrong) | $52.88 to $58.11 (57 to 62 percent) | same as Mid | $65.52 to $79.75 (41 to 50 percent) |

Against the whole full-lane spend of $368.19 the Mid case is 14.5 to 18.3 percent, from two tickets. Which scenario holds is open: High assumes the first plan is right, and the T-0040 evidence says a plan of seven guarded steps was not.

## What would be lost

- Independent plan review at L4 and L5. It returned one real replan on T-0040 and passes elsewhere. Mitigation: keep one review of the chunk plan, which costs one row ($4.8 to $7.2 here) and sits between Low and Mid.
- Per-step verification. T-0044 steps 1 to 7 each got a Sonnet L2 verifier at $0.3 to $0.7 that found nothing recorded in the ticket folder; the two Fable L3 step verifiers (steps 2 and 8) caught the step 8 defect cycle. With one ticket verifier a wrong step 2 surfaces at the end, after steps 3 to 12 built on it [U].
- Gate feedback between steps. The solo sessions here skipped the eight full-corpus sweeps locally and CI then failed twice (`fleet-retro-2026-10-09-12.md` row on PR #827), which is a gate-placement failure that chunking neither causes nor fixes; a chunk plan must keep the sweeps in the last chunk's criteria.
- Context risk: one solo carries a chunk's whole design. The T-0040 solo restarted twice after crashes (the solo dispatch brief says so), and `WIP` commits after each green check are the cover.
- Parallel lanes within a ticket (T-0044 steps 5 to 7 saved about 40 minutes by the retro's estimate [U]) give way to one session; that is a wall-time cost this replay does not price.

## Limits

- n is two tickets from one repo, both in the same component family each, chosen by the user after friction.
- Solo cost is the unmeasured term. Every solo row reads `cost_usd` null, so the 1.0 to 1.5 factor is a guess bounded by the chain builder rows ($1.2 to $6.6) and the Opus planner rows ($3.9 to $8.2) in the same repo.
- The tier re-pricing for the L5 builder uses fitted blended rates (`prices.json` states a 35 percent band).
- Duration is 0.0 in the collector for every role, so no time saving is computed.
- Planner and plan-review dollars are ticket level; the per-step shares are equal splits.

## Follow-up ticket text

Title: Chunked solo lane for L3 and L4 tickets: planner groups file-sharing steps, one plan review, one ticket verifier

Type: feature. Size: L3. Priority: P2. Depends: none.

Goal: A ticket of size L3 or L4 whose plan groups into at most 4 chunks of steps that share files can run as one solo L3 session per chunk with a `WIP` commit after each green check, one review of the chunk plan, and one ticket verifier, and the collector prices the solo rows so the saving is measured.

Do:
- Let the planner emit a `Chunk:` line per group of steps that share files and a `chunks: <n>` count; `steps.py lane` prints `solo` with the reason "plan groups into <n> chunks of file-sharing steps, none above L4" after planning when n is at most 4 and no step is L5, and keeps `full` otherwise.
- Price solo sub-agent usage in `dispatch.py record` (the 21 solo rows in ultimate-tokens read `subagent usage not priced`) so `fleet_collect.py` shows solo dollars per ticket.
- Rerun this replay on the next two L3 or L4 tickets that use the lane and record the metered comparison in a dated report.
- Non-goals: changing any model or effort default; L5 or merge tickets.

Done when:
- `steps.py lane` on a fixture plan with 3 chunks prints `solo` and a reason naming the chunk count, and on a plan with an L5 step prints `full`; the fixture is a positive and a negative control.
- A solo run recorded by `dispatch.py record` has a non-null `cost_usd`.
- A dated report compares the chunked run's metered cost with this report's Mid range.
