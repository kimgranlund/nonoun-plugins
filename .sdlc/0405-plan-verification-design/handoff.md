---
id: T-0405
title: "plan-verification skill design: intent, rubric and KPI capture that plan-goal uses"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A written design for a `plan-verification` skill that captures intent, a rubric and KPIs for a piece of work, and that `plan-goal` calls, with its boundaries against the roles and skills it could duplicate.

## Intent
- Do: design only, Markdown, in docs/specs/sdlc-lite/plan-verification.md with a status line. Read skills/plan-goal (SKILL.md, references/goal-rules.md), scripts/plan_check.py, skills/handoff-format, agents/planner.md, agents/verifier.md, skills/checks-that-bite, skills/fleet-retro/rubric.md, docs/specs/repo-onboarding/goals-and-kpi.md and docs/goals, docs/kpi. Decide and write down: (1) what the skill produces (an outcome block: Outcome and why, Measured by with a KPI id or a runnable command and its before value, a rubric of 3 to 5 criteria with pass thresholds, and one negative control), (2) exactly what it does NOT own (planner steps and acceptance criteria, the verifier verdict, handoff Intent), (3) how plan-goal calls it and what plan_check.py goal then checks (new sections, with a negative control each), (4) whether plan-loop, plan-fanout and ticket use it later, (5) the shared reference file location under the skill so other skills reach it through the plugin root, (6) the build as a separate ticket with its checks, and a migration note for existing goals.
- Non-goals: writing the skill or changing plan_check.py in this ticket; model or effort changes.
- Done when:
  - The design names every file the build changes, the two new plan_check.py goal fail rules and a negative control for each, and the rejected alternatives (extend plan-goal only, tickets only).
  - docs_check.py and check.py pass.

## Context
Maintainer decision 2026-10-09: intent, rubric and KPI capture becomes a new plan-verification skill that plan-goal uses. Finding: plan-goal has no intent or KPI section, its Done-when can be satisfied by closing tickets, and it never reads docs/goals or docs/kpi (T-0392, 0.22.1).

## Constraints
Design only. No em or en dashes. No push or publish. Build waits for its own ticket.

## Acceptance criteria
1. `docs/specs/sdlc-lite/plan-verification.md` exists, begins with a status line (design for review, ticket T-0405) and has no em or en dash: `grep -nP '\x{2014}|\x{2013}' docs/specs/sdlc-lite/plan-verification.md` prints nothing.
2. The design covers items 1 to 6 of the Intent: the outcome block parts (Outcome and why, Measured by with before value, 3 to 5 rubric criteria with pass thresholds, one negative control), what it does not own (planner, verifier, handoff Intent), how plan-goal calls it, plan-loop/plan-fanout/ticket decisions, the shared reference path under the skill, and the build ticket with checks plus migration note.
3. It names every file the build changes (section 7), the two new `plan_check.py goal` fail rules (`outcome-block`, `done-measured`) each with a negative control, and the rejected alternatives (extend plan-goal only, tickets only).
4. `python3 plugins/sdlc-lite/scripts/docs_check.py --root .` exits 0 and `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
5. The document is listed in `docs/README.md`, `docs/specs/sdlc-lite/README.md` and the managed block of `docs/specs/sdlc-lite/AGENTS.md`; no plugin script or skill is changed (`git diff --stat -- plugins` is empty).
