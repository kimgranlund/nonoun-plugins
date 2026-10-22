---
id: T-0700
title: "fanout prep counts other lanes and the load before opening lanes"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py prep` opens fewer lanes when the machine is already busy, counting live lanes from every repo and the current load.

## Intent
- Do: in `plugins/sdlc-lite/scripts/fanout.py prep`, before opening lanes, read the load and the gate-lock ledger (`gate_lock.py context` or its module). When the load is above the effective `max_load` (T-0697's default applies), open at most 1 lane and print `prep: load <x> over <max>: opening 1 of <n> lanes`. Print the number of live gate-lock holders from other repos. `--force` keeps today's behavior.
- Non-goals: cross-repo lane counting beyond the gate-lock ledger.
- Done when: the criteria pass.

## Context
Issue: GitHub #44 (machine-wide concurrency, 2026-10-21: six lanes plus Codex and a second conductor drove an 18-core Mac to load 128; all load came from test runners). "`fanout.py prep` caps lanes with `--max-lanes` (default 4). Lanes from several conductors on one machine share nothing. It could read the gate-lock ledger and the load before it opens more lanes."

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a new case: with a faked load above max_load, prep of 3 lanes opens 1 and prints the `prep: load` line; with `--force` it opens 3; the case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/check.py` and `python3 scripts/check-packaging.py` exit 0 (a new flag needs its Arguments row in `skills/fanout/SKILL.md`).
3. `git diff --check <base sha>` exits 0.
