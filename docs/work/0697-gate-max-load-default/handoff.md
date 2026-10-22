---
id: T-0697
title: "gate_lock admits by load from a CPU-count default when policy sets no max_load"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A fresh install admits no new gate while the load is above about 0.8 x the CPU count, without anyone running `policy set max_load=N`.

## Intent
- Do: in `plugins/sdlc-lite/scripts/gate_lock.py`, when `policy.json` has no `max_load` key, use `max(1, int(0.8 * os.cpu_count()))`. An explicit `max_load=0` still turns the cap off. `policy show` prints the effective value and says `(default from N CPUs)` when it is the default. Update the module docstring sentence that says absent is off.
- Non-goals: changing how load is read or the grant math.
- Done when: the criteria pass.

## Context
Issue: GitHub #44 (machine-wide concurrency, 2026-10-21: six lanes plus Codex and a second conductor drove an 18-core Mac to load 128; all load came from test runners). "`max_load` is off by default. Load-based admission exists, but a fresh install never turns it on." Today `gate_lock.py` docstring line 27: "absent or 0 is off, the default".

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 with new cases: no `max_load` key with a load above 0.8 x a faked CPU count refuses a new grant; `max_load=0` admits it; `policy show` names the default. Each case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
3. `git diff --check <base sha>` exits 0.
