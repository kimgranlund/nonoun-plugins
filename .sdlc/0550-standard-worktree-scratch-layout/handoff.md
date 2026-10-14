---
id: T-0550
title: "Worktrees and scratch follow host defaults: .claude/worktrees, session scratch, owner markers and a crash sweep"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A session with no SDLC Lite context finds every worktree SDLC Lite creates in Claude Code's default place, `<main checkout>/.claude/worktrees/`, and SDLC Lite leaves no scratch, lane, or probe folder anywhere it does not own and clean up.

## Intent
- Do: one root for all worktrees, `<main checkout>/.claude/worktrees/`, on both hosts: fanout lanes and integration (`fanout-<NN>/<lane>`), role throwaway worktrees (`tmp/<agent name>/`), and any other `git worktree add` in scripts, agents, skills, hooks and docs (about 32 files name `.worktrees` today).
- Do: resolve the root from the main checkout (`git rev-parse --git-common-dir` parent), never from the current tree, so a role inside a lane never nests (`.worktrees/t0535-lane/.worktrees/tmp/...` seen in maison, 2026-10-14).
- Do: non-worktree scratch (probe files, mutated copies) goes to a per-run dir under the system temp dir (`$TMPDIR`), matching Claude Code's session scratchpad convention, not into the repo.
- Do: each run's folder holds an owner marker (pid, start time, ticket, role). The sweep (`lanes.py sweep`, and the `dispatch.py record` stray check) removes only folders whose owner is dead and older than a time limit, and reports folders with no marker (legacy, hand-made) without deleting them.
- Do: migration. Existing `.worktrees/` in consumer repos keep working for reads and landing; new runs create under the new root; the sweep reports `.worktrees/` leftovers; release notes say how to move or remove them. The `block-role-worktree` and `block-role-rm` hooks accept the new prefix.
- Non-goals: changing Claude Code's own `--worktree` or Agent-isolation behavior; deleting a consumer's existing folders automatically.
- Done when: a fanout run and a sub-agent role run in a throwaway project create worktrees only under `.claude/worktrees/` and scratch only under `$TMPDIR`; a role started inside a lane gets a prefix under the main checkout's root (selftest with a negative control); the sweep removes a dead-owner folder past the limit, keeps a live one, and reports an unmarked one (selftest); `check.sh` and packaging checks pass.

## Context
Maintainer decision 2026-10-14: "a new session that does not use SDLC or has context should not have to figure out that in this project the worktrees go somewhere unusual"; chose `.claude/worktrees/` (Claude Code's default for `claude --worktree`, EnterWorktree, and Agent `isolation: worktree`) for both hosts. Today: lanes in `.worktrees/fanoutNN/`, role scratch in `.worktrees/tmp/<agent>` (`dispatch.py` :906, `run.sh` :37, builder/verifier/planner contracts), lane archive in `.git/sdlc-lane-archive/`. Maison holds many unowned `.worktrees/` folders (`batchA`, `b-0152-s3`, `acc-*`).

## Constraints
Run after 0.23.0 ships. Do not move worktrees a running lane is using. The failing selftests land before or with the change.
