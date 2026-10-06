---
id: T-0283
title: "Launcher skills dispatch through sub-agents"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0282]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The launcher skills and /agent route a role through dispatch instead of run.sh.

## Intent
- Do: Launcher skills dispatch through sub-agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `skills/build`, `plan`, `verify`, `research`, `scout`, `architect`, `dig`, `file`, `agent`, `ticket`, `bench`, `review-traces`, and `sdlc-lite` name the dispatch path for the Claude backend; `git grep -n "scripts/run.sh" plugins/sdlc-lite/skills` finds only Codex-transport or legacy-note lines (list them in the ticket).
  - `check.py` item 25 (agent command names) passes, and a skill that names a role absent from `agents/` fails it (negative control).
  - `python3 scripts/check-packaging.py` and `python3 plugins/sdlc-lite/scripts/check.py` pass.

## Context
Design section 1. Text only; mechanics are in dispatch.py.

## Constraints
No script changes. No em dashes. No push, tag, or publish.
