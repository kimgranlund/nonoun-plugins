---
id: T-0276
title: "Claude level table and per-level generated agents"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0275]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One table (`adapters/claude/levels.json`) holds the role, level, model, effort rows; a generator writes one agent definition per row so effort comes from the definition and model from the Agent call.

## Intent
- Do: Claude level table and per-level generated agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0, and exits 1 after one generated file is edited by hand or one `levels.json` effort is changed without regenerating (observed negative controls).
  - `python3 plugins/sdlc-lite/scripts/evals.py hash` prints the same sha256 before and after the change (values unchanged; only the table home moved), and `evals.py check` passes.
  - `python3 plugins/sdlc-lite/scripts/check.py` passes with item 1 comparing levels.json, run.sh, and the level-rubric three ways; changing one effort in any one of the three makes it fail (negative control per source).
  - Every generated definition has the role body of `agents/<role>.md` verbatim, frontmatter `name`, `description`, `model`, `effort`, `disallowedTools` (read-only roles), and `skills`; `check.py` item 2 holds that every `levels.json` row has a `run.sh` case until run.sh is retired.
  - Names are `<role>-L<n>` (solo: `solo-S`, `solo-M`, `solo-L`).

## Context
Design section 1 and 8. Verifier family remap changes only the Agent `model` parameter, never the definition, so no extra definitions exist for it. Depends on the P1 probe result for `effort` frontmatter; if P1 fails, fall back to one definition per effort and say so in the ticket.

## Constraints
Model and effort values must not change (user decision). Codex files and `models.json` untouched. No em dashes. No push, tag, or publish.
