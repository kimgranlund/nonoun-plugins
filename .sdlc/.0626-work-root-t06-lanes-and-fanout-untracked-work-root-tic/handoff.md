---
id: T-0626
title: "work_root t06: lanes and fanout: untracked work-root tickets are trail, not dirt; generated work-root fil"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0622]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

base: c3e435b7778ec1fd7ecc3556952129169a0dfca9

## Goal
lanes and fanout: untracked work-root tickets are trail, not dirt; generated work-root files auto-resolve on land.

## Context
Part 6 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t06` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/lanes.py`, `plugins/sdlc-lite/scripts/fanout.py`

Actions this ticket hosts:
-  keep lane open, land and close working when ticket folders are tracked under docs/

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with the case: under `work_root: docs/work` an untracked docs/work/0002-b/ in a lane does not make it dirty (red before); `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a land whose only conflict is docs/work/ROADMAP.md resolved by regeneration

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: The fanout selftest case for the docs/work/ROADMAP.md conflict is not red at c3e435b7. `generated_files` already resolves a work-root roadmap via `tickets.layout_paths` (T-0621/T-0623). The criterion does not mark that half "(red)", so this does not fail it. The new case is a regression guard, and the roadmap-removal mutant above shows it bites.) · verifier: verifier-L2 (sonnet) · base: 6acec72a394f
- Changed: see commits
- Commits: 80bf4a6 T-0626: work_root t06: lanes and fanout: untracked work-root tickets are trail, not dirt; generated work-root fil
- Check: 1 lanes.py selftest exits 0 with the work_root untracked-ticket case (red before), and fanout.py se...: pass
