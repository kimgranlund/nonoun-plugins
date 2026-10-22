---
id: T-0740
title: "Solo lanes in host worktrees commit and report where land reads"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo running in a Claude Code host worktree (`isolation: worktree`) ends with its change committed on its lane branch and its report where `dispatch.py record` and `fanout.py land` read it, with no manual conductor step.

## Intent
- Do: First establish which layer refuses the git commands ("too complex to verify" is not in `plugins/sdlc-lite/hooks/`; check whether it is Claude Code's own worktree isolation) and record it in the Outcome. Then fix the plugin side: either the brief from `fanout.py prep` stops asking a host-worktree solo to run git (it leaves changes uncommitted) and `land` commits a dirty host lane itself, or the hooks allow git inside the agent's own worktree if a plugin hook is the cause. Make the brief's `Report file:` point at a path the solo can write, and make `record` and `land` read it there (reuse the T-0720 fallback where it fits).
- Non-goals: the other parts of the same issue.
- Done when: the criteria pass.

## Context
GitHub issue #68 (quoted):

> **Version:** sdlc-lite 0.33.0, Claude Code host, `fanout.py prep` sub-agent lanes (`isolation: worktree`). Seen in ui-kit-neue 2026-10-22 (T-0294, T-0295, T-0296, T-0298, T-0299).
>
> **What happened**
> In all five solo lanes the worktree guard hook refused every git command, even `git status` and `git log`, as "too complex to verify". So the solo could not:
> - run the brief's first step, `git merge --ff-only <base sha>`;
> - make the `WIP <id>` commits or the final `<id>: <title>` commit the brief asks for;
> - write its report to the brief's `Report file:` path in the primary checkout (`<repo>/.sdlc/runtime/tasks/<task>/<id>-solo.md`). The Write was refused as outside the worktree.
>
> Each solo ended `done` (or `blocked` only for git) with its change uncommitted and its report at the worktree copy of the report path.
>
> **Expected**
> A solo in a host worktree can run git inside its own worktree and commit on its branch, and it can write the report where `dispatch.py record` and `fanout.py land` look for it. Otherwise the brief should not ask for any of these.
>
> **Workaround used**
> The conductor read each report from `<worktree>/.sdlc/runtime/tasks/<task>/`, ran `git add <named files> && git commit -m "<id>: <title>"` in the worktree, and copied the report into the primary checkout's records dir before `fanout.py land`. This happened 5 of 5 times.
>
> **Ask**
> Either allow git (status, log, diff, add, commit, merge --ff-only) inside the agent's own worktree in the guard hook, or make the solo brief say "leave changes uncommitted; the conductor commits" and have `land` commit a dirty lane itself. Point the brief's report path at the worktree copy, or have `record` and `land` read from there. Related to #45 (closed; that one was about shell variables).

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
