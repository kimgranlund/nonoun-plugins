---
id: T-0542
title: "Lean records C: Fanout carries records by copy (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0540]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Fanout carries records by copy: part C of SDLC Lite 0.23.0 lean work records (wave 2).

## Intent
- Do: build part C of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for C, Interfaces and Risks). Files: `fanout.py` (`commit_lane_records` becomes a copy; `branch_verdict` and `host_branch_ticket` read the lane worktree's records dir, else git objects; the :1574 copy condition no longer keys on `filer-L*.md`; the :1199-1213 copy includes the records dir; the close commit untracks ignored records; integration records are copied to the main checkout's runtime; headless prompt :446-450 drops the filer), `lanes.py` (`copy_sdlc` archive includes `runtime/tasks/<name>`), `skills/fanout/SKILL.md`. An external lane with no worktree delivers its verdict by committing the verifier result into the ticket folder with `git add -f`, which is the prefix the git-objects fallback reads, and land untracks it in the close commit
- Non-goals: the other parts (A to F) of the same design.
- Done when: `fanout.py selftest` exits 0 with a land whose close commit tracks only `handoff.md` under the ticket folder, and a branch with no worktree still lands from git objects. Negative control: with the copy step removed, land reports `no verifier result`

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.
