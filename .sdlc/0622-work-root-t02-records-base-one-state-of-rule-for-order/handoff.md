---
id: T-0622
title: "work_root t02: records base: one state_of rule for order.py, records.sh, steps.py, budget.py, dispatch.py"
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
records base: one state_of rule for order.py, records.sh, steps.py, budget.py, dispatch.py.

## Context
Part 2 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t02` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/order.py`, `plugins/sdlc-lite/scripts/records.sh`, `plugins/sdlc-lite/scripts/steps.py`, `plugins/sdlc-lite/scripts/budget.py`, `plugins/sdlc-lite/scripts/dispatch.py`, `plugins/sdlc-lite/scripts/hook-selftest.sh`

Actions this ticket hosts:
-  put a task's runtime records under .sdlc/runtime/tasks/<key> wherever its ticket folder lives, in Python and bash
-  map a runtime records dir back to its ticket folder in the work root
-  lint the record paths a step handoff cites when they sit in the work root
-  hooks and the Codex runner that resolve a handoff's records dir work for a work-root handoff

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/order.py selftest` exits 0 with the case: under `work_root: docs/work`, `order.py records-dir <top>/docs/work/0001-a` prints <top>/.sdlc/runtime/tasks/0001-a and `order.py task-dir` maps it back (red before: <top>/docs/work/runtime/tasks/0001-a); `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0 with the same case through records.sh
