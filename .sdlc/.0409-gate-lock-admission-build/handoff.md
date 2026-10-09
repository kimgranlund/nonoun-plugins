---
id: T-0409
title: "Build gate_lock.py weighted admission with FIFO, priority and liveness (design T-0386)"
type: feature        # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`gate_lock.py` is the weighted shared admission authority designed in docs/specs/sdlc-lite/gate-lock-admission.md, with FIFO order, priority and a queued/admitted/liveness status.

## Intent
- Do: build exactly the design in docs/specs/sdlc-lite/gate-lock-admission.md with the approved caps of 6 compute units and 3 browser jobs, and maison's acceptance from maison .sdlc/tickets/0300-shared-resource-lease-design/codex-live-admission-followup.md (queue order, priority, liveness). Keep the existing gate_lock.py behavior for current callers unless the design changes it, and update the docs/references/sdlc-internals.md entry.
- Non-goals: changing the caps; model or effort changes; editing consumer repos' browser-slot.sh.
- Done when:
  - Selftest cases, each observed failing first: a second job waits in FIFO order behind the first when the cap is full; a higher priority job is admitted first among waiters; a dead holder is reclaimed and a live one is not; the status command prints queued and admitted rows; exit codes are unchanged for the existing callers.
  - gate_lock.py selftest, check.py, hook selftest and tickets.py check pass.

## Context
T-0386 design (gate-lock-admission.md) was pending the maintainer; the maintainer approved the numbers and the build on 2026-10-09. Live contention evidence from maison, 2026-10-09 (a Codex job that blocked an integration waited behind lower-priority runs).

## Constraints
No em or en dashes. No push or publish. The design is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 and prints a negative control observed for each of: weighted cap, FIFO order, priority, dead holder reclaimed, live group not reclaimed, start identity, group drain.
- A second job waits in FIFO order behind the first when the cap is full, and a higher priority job is admitted first among waiters: `gate_lock.py run --need compute_units=6 --priority 5 -- <cmd>` queued behind a full holder runs before an earlier priority 0 waiter.
- `gate_lock.py status` prints `admitted` and `queued` rows (and `status --json` the same with `state` fields) while a holder runs and a job waits.
- A dead holder (wrapper and process group gone) is reclaimed; a dead wrapper with a live process group keeps its charge.
- Exit codes are unchanged for existing callers: the command's own status, 137 for SIGKILL, 127 and 126 for an unrunnable command, 143 on SIGTERM, 3 with a `gate_lock: timeout` first line on a wait timeout; `SDLC_GATE_SLOTS=0` and `--no-gate-lock` run bare.
- The built-in policy is capacity 6 compute units and 3 browser jobs (`gate_lock.py policy show`).
- `python3 plugins/sdlc-lite/scripts/check.py`, `bash plugins/sdlc-lite/scripts/hook-selftest.sh`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, `python3 plugins/sdlc-lite/scripts/fanout.py selftest`, `python3 scripts/check-packaging.py` and `git diff --check` pass.
- `docs/references/sdlc-internals.md` describes the new gate_lock.py behavior.

## Closed

2026-10-09: delivered by the solo agent (level L2); verified pass by an independent L3 verifier
