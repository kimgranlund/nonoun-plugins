---
id: T-0631
title: "work_root t09b: plan_check, plan_done, solo_run: notes-path rule and new plain task folder from the resolv"
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
plan_check, plan_done, solo_run: notes-path rule and new plain task folder from the resolver.

## Context
Part 11 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t09b` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/plan_check.py`, `plugins/sdlc-lite/scripts/plan_done.py`, `plugins/sdlc-lite/scripts/solo_run.py`

Actions this ticket hosts:
-  create, claim, list and regenerate the roadmap for tickets in the work root
-  read and append notes, evals, proposals and the fleet registry at their work-root paths

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0 with the case: under `work_root: docs/work` a goal whose stop rule names docs/work/NOTES.md passes stop-state (red before: fails); `plan_done.py selftest` accepts the same; `solo_run.py selftest` creates a new task under docs/work

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: plugins/sdlc-lite/scripts/solo_run.py:958 only selftest lines changed here. `new_task` already resolves the work root through `tickets.ticket_dir`, so the solo_run part of the criterion confirms behavior from earlier work. This ticket adds no code change there.) · verifier: verifier-L2 (opus) · base: b9e57a78b1a2
- Changed: see commits
- Commits: b3a006f T-0631: work_root t09b: plan_check, plan_done, solo_run: notes-path rule and new plain task folder from the resolv
- Check: 1 `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0 with the case: under `work_roo...: pass
