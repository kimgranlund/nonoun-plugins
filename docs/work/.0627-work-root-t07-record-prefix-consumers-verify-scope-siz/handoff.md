---
id: T-0627
title: "work_root t07: record-prefix consumers: verify_scope size/protected gates, reorg freeze and digest, inven"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0621]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
record-prefix consumers: verify_scope size/protected gates, reorg freeze and digest, inventory exclusion.

## Context
Part 7 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t07` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/verify_scope.py`, `plugins/sdlc-lite/scripts/reorg.py`, `plugins/sdlc-lite/scripts/inventory.py`

Actions this ticket hosts:
-  treat work-root paths as sdlc records in verifier scope gates, reorg freeze and the document inventory

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/verify_scope.py selftest` exits 0 with the case: under `work_root: docs/work` nine changed files under docs/work/ do not count toward the 8-file cap (red before); `reorg.py selftest` keeps its digest on a docs/work edit; `inventory.py selftest` skips docs/work without --include-sdlc

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: verify_scope.py:67 removes the `OUTSIDE_SDLC` constant. `git grep OUTSIDE_SDLC` finds no other user. The dependent `tickets.py selftest` (it imports verify_scope) passes (`tickets selftest: PASS`), and `git diff --check` is clean.) · verifier: verifier-L2 (opus) · base: 097fed3eca1e
- Changed: see commits
- Commits: 7b176a6 T-0627: work_root t07: record-prefix consumers: verify_scope size/protected gates, reorg freeze and digest, inven
- Check: 1 `python3 plugins/sdlc-lite/scripts/verify_scope.py selftest` exits 0 with the case: under `work_r...: pass
