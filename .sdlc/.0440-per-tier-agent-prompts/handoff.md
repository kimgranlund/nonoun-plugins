---
id: T-0440
title: "Design: tune each agent prompt to its model and effort tier"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
How should each SDLC Lite agent prompt differ by the model and effort it runs at, and what is the smallest build that proves it pays?

## Goal
A design for how each SDLC Lite agent prompt should differ by the model and effort it runs at, so low-effort agents get direction and strong agents get a goal, KPI and budget, without changing any model or effort row.

## Intent
- Do: produce an architect design (approach, interfaces, constraints, rejected alternatives, a build split, and a measurement plan). Cover every role in `plugins/sdlc-lite/agents/*.md` and every row of `plugins/sdlc-lite/adapters/claude/levels.json` (builder L1 sonnet low through L5 fable xhigh; solo, planner, verifier, researcher and the single-row roles); the Codex rows in `adapters/codex/models.json` only to say what carries over. Answer: (1) what must stay identical at every tier (safety, output sections, hooks, red checkpoint, no push), (2) what varies: process scaffolding and gap defaults for low-effort models, Goal+KPI+budget framing for high-effort ones, (3) the mechanism: today `scripts/claude_roles.py` copies each role body verbatim into every level's generated definition; weigh a per-tier overlay file appended at generation time against alternatives (one body with conditional sections, per-row bodies, no change), including `generate --check`, `check.py` parity, `codex_roles.py` and the Codex adapter, (4) how to prove it: a replay A/B on a fixed ticket set with named measures (cost, first-pass rate, blocked rate, verifier minutes) and what result would make us drop the idea, (5) the smallest first build that is worth shipping.
- Non-goals: changing any model or effort row (user decisions); building anything; editing agent files.
- Done when: the architect result names a recommended approach, the rejected ones, the first build ticket with its files and checks, and the measurement.

## Context
Hypothesis from the maintainer: a simple builder on sonnet low needs more direction, while opus and fable agents can be goal and KPI based and more open ended. Evidence so far (observations, not an A/B): in the 2026-10-11 plan-doc live run and rehearsals, Sonnet low drivers followed the run rules literally and stopped at every gap with no rule (reports: `docs/reports/2026-10-11-plan-doc-live-run.md`); the L4 full chain cost $359 against $33 for solo runs in ultimate-tokens (`docs/reports/2026-10-09-l4-full-chain-cost-replay.md`); verifier minutes are long (`docs/reports/2026-10-10-verifier-minutes.md`); the close-first doctrine (T-0428) tells every role to aim at a closed ticket and not to verify what needs no verification. Strong models' failure so far is over-diligence, not missing rules. `agents/builder.md` is 46 lines with 11 numbered rules shared by builder L1 to L5. Read `AGENTS.md` and `plugins/sdlc-lite/AGENTS.md` first; `docs/specs/sdlc-lite/pillars.md` (performance, cost, quality, resilience) is the yardstick. Cost data: `fleet_collect.py` fingerprints under `.sdlc/fleet-retro-*`.

## Constraints
Model and effort defaults stay as they are. Hard invariants (no push or publish, tmp worktree prefix, result sections and `results.py` schema, hooks, red checkpoint) do not vary by tier. Generated agent files are never hand-edited.

## Closed

2026-10-11: design done: architect-L1.md; build split filed as three tickets
