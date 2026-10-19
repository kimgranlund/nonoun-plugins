---
id: T-0623
title: "work_root t03: tickets.py resolution sites: new/claim/roadmap/check/tidy in the work root (ROADMAP.md, NO"
type: chore           # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0621]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
tickets.py resolution sites: new/claim/roadmap/check/tidy in the work root (ROADMAP.md, NOTES.md names), strays left in .sdlc, other worktrees and external branches.

## Context
Part 3 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t03` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/tickets.py`

Actions this ticket hosts:
-  resolve another worktree's or git branch's work root from its own config so ticket ids stay unique
-  create, claim, list and regenerate the roadmap for tickets in the work root
-  flag a ticket folder stranded in .sdlc after a repo moved its work root
-  name the work-root singletons as UPPERCASE masters ROADMAP.md and NOTES.md, with ticket folders as the children

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with the cases: under `work_root: docs/work`, `tickets.py --root .sdlc new chore a` writes docs/work/0001-a/handoff.md and `roadmap` writes a file whose name in os.listdir(docs/work) is exactly ROADMAP.md (red before: .sdlc/0001-a and .sdlc/roadmap.md); `check` fails a ticket folder left at .sdlc/0002-b as a stray; an id in another worktree's docs/work counts toward the next id
