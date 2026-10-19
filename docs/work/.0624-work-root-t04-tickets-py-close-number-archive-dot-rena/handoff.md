---
id: T-0624
title: "work_root t04: tickets.py close/number/archive: dot rename and citation scan under the work root"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0623]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
tickets.py close/number/archive: dot rename and citation scan under the work root.

## Context
Part 4 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t04` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/tickets.py`

Actions this ticket hosts:
-  close a ticket with the dot rename inside the work root and a citation scan across the repo and the state root
-  number and archive closed tickets in the work root

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with the case: under `work_root: docs/work`, `close` renames docs/work/0001-a to docs/work/.0001-a and names docs/specs/x.md citing docs/work/0001-a/handoff.md, while a cite under .sdlc/runtime/ is never named (red before)

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: tickets.py:5957-6011 the diff adds only selftest cases, no production change, so the criterion's "red before" is not observable at the base sha (the case does not exist there). The production behavior already holds, presumably from T-0623; no `red-checkpoint` deviation was reported by redck.py and the criterion carries no `(red)` tag. | note: scratch mutated copies under /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0624-verifier-L2/{m1,m2} could not be removed (rm was denied); they sit outside the repo.) · verifier: verifier-L2 (sonnet) · base: 8b8a55b051c4
- Changed: see commits
- Commits: e9871ac T-0624: work_root t04: tickets.py close/number/archive: dot rename and citation scan under the work root
- Check: 1 `tickets.py selftest` exits 0 with the work_root close case (docs/work/0001-a renamed to .0001-a,...: pass
