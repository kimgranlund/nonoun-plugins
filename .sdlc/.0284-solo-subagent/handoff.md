---
id: T-0284
title: "Solo and its verifier run as sub-agents"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0282]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Solo runs as a background sub-agent at its tier, and the batched verifier for tiers M and L is dispatched by the parent after solo returns, which keeps independence in the parent and does not depend on nested spawning (probe P8).

## Intent
- Do: Solo and its verifier run as sub-agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `agents/solo.md` no longer tells solo to run `run.sh verifier`; it ends with a report and the parent runs one `prepare verifier L<n>` at the task dir on another model family (cases in `dispatch.py selftest`: Sonnet solo gets an Opus verifier).
  - `solo_run.py run` for the Claude backend prints the dispatch JSON (it no longer starts `claude -p`) and `solo_run.py` budget-gate behavior (exit 4 at 80 percent, no ack) is preserved by `prepare`; the selftest case for exit 4 passes against `prepare`.
  - `check.py` items 18, 21, 24, 27 pass with the solo tiers agreeing across `agents/solo.md`, `levels.json`, `fanout.SOLO_TIERS`, and the generated `solo-S/M/L`.
  - Codex solo (`codex_exec.py solo L1..L3`) unchanged and its selftest passes.

## Context
Design sections 1, 2, 5.

## Constraints
Tier model and effort values unchanged. No em dashes. No push, tag, or publish.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
