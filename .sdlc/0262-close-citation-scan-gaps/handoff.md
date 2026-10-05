---
id: T-0262
title: "tickets.py close needs --force on tracked citations and cannot see .sdlc citations"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py close` explains citation refusals better and sees `.sdlc` citations.

## Context
Two gaps. 1) close refuses when tracked files cite the folder and needs `--force`. 2) The citation scan cannot see citations under `.sdlc`, so 14 links broke silently on a close. Evidence: conductor report, 0.20.8 field use.
Read the ticket skill's close and `--rewrite-refs` text before editing.

## Constraints
No push, tag, version bump, or publish. No em dashes.
