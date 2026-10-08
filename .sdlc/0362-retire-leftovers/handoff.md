---
id: T-0362
title: "Headless retirement leftovers: gate before the solo return in default_driver, three stale text lines"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo lane reports the headless-retirement pointer in the fanout run report like a full lane does, and no text still describes the old Claude headless default.

## Intent
- Do: the two defects from the second verifier pass (.sdlc/verify-retire-solo-gate/verifier-L3.md, "For the next attempt"). (1) plugins/sdlc-lite/scripts/fanout.py around lines 471-482: `default_driver` returns `solo_command` before the Claude gate. Move or duplicate the gate ahead of the `kind == 'solo'` return for the claude backend (the Codex solo path stays ungated). Add a fanout selftest case beside case 15 (about line 2769) that `default_driver('h.md','solo','L1')` and `('solo','L2')` raise `Refuse` without `SDLC_CLAUDE_EXEC=1` and return the solo_run command with it, observed failing first. (2) Repair three lines: fanout.py:136-137 (the `Default: a headless conductor (claude -p --agent sdlc-lite:conductor, Opus medium)` help needs "on Claude needs SDLC_CLAUDE_EXEC=1"), skills/fanout/SKILL.md:16 (the solo lane's `claude -p --agent sdlc-lite:solo` start and "Anything else keeps the headless conductor running /chain" need the same caveat docs/references/sdlc-internals.md:95 has), docs/references/sdlc-internals.md:21 (`repoint it when run.sh is retired (T-0288)` names a retirement T-0288 did not do: say run.sh stays the Codex runner and its Claude branch is gated). Regenerate agents if any generated text changes.
- Non-goals: any model or effort change; anything else.
- Done when:
  - The new selftest case fails on the pre-change fanout.py (observed) and passes after; a two-lane `fanout.py run` without the flag (stub claude on PATH, one L1 and one L3 ticket) shows the pointer in the report row for both lanes and starts no stub.
  - `grep -n "T-0288" docs/references/sdlc-internals.md plugins/sdlc-lite/scripts/fanout.py plugins/sdlc-lite/skills/fanout/SKILL.md` shows no statement that a retirement is still to come.
  - check.py (the _fn_body guard still holds), tickets.py check, both generate --check, fanout, solo_run and dispatch selftests, and check.sh pass.

## Context
T-0288 and T-0361 are on main (acbf0125). The user authorized this one extra fix on 2026-10-08, past the replan cap, then 0.22.0.

## Constraints
No em or en dashes. No push or publish.
