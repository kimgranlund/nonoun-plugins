---
id: T-0297
title: "Planner guard dry-run; split inherits earlier widenings"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
(a) The planner contract tells the planner to dry-run each step's `(guard)` commands and confirm they are green at the base before returning. (b) `steps.py split` inherits earlier widenings into later steps' scope allow-lists.

## Context
Agent-ui no-barrels: 12 planner results, because guards diff against the base commit and scope allow-lists omitted paths widened by earlier steps (steps 5 to 8 each blocked once). Files: agents/planner.md (keep generated agents in parity via `codex_roles.py generate`), plugins/sdlc-lite/scripts/steps.py. Smallest observable change for (b): when `split` writes `step-<n>/handoff.md` and an earlier live `step-<m>/handoff.md` (m<n) has a `## Scope widened` section, add those paths to step n's scope allow-list (the forms `widen` recognizes) and list them in step n's own `## Scope widened` section. Full `split` still runs no guards.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with a new case: step 1 widened by path P, then `split --only 2` yields a step 2 scope allow-list containing P and a `## Scope widened` entry; a step 2 with no prior widening is unchanged.
- [ ] Negative control shown once: without the inheritance the case fails.
- [ ] agents/planner.md holds one sentence requiring the dry-run of each `(guard)` at base before returning; `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.
