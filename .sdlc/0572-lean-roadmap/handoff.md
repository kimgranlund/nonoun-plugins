---
id: T-0572
title: "roadmap.md lists open tickets plus a closed count"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0565]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`roadmap.md` stays small: open tickets in order, plus one line counting closed tickets. So it rarely changes, rarely conflicts, and costs an agent little context.

## Intent
- Do:
  1. `tickets.py roadmap` writes open tickets (proposed, ready, claimed, paused, blocked) as today, and replaces the done and dropped list with `Closed: <n> done, <m> dropped (git log or .NNNN-* folders)`.
  2. Every reader of `roadmap.md` that relies on closed rows keeps working. Search `plugins/sdlc-lite/scripts`, `skills` and `agents` for `roadmap.md`, and update whatever parses it.
- Non-goals: router `AGENTS.md` content; the T-0565 merge handling.
- Done when: the criteria pass.

## Context
Gap G3 (2026-10-15): `.sdlc/roadmap.md` is 112 KB and 570 lines, 526 of them closed tickets, and it changed in 633 commits since 2026-10-01. Every lane merge regenerates it. Code: `tickets.py` `write_roadmap`.

## Constraints
Open-ticket ordering and fields are unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new case shows a fixture with 3 done tickets and 1 open ticket: the roadmap has one row for the open ticket and the line `Closed: 3 done, 0 dropped`. The case failed before the change.
2. After `tickets.py --root .sdlc roadmap` in this repo, `wc -c < .sdlc/roadmap.md` is under 10000.
3. `bash plugins/sdlc-lite/scripts/run-selftest.sh` and `git diff --check` exit 0.
