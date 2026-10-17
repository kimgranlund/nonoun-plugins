---
id: T-0582
title: "Plan criteria replayed on main; criterion-only fixes amend without spending the replan"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A plan's acceptance criteria survive contact with current main. The plan reviewer replays each criterion's check command against current main. A finding tagged `criterion-only` (a fact mismatch: a moved path, a deleted file, wrong gate-log logic) is fixed by a logged in-place amend that does not spend the one replan; the replan cap counts design replans only.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, items 1 and 3. Three of four maison W1 stops were criteria that did not match main (a file T-0510 deleted, gate-log logic, a stale-proof path), costing about 2 h and 3 user questions. Each review round on a long integration plan costs about 45 min, and the second replan stopped for one criterion. 0.22.7 routes fact mismatches after the replan to the user. `steps.py amend` already allows one criterion amend per step.

## Intent
- Do: (1) plan-reviewer agent and skill text: replay each criterion's command on current main and tag fact-only findings `criterion-only`; (2) `steps.py` routes a `criterion-only` finding to `amend` even after the replan is used, logging it, while design findings keep the cap; (3) planner guidance: outcome-shaped criteria with a check command.
- Non-goals: raising the design replan cap.
- Done when: the criteria pass.

## Constraints
Maintainer decision 2026-10-15 to file this. Independent verification and the design-replan cap stay. Each amend is recorded.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0. Its new cases show a `criterion-only` finding after the replan routes to `amend`, while a design finding after the replan still routes to the user. The cases failed before the change.
2. `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `codex_roles.py generate --check` exit 0.
3. `git diff --check` exits 0.
