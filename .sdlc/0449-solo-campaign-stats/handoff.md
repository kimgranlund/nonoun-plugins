---
id: T-0449
title: "Committed solo lane stats script and a KPI with a baseline"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A committed, repeatable measure of how the solo lane performs across the fleet (closed rate, first-pass verifier rate, rounds to pass, priced cost per solo ticket), with a KPI file and a dated baseline.

## Intent
- Do: add a read-only script (extend `fleet_collect.py` with a `solo` block, or a new `solo_stats.py` with the same fingerprint style) that, for a repo and a `--since` date, counts solo tickets (a ticket folder whose `runs.jsonl` has a `solo` role row in the window; hidden closed `.NNNN-*` folders included, worktree copies excluded), closed versus open, verified versus no verifier (docs-only skip and L1 default), first-round verifier pass, ended-in-pass, multi-round tickets (verifier result files ordered `verifier-L2.md`, `-2`, `-3` by round number, not by name), closed without a final pass, and priced cost and minutes per solo run with the unmetered count stated. Add `docs/kpi/005-solo-first-pass-rate.md` (command, unit, target, goal served, `before` from the baseline) and, if a goal fits, cite it in `docs/goals/`. Selftest with a fixture repo and an observed-red control per count (a name-ordered round mistake, a worktree copy, a hidden closed folder).
- Non-goals: judging whether a pass meant the intent was met; a solo-versus-chain comparison (separate report); changing any role.
- Done when: the selftest passes with observed-red controls; `fleet_collect.py` or the new script run on this repo reports the same counts as the 2026-10-11 hand tally in `docs/reports/2026-10-11-solo-campaign-baseline.md` (166 solo tickets, 122 closed, 123 verified, 89 first-pass, 107 ended in pass, 32 multi-round across ui-kit-maison, agent-ui, ultimate-tokens and sdlc-lite since 2026-10-08); `check.sh` exits 0.
- outcome metric: K-005 (docs/kpi/005-solo-first-pass-rate.md), before: 89 of 123 first-pass (72 percent), 107 of 123 ended in pass (87 percent)

## Context
Tally method and caveats: `docs/reports/2026-10-11-solo-campaign-baseline.md` (written with this ticket). Existing collector: `plugins/sdlc-lite/scripts/fleet_collect.py`, KPIs `docs/kpi/001` to `004`. Cost is unmetered for most non-sdlc-lite solo runs (K-001; T-0446 fixes pricing for new runs).

## Constraints
Read-only against every repo it inspects. No model call. State unpriced runs; never estimate cost.
