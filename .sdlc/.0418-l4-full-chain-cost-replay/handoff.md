---
id: T-0418
title: "Replay solo-sized chunks on ultimate-tokens T-0040 and T-0044 to size the full-chain cost on L4"
type: spike           # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
The exact question this spike answers.

## Goal
A dated report with a verdict on whether solo-sized chunks would have cut the cost of L4 tickets, with numbers from the collector and the ticket records.

## Intent
- Do: spike, no code. Read ultimate-tokens' run records (read only): fleet_collect.py collect /Users/kimgranlund/Projects/nonoun/ultimate-tokens --since 2026-10-08 (runs.by_lane full $359.21, solo $33.42), the T-0040 folder (.sdlc/match-peer-lightness) and the T-0044 folder (.sdlc/ui-standardization), and its retro answer .sdlc/fleet-retro-2026-10-09.md and -12.md. For each step of those two tickets list the files it touched and the cost of its planner, plan-reviewer, builder and verifier runs, and decide which adjacent steps share files and could have been one solo chunk. Estimate the saving per ticket from the solo run costs in the same repo, label every estimate [U], and say what would have been lost (independent plan review at L4/L5, per-step verification). End with a verdict: change the L4 lane rule (and to what), keep it, or measure more, plus the one follow-up ticket it implies.
- Non-goals: changing the lane script or any model or effort default.
- Done when:
  - docs/reports/2026-10-09-l4-full-chain-cost-replay.md exists with the per-step table, the verdict and the follow-up ticket text; every figure cites a file or command; no dashes.
  - docs_check.py and tickets.py check pass.

## Context
Keep-or-loosen list item 1 (plan file /Users/kimgranlund/.claude/plans/inherited-imagining-tulip.md) and fleet retro 2026-10-09 row 2. The maintainer asked for this spike on 2026-10-09.

## Constraints
No em or en dashes. No push or publish. Read-only on every consumer repo.

## Acceptance criteria
- `test -f docs/reports/2026-10-09-l4-full-chain-cost-replay.md && grep -q '^## Verdict' docs/reports/2026-10-09-l4-full-chain-cost-replay.md && grep -q '^## Per-step table, T-0040' docs/reports/2026-10-09-l4-full-chain-cost-replay.md && grep -q '^## Per-step table, T-0044' docs/reports/2026-10-09-l4-full-chain-cost-replay.md && grep -q '^## Follow-up ticket text' docs/reports/2026-10-09-l4-full-chain-cost-replay.md && grep -q '^## What would be lost' docs/reports/2026-10-09-l4-full-chain-cost-replay.md` exits 0.
- `python3 -c "import sys; t=open('docs/reports/2026-10-09-l4-full-chain-cost-replay.md').read(); sys.exit(1 if ('\u2014' in t or '\u2013' in t) else 0)"` exits 0 (no em or en dashes).
- `python3 plugins/sdlc-lite/scripts/docs_check.py` ends `0 errors` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.
- Spot check of figures against the consumer repo (read only): the sums of `cost_usd` over `.sdlc/match-peer-lightness/runs.jsonl` plus `step-*/runs.jsonl` and over the same files in `.sdlc/ui-standardization` equal $93.38 and $65.31 as the report's totals table states.

## Closed

2026-10-10: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
