---
id: T-0758
title: "The land command prep prints names the branch the host actually made"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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
`fanout.py land` resolves a printed `worktree-<id>-solo` name that is no local branch to the host branch a host lane record names for the ticket (`host_branch_of`, called from `branch_repo`); the record is the one `dispatch.py record --agent-id` or `advance --agent-id` rebinds to `agent-<id>` (T-0763). The first version also scanned `worktree-agent-*` branches; the verifier showed that lands a sibling's branch (every branch cut from main holds every open ticket), so the scan is dropped. With no record naming a branch and `worktree-agent-*` branches present, land refuses (exit 2) listing them and naming the record step; two records naming the ticket are refused naming both; with no host branch at all the old refusal stays. Docs: fanout.py docstring, lane-lifecycle.md, fanout SKILL.md. Main merged into the lane (T-0763 landed).
- Selftest case 23 (T-0758): the verifier's probe (h1 for T-0001, sibling h2 for T-0002, no record) refuses naming both; two records refuse; a record written by `rebind_host_record` lands h1 and not h2; no branch keeps the old refusal. With the scan restored the probe case fails: `no record names a host branch, two worktree-agent-* branches hold T-0001 open ... got rc=0 err='fanout: worktree-T-0001-solo is not a local branch; landing the host branch worktree-agent-h1'`.
- `fanout.py selftest` via gate_lock exit 0, `dispatch.py selftest` via gate_lock exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check main` exit 0.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 5a39eafb6679
- Changed: see commits
- Commits: b8da8a0 T-0758: land resolves the host branch only through a host record, no branch scan; 46d163d T-0758: land resolves the printed worktree-<id>-solo name to the host branch
- Check: 1 A `fanout.py` selftest case: with only a `worktree-agent-<id>` branch present for the ticket (hos...: pass
- Check: 2 gate_lock fanout selftest exits 0, check.py exits 0, check-packaging.py passes, `git diff --check...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:2615 prints landing the host... -> notes.md
- Follow-up: note: the probe's fanout/h holds two T-0001: Ticket t1 commits -> notes.md
