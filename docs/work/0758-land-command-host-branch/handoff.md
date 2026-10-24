---
id: T-0758
title: "The land command prep prints names the branch the host actually made"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
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

## Outcome
`fanout.py land` now resolves a printed `worktree-<id>-solo` name that is no local branch to the host branch (`host_branch_of`, called from `branch_repo`): the branch a host lane record names for the ticket, else the one local `worktree-agent-*` branch whose tree holds the ticket open and whose record or run record names no other ticket. Two candidates are refused naming both (exit 2); none keeps the old refusal. Docs: fanout.py docstring, lane-lifecycle.md, fanout SKILL.md.
- Selftest case 23 (T-0758): ambiguity refusal, record resolution, scan resolution, no-candidate refusal. With the resolution call replaced by `''` the selftest fails: `case 23 land (T-0758): the host record names worktree-agent-h1 ... got rc=2 out='' err='fanout: worktree-T-0001-solo is not a local branch with a commit'` (3 new cases red).
- `fanout.py selftest` via gate_lock exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check e98473dc` exit 0.
- Not done: T-0763 had not landed on main when this finished, so no merge of main.
