---
id: T-0650
title: "Aggregate recurring Rule gap findings into a guidance ticket proposal"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0649]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A guidance gap that ui-designer reviews report in 3 or more tickets surfaces as one proposed guidance ticket, so a recurring defect class becomes a repo skill rule instead of a fresh finding in every ticket.

## Intent
- Do: (1) A new `guidance-gap` detector in `plugins/sdlc-lite/scripts/traces/detectors/plan.py`: over ui-designer result rows, read each `Rule: gap (proposed: "<text>")` item (from `## Guidance gaps`, else `## Findings`), group by the normalized proposed text (lowercase, whitespace collapsed, trailing punctuation stripped), and emit one finding per group seen in at least `guidance_gap_tickets` distinct tickets, layer `project`, evidence one result path and line per ticket. (2) `plugins/sdlc-lite/scripts/traces/detectors/thresholds.py` gains `guidance_gap_tickets: 3` and a severity entry; `docs/references/sdlc-internals.md` thresholds table lists it. (3) `plugins/sdlc-lite/skills/review-traces/SKILL.md` stage 5: a `guidance-gap` finding skips diagnose and verify (it is mechanical) and is offered in the same AskUserQuestion round as a `chore` ticket in the reviewed repo whose Goal names the proposed rule and the skill to add it to; headless runs write it to `report.md`.
- Non-goals: aggregation inside `tickets.py close` (one cross-ticket reader is enough; `close` sees one ticket). Fuzzy or semantic grouping of differently worded gaps. Writing the rule into any skill.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #12, ui-kit-neue audit 2026-10-20. This ticket is part b (cross-ticket rollup of `Rule: gap` items); part a, T-0649, defines the `Rule: gap (proposed: "...")` finding form and the `## Guidance gaps` section this detector reads.
- In ui-kit-neue, forced-colors defects recurred in 15 tickets and RTL defects in 13, and no skill held a rule for either; 9 of 386 review findings cited a rule.
- Confirmed in this repo: detector families live in `plugins/sdlc-lite/scripts/traces/detectors/` (`plan.py:196` `DETECTORS`, `plan.py:199` `detect`); rows carry `ticket`, `role`, and `sources` (`plugins/sdlc-lite/scripts/traces/table.py:23-25`); `escalation._result` and `_row_dir` (`plugins/sdlc-lite/scripts/traces/detectors/escalation.py:131,139`) open a row's result file. Every number lives in `thresholds.py` (`THRESHOLDS`, `plugins/sdlc-lite/scripts/traces/detectors/thresholds.py:10`).
- Findings take a layer from `LAYERS` (`plugins/sdlc-lite/scripts/traces/findings.py:31`, includes `project`). `review-traces` keeps only sdlc-lite layer findings for verify and sends the rest to `report.md` unfiled (`plugins/sdlc-lite/skills/review-traces/SKILL.md:52,116`), so stage 5 needs the explicit `guidance-gap` route.
- `traces.py selftest -k plan` runs one family (`docs/references/sdlc-internals.md:203`).

## Constraints
Existing plan-family detectors and their findings are unchanged. Stages 1 and 2 of review-traces stay model-free. Nothing is filed without the approval round.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/traces.py selftest` exits 0 with new cases: three ui-designer results in three tickets carrying the same proposed gap (one differing only in case and spacing) produce one `guidance-gap` finding with three evidence entries; the same gap in two tickets produces none; two gaps in one ticket count once. The three-ticket case fails with the detector removed from `DETECTORS`.
2. `grep -n 'guidance_gap_tickets' plugins/sdlc-lite/scripts/traces/detectors/thresholds.py docs/references/sdlc-internals.md` finds both.
3. `grep -n 'guidance-gap' plugins/sdlc-lite/skills/review-traces/SKILL.md` finds the stage 5 route.
4. `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0.
