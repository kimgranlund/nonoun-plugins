---
id: T-0630
title: "work_root t09a: evals, proposals, promote read and write the work root"
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
evals, proposals, promote read and write the work root.

## Context
Part 10 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t09a` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/evals.py`, `plugins/sdlc-lite/scripts/proposals.py`, `plugins/sdlc-lite/scripts/promote.py`

Actions this ticket hosts:
-  read and append notes, evals, proposals and the fleet registry at their work-root paths

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/evals.py selftest` exits 0 with the case: `evals.py --root .sdlc list` under `work_root: docs/work` reads docs/work/evals/ (red before); `proposals.py selftest` scans docs/work/NOTES.md; `promote.py selftest` appends to docs/work/NOTES.md
- Moved from T-0632: `check.py`'s evals lock guard (`_evals`, which runs `evals.py --root .sdlc check`) reports a `docs/work/evals/` path on a `work_root: docs/work` fixture with an invalid eval there; this observed run is the control. `check.py` is added to this ticket's files for that one control.
- From T-0634: `promote.py` takes its targets from `docs_check.DEFAULT_HOMES`, which now includes `work`; `promote.py` refuses `work` as a promotion target (a promoted note there would be flagged B-2a), with a selftest case.

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/T-0630-t0630/plugins/sdlc-lite/scripts/proposals.py:81 `import roots` runs before `sys.dont_write_bytecode = True` (line 85), so the import can write a roots .pyc. It is harmless and gitignored (git status --ignored shows nothing new), but it sits apart from the rest of the import block. | note: the artifacts dir holds no builder-*.md report, so builder claims could not be cross-checked; every criterion above rests on observed runs. `redck.py deviations` printed no process deviation lines. | note: the leftover /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/tmp/0630-verifier-L2 dir and /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0630-verifier-L2 scratch dir could not be removed (rm denied). Both throwaway worktrees were removed with git worktree remove.) · verifier: verifier-L2 (opus) · base: 57fa6b46ba0a
- Changed: see commits
- Commits: 2930dea T-0630: work_root t09a: evals, proposals, promote read and write the work root
- Check: 1 `evals.py selftest` exits 0 with the work_root list case (red before); `proposals.py selftest` sc...: pass
- Check: 2 check.py evals lock guard reports a docs/work/evals path on a work_root fixture with an invalid eval: pass
- Check: 3 promote.py takes its homes from docs_check.DEFAULT_HOMES, refuses `work`, and has a selftest case: pass
