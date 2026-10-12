---
id: T-0459
title: "gate_lock selftest isolation case fails when other sessions use the real gate-lock state"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`gate_lock.py selftest` passes whenever its own code is correct, no matter how many other sessions are using the real machine-wide gate lock at the same time.

## Intent
- Do: find the selftest case named `isolation: the real state root was not touched by the selftest` in `plugins/sdlc-lite/scripts/gate_lock.py` and change its comparison so it checks only what the selftest itself could have written (a before and after listing of its own private state root plus a check that the selftest never opened the real ledger path for writing), not a snapshot of the real state root that a peer's gate run legitimately changes. Keep an observed-red control: a selftest that does write the real state root is still caught.
- Non-goals: any lock behavior or capacity; the weights ticket (T-0456).
- Done when: `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 while a second process holds and releases real gate-lock slots in a loop (a stub run in the selftest or a manual loop, state how it was exercised), the observed-red control fails when the selftest is made to write the real root, and `check.sh` exits 0.
- outcome metric: gate_lock selftest isolation flakes per wave, before: 3 observed on 2026-10-11 (T-0447 step 4 builder, T-0452 step 3 builder, and one `inherited red` stop that lost a ticket step)

## Context
Evidence: `.sdlc/.0447-doc-standards-suite/step-4/builder-L3.md` (`inherited red: gate_lock selftest (isolation: the real state root was not touched by the selftest)`), the T-0452 filer warning (`check.sh` exited 1 on that case, rerun exited 0, unchanged `gate_lock.py`), and `gate_lock.py selftest` passing on main when run alone. Other repos' gate runs write the real ledger continuously.

## Constraints
No model or effort change. The selftest must still prove the real root is not touched by the selftest.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 while another process runs `gate_lock.py run -- true` against the real state root in a loop (the real ledger mtime changes during the run).
- The selftest no longer compares the real ledger mtime; its isolation check covers only roots it handed out (all under its own temp dir) and in-process writes under the real root.
- Observed-red controls print `negative control observed (isolation, ...)` for a real-root env, a missing root, an outside root, and an in-process write under a watched root.
- A copy of `gate_lock.py` whose `env_for` hands out a root outside the temp dir makes `selftest` exit 1 with `isolation:` lines.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
