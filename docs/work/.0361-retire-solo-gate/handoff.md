---
id: T-0361
title: "Finish the headless retirement: gate solo_run --exec, make the check.py guard bite, repair stale text"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The Claude headless path is retired for solo lanes too: `solo_run.py run --exec` on the Claude backend refuses without `SDLC_CLAUDE_EXEC=1`, the check.py guard for it bites, and no text still describes the old default.

## Intent
- Do: the three fixes from the independent verifier of T-0288 (.sdlc/verify-retire-solohigh/verifier-L3.md, "For the next attempt"). (1) Gate the solo headless path like the conductor one: `plugins/sdlc-lite/scripts/solo_run.py` `run --exec` on the Claude backend exits 2 with one line pointing to `fanout.py prep` / `dispatch.py prepare` unless `SDLC_CLAUDE_EXEC=1`, or `fanout.default_driver` applies the gate before `solo_command` (fanout.py around 472-473); the solo_run and fanout selftests opt in (fanout.py:1899 already does) and gain a refusal case with an observed-failing-first negative control. (2) Make the check.py item 21 fanout guard bite: require `SDLC_CLAUDE_EXEC` inside the `default_driver` body (check.py around 748-753), not anywhere in fanout.py; deleting the gate lines in fanout.py must turn check.py red (observe it). (3) Repair stale text: fanout.py:3439 (`--driver` help) and :136 and :468, skills/fanout/SKILL.md:16 and :29, agents/solo.md:38 then `claude_roles.py generate` and `codex_roles.py generate`, solo_run.py:12-13, docs/references/sdlc-internals.md:21, 95, 97, 99 (line 5: `SDLC_BACKEND` defaults to `claude` and that branch refuses without the legacy flag).
- Non-goals: any model or effort change; anything beyond these three fixes.
- Done when:
  - `solo_run.py run --exec` with the flag unset on the Claude backend exits 2 with the one-line pointer, with the flag set it starts as before (selftests cover both); the fanout lane path (`fanout.py prep`/`land`, `--driver CMD`) is unaffected.
  - Deleting the default_driver gate makes check.py fail (observed), restored it passes.
  - `grep -rn "legacy default\|until T-0288" plugins docs/references` finds no stale statement (dated reports stay history).
  - check.py, tickets.py check, both generate --check, run-selftest.sh, solo_run, fanout and dispatch selftests, and check.sh pass.

## Context
T-0288 merged in dc4f32aa; its verifier failed three criteria (this ticket). T-0360 passed. This is the one allowed replan.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
