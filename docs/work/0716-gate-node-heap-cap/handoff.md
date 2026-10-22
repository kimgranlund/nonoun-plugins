---
id: T-0716
title: "gate_lock run stops a gate whose process tree exceeds a memory cap"
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
`gate_lock.py run` stops a gate whose process tree's resident memory exceeds a cap, with a clear error, so a leaking test fails fast instead of taking a quarter of the machine's RAM.

## Intent
- Do: in `plugins/sdlc-lite/scripts/gate_lock.py` `run`, while the gate command runs, sample the total RSS of its process tree (the child and all descendants, for example from one `ps -axo pid=,ppid=,rss=` per sample) every 2 seconds. When the total exceeds the cap, stop the tree (SIGTERM, then SIGKILL after 5 s), release the grant as on any exit, print one stderr line `gate_lock: stopped <name>: process tree RSS <x> MB over max_rss_mb <N>`, and exit non-zero (137). The cap comes from a new policy key `max_rss_mb` (`policy set max_rss_mb=N`; 0 turns it off; absent means 25% of physical RAM, from `sysctl hw.memsize` on macOS or `os.sysconf` elsewhere). `policy show` shows it. Remove the `node_heap_mb` / `NODE_OPTIONS` heap cap from the first attempt. Document it in the usage text, `docs/specs/sdlc-lite/gate-lock-admission.md` and the "Gate worker caps" table of `plugins/sdlc-lite/skills/fanout/references/land.md`.
- Non-goals: memory-aware admission; a per-heap Node cap.
- Done when: the criteria pass.

## Replan
2026-10-22, from the first build: Node's default V8 heap limit on this host is already 4288 MB, so a 4096 MB `--max-old-space-size` default changes nothing, and the reported 13 to 18 GB resident likely sat outside the V8 heap (Buffers, ArrayBuffers or worker-thread heaps) [U]. The maintainer chose an RSS watchdog over the process tree instead.

## Context
CPU diagnostics from the user's second machine, 2026-10-22 (three reports, Claude and Codex): `node --test --test-concurrency=3` running `src/application/test/prepared-reuse.test.mjs` in ultimate-tokens, launched through the gate queue, reached 13 to 18 GB resident at 280 to 338% CPU within 2 minutes on a 64 GB machine. The worker cap held; nothing capped the heap. One report: "cap the test heap with `--max-old-space-size` so a leak fails fast."

## Acceptance criteria
1. A `gate_lock.py` selftest case runs a gate whose child process allocates past a small `max_rss_mb` (for example 200, with a child that grows to about 400 MB of RSS) and asserts the run exits 137 within 15 s, prints the `stopped ... over max_rss_mb` line and leaves no grant held; a second case with `max_rss_mb=0` lets the same child finish. With the watchdog disabled, the first case fails (state the FAIL line in the Outcome).
2. `git grep -n "node_heap_mb" plugins docs/specs` prints nothing.
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0, `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
The first attempt (`node_heap_mb`, `NODE_OPTIONS`) is removed from `gate_lock.py`, the spec and `land.md`; the RSS watchdog replaces it.

- `plugins/sdlc-lite/scripts/gate_lock.py`: `tree_rss` (one `ps -axo pid=,ppid=,rss=` per sample, sums the child and its descendants), `wait_watched` (samples every 2 s, `SDLC_GATE_RSS_SECS` for tests; over the cap it drains the process group, SIGKILLs descendants that left it, prints `gate_lock: stopped <name>: process tree RSS <x> MB over max_rss_mb <N>` and returns 137), the policy key `max_rss_mb` (absent is 25% of RAM, derived and never written, 0 off) in `policy set` and `policy show`, and the usage text. Top-level `run` only; the receipt outcome is `rss_exceeded`.
- Docs: section 15 of `docs/specs/sdlc-lite/gate-lock-admission.md` and a row in the "Gate worker caps" table of `plugins/sdlc-lite/skills/fanout/references/land.md`.
- Criterion 1: selftest control `memory cap` (`case_rss`, marker `RSS-CAP`): a child plus grandchild holding about 400 MB under `max_rss_mb=200` exits 137 with the stopped line within 15 s, leaves no grant and no process; with `max_rss_mb=0` the same gate prints `done` and exits 0; `policy show` and the unwritten default are checked. With the `RSS-CAP` line changed to `used, pids = 0, []` the control FAILs: `negative control observed (memory cap): rss cap missing: a 400 MB tree under max_rss_mb=200 gave rc=0 after 5.2s 'done\n' '', wanted 137 and the stopped line within 15 s`.
- Criterion 2: `git grep -n "node_heap_mb" plugins docs/specs` prints nothing (exit 1).
- Criterion 3: `gate_lock.py selftest` exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check 3575fb51` exit 0.
- Limit: a sample every 2 s misses a shorter spike; the real 13 to 18 GB leak was not reproduced here, only the 400 MB fixture.
