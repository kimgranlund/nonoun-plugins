---
id: T-0715
title: "Plan review lines in a tracked handoff use repo-relative paths"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Lines the conductor or `steps.py` append under `## Plan review` in a tracked handoff carry repo-relative paths, never an absolute home path.

## Intent
- Do: `plugins/sdlc-lite/scripts/steps.py review` prints `read: <path>` repo-relative (about line 232 docs); `steps.py split`, `swap` and `amend`, wherever they append under `## Plan review`, strip the repo or worktree prefix to a relative path; `plugins/sdlc-lite/skills/chain/SKILL.md` line 49 says to write the result path repo-relative. Reuse the helper T-0686/#22 added for repo-relative paths if one exists. Add selftest cases.
- Non-goals: paths in untracked runtime records.
- Done when: the criteria pass.

## Context
GitHub issue #48 (quoted):

> ## What happened
> Following /chain section 3 on a replan, the conductor appends `plan review: replan: <result path>` plus the findings to the tracked task handoff's `## Plan review`. The path that `steps.py review` prints (`read: <path>`), and that the plan-reviewer findings quote, is absolute: `/Users/<me>/Projects/<repo>.worktrees/<lane>/.sdlc/runtime/...`.
>
> The repo's `check:boundaries` gate rejects absolute home paths in tracked files. The next builder therefore reported `inherited red` on a gate the conductor's own record broke, and the step needed a rebuild.
>
> ## Expected
> - `steps.py review` prints, and /chain tells the conductor to write, a repo-relative result path.
> - Lines appended into a tracked handoff have home paths stripped. `steps.py split`, `swap` and `amend` already append under `## Plan review`, so they should apply the same rule.
>
> ## Repro
> 1. Get a plan-reviewer `replan`.
> 2. Follow /chain 3 literally into `docs/work/<t>/handoff.md`.
> 3. Run a repo check that rejects absolute home paths.
>
> Seen on 0.30.0. Related: #22, which fixed absolute paths written by `tickets.py close` and the gate ledger.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `steps.py` selftest case shows `steps.py review` printing a repo-relative `read:` path and an append under `## Plan review` holding no absolute home path; with the change reverted, the case fails (state the FAIL line in the Outcome).
2. `git grep -n "plan review: replan: <result path>" plugins/sdlc-lite/skills/chain` shows the instruction names a repo-relative path.
3. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
