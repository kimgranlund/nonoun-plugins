---
id: T-0386
title: "Design review: gate_lock.py as the weighted shared admission authority"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A written design answer for the proposal to extend gate_lock.py into the weighted shared admission authority, with a decision from the maintainer before any implementation.

## Intent
- Do: Review the maison proposal (.sdlc/tickets/0300-shared-resource-lease-design/interface-contract.md, regression-cases.md, author-message.md): one local state namespace per host and OS user across repos and worktrees, atomic vector grants (compute_units and browser_jobs), FIFO within a repo and round robin across repos, authenticated nesting, durable spawn fence and exact process identity, separate wait and execution timing, required mode failing before heavy work. Compare with gate_lock.py as it is (slot count per command under the caller TMPDIR, SDLC_GATE_LOCK_HELD trusted) and with SDLC_GATE_WORKERS. Return an agreed interface or a counter-design with the owner split, in a design document under docs/specs/. The proposed numbers 6 and 3 are NOT approved; calibration comes only from future real runs. Design only; no implementation.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - A design document with the interface, what stays repo-side and what is plugin-side, migration for old plugin paths, and the regression cases it must pass.
  - The maintainer's decision recorded here before any build ticket is filed.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Maison proposal 2026-10-08 (T-0300 design spike). Related maison items: T-0298 (Panda process and lock edges), T-0299 (receipt and preflight), and the load false reds in the fleet retro (load 20 to 57, Phase A 76 minutes). Needs the maintainer's agreement: it moves machine-wide scheduling into the plugin. No response is treated as approval. Source: the maison conductor's delivery check of 2026-10-08 (13 unread messages in the maison repo, .sdlc/messages/new/sdlc-lite-author/; RCA ledger /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/rca-ledger-2026-10-08.md). The user's RCA directive there: fix at the origin; workarounds retire only after an installed proof and a live discriminating rerun.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run live here; mark it unverified.
