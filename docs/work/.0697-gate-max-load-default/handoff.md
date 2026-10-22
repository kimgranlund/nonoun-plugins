---
id: T-0697
title: "gate_lock admits by load from a CPU-count default when policy sets no max_load"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
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

## Outcome
`gate_lock.py` now derives `max_load = max(1, int(0.8 * CPU count))` when `policy.json` has no `max_load` key (`set_default_max_load`, called from `load_policy`; `SDLC_GATE_CPUS` is the tests-only CPU seam). `policy set max_load=0` now writes 0, which turns the cap off and survives later `policy set` calls; `policy set` never writes the derived default into the file. `policy show` and `capabilities` carry `max_load_default: "default from N CPUs"` only when the default is in force. Docstring, `docs/references/sdlc-internals.md` and `docs/specs/sdlc-lite/gate-lock-admission.md` updated.

Selftest: new `case_load_default` (10 fake CPUs, cap 8, load 12 refuses a fitting second gate; `policy show` names the default; `policy set compute_units=6` leaves policy.json without max_load; `max_load=0` admits) with a mutant control on the `LOAD-DEFAULT` line, observed failing ("the waiter ran over the default load cap"). `env_for` now gives every case a quiet load file so the default cap cannot stall cases on a busy host.

Starvation guard (added after review): the cap applies only while a grant (or a legacy holder) is held; with none held the head is admitted at any load, and `status` reports `over` only in that state. New `case_load_idle` (real processes, load 36.5, max_load 24, no holder: the first gate starts, the second waits) with a mutant control restoring the unguarded line, observed failing ('the starved head ...'); `case_rr` now holds a grant for the over-cap check and asserts the idle ledger grants only the head.

Checks: `gate_lock.py selftest` PASS, `check.py` exit 0, `scripts/check-packaging.py` PASS, `git diff --check a8680df4` exit 0.

## Outcome

2026-10-21 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: a8680df45305
- Changed: see commits
- Commits: a17b61b T-0697: apply the load cap only while a grant is held; b72a41f T-0697: gate_lock admits by load from a CPU-count default when policy sets no max_load
- Check: 1 `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 with new cases (no max_load key...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass
- Check: 3 `git diff --check <base sha>` exits 0: pass
- Follow-up: fix-now: docs/specs/sdlc-lite/gate-lock-admission.md:208 still says "the cap... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/gate_lock.py:1466 the case_rr "over the... -> notes.md
- Follow-up: note: docs/specs/sdlc-lite/gate-lock-admission.md:213 the Reason bullet... -> notes.md
