---
id: T-0581
title: "close --preflight at merge-ready, --reason skip lines, serialized closes"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Closing a ticket holds no surprises. `tickets.py close <slug> --preflight` lists in one pass everything close will demand: verdict, filer, `## Skipped` lines, refs needing `--rewrite-refs` or `--keep-refs`, and open warnings. `--reason` writes the skip lines it needs, and closes take a lock so they run one at a time.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 2. Each close needed a filer run, `## Skipped` lines, `--keep-refs` and `--ack-warnings`, and took about a minute of admission. 21 parallel close dry-runs crashed maison's host (their T-0597 item 20). This repo hit the same `## Skipped` refusal on T-0563 (2026-10-15).

## Intent
- Do: add `--preflight`, read-only, exit 0 with `ready` or exit 1 with one line per missing item; make `--reason` append the `## Skipped` lines its lane needs; and add a repo-level close lock (`.sdlc/runtime/close.lock`, flock) so a second close waits.
- Non-goals: changing what close requires.
- Done when: the criteria pass.

## Constraints
Close output and requirements stay the same apart from these.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new cases show: preflight on a full-lane ticket with no skips.md entry lists it and exits 1; `--reason` on that ticket closes with the skip line written; and two concurrent closes run one after the other (the second reports waiting). The cases failed before the change.
2. `git diff --check` exits 0.
