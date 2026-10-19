---
id: T-0632
title: "work_root t10: check.py reads record paths from the resolver: NAME_ALLOW and the evals lock path"
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
check.py reads record paths from the resolver: NAME_ALLOW and the evals lock path.

## Context
Part 12 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t10` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/check.py (NAME_ALLOW, evals lock guard)`

Actions this ticket hosts:
-  keep the spelling allowlist and broken-link baseline valid for closed tickets in the new root

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0 with a NAME_ALLOW negative control: under `work_root: docs/work` a retired spelling under docs/work/.0001-a/ is allowed and one under docs/specs/ is flagged (red before: flagged). (Amended 2026-10-19, the ticket's one replan: the evals guard clause moved to T-0630, because the guard reads through `evals.py`, which T-0630 changes; check.py must not claim the guard reads the work root before then.)
