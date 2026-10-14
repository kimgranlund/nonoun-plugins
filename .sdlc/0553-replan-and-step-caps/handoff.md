---
id: T-0553
title: "Hard gates: a third planner run and an oversized plan stop for the person"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ticket cannot loop: the third planner run on a ticket, and a plan with more steps than its level allows, are refused until the person approves, on both hosts.

## Intent
- Do: `dispatch.py prepare planner ...` (and `run.sh planner`, which Codex uses) refuses when the ticket's records already hold two planner results (the first plan plus the one allowed replan), printing the count and the approval flag. `--approved "<who: why>"` lets it through and records the approval in the ticket's records. Step handoffs written by `steps.py split` are not planner runs and do not count.
- Do: `steps.py lint` (run before split) refuses a plan whose step count exceeds the cap for the ticket's `size:` level: L1 and L2 3 steps, L3 6, L4 10, L5 15. The message says to split the ticket or get approval; `--approved` lets it through the same way.
- Do: the conductor, `/chain` and `/fix` contracts say what to do on either refusal: stop and ask the person with one AskUserQuestion (split the ticket, approve one more replan, or drop scope); headless runs stop with status `blocked` naming the cap.
- Non-goals: changing the plan-reviewer rules; cleaning up Codex lock files (left to T-0550's sweep, maintainer decision 2026-10-14).
- Done when: selftests show a third planner prepare refused and allowed with `--approved`, a 7-step L3 plan refused by lint and a 6-step one passed (negative controls observed red); `check.sh`, `claude_roles.py generate --check` and packaging pass.

## Context
Maintainer request 2026-10-14 after maison `.sdlc/tickets/0541-app-shell-reference-closeout` (L3): 22 planner results, 4 plan reviews, 25 steps, 36 builder and 34 verifier runs, 97 runs, 7.7 agent-hours, 964 files (7.2 MB), still open. The rule "replan at most once, then ask" exists only as prose (repo AGENTS.md, chain skill), so nothing stopped the loop. Caps chosen with the maintainer: L1-L2 3, L3 6, L4 10, L5 15.

## Constraints
Ships in 0.23.0. The failing selftests land before or with the gates.
