---
id: T-0273
title: "codex-selftest fanout test fails when repo path contains claude"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The bug is fixed and a test that failed before the fix passes after it.

## Repro
Run `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_fanout_uses_codex` from a checkout whose path contains `claude` (a worktree under `.claude/worktrees`).

## Expected
The test passes: it checks that the Codex driver runs `codex_exec.py`, not the `claude` CLI.

## Actual
`AssertionError: 'claude' unexpectedly found in "/.../.claude/worktrees/.../codex_exec.py conductor L1 ..."`; the test searched the whole command string for `claude`, so the repo path failed it.

## Context
codex-selftest.py `test_fanout_uses_codex`. Cause: a substring check on the command text instead of the argv role or backend.

## Constraints
The failing test lands with the fix. No push, tag, version bump, or publish. No em dashes.
