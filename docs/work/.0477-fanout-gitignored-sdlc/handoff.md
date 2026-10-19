---
id: T-0477
title: "fanout copies an uncommitted ticket folder into fanout-owned lane worktrees (T-0470 finding 8)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py run` copies an uncommitted, gitignored ticket folder (handoff and plan) into each fanout-owned lane worktree instead of refusing.

## Repro
In a repo with `.sdlc/` gitignored, run `fanout.py run` on a ticket whose `handoff.md` is uncommitted.

## Expected
The lane starts with the handoff copied in.

## Actual
`not committed at <sha>` (`fanout.py:825-829`, `:1116-1121`).

## Context
Origin: T-0470 investigation, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Report item 8. Precedent: `.sdlc/config` is copied untracked into each lane (`fanout.py:1108-1115`). Red check: a `fanout.py selftest` case with a gitignored handoff. The host-lane half (`fanout.py prep <name>=<id>`, `fanout.py:1826`) needs a design line (brief names the primary checkout handoff path; `dispatch.py prepare --tree` supports it) and is out of this ticket.

## Constraints
The failing test lands before or with the fix, with an observed-red control. No prompt wording change.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, including case 20b: a repo with `.sdlc/` gitignored and an uncommitted `handoff.md` and `plan.md` runs `fanout.py run alpha=T-0001` to a merged row, with a driver that fails unless `plan.md` is in the lane worktree.
- [ ] An uncommitted handoff in a repo that does not ignore `.sdlc/` is still refused (`not committed at`, case 20), and `fanout.py prep` still refuses a gitignored uncommitted handoff (case 22).
- [ ] `git diff` touches only `plugins/sdlc-lite/scripts/fanout.py` and `docs/references/sdlc-internals.md` (plus this ticket folder).

## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
