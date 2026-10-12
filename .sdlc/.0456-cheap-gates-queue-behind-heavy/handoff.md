---
id: T-0456
title: "Cheap fanout gates time out in the machine-wide gate lock behind heavy browser jobs"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A cheap fanout gate (`check.py`, `generate --check`, packaging) lands in seconds even while heavy browser jobs hold the machine-wide gate lock, so a queue wait never reads as a red gate.

## Intent
- Do: in `fanout.py` (the gate argv at the `gate_lock.py run` call near line 447) let a gate declare its weight: a `--gate` may carry a need (for example `--gate-need compute_units=1` for all gates, or a per-gate prefix), and cheap gates default to a small need so they are admitted next to heavy jobs; a gate that times out in the lock (`gate_lock: timeout`, rc 3) is reported as `gate waited N s for a slot, not run` and `fanout.py land` retries it once or reports a stop, never `red` (a red means the command ran and failed). Update the docs in `gate-lock-admission.md` and the fanout docstring; selftest cases with a negative control: a timed-out gate is not red, a failing command still is.
- Non-goals: changing the lock's capacity or the approved numbers (a user decision); the heavy gates' behavior.
- Done when: `fanout.py selftest` exits 0 with an observed-red control for each new rule; `gate_lock.py selftest` still exits 0; `check.sh` exits 0.
- outcome metric: `grep -c 'gate_lock: timeout' .worktrees/fanout*/logs/gate-*.log` over a wave with heavy peers, before: 3 of 5 gates in waves 33 and 34 (T-0446, T-0450 red at rc 3)

## Context
Evidence: `.worktrees/fanout/logs/gate-d-T-0446-1-a1.log` (waited 371 s for a slot behind maison jobs `pre7c-*`, then a gate returned rc 3); `/tmp/fanout-f52.log` and `/tmp/fanout-f53.log` show `red: python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check rc=3` for T-0446 and T-0450, while the same command exits 0 on main. The machine-wide queue is shared across repos, so peers' compute jobs delay this repo's cheap gates. Workaround used: `--no-gate-lock` on the cheap gates.

## Constraints
No model or effort change. Heavy gates keep going through the lock. No capacity change.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0; its case 21b shows a cheap gate (`check.py`) granted 1 compute unit and a default gate 3, `--gate-need` overriding both, and a bad spec refused with exit 2.
- With a peer holding 5 of 6 compute units and `SDLC_GATE_TIMEOUT=1`, a cheap gate merges while a default gate ends as `gate waited 1 s for a slot, not run: ...` (no `red:`, merge reset, logs a1 and a2); a gate command that exits 3 itself stays `red: ... rc=3` (negative control).
- `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0; `bash plugins/sdlc-lite/scripts/check.sh` exits 0; `python3 scripts/check-packaging.py` exits 0.
- `docs/specs/sdlc-lite/gate-lock-admission.md` (section 13), `docs/references/sdlc-internals.md` and the `fanout.py` docstring describe `--gate-need`, `SDLC_GATE_TIMEOUT`, the cheap-gate default and the not-run report; the lock's capacity and default need are unchanged.

## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
