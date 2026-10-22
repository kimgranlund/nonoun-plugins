---
id: T-0700
title: "fanout prep counts other lanes and the load before opening lanes"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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

## Outcome
- Base: 47fb0e8c (main merged into the lane, fast-forward, bringing T-0697's default max_load and no-holder guard).
- `fanout.py prep` now calls `load_cap` after the refusals and the sweep: it reads `gate_lock.status_data` (the ledger, the policy with T-0697's CPU default, the load), prints `prep: <n> live gate-lock holder(s) from other repos`, and when the load is over the effective max_load keeps only the first regular lane, printing `prep: load <x> over <max>: opening 1 of <n> lanes`. `--force` (new, prep only) opens every lane. An unreadable ledger caps nothing.
- Selftest: case 22 prep load cap (load file 1000, 4 CPUs so max_load 3): 1 of 3 dispatches with the line; `--force` and a quiet load give 3. `gate_env` now defaults to a quiet load file so a busy host never caps the other prep cases. With `load_cap` reverted the new case fails (the only failure).
- Docs: `--force` row in `skills/fanout/SKILL.md` (17,847 characters), usage line and prep paragraph in the fanout.py docstring.
- Checks: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` (through gate_lock.py run --need compute_units=1 --nice) exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check 47fb0e8c` exit 0.

## Outcome

2026-10-21 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 05c7d6f28c27
- Changed: see commits
- Commits: b9ab04c T-0700: fanout prep counts other lanes and the load before opening lanes
- Check: 1 selftest with a new load-cap case: pass
- Check: 2 check.py and check-packaging.py exit 0: pass
- Check: 3 `git diff --check <base sha>`: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py load_cap: the ledger-unreadable... -> notes.md
