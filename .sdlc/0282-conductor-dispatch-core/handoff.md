---
id: T-0282
title: "Conductor and chain dispatch roles as sub-agents"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0276, T-0278, T-0279, T-0280, T-0281]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The conductor, chain, fix, level-rubric, and handoff-format texts replace "run run.sh" with prepare, Agent spawn, record; this is the flip that makes sub-agents the Claude mode.

## Intent
- Do: Conductor and chain dispatch roles as sub-agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `agents/conductor.md`, `skills/chain/SKILL.md`, `skills/fix/SKILL.md`, `skills/level-rubric/SKILL.md`, and `skills/handoff-format/SKILL.md` name `dispatch.py prepare`, the `Agent` spawn with `name`, `model`, and `run_in_background`, and `dispatch.py record`; none tells the conductor to run `run.sh` for the Claude backend.
  - `check.py` guards (items 4, 11, 21 and a new dispatch item) pass and each new phrase guard has a negative control (phrase removed, check fails).
  - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` passes after regeneration; the Codex path text is unchanged in meaning.
  - A throwaway-project run of one `/fix` item through the conductor produces a recorded builder and verifier result with `transport: subagent`, and `steps.py next` reads them (evidence pasted in the ticket).

## Context
Design sections 1, 4, 8. Land only after the hook gate (G) so conductor spawns are not denied. The headless conductor rules (`SDLC_HEADLESS`) keep foreground spawns.

## Constraints
Do not remove run.sh or its Claude branch in this ticket. No em dashes. No push, tag, or publish.
