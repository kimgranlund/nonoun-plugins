---
id: T-0219
title: "Skips guard covers lane solo and full"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The skips guard in tickets.py covers a done ticket whose last lane is solo or full.

## Intent
- Do: `skip_missing` now checks lanes solo, lean, fix and full. A solo ticket needs `## Skipped` entries for planner and filer (it has no steps); a full ticket needs the planner, per-step verifier and filer results or entries. No skips.md or no lane record stays exempt, and open tickets are not checked. The old lean-then-full selftest case now uses full-chain results on purpose. Docs in tickets.py and skills/handoff-format/SKILL.md updated; four new selftest cases.
- Non-goals: model or effort defaults; a version bump, tag, push, or publish.
- Done when: the change is merged into local main with checks green and an independent verifier passed.

## Context
Closes a known limit listed in docs/reports/release-0.20.5.md. Built under the burn-down rules (one handwritten step, one L2 verifier).

## Evidence
Independent L2 verifier: pass (`.sdlc/verify-0219/step-1/verifier-L2.md`). It confirmed the mutation (guard tuple reverted) makes the selftest fail and that `tickets.py --root .sdlc check` still passes on the repo's real tickets. Limit: a solo ticket's independent batched verifier is not required by this guard.

## Constraints
None beyond the repository guidance.

## Closed

2026-10-04: Built and verified on branch limits (L2 verifier pass, evidence in the ticket); merged into local main in the limits merge.
