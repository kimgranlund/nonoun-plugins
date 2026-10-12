---
id: T-0457
title: "steps.py lint refuses cited paths a step will create and paths from another repo"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lint` accepts a plan whose step names a file the step itself will create, and a path that belongs to another repository, while still refusing a cited path that should exist and does not.

## Intent
- Do: in the cited-path rule of `plugins/sdlc-lite/scripts/steps.py`, skip (1) a path listed as a step output or declared future (a path in the step's `### Do` as a create target, an `Outputs` line, or a `[creates: <path>]` marker, and a path inside a `(red)` criterion code span that only runs after the build), and (2) an absolute path outside the repository or a path prefixed with another repo's name given in a `Context` line; keep refusing a cited repo path that is missing and is neither a declared output nor foreign. Update the planner and handoff-format guidance with the marker. Selftest cases with an observed-red control each: a created file passes, a foreign path passes, a missing cited file still fails.
- Non-goals: the circular-criteria rule (T-0430), the placeholder regex (T-0404); any change to what counts as a cited path elsewhere.
- Done when: `steps.py selftest` exits 0 with the three controls observed red before the change; `check.sh` exits 0.
- outcome metric: `refusals.jsonl` lines with `cited path` text in a fleet retro window, before: 2 in this repo for T-0450 (2026-10-11) and 1 reported by ui-kit-maison (retro 12h row 7)

## Context
Evidence: `.sdlc/0450-review-traces-solo-fails-and-blocks/refusals.jsonl` (the T-0450 builder dispatch was refused because the step cites `.sdlc/0450-review-traces-solo-fails-and-blocks/sample.py`, a script it was to create, and `.sdlc/tickets/`, a ui-kit-maison path); `docs/reports/2026-10-11-fleet-retro-12.md` row 7 ("`steps.py lint` refuses cited paths a step will create", about 10 minutes, maison). Two repos, same mechanism.

## Constraints
No model or effort change. The rule must stay able to fail: a cited existing-path typo is still refused.
