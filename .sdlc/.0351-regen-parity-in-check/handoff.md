---
id: T-0351
title: "check.py guards Codex generated-agent parity so a source edit without regenerate fails the normal gate"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Verifier finding 2: T-0344 edited agents/conductor.md without regenerating the Codex conductor TOML and check.py passed

## Intent
- Do: Verifier finding 2: T-0344 edited agents/conductor.md without regenerating the Codex conductor TOML and check.py passed. Add a check.py guard that runs the generate --check equivalents for both Claude and Codex definitions (or compares source hash stamps) so the default gate fails on drift, with a planted-edit negative control observed failing. Fix the verify-folder docs_check B-2a warnings too: record folders .sdlc/verify-* are known record folders for docs_check (or live under a recognized name), 13 warnings go back to 11.
- Non-goals: model or effort changes; anything outside the named scripts and skills.
- Done when:
  - check.py fails when an agent source is edited without regenerating, and docs_check stops warning on .sdlc/verify-* record folders (observed, failing on the current main first).
  - check.py, tickets.py check, fanout, dispatch and solo_run selftests and `codex_roles.py generate --check` pass.

## Context
Independent verifier verdict on T-0343 to T-0348 (.sdlc/verify-maisonfix/verdict.md, Fable, 2026-10-07), findings numbered there.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
