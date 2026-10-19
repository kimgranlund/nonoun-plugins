---
id: T-0629
title: "work_root t08b: fleet registry and notes readers: fleet_config, fleet_status, fleet_doctor"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0621]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
fleet registry and notes readers: fleet_config, fleet_status, fleet_doctor.

## Context
Part 9 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t08b` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/fleet_config.py`, `plugins/sdlc-lite/scripts/fleet_status.py`, `plugins/sdlc-lite/scripts/fleet_doctor.py`

Actions this ticket hosts:
-  read and append notes, evals, proposals and the fleet registry at their work-root paths

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest` exits 0 with the case: under `work_root: docs/work` the default registry is docs/work/fleet.json and a blocked ticket's owner is read from docs/work/NOTES.md (red before); `fleet_config.py selftest` and `fleet_doctor.py selftest` exit 0
