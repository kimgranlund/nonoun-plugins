---
id: T-0818
title: "Spawn gate and lane path tests for direct and hybrid sessions"
type: chore           # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0815, T-0819]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Regression tests pin the mode boundaries: the conductor spawn gate stays silent in `sdlc:live` and `sdlc:hybrid` sessions, the guard hooks still block in them, and a hybrid lane still goes through a prepared dispatch.

## Context
- Names follow T-0819 (plugin `sdlc`, agents `sdlc:factory`, `sdlc:hybrid`, `sdlc:live`); build on the renamed tree.
- Design agreed with the user on 2026-10-30 (session reply "sdlc:live and hybrid modes"): the mode is the choice of Claude Code session agent; scripts, hooks and tickets stay shared. Evidence: plain session $0.82 vs solo plus verifier $2.51 on the same builds, hidden tests 10 of 10 in both (`docs/reports/2026-10-28-speed-experiment.md`).
- `plugins/sdlc/hooks/block-role-spawn.sh` gates only conductor sessions; `hooks/_role.sh` resolves session agents to no role. Hook tests: `scripts/hook_selftests.py` or the commands in `docs/references/claude-hooks.md`.

## Do
1. Add hook selftest cases with `agent_type` `sdlc:live` and `sdlc:hybrid`: an Agent spawn passes the spawn gate; a publish command is still blocked by `block-publish.sh`; a stray worktree is still blocked.
2. Add a case that `sdlc:live` and `sdlc:hybrid` resolve to no role in `_role.sh`.

## Acceptance criteria
- The hook selftest command named in `docs/references/claude-hooks.md` exits 0 with the new cases, and each new case fails when its hook line is removed (state the negative control in the report).
- `python3 plugins/sdlc/scripts/check.py` exits 0.
