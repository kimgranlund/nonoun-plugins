---
id: T-0406
title: "plan-campaign skill and plan_check.py campaign (from gen-ui-kit)"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A `plan-campaign` skill returns a wave plan (Wave 0 tool and gate, Wave 1 file-disjoint lanes, Wave 2 bulk review, Wave 3 bulk PRs) plus one `/goal` block, and `plan_check.py campaign` rejects an unsound plan.

## Intent
- Do: build v1 from the brief in this folder (brief.md, from the gen-ui-kit conductor): skills/plan-campaign/SKILL.md modelled on skills/plan-goal and plan-fanout (gather from the repo first, one AskUserQuestion round, a plan that passes the check, one copy/paste output), a references file with the campaign template and the lessons, and `plan_check.py campaign` with the FAIL and WARN rules listed in the brief. v1 scope per the brief: the template plus the partition check (file-disjoint, lane cap, dependency order); the rest may follow. Keep the skill self-contained (check.py item 42). The `/goal` block it returns must pass `plan_check.py goal`. Register the skill the way sibling plan-* skills are (Codex mapping, routes, any index) and run claude_roles.py and codex_roles.py generate if the change needs it.
- Non-goals: editing gen-ui-kit; running a campaign; model or effort changes. Intent, rubric and KPI capture is T-0405 (plan-verification design): leave a one-line pointer in the template where that skill will plug in, do not build it here.
- Done when:
  - plan_check.py selftest has a positive case for the gen-ui-kit page-CSS example from brief.md and an observed-failing negative case for each FAIL rule (no Wave 0 gate; done-when not a command exit on main; overlapping files; lane count over the cap with no reason; no dollar stop rule; unbounded PR count; no dependency order).
  - plan_check.py selftest, check.py, claude_roles.py and codex_roles.py generate --check, scripts/check-packaging.py and tickets.py check pass.

## Context
Build request from the gen-ui-kit conductor, 2026-10-09. Full brief: brief.md in this folder.

## Constraints
No em or en dashes. No push or publish. Edit only this repo.
