---
id: T-0303
title: "gate_lock.py machine-wide semaphore for heavy gates"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/sdlc-lite/scripts/gate_lock.py`: a machine-wide semaphore so at most N heavy gates (npm test, browser shards, tsc) run at once across every session and repo. USER DECISION. Realizes the idea in T-0292 (filed on another branch); T-0292 is dropped when this merges.

## Requirements
- `gate_lock.py run [--slots N] [--name X] [--nice] [--timeout SECS] -- <cmd...>` takes one of N slots (default 2, env `SDLC_GATE_SLOTS`), lock dir `${TMPDIR:-/tmp}/sdlc-gate-locks`, one file per slot holding pid and start time (create exclusively); a slot whose pid is dead is stolen. Waits with a bounded timeout (default 30 min, 1800 s), printing who holds the slots while waiting (rate-limited). Exports `SDLC_GATE_WORKERS` = max(1, floor(cpus / slots)) to the command (for Playwright and vitest worker settings). `--nice` runs the command under nice. Releases the slot on exit and on SIGTERM/SIGINT/SIGHUP (killing the command's process group first), and exits with the command's status; timeout exits 3 with one stderr line.
- `gate_lock.py status` lists holders (slot, pid, name, age); `selftest`.
- fanout.py: each `--gate` command runs through `gate_lock.py run --name <lane/ticket> --` (the gate log still gets its output; the gate-vacuous check and rc handling stay the same). `SDLC_GATE_SLOTS=0` or `--no-gate-lock` skips the wrapper. Selftest cases in fanout.py keep passing.
- Docs: docs/maintenance/sdlc-internals.md gets a `scripts/gate_lock.py` entry; agents/conductor.md says heavy gates (npm test, browser shards, tsc) run through `gate_lock.py run`. If agent bodies change run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Add the script to wherever check.sh lists selftests.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 using real child processes: with 2 slots, two holders run and a third waits then runs after one exits; a SIGKILLed holder's slot is stolen by the next run; SDLC_GATE_WORKERS is visible to the child; the command's exit status is returned; the timeout path exits 3.
- [ ] Negative control shown once: a copy of gate_lock.py with the slot cap removed lets the third holder start at once, so the case fails.
- [ ] `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and a case shows a `--gate` command runs through gate_lock (observed via the lock dir or an env marker); `--no-gate-lock` skips it.
- [ ] sdlc-internals.md and agents/conductor.md name `gate_lock.py run` for heavy gates; `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
