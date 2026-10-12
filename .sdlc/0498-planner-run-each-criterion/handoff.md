---
id: T-0498
title: "agents/planner.md: run each criterion against a reference sibling before shipping (retro 12h row 5)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The planner runs each acceptance criterion against a reference sibling (or the base tree) before it ships a plan, so a criterion that can never pass is found at planning, not at a blocked build.

## Intent
- Do: add one affirmative line to `plugins/sdlc-lite/agents/planner.md` (handle `Probe-criteria`): "Run each criterion span against the nearest reference sibling or the base tree and keep a criterion only when it can exit 0 on a correct tree." Regenerate with `claude_roles.py generate` and `codex_roles.py generate`.
- Non-goals: any other wording change (T-0461 style pass owns it); a new lint.
- Done when: a `check.py` item or `prompt_lint.py` case fails when `planner.md` lacks the handle (observed red first); `prompt_lint.py` prohibition count for `planner.md` does not rise; `generate --check` for both hosts and `check.py` exit 0.

## Context
Evidence: `docs/reports/2026-10-12-fleet-retro-12.md` row 5: agent-ui, a planner wrote a grep for an href the sitemap generator never emits; one blocked L3 build and a replan, about 45 min. Mirrors solo's Run-verbatim rule (T-0471). Planner prompt lint baseline: `docs/reports/2026-10-11-agent-prompt-lint-baseline.md` (36 prohibitions against a budget of 5; do not add one).

## Constraints
Affirmative wording, one rule per line. No model or effort change.
