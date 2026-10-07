---
id: T-0310
title: "fleet.json: the active repo registry and conductor list"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One config file says which repos and conductors are active, so excluding a repo is a setting and not a memory.

## Intent
- Do: Add .sdlc/fleet.json (schema documented in docs/specs/sdlc-lite/, plus a loader in scripts/fleet_config.py with `show`, `add`, `exclude <repo>`, `include <repo>`, `selftest`): entries have path, name, conductor session name, optional gh repo, status active|excluded with a reason and date. Seed it with ui-kit-maison, agent-ui, gen-ui-kit (and sdlc-lite itself) active, maison-testing and native-dom-charts excluded with the 2026-10-06 reason.
- Non-goals: Collection, rendering, messaging conductors.
- Done when:
  - `fleet_config.py selftest` passes; an excluded repo is absent from `show --active` and present in `show` (observed).
  - A malformed file exits 1 naming the line and never silently drops a repo.
  - `check.py` and `tickets.py check` pass.

## Context
Decided by the user on 2026-10-06. Replaces the hand-built status the author session produced about 20 times (a bash loop, grep filters and a composed table). Problems to fix: rows that lie (board says building for work that never started, or verifier fail for merged work), load with no trend or verdict, 'needs you' buried, no since-last delta, hard-coded repo list. Order of the output: Machine, Needs you, Moving (with a liveness mark), Stale or stuck, Done since last report, Release state. sdlc-lite must own the rendering and not depend on the user-scoped harness rag-board skill. Reuses fleet_collect.py (T-0305) for process classes and run totals. Builds after fleet-retro (T-0305 to T-0308); target 0.21.1.

## Constraints
No model call. Read-only on every repo inspected. No em dashes. No change to any model or effort value. No push, tag or publish.

## Closed

2026-10-06: built and merged on the fleet integration branch; verifier passed
