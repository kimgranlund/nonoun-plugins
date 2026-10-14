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

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0; its T-0544 cases cover the `check` warning on a stray top-level file with an allowed name and a `top_level_allow:` glob silent (negative control), `tidy` without `--apply` leaving the tree identical, `tidy --apply` moving the stray into `archive/`, refusing while a `*.running` marker exists and when the destination exists, and `claim --by astra` accepted.
2. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0 (the regenerated `.sdlc/AGENTS.md` router with the Folder layout and Ticket lifecycle sections is current).
3. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0 with the updated Work records block.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `python3 scripts/check-packaging.py` exits 0.
5. The grill, review-traces, bench and fleet-retro skills write their work files in the records dir that `order.py records-dir` prints and the fleet-retro interview answer goes by `messages.py send`: `git grep -n -F -e ".sdlc/fleet-retro-<date>.md" -e "<review task>/cluster" -e "<slug>/design.md" -- plugins/sdlc-lite/skills` exits 1.
