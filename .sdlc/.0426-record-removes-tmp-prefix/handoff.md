---
id: T-0426
title: "dispatch.py record removes the role's own tmp worktree prefix"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After `dispatch.py record` a role's throwaway worktrees under its tmp prefix are gone, so verifiers stop leaving `.worktrees/tmp/*` entries behind.

## Intent
- Do: the dispatch JSON names `tmp_prefix` (for example `<tree>/.worktrees/tmp/<name>`); roles may only add detached worktrees there and cannot remove the prefix themselves. In scripts/dispatch.py `record`, after the result is validated and recorded, remove every git worktree registered under that exact prefix (`git worktree remove --force`) and then the prefix directory itself, refusing any path that is not strictly under `.worktrees/tmp/` of the dispatch tree or that is a symlink, and print one line `cleaned: N tmp worktrees`. Never touch a path outside the prefix, a branch, or another role's prefix. Also run the same cleanup when `record` is called for a failed or interrupted attempt.
- Non-goals: removing lane worktrees (T-0422, T-0423); model or effort changes.
- Done when:
  - Selftest cases, each observed failing first: a recorded verifier with two detached worktrees under its prefix leaves none; a sibling role's prefix and a path outside `.worktrees/tmp` are untouched; a symlinked or out-of-prefix `tmp_prefix` is refused with a message.
  - dispatch.py selftest, check.py, hook selftest (`block-stray-worktree` still denies a role creating one outside its prefix) and tickets.py check pass.

## Context
Maison, 2026-10-10: roles cannot rm -rf their tmp prefix (denied), so the conductor cleans by hand; 35 entries under .worktrees/tmp at the start of the day. AGENTS.md invariant: preserve owned cleanup and stray-worktree reporting.

## Constraints
No em or en dashes. No push or publish. Do not remove any worktree or branch outside the role's own tmp prefix.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` passes, including the five `T-0426` cases (two detached worktrees under a recorded role's prefix leave none and print `cleaned: 2 tmp worktrees`; a sibling prefix and an outside worktree survive; a symlinked `tmp_prefix` and `.worktrees/tmp` itself are refused with a message; a failed attempt cleans too).
- Those cases failed before the change to `remove_tmp` in `scripts/dispatch.py` (symlink case, cleaned line, failed-attempt line).
- `python3 plugins/sdlc-lite/scripts/check.py`, `bash plugins/sdlc-lite/scripts/hook-selftest.sh`, and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass.
- No path outside the role's own prefix is removed (inspect `remove_tmp`).

## Closed

2026-10-10: delivered by the solo agent (level L2); verified pass by an independent L2 verifier on the second round
