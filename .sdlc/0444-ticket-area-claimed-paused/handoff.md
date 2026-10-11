---
id: T-0444
title: "Ticket vocabulary: add area, status claimed and status paused"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ticket can carry a domain `area:`, and its status can say `claimed` and `paused`, with the roadmap, board and tracker mapping showing them.

## Intent
- Do: (1) `area:` front-matter field, free text from a list kept in `.sdlc/config` (`areas: ui-kit, front-end, back-end, data-lake, agent-os`), validated by `tickets.py check`, shown in `roadmap` and `/board`, and kept distinct from a worktree lane (`lane/<ticket>-<slug>`); (2) `status: claimed` set when a `claimed_by:` line is added (and cleared on release), and `status: paused` with a one-line `paused_reason:`; both accepted by `tickets.py`, `roadmap` stages, `steps.py`, `board`, `fleet_status.py` and `fleet_collect.py` counters; (3) a mapping table to Linear and GitHub (status to state or label, area to label or team, size L1 to L4 to estimate) in the lane lifecycle spec section 8.1 or a new reference; (4) a `tickets.py migrate` or a no-migration statement for existing tickets (absent `area` is valid; existing statuses stay valid).
- Non-goals: renaming size L1 to L4 to xs to xl (size is the model level, see `skills/level-rubric`); changing model or effort rows; building any Linear or GitHub integration beyond the mapping text.
- Done when: selftests for each new field and status with a negative control (an unknown area, a `paused` with no reason, and `claimed` with no `claimed_by` are rejected), `tickets.py roadmap` shows the new values, `check.sh` exits 0, and the README or `.sdlc/AGENTS.md` managed block lists the vocabulary.

## Context
Today: status is `proposed | ready | blocked | done | dropped`; a claim is a `claimed_by: <who> <date>` line and progress shows only on `/board`; size is `L1` to `L4` (`L5` reserved) and doubles as the model level; priority `P1 | P2 | P3`; type `feature | bug | chore | spike | idea`. Files: `plugins/sdlc-lite/scripts/tickets.py`, `steps.py`, `fleet_status.py`, `fleet_collect.py`, `.sdlc/AGENTS.md` (router, generated block), `skills/*` ticket and file skills. Related: lane lifecycle spec section 8.1 (every lane has a ticket), T-0422.

## Constraints
Existing tickets stay valid with no migration required. Keep the status set small; do not add a status the board cannot show. No model or effort change.
