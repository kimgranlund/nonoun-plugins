---
id: T-0699
title: "fanout prep warns when a gate runs a test runner with no worker cap"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A gate command that runs `node --test`, `vitest`, `playwright` or `jest` without a worker cap is flagged before lanes start, and the docs say how each runner reads `SDLC_GATE_WORKERS`.

## Intent
- Do: in `plugins/sdlc-lite/scripts/fanout.py prep`, print one `warning: gate runs <runner> with no worker cap; add <flag>` line per `--gate` that names one of these runners without its flag: `node --test` needs `--test-concurrency`, `vitest` needs `--maxWorkers` (or `VITEST_MAX_WORKERS`), `playwright` needs `--workers`, `jest` needs `--maxWorkers`. The warning never changes the exit code. Add the runner-to-flag table to `plugins/sdlc-lite/skills/fanout/references/land.md` with `$SDLC_GATE_WORKERS` as the value.
- Non-goals: rewriting the gate command.
- Done when: the criteria pass.

## Context
Issue: GitHub #44 (machine-wide concurrency, 2026-10-21: six lanes plus Codex and a second conductor drove an 18-core Mac to load 128; all load came from test runners). "Granted gates ignore their grant. The lock exports `SDLC_GATE_WORKERS`, but common runners don't read it. `node --test` defaults to one worker per core, `vitest` to cores minus 1, and `playwright` to half the cores."

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a new case: `--gate "npx vitest run"` warns naming `--maxWorkers`, and `--gate "npx vitest run --maxWorkers=2"` does not; the case fails with the change reverted.
2. `git grep -n "SDLC_GATE_WORKERS" plugins/sdlc-lite/skills/fanout/references/land.md` prints a line.
3. `python3 plugins/sdlc-lite/scripts/check.py` and `python3 scripts/check-packaging.py` exit 0.
4. `git diff --check <base sha>` exits 0.
