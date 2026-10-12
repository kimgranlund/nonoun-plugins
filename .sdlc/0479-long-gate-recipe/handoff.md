---
id: T-0479
title: "Long gates recipe in run-operations.md (T-0470 finding 12)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/sdlc-lite/skills/handoff-format/run-operations.md` has a `Long gates` section a role can follow: `gate_lock.py run --receipt <file> --timeout <s> -- <cmd>` with `run_in_background: true`, wait for the completion notice (never `sleep`), read the receipt and the log; a consumer sets `env.BASH_MAX_TIMEOUT_MS` in `.claude/settings.json` for a 90 minute foreground gate.

## Repro
Open `run-operations.md`.

## Expected
A `Long gates` section.

## Actual
No such section.

## Context
Origin: T-0470 investigation, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Report item 12. Facts: `hooks/block-background.sh:9-10` allows `run_in_background` for interactive roles; `dispatch.py` sets no environment, so a sub-agent keeps the 600000 ms default. The sentence in builder, verifier and solo prompts that points at the recipe is T-0461 scope. Docs only: validate with the docs checks and `check.py`.

## Constraints
Docs-only change; no prompt wording outside the recipe section.
