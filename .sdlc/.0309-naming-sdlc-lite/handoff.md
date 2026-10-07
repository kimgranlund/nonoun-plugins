---
id: T-0309
title: "Name the product SDLC Lite and rename docs/lean-sdlc to docs/specs/sdlc-lite"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Name the product `SDLC Lite` everywhere in prose and rename the design hub docs/lean-sdlc/ to docs/specs/sdlc-lite/, with a check guard so the old variants do not return.

## Intent
- Do: 'Lean SDLC' and 'lean SDLC' become 'SDLC Lite'; bare 'SDLC' meaning this product becomes 'SDLC Lite'; rename the hub with rename_refs.py; add a three-line vocabulary note to the hub README; add a check.py guard on 'Lean SDLC', 'lean SDLC', 'SDLC-Lite', 'sdlc lite' outside an allowlist.
- Non-goals: identifiers (`sdlc-lite`, `SDLC_*`, `.sdlc/`), model or effort values, managed block text in onboard.py and router blocks in tickets.py, dated evidence (docs/reports, closed tickets, bench/results, run workspaces under .sdlc/), tags and release pages. 'lean lane' and the '## Lean chain' heading stay.
- Done when: guard passes with a negative control, links not increased, all listed checks green, one independent verifier passes, record docs/reports/naming-sdlc-lite.md written.

## Context
Method and allowlist pattern: docs/reports/rename-validation-to-reports.md. Lane: solo.

## Constraints
Mechanical diff only; other branches are in flight.

## Closed

2026-10-06: Solo lane; verifier L3 (fable) pass, all criteria; full check.sh green from a /tmp clone; see docs/reports/naming-sdlc-lite.md
