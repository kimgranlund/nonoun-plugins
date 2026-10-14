---
id: T-0552
title: "sdlc-doctor skill: diagnose slow or stuck runs and offer resolutions"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:sdlc-doctor` tells the person why runs are slow or stuck, with evidence, and offers ranked resolutions it carries out only on a yes. The name avoids Claude Code's built-in `/doctor`.

## Intent
- Do: `scripts/doctor.py collect` writes one JSON snapshot with no model call: load average and core count, the top CPU processes, each live lane and role (age, newest transcript write, child process tree), and per-role durations from `runs.jsonl` in the records dirs.
- Do: `doctor.py detect` applies fixed rules and prints one finding per hit with its evidence: `stdin-wait` (a role child such as `cat` or `read` idle on stdin for more than 5 min), `stalled` (no transcript write and no child-process change for more than 20 min), `slow-check` (`check.sh` running longer than 2 times its recorded median), `overloaded` (load above 1.5 times the cores), `runaway-proc` (a long-lived system process above 80% CPU), `heavy-peer` (another repo's lane running browser or test work), `replan-cost` (planning above 40% of a ticket's time).
- Do: skill `skills/sdlc-doctor/SKILL.md`: render the findings, map each rule to fixed resolutions with cost and risk (kill one named pid; restart a process only from a list of daemons the OS respawns, e.g. `fontd`; a one-line throttle message to a busy conductor; file or link a ticket), ask once with AskUserQuestion of at most 4 items, recommendation first, then act only on approval. It never kills by name except for listed daemons, and never stops a role, lane, or another repo's process without a yes. Headless: list findings, act on nothing.
- Non-goals: replacing `/fleet-status` (what is moving) or `/fleet-retro` (what went wrong over a window); any automatic action.
- Done when: `doctor.py selftest` has a positive case and an observed negative control per rule; the skill passes packaging and skill checks; one live run on a machine with a planted stdin-wait reports it and kills only that pid on approval.

## Context
Maintainer request 2026-10-14, after a manual diagnosis in the maintainer session: the T-0543 step 2 builder hung 39 min on `cat > /tmp/x` (T-0548); `check.sh` took 47 min against an 18 min norm with load average 54 on 20 cores; `fontd` at 101% CPU for 26 days; maison Playwright lanes were the heavy peer. The fixes applied by hand: kill the one pid, `killall fontd`, a one-line throttle message to the maison, agent-ui and gen-ui-kit conductors, tickets T-0548 and T-0551. Name `sdlc-doctor`, so it does not collide with Claude Code's built-in `/doctor` (user decision).

## Constraints
The failing selftests land before or with the rules. After 0.23.0.
