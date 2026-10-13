---
id: T-0538
title: "Role brief: the result header is added at record time, and cleanup under the tmp prefix is allowed (maison T-0546)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Role brief: the result header is added at record time, and cleanup under the tmp prefix is allowed.

## Intent
- Do: the brief or the role bodies say that the `<!-- role=... -->` header is added by `record`, so a role that validates its own result file passes `results.py validate` without it, or `validate` gets a flag the brief names. Pick one and keep one statement of it.
- Do: reproduce the denial of removing scratch output under the brief's tmp prefix (find the hook or permission that refuses it in `plugins/sdlc-lite/hooks/`), then make the hook and the brief agree.
- Non-goals: widening role write access beyond the tmp prefix.
- Done when: the hook selftest has a case where a read-only role removes a file under its tmp prefix (allowed) and one outside it (refused), and `results.py selftest` covers the header rule.

## Context
maison T-0546 observations 39, 40: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (section "Added after the author's reply"). Read only; never edit maison.

## Constraints
A new or changed check needs a positive case and an observed negative control.
