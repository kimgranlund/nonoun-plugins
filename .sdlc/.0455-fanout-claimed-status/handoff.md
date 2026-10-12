---
id: T-0455
title: "fanout prep and run-plan rules set status: claimed with claimed_by"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0452]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A fanout or run-plan claim sets `status: claimed` together with `claimed_by:`, so the roadmap and board show claimed lanes.

## Intent
- Do: in `fanout.py prep` and the run-plan rules (`plugins/sdlc-lite/skills/run-plan/references/run-rules.md`), set `status: claimed` when `claimed_by:` is added, using the T-0444 vocabulary; release (a stop or a close) leaves the status valid; a selftest case with a negative control.
- Non-goals: other status values; the board layout.
- Done when: the selftest passes with an observed red before the change; `check.sh` exits 0.

## Context
Design (approved by the maintainer 2026-10-11, build A to D as a chain): `docs/specs/sdlc-lite/lane-lifecycle.md`, especially section 13 (ticket table), section 7 (the landed test and truth table), section 8 (who calls close) and section 8.1 (every lane has a ticket, tracker-agnostic). Interim lane guidance now in `plugins/sdlc-lite/AGENTS.md` (Lanes). Maintainer tool `~/.claude/lane/sweep.py` is the logic to port. Shared hot files (`check.sh`, `check.py`, `fanout.py`): one writer at a time.

## Constraints
No model or effort change. Never delete unmerged work; archive ref `refs/archive/<date>/<branch>` before any removal. A locked worktree is a running lane. No push, tag or publish. Read-only against any repo it does not own.

## Closed

2026-10-12: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
