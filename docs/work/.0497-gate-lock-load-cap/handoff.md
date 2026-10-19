---
id: T-0497
title: "gate_lock.py: cap admission by load average, with per-repo fairness (retro 12h rows 1 and 2)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`gate_lock.py` admits no new grant while the host load average exceeds a declared cap, in addition to the unit capacity, and keeps one repo from starving another, so a critical gate is not stretched by other repos' CPU-bound gates.

## Intent
- Do: in `gate_lock.py` `schedule` and `fits` (`:360-410`), add a policy key `max_load` (load average per CPU times CPU count, default off) read from `policy.json` through `gate_lock.py policy set max_load=<n>`; with it set, a queued head is not admitted while `os.getloadavg()[0]` exceeds it (a held grant is never revoked). Keep round robin by repo. Print the reason in `status` (`waiting: load 36.5 over cap 24`). Ticket T-0484 (policy reread per poll) is merged and applies.
- Non-goals: killing or pausing a running gate; changing the built-in capacity or default need; per-job priority that pauses lower jobs (a later ticket if the cap is not enough).
- Done when: a `gate_lock.py selftest` case with a fake load above the cap admits nothing and one below admits the head (red first: today it admits), a held grant survives a load rise, `status` prints the reason; `check.py` exits 0.

## Context
Evidence: `docs/reports/2026-10-12-fleet-retro-12.md` rows 1 and 2: maison's 7b full gate timed out at the 1800 s guard (1702 s at load 5 to 7) after the capacity went 6 to 48, load 22 to 41 on 20 CPUs, gates stretched from 56 to over 90 minutes. Capacity is now 32 (maintainer). Related: T-0491 (land gate priority, merged), maison finding 7 in `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`.

## Constraints
No change to the default policy. A repo opts in through `policy.json`. One writer on `gate_lock.py`.
