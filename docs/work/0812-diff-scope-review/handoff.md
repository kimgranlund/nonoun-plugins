---
id: T-0812
title: "Decide diff-scope verifier: drop the revert step or turn it off by default"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
claimed_by: sdlc-lite-author 2026-10-29
branch: lane/T-0812-t0812
worktree: ../sdlc-lite.worktrees/T-0812-t0812
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Decide, from measurement, whether the T-0799 `Scope: diff` verifier stays the default, and act on it: drop its revert step (3) when the Outcome carries red/green evidence, or turn diff scope off by default.

## Context
- Speed experiment: diff $1.4041 vs full $1.4098 (`docs/reports/2026-10-28-speed-experiment.md`).
- Overnight MacBook run: 17 diff verifiers mean $0.498 and median 9.5 min vs 23 full L2 mean $0.479 and median 8.2 min; different tickets and hours, not controlled (`docs/reports/2026-10-29-sdlc-retro-macbook-pro/ultimate-tokens-color-science-attempts.jsonl`; `docs/reports/2026-10-29-sdlc-retro-macbook-pro.md` Finding 8).
- T-0248: a diff verifier passed a change that broke an untouched test; the land gate caught it (`docs/reports/2026-10-29-sdlc-retro-macbook-pro.md` Finding 9).
- `SCOPE_DIFF` in `plugins/sdlc-lite/scripts/dispatch.py`.

## Constraints
- Measure first on this repo's own `runs.jsonl` (diff vs full verifier cost and wall on comparable L2 tickets) and state the numbers in the Outcome.
- Smallest change that the numbers support; keep the `escalate: full` route.
- outcome metric: mean verifier cost and median wall, diff vs full, before: $0.498 / 9.5 min vs $0.479 / 8.2 min.
