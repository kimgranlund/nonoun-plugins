---
id: T-0417
title: "Measure verifier minutes and decide on a delta verifier"
type: spike           # feature | bug | chore | spike | idea
status: done
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0411]
created: 2026-10-09
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
The exact question this spike answers.

## Goal
Measure verifier minutes and decide on a delta verifier. Serves goal G-002 (docs/goals/002-restart-and-blocked-run-cost.md); spec: docs/specs/sdlc-lite/restart-and-blocked-run-plan.md; plan step 7 in .sdlc/plan-reliability-docs/plan.md.

## Intent
Ticket: spike, size L1, candidate 7 of the spec (section 7). Depends on: step 1 (it reads `attempts.by_role`). Measurement only: no code changes.

Run `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since <date>` (read-only; about 90 s per repository on this host) for ultimate-tokens, ui-kit-maison and agent-ui over the last full retro window, and read `attempts.by_role.verifier`. From the same repositories' attempt records, count re-verifies: second and later verifier attempts in one handoff dir, and their minutes. Write `docs/reports/<YYYY-MM-DD>-verifier-minutes.md` (the build date): the commands run, a table per repository (verifier count, median and max minutes, re-verify count and share of verifier minutes), and a last line exactly `Verdict: build a delta verifier` when re-verifies take 25 percent or more of verifier minutes in ultimate-tokens or agent-ui, else `Verdict: do not build a delta verifier`. Report maison's share beside them as the control the spec names (its rounds came from unmet prerequisites, not fixes) and do not let it decide the verdict. If the verdict is build, the report proposes a verifier-minutes KPI in one line; it files nothing and adds no `docs/kpi/` file. Validation scope: `docs_check.py`.

## Read first
- `docs/reports/AGENTS.md`

## Done when
- (red) `ls docs/reports | grep -qxE '[0-9]{4}-[0-9]{2}-[0-9]{2}-verifier-minutes\.md'`
- (red) `for t in 'fleet_collect.py collect' ultimate-tokens ui-kit-maison; do cat docs/reports/*-verifier-minutes.md | grep -qF "$t" || exit 1; done`
- (red) `cat docs/reports/*-verifier-minutes.md | grep -qxE 'Verdict: (build a delta verifier|do not build a delta verifier)'`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'docs/reports/[0-9]{4}-[0-9]{2}-[0-9]{2}-verifier-minutes\.md')"`

## Context
Planner L3 output for the 2026-10-09 retros. KPIs: K-002 restart recovery minutes, K-003 blocked builders per wave, K-004 unsatisfiable criteria caught. The spec marks which candidates may already be fixed or need diagnosis first; follow it.

## Constraints
No em or en dashes. No push or publish. The plan step is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Closed

2026-10-10: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
