---
id: T-0277
title: "dispatch.py prepare: the pre-launch half of run.sh"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0276]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prepare <role> <level> <handoff>` runs every gate and decision `run.sh` makes before launching a role and prints a dispatch JSON the conductor passes to the Agent tool.

## Intent
- Do: dispatch.py prepare: the pre-launch half of run.sh.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - For every `role:level` row and a set of fixtures (builder newest in step dir, verifier at a task dir, plan-reviewer after an Opus planner), `prepare` prints the same model, effort, and result name as `SDLC_DRY_RUN=1 run.sh` (a parity selftest in `dispatch.py selftest`).
  - `prepare` refuses with the same exit codes as run.sh: 2 for goal precheck, specgate, preflight; 4 for the budget gate; 5 for the lane gate unless `SDLC_LANE_OVERRIDE` is set; each has a refusal case plus a negative control (the gate removed lets the bad input through).
  - It writes `<name>.attempt.json` (status running, `transport: subagent`, parent pid) and `<name>.dispatch.json` (subagent_type, model, effort, name, result path, tmp prefix, base sha, brief text); the verifier and plan-reviewer family rules read `model=` from result headers exactly as run.sh does.
  - A second `prepare` on a handoff dir with a running attempt refuses (the lock replacement), and a dead-parent attempt is recovered first.
  - `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` and `bash plugins/sdlc-lite/scripts/run-selftest.sh` both pass; run.sh is not edited.

## Context
Design sections 1, 2, 3. Reuse `order.py`, `steps.py`, `specgate.py`, `budget.py`, `readiness.py` by import or subprocess; do not copy them. The brief text is the run.sh prompt (Handoff, Artifacts dir, result path, output format sentence) plus the tree and tmp prefix lines.

## Constraints
run.sh behavior unchanged; Codex paths untouched. No em dashes. No push, tag, or publish.
