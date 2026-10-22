---
id: T-0716
title: "gate_lock run caps the Node heap of a gate"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A gate run through `gate_lock.py run` gets a Node heap cap, so one leaking test fails fast instead of taking a quarter of the machine's RAM.

## Intent
- Do: in `plugins/sdlc-lite/scripts/gate_lock.py`, where `run` builds the gate env (`SDLC_GATE_WORKERS`, about lines 588 and 717), append `--max-old-space-size=<MB>` to `NODE_OPTIONS` unless `NODE_OPTIONS` already holds a `--max-old-space-size`. The MB comes from a new policy key `node_heap_mb` (`policy set node_heap_mb=N`; 0 turns it off; absent means 4096). `run` prints one stderr line naming the cap it applied. `policy show` shows the key. Document it in the usage text, in `docs/specs/sdlc-lite/gate-lock-admission.md`, and as a row in the "Gate worker caps" table of `plugins/sdlc-lite/skills/fanout/references/land.md`.
- Non-goals: memory-aware admission; non-Node runners.
- Done when: the criteria pass.

## Context
CPU diagnostics from the user's second machine, 2026-10-22 (three reports, Claude and Codex): `node --test --test-concurrency=3` running `src/application/test/prepared-reuse.test.mjs` in ultimate-tokens, launched through the gate queue, reached 13 to 18 GB resident at 280 to 338% CPU within 2 minutes on a 64 GB machine. The worker cap held; nothing capped the heap. One report: "cap the test heap with `--max-old-space-size` so a leak fails fast."

## Acceptance criteria
1. A `gate_lock.py` selftest case: `run` with no `NODE_OPTIONS` passes the child `--max-old-space-size=4096`; with `NODE_OPTIONS=--max-old-space-size=2048` it leaves it unchanged; with `policy set node_heap_mb=0` it adds nothing; with the change reverted the first case fails (state the FAIL line in the Outcome).
2. A real check: `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 -- node -e "console.log(require('v8').getHeapStatistics().heap_size_limit>>20)"` prints a value near 4096 (state it in the Outcome).
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0, `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
