---
id: T-0583
title: "Driver loop wakes on role completion or state change, not timed polling"
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor running a plan or wave wakes when a role finishes or the board changes, not on a timer, so idle "nothing moved" turns go away.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 5. maison's 10-minute check prompts repeated "nothing moved" dozens of times. Claude Code already re-invokes the parent when a background sub-agent finishes. The waste is in timed status loops layered on top. Idea ticket: shape before building.

## Intent
- Do: propose the smallest mechanism, for example a `supervisor.py`/`messages.py` event that the conductor's loop waits on, plus a built-in plan-driver prompt, and the change to `/board` or skill guidance that retires fixed-interval polling.
- Non-goals: building it in this ticket.
- Done when: a design note in the Outcome names the mechanism, the files it touches, and a measurable before/after (turns per wave).

## Constraints
None.

## Acceptance criteria
1. The Outcome holds the design: mechanism, files, and the metric to measure.
