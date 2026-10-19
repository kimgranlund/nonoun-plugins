---
id: T-0639
title: "lanes.py close crashes in carry_lane_records under work_root"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`lanes.py close` (and `finish`, which calls it) carries a lane's ticket records into the main checkout under `work_root: docs/work` without crashing, proven by a selftest that failed before the fix.

## Repro
1. In this repository (now `work_root: docs/work`), open a lane, then run `python3 plugins/sdlc-lite/scripts/lanes.py close <lane>`.
2. It raises `ValueError: '<lane>/docs/work' is not in the subpath of '<lane>/.sdlc'` from `carry_lane_records` (`plugins/sdlc-lite/scripts/lanes.py:837`).

## Expected
The destination is the main checkout's own ticket dir: `tickets.ticket_dir(<main>/.sdlc) / slug`, which resolves to `docs/work/<slug>` under work_root and stays the same as today without it.

## Actual
`carry_records(ltdir / slug, mroot / ltdir.relative_to(lroot) / slug)` assumes the ticket dir sits inside `.sdlc`.

## Context
Found closing T-0636 (this repository's migration) on 2026-10-19; T-0626's `case_work_root` covered `copy_sdlc` and `first_dirty` but not `carry_lane_records`. Every lane close in this repository crashes until this lands.

## Constraints
The failing test lands before or with the fix. No change with no `work_root:` line.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with a case that closes a lane under `work_root: docs/work` and finds the ticket's records carried to the main checkout's records dir (red before: ValueError).
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
