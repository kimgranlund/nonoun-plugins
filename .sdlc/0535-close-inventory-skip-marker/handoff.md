---
id: T-0535
title: "tickets.py close: a marker that excludes an inventory file from the citation scan (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0530]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
tickets.py close: a marker that excludes an inventory file from the citation scan.

## Intent
- Do: a file that lists many ticket folders by path (an audit, a path inventory) can opt out of the close citation scan, by a config key `citation_skip:` (globs under the ticket root) or a first-line marker; pick one and document it in the ticket skill. `close` names skipped files in its note.
- Non-goals: changing `--keep-refs` or `--rewrite-refs`.
- Done when: `tickets.py selftest` passes with a close that succeeds beside a skipped inventory, and the same close refused when the file is not marked (negative control).

## Context
maison T-0546 observations 34: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (section "Added after the author's reply"). Read only; never edit maison.

## Constraints
A new or changed check needs a positive case and an observed negative control.
