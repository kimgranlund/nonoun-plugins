---
id: T-0580
title: "Handover and cleanup can strand unique work on snapshot refs or dangling commits"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
No cleanup or handover strands unique work. `tickets.py claim --handover` pins the ticket's branch tip as `refs/archive/<date>/<branch>` first, and `lanes.py orphans` lists snapshot refs and dangling commits that hold work not on any branch.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 8. A Codex archive cleanup emptied maison's worktrees. The only copies of T-0470 and T-0518 sat on a snapshot ref and a dangling commit (their `0602-post7b-inventory/architect-L1.md` Q4). The Lanes rule already says to keep a branch reachable as `refs/archive/<date>/<branch>` before removal.

## Intent
- Do:
  1. `claim --handover` pins the branch before reassigning.
  2. New `lanes.py orphans` (read-only) lists `refs/archive/*`, other non-branch refs and `git fsck --lost-found`-style dangling commits whose patch is not on the default branch or any local branch, one line each with sha, ref or `dangling`, subject and changed-file count.
- Non-goals: deleting or restoring anything.
- Done when: the criteria pass.

## Constraints
`orphans` changes nothing in the repo.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0. Its new case shows a fixture with a dangling commit holding a unique change and a snapshot ref whose change is already on main: `orphans` lists the first and not the second. The case failed before (no command).
2. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its handover case shows the archive ref exists after `claim --handover`.
3. `git diff --check` exits 0.
