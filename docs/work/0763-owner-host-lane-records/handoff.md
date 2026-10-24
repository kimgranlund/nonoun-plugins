---
id: T-0763
title: "dispatch status and steps next from main see a host lane's records"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
From the main checkout, `dispatch.py status <task dir>` and `steps.py next <task dir>` of a ticket running in a Claude Code host worktree read its records from the host worktree (the owner tree), as they do for a lanes.py or fanout lane (T-0750, T-0755).

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/dispatch.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: from /Users/kimgranlund/Projects/nonoun/live036, `dispatch.py status .sdlc/add-div` printed `no attempts in .../live036/.sdlc/runtime/tasks/add-div` and `steps.py next .sdlc/add-div` exited 1 `no builder result and no .../runtime/tasks/add-div/handoff.md to read a level from`, while the records were in `.claude/worktrees/agent-a05ad66023f64f17f/.sdlc/runtime/tasks/add-div`. Check whether `wtroot.owner_trees` finds the host lane for the ticket (host record under `<lanes root>/host/`, `lanes_root:`), and fix the lookup.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A selftest case (wtroot, dispatch or steps): a ticket whose only lane is a host worktree with a host record; status and next from the primary checkout see its records; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
