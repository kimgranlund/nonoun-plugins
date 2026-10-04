---
id: T-0214
title: "Per-ticket cost budget: budget.py, run.sh exit 4, board column"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L
priority: P2         # P1 | P2 | P3
depends: [T-0187, T-0199, T-0212]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Meter spend per ticket and stop to ask at 80 percent of a budget set at filing from the risk tier.

## Intent
- Do: Section D. Optional front matter `budget_usd` (tier defaults S $5, M $30, L $60, XL none, confirmed by the user 2026-10-04; stop and ask at 80 percent; editable per ticket), set at filing by `budget.py set <ticket> --tier S|M|L` and the ticket skill. `scripts/budget.py`: `status <ticket dir>` prints spend, budget, percent, state (ok, warn at 80, over at 100) and `unmetered_runs: N`, exit 0 ok, 3 warn or over, 2 no budget (internal codes); `ack <ticket dir> --usd N --reason TEXT` writes budget-ack.md raising the ceiling once; `ticket_of(handoff dir)` walks up from a step or superseded step dir to the nearest handoff.md with front matter, bounded by the .sdlc root. Spend is cost_usd summed recursively over every runs.jsonl under the ticket, deduplicated by attempt_id; null cost counts 0 and is reported unmetered; Codex runs record no cost, so the meter covers Claude roles only (the entry file says so). `run.sh`, before `exec run_lifecycle.py`, exits 4 (3 already means invalid result) with `run.sh: budget <pct>%: ask the user; budget.py ack` when status is warn or over with no later ack; T-0199 stop rule (d) turns exit 4 into one question. `board.py` gains a Budget column rendered only when some task's ticket has budget_usd (gated like ID and Ticket; default output byte-identical), values from `budget.py status`. tickets.py is not edited.
- Non-goals: changing any model or effort default; conductor wording beyond a pointer line; a version bump, tag, push, or publish.
- Done when: the changes are built, an independent verifier passed each step, and selftest with seeded run records: under 80 ok, at 80 warn (exit 3), over 100 over, a duplicated attempt_id counts once, a null cost is unmetered, a superseded-dir run counts, no budget exits 2; negative controls: run.sh with a seeded warn and no ack exits 4 before any model call, with an ack it launches, a ticket with no budget launches unchanged, board default output with no budget is byte-identical; live: a ticket seeded at 85 percent shows the single question on Claude. `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Cost-control addendum to the lean SDLC design: `docs/lean-sdlc/cost-control.md` v0.2, reviewed in `docs/validation/lean-sdlc-cost-control-review.md`. Measured on 2026-10-04: about $190 over 78 role runs, 4 of 7 plans returned for replan. Owning files and ordering: scripts/budget.py (new), scripts/run.sh (gate), scripts/board.py (column), skills/ticket/SKILL.md, scripts/check.sh, scripts/check.py, docs/maintenance/sdlc-internals.md. Waits for T-0187 (board.py), T-0199 (conductor text) and T-0212 (run.sh, run_lifecycle.py). Plan level L3: the conductor parses run.sh exit codes, so a new exit code is a parsed contract.

## Constraints
Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's (change none), no em dashes, one authoritative location for each fact, checks that can fail with a negative control. Read the design first: docs/lean-sdlc/cost-control.md (v0.2) and docs/validation/lean-sdlc-cost-control-review.md; re-read every cited line number at plan time, since T-0196, T-0197, T-0199, T-0200, T-0201 and T-0202 move them. Conductor wording is T-0199's file (agents/conductor.md): do not restate it, and edit it only as a pointer line after T-0199 merges. Merge main into the build branch before each local merge and keep both sides of check.py and check.sh conflicts. Run roles from the main checkout's run.sh in a separate worktree. No version bump, tag, push or publish.

## Update
Un-parked 2026-10-04 for the 0.20.5 release scope (user decision). Build as one handwritten step under the burn-down rules: no planner, one verifier. Pull main first; T-0212 and T-0214 share files, so build T-0214 first, then T-0212.
