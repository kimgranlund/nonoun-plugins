---
id: T-0707
title: "Briefs say to write worktree and rm paths literally"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every prepared role brief tells the role to write `git worktree add` and `rm` paths literally, never through a shell variable.

## Intent
- Do: add one sentence to the brief that `plugins/sdlc-lite/scripts/dispatch.py` prepare builds (the `Throwaway worktrees only under` line, about line 1310), and to any other brief builder with the same worktree line (`solo_run.py`, `fanout.py prep`, `run.sh`, if they carry one): write each worktree and rm path literally (the full path, or under `$SDLC_TMP_WORKTREES`), never through another shell variable such as `$T` or `$S`, because the guard hooks cannot read it and refuse the command. Update the selftest that pins the brief text.
- Non-goals: hook changes.
- Done when: the criteria pass.

## Context
Transcripts under `~/.claude/projects` hold 606 hook refusals "a git worktree add the hook cannot parse safely" (verifier 312, solo 98, conductor 74, planner 64, builder 36, plan-reviewer 22) and 2 "rm of $W/$d (the hook cannot ...", 14 of them in the last 7 days. Each costs a retry. A consumer conductor traced its 5 to paths held in `$T` and `$S`.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and a case asserts a prepared brief contains the literal-path sentence.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
