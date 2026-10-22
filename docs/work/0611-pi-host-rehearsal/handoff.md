---
id: T-0611
title: "Rehearse a Pi host working tickets beside Claude and Codex"
type: chore           # feature | bug | chore | spike | idea
status: blocked      # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
blocked_reason: Pi 0.73.1 installed 2026-10-22 (npm -g @mariozechner/pi-coding-agent); no provider login (~/.pi/agent/auth.json empty, no API key env). The user runs `pi` then `/login` once.
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Evidence that a Pi host can claim, work and signal ready on tickets beside Claude Code and Codex in one repo.

## Context
T-0592 planned a three-host rehearsal; Pi was not installed (`pi` not found), so it ran Claude Code and Codex only (`docs/reports/2026-10-15-two-host-rehearsal.md`). Pi has no `run.sh` backend; drive it as a mailbox worker in its own session. The two-host run showed the claim race, lanes, ready, cross-family verify, finish and close working; repeat the same script with Pi as a third host.

## Intent
- Do: install Pi, then repeat the T-0592 rehearsal with three hosts and three tickets in a throwaway repo: all three race one claim, each takes one ticket through `lanes.py open` and `ready`, the conductor verifies with a different family each time, finishes and closes. Write a dated report and file each failure as a ticket.
- Non-goals: fixing failures here.
- Done when: the criteria pass.

## Constraints
Throwaway repo only. No push.

## Acceptance criteria
1. The report exists and shows exactly one host winning the shared claim and all three tickets `status: done` in main, or names the ticket filed for each failure.

## Deferred
2026-10-22: paused by the maintainer ("Keep holding"): it needs the Pi host installed and logged in, which waits for the user.
2026-10-22 05:45 PDT: user approved install; installed Pi 0.73.1. `pi -p` fails for anthropic and openai-codex with no credentials; login is interactive OAuth.
