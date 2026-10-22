---
id: T-0731
title: "gate_lock status explains a load-cap stall"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When the queue waits on the load cap, `gate_lock.py status` shows how long it has waited and the top non-gate CPU consumers, so a stall caused by outside load is visible and actionable.

## Intent
- Do: In `gate_lock.py status` (and the waiting line `run` prints), add the queue wait time and the top 3 non-gate processes by CPU when the reason is the load cap. Admission rules stay as T-0697 set them.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #67 (quoted):

> **Observed**: with `max_load=10`, four non-test processes (hung browser tabs, about 4 cores) kept the 1-minute load near 10.5; `gate_lock status` showed 9 queued jobs and `waiting: load 10.8 over cap 10`, with nothing admitted for a long stretch.
>
> **Expected**: admission considers load from admitted gate jobs (or subtracts a baseline), or escalates a stall (print the top non-gate CPU consumers and how long the queue has waited).
>
> **Evidence**: `gate_lock.py status` on 2026-10-22 ~07:38 PDT.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `gate_lock.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`gate_lock.py status` now adds a row `queue waited <S>s; top non-gate CPU: pid <p> <c>% <command>; ...` (and `--json` a `stall` key) while a non-empty queue waits on the load cap, and the waiter's periodic stderr line ends with `waiting on load <n.n> over cap <N>, top non-gate CPU: ...`. The top 3 exclude wrappers in the ledger, admitted commands' groups and their children. Admission is unchanged. New selftest case `case_stall` plus two mutant controls (`STALL-NOTE`, `STALL-LINE`). Docs: `docs/references/sdlc-internals.md`, `docs/specs/sdlc-lite/gate-lock-admission.md`.

- Negative control (case_stall run against the unchanged script): FAIL `status does not say how long the queue waited and the top non-gate CPU, got [... 'waiting: load 36.5 over cap 24']`, plus `status --json does not carry the stall, got {}` and the waiting-line failure.
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0
- `python3 scripts/check-packaging.py` exit 0
- `git diff --check f1e0d7784e64200b2d8f1c837a0c38af12e6dfd2` exit 0

### Rework after verification
Defect: `outside_cpu` decoded `ps` output strictly, so a live process with a non-UTF-8 command line raised `UnicodeDecodeError` and crashed `status` and a waiting `run` (rc 1). Fix: `ps` output and the test file are read with `errors='replace'`, and `outside_cpu` wraps `_outside_cpu` so any exception gives `[]`. New control: `case_stall(raw=True)` (a 99.5% process with `\xff\xfe` in its command line must head the list as U+FFFD) plus a `STALL-DECODE` mutant. Against the previous commit's script the case fails: status shows no stall row, `--json` has no `stall`, and the waiter's stderr is a `Traceback`. Rerun: selftest (direct and through `gate_lock.py run --need compute_units=1 --nice --`) exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check f1e0d7784e64200b2d8f1c837a0c38af12e6dfd2` exit 0.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: f1e0d7784e64
- Changed: see commits
- Commits: c1d9a38 T-0731: stall report reads ps with errors=replace and fails open; 8d2362c T-0731: gate_lock status and waiting line explain a load-cap stall
- Check: 1 A `gate_lock.py` selftest case reproduces the issue's repro and passes; with the change reverted ...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plug...: pass
- Check: 3 `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:2254 load_cap calls... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/gate_lock.py:464 outside_cpu catches... -> notes.md
