---
id: T-0004
title: "Git preflight before role runs"
type: bug
status: done
size: L1
priority: P1
depends: []
created: 2026-09-24
source: setup-sdlc-lite-generative-ui session, from gen-ui-system-svelte-lite setup
---

## Goal
A role run in a folder that is not a git repo stops up front with a clear message instead of failing partway through.

## Intent
- Do: a preflight in `scripts/run.sh` (or /chain) that exits early with "not a git repo: run git init and commit first" when the cwd is not inside a git work tree with at least one commit.
- Non-goals: initializing git automatically.
- Done when: run.sh refuses in a non-git temp dir (seen to fail), still runs in a git repo, and check.sh passes.

## Context
- `agents/verifier.md` step 2 runs `git diff` and `git worktree`; /chain and /bench use worktrees. Git is a hidden precondition today.

## Constraints
None.
