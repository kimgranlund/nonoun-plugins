---
id: T-0534
title: "A layout rule for the top of .sdlc, any agent name in claims, and one ticket lifecycle page (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0530]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A layout rule for the top of .sdlc, any agent name in claims, and one ticket lifecycle page.

## Intent
- Do: the generated router block (`ROUTER_PROCEDURES` in `tickets.py`) gains a short `Folder layout` list of what may sit at the top of the ticket root (ticket folders, `roadmap.md`, `notes.md`, `config`, `AGENTS.md`, `CLAUDE.md`, `messages/`, `evals/`, `proposals/`, `runtime/`, `goals/`) and where everything else goes. `tickets.py check` warns on any other top-level entry, with a config key to allow extra names.
- Do: the claim text and `claim --by` accept any one lowercase word as the agent name, not only claude or codex.
- Do: one `Ticket lifecycle` section in the router block or a linked plugin page: pick and claim, lane, build, verify, land, close, each with its command.
- Do: say in that page that a file under the ticket root that a running role uses must not be moved while any `*.running` marker exists; `check` prints the running markers so a cleanup can see them.
- Non-goals: moving any consumer file.
- Done when: `tickets.py selftest` passes with a stray top-level file warned (and an allowed name not warned, negative control), and `claim --by astra` accepted.

## Context
maison T-0546 observations 33, 41, 42: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (section "Added after the author's reply"). Read only; never edit maison.

## Constraints
A new or changed check needs a positive case and an observed negative control.

## Closed

2026-10-13: merged into T-0544 (layout rule, tidy, claim names, lifecycle page) by the T-0539 design
