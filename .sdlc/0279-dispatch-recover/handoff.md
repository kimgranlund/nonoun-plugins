---
id: T-0279
title: "dispatch.py status and resume for dead or interrupted sub-agents"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0278]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Detect a dispatch whose parent died or whose agent never reported, and print the resume ladder: SendMessage by name, by id, then a new attempt.

## Intent
- Do: dispatch.py status and resume for dead or interrupted sub-agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `dispatch.py status <dir>` prints each attempt with `running`, `completed`, `failed`, or `orphaned`; a fixture with a running attempt whose parent pid is dead and no result prints `orphaned`, and one whose parent pid is alive prints `running` (negative control).
  - `dispatch.py resume <name>` for an orphan prints, in order, a `SendMessage` line (name and id), then the new-attempt command with a brief addendum naming the transcript path and `git status` as the first step; it never replays an old report.
  - `dispatch.py recover <dir>` marks orphaned attempts `interrupted` with the same recovery text as `run_lifecycle.py recover`, and `prepare` calls it for a dead-parent attempt.
  - `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` passes.

## Context
Design section 6. Parent liveness is the claude pid recorded by `prepare` (walk the process parents), not file mtimes.

## Constraints
None. No em dashes. No push, tag, or publish.
