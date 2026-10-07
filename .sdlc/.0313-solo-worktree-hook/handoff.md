---
id: T-0313
title: "solo role blocked by block-stray-worktree: conductor must create the lane worktree and branch first"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo run in a fresh lane does not fail because its role cannot create a branch or worktree.

## Intent
- Do: Reproduce with `solo_run.py run` in a repo with no lane worktree (agent-ui reported the first attempts of T-0015 and T-0018 were blocked by block-stray-worktree.sh). Pick the smaller fix and say why: (a) solo_run.py creates the lane worktree and branch before it starts the session when `--worktree <name>` is given, or (b) agents/solo.md and the agent skill state that the conductor creates the worktree and branch first, with the exact commands. Implement it with a selftest.
- Non-goals: loosening block-stray-worktree.sh for roles; any model or effort change.
- Done when:
  - A selftest in solo_run.py shows the chosen behavior (a run with `--worktree` in a throwaway repo gets a worktree on a new branch and the session cwd is that worktree), red at base, green after.
  - agents/solo.md and skills/agent/SKILL.md state the rule, and `check.py` and `codex_roles.py generate --check` pass.

## Context
Reported by the agent-ui conductor on 2026-10-06. Related: block-stray-worktree.sh denies a role creating worktrees on purpose (runner-owned temporary worktrees).

## Constraints
No em dashes. No push, tag or publish.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
