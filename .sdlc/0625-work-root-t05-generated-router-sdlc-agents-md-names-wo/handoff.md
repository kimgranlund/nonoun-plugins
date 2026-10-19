---
id: T-0625
title: "work_root t05: generated router .sdlc/AGENTS.md names work-root paths; work-root entry file; onboard root"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0624, T-0634]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
generated router .sdlc/AGENTS.md names work-root paths; work-root entry file; onboard root block.

## Context
Part 5 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t05` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/tickets.py (router_files, router text)`, `plugins/sdlc-lite/scripts/onboard.py`

Actions this ticket hosts:
-  generate the .sdlc/AGENTS.md router naming work-root ticket paths, with an entry in the work root pointing to it
-  name the resolved roadmap, notes and archive paths in the onboarded root AGENTS.md block

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with the case: under `work_root: docs/work` the router .sdlc/AGENTS.md lists `(docs/work/0001-a)` and docs/work/AGENTS.md points to .sdlc/AGENTS.md (red before); `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0 with a root block naming docs/work/ROADMAP.md and docs/work/NOTES.md
