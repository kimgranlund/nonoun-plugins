---
id: T-0707
title: "Briefs say to write worktree and rm paths literally"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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
- Do: add one sentence to the brief that `plugins/sdlc-lite/scripts/dispatch.py` prepare builds (the `Throwaway worktrees only under` line, about line 1310), and to any other brief builder with the same worktree line (`solo_run.py`, `fanout.py prep`, `run.sh`, if they carry one): write each worktree and rm path literally as the full path under the prefix the brief names, never through a shell variable such as `$T`, `$S` or `$SDLC_TMP_WORKTREES` (a `prepare` brief does not set it), because the guard hooks cannot read it and refuse the command. Update the selftest that pins the brief text.
- Non-goals: hook changes.
- Done when: the criteria pass.

## Replan
2026-10-22, from verifier-L2 `plan defect:`: `$SDLC_TMP_WORKTREES` is unset for `dispatch.py prepare` roles (only run.sh sets it), so the sentence must name only the literal prefix.

## Context
Transcripts under `~/.claude/projects` hold 606 hook refusals "a git worktree add the hook cannot parse safely" (verifier 312, solo 98, conductor 74, planner 64, builder 36, plan-reviewer 22) and 2 "rm of $W/$d (the hook cannot ...", 14 of them in the last 7 days. Each costs a retry. A consumer conductor traced its 5 to paths held in `$T` and `$S`.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and a case asserts a prepared brief contains the literal-path sentence.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Added one sentence to the brief `dispatch.py prepare` builds (end of the `Throwaway worktrees only under` line): write each worktree and rm path literally as the full path under the prefix that line names, never through a shell variable such as `$T`, `$S` or `$SDLC_TMP_WORKTREES` (unset for prepare roles; only run.sh sets it). `solo_run.py`, `fanout.py`, and `run.sh` carry no such brief line, so they are unchanged. The selftest case asserts the sentence. Checks: `dispatch.py selftest` PASS, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check 3fbfdf44` exit 0.

## Outcome

2026-10-21 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (opus) · base: 3fbfdf44dae1
- Changed: see commits
- Commits: 3c47b09 T-0707: brief names the full path under the prefix, no shell variable; 14048da T-0707: briefs say to write worktree and rm paths literally
- Check: 1 `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and a case asserts a prepared br...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/dispatch.py:1313 says the guard hooks... -> notes.md
