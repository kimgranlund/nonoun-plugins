---
id: T-0095
title: "Role runs leave throwaway git worktrees behind"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
No role run leaves a git worktree behind, on success or failure.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
2026-09-25: gen-ui-system-svelte-lite has 12 detached worktrees in /private/tmp (v0167-base, verify-worktree-0044, b0167-L5-base, t0144-nc and others). Verifiers and builders created them to prove a check can go red, and the 0.9.0 verifier prompt tells them to use "the throwaway worktree at HEAD". Proposal:
- Roles create throwaway worktrees only under `<toplevel>/.worktrees/tmp/<role>-<pid>`.
- run.sh removes every worktree under that prefix when the role exits, through a trap that also fires on failure, then runs `git worktree prune`.
- The agent prompts (verifier, builder, and checks-that-bite if it names a location) point at that prefix.
- A selftest fails if a worktree survives a role run, and includes a failing-role case.

## Constraints
The failing test lands before or with the fix, never after.
