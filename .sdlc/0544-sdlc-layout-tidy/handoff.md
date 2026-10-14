---
id: T-0544
title: "Lean records E: Layout rule and tidy (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0543]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Layout rule and tidy: part E of SDLC Lite 0.23.0 lean work records (wave 4).

## Intent
- Do: build part E of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for E, Interfaces and Risks). Files: `tickets.py` (top-level allow-list `check` warning, `tidy [--apply]`, router `Folder layout` and `Ticket lifecycle` sections, `claim --by <word>` from T-0534), `skills/fleet-retro/{SKILL.md,interview.md}`, `skills/{grill,review-traces,bench}/SKILL.md` (write in the records dir), `onboard.py` "Work records" block :382-391
- Non-goals: the other parts (A to F) of the same design.
- Done when: `tickets.py selftest` exits 0 with: `check` warns on a stray top-level file and stays silent for an allowed name (negative control); `tidy` without `--apply` changes nothing; `tidy --apply` moves the stray file into `archive/` and refuses while a `*.running` marker exists; `claim --by astra` is accepted

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.
