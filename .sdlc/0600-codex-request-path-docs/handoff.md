---
id: T-0600
title: "Codex docs name the ticket folder for solo request files; they land in the records dir"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0600-t0600
worktree: ../sdlc-lite.worktrees/T-0600-t0600
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The Codex docs name the directory where a native solo or verifier request file appears, as the live run found it.

## Intent
- Do:
  1. In `docs/references/codex-role-execution.md` and `plugins/sdlc-lite/adapters/codex/instructions.md`, replace `<ticket folder>/solo-<level>-<attempt>.request.json` and "beside the handoff" with the records dir that `order.py records-dir <ticket folder>` prints (`.sdlc/runtime/tasks/<slug>/` in the T-0570 run).
  2. Regenerate the Codex agents if `instructions.md` feeds them, and run their freshness check.
- Non-goals: moving the request file.
- Done when: the criteria pass.

## Context
The T-0570 live run (codex-cli 0.162.1, report `docs/reports/2026-10-15-codex-live-lane.md`) found `solo-L1-<attempt>.request.json` and `verifier-L1.request.json` under `<lane>/.sdlc/runtime/tasks/greeting/`, not in `<lane>/.sdlc/greeting/`. The Codex conductor's glob on the documented path failed (`zsh:1: no matches found: .sdlc/greeting/solo-L1-*.request.json`) and it found the file by search.

## Constraints
None.

## Acceptance criteria
1. `git grep -n "ticket folder>/solo-" -- docs plugins` prints nothing.
