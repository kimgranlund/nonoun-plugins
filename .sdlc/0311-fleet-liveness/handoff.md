---
id: T-0311
title: "fleet_status.py: liveness join, load trend and snapshot"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0305, T-0310]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Collector additions that decide whether each board row is really moving, plus the load trend and a snapshot for the since-last section.

## Intent
- Do: Extend scripts/fleet_collect.py or add scripts/fleet_status.py `collect` with: liveness per ticket row (a live process whose command names the ticket folder or its worktree, a `.running` marker with a live pid, or activity in the last N minutes by file mtime of runs.jsonl and logs; marks `live`, `idle`, `dead` for a marker with no process, `stale` for a board row with none of these); load samples appended to .sdlc/runtime/load.jsonl on every call with a trend (1, 5 and 15 minute loads, direction arrow, cores, verdict against a configurable stop line, default 14), top consumers by class (chromium, hooks, claude, watchers); needs-you extraction from tickets with status blocked and an `owner` found in their notes (user or conductor) and from open PRs waiting on a merge via gh; release state (local main vs origin/main, last tag, unpushed commits); a snapshot file .sdlc/runtime/fleet-status.json and a `delta` since the previous snapshot (rows that changed state, tickets closed, PRs merged).
- Non-goals: Rendering; conductor messaging.
- Done when:
  - Fixture repo: a board row with a live process is `live`; a row with a `.running` marker whose pid is dead is `dead`; a row with no process, marker or recent activity is `stale` (three observed cases, plus the negative control that removing the marker changes `dead` to `stale`).
  - Load: two samples a minute apart give a trend; a load above the stop line gives the `over` verdict.
  - Run on /Users/kimgranlund/Projects/maison/ui-kit-maison flags T-0039, T-0043 and T-0105 as not `live` if no process or recent activity exists for them (compare with the conductor's own audit) and writes no file in that repo.
  - Snapshot delta lists a ticket that closed between two runs.
  - `check.py` and `tickets.py check` pass.

## Context
Decided by the user on 2026-10-06. Replaces the hand-built status the author session produced about 20 times (a bash loop, grep filters and a composed table). Problems to fix: rows that lie (board says building for work that never started, or verifier fail for merged work), load with no trend or verdict, 'needs you' buried, no since-last delta, hard-coded repo list. Order of the output: Machine, Needs you, Moving (with a liveness mark), Stale or stuck, Done since last report, Release state. sdlc-lite must own the rendering and not depend on the user-scoped harness rag-board skill. Reuses fleet_collect.py (T-0305) for process classes and run totals. Builds after fleet-retro (T-0305 to T-0308); target 0.21.1.

## Constraints
No model call. Read-only on every repo inspected. No em dashes. No change to any model or effort value. No push, tag or publish.
