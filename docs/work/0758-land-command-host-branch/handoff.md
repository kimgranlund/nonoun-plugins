---
id: T-0758
title: "The land command prep prints names the branch the host actually made"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py prep` prints a land command that works for a host lane: it names the branch the host creates (`worktree-agent-<agent_id>`) or `land` resolves the printed `worktree-<id>-solo` name to it, so the printed command runs as is.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: `fanout: worktree-T-0001-solo is not a local branch with a commit` (rc=2) for the land command prep printed; every land had to use the branch from the Agent result.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case: with only a `worktree-agent-<id>` branch present for the ticket (host record names it), the land command prep printed succeeds; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
