---
id: T-0517
title: "Codex solo L1 follows the shifted builder ladder: gpt-6.1-sol medium"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0516]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The Codex solo ladder follows the Codex builder ladder shifted down one: solo L1 gpt-6.1-sol medium (was low), L2 sol high and L3 sol xhigh unchanged. Maintainer decision 2026-10-12 ("yes", after T-0516).

## Intent
- Do: in `plugins/sdlc-lite/adapters/codex/models.json` set `solo.L1` to `["gpt-6.1-sol", "medium"]`; update what pins the old row: `scripts/check.py` `SOLO_CODEX` (about line 762, its negative control at about 778) and the item text, `scripts/codex-selftest.py` (about line 643, tier L1 effort), `agents/solo.md` Codex row if it states the effort, the level rubric solo text; regenerate with `codex_roles.py generate`; add a new eval later than the T-0516 eval (`evals.py add`, then `evals.py lock --eval`) recording the decision and that no replay ran.
- Non-goals: Claude rows (T-0516), any other Codex role.
- Done when: `codex_roles.py generate --check`, `codex-selftest.py`, `evals.py check`, `check.py` and `check-packaging.py` exit 0 (check.py may fail only on the unrelated progressive-context link); the `SOLO_CODEX` negative control observed red against the old row before the change.

## Context
Builder Codex ladder: L1 Sol low, L2 medium, L3 high, L4 xhigh, L5 max (commit 266cb9dc). Solo Codex today: L1 low, L2 high, L3 xhigh.

## Constraints
Model and effort are the maintainer's decision: change nothing beyond the one row. One writer on the model tables; run after T-0516 merges.

## Closed

2026-10-12: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full
