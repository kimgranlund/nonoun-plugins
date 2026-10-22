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

## Outcome
Built in `plugins/sdlc-lite/scripts/gate_lock.py`: `apply_heap_cap` (top-level `run` only), policy key `node_heap_mb` (absent 4096, derived at load and never written, 0 off), `policy set`/`policy show`, usage text. Docs: section 15 of `docs/specs/sdlc-lite/gate-lock-admission.md`, a row in the "Gate worker caps" table of `plugins/sdlc-lite/skills/fanout/references/land.md`.

- Criterion 1: new selftest control `node heap cap` (`case_heap`, marker `HEAP-CAP`). With the cap line changed to `pass` the selftest prints the negative-control FAIL line: `negative control observed (node heap cap): heap cap missing: no NODE_OPTIONS gave '[]\n' 'gate_lock: node heap capped at 4096 MB ...` and passes on the real script.
- Criterion 2: the span as written exits 0 but prints `192`, not near 4096, because `>>` is a 32-bit shift in JS and the limit with a 4096 cap is 4288 MB (4496293888 bytes; 4288 mod 4096 = 192). Plan defect in the span. Run with `env -u NODE_OPTIONS` (the shell's NODE_OPTIONS preload module is missing). The same limit as `heap_size_limit/1048576` prints 4288 (Node's own default on this 64 GB host is also 4288, so the default cap changes nothing here). With `SDLC_GATE_DIR` set to a scratch dir and `policy set node_heap_mb=1024` the limit reads 1216, which shows the cap takes effect.
- Criterion 3: `gate_lock.py selftest` exit 0 (PASS), `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check 3575fb51` exit 0.
