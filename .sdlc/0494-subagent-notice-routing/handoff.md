---
id: T-0494
title: "A role that spawns background sub-agents then ends its turn never wakes: completion notices go to the parent session (T-0493)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A pipeline role that delegates to sub-agents gets their results inside its own turn, so it never ends a turn waiting for a notice that goes to another session.

## Repro
1. Dispatch `architect-L1` on a handoff that asks for parallel research (T-0493, `.sdlc/0493-industry-alternatives-review/handoff.md`).
2. The architect spawns researchers with `Agent` and `run_in_background` set (or defaulted), then continues two of them with `SendMessage`, then ends its turn with "Nothing to do until the two research continuations report."
3. Watch the parent session.

## Expected
The architect waits in-turn (foreground sub-agents, or a blocking read of their output) and finishes.

## Actual
The two continuations finished at 11:4x PDT and their `task-notification` events arrived in the maintainer session, not in the architect. The architect's transcript (`agent-a0493-architect-L1-*.jsonl`) shows no notification event after its last `SendMessage` (line 132); its last write is line 138, 11:44:35. It sat idle 11 minutes until the maintainer relayed the output-file paths with `SendMessage`.

## Context
Root cause (confirmed by the transcript, one inference marked): a background sub-agent's completion notice is delivered to the top-level session that owns the task, not to the agent that spawned it. A sub-agent that ends its turn to "wait" therefore has no wake source. The architect first used named teammate spawns (lines 82 to 93, refused: "Teammates cannot spawn other teammates"), then unnamed ones (lines 96 to 99); it read the first results by polling output files with Bash (lines 111, 119), which worked, but it chose to end the turn after the `SendMessage` continuations, which have no output to poll [U on whether it had the output paths]. Nothing in `agents/architect.md` says how to wait; no script notices an idle role that has an open attempt (T-0476 flags silence after 30 minutes, here 11).

Smallest fix: one affirmative line in the shared role bodies that may delegate (`agents/architect.md`, and `researcher`/`planner` if they can spawn): "Run each sub-agent in the foreground in one parallel block and read its result in the same turn; a background sub-agent reports to the session that started you, so never end a turn to wait for one." Optional second piece: `dispatch.py status` marks a running attempt `idle` when its transcript ended on a model message with no tool call (not only silent after 30 minutes), so the conductor relays at once. Wording belongs to the controlled-language pass; this ticket adds the line and the check only.

## Constraints
Red check: a `check.py` item (or `prompt_lint.py` case) that fails when `agents/architect.md` lacks the foreground rule, observed red before the edit. Regenerate with `claude_roles.py generate` and `codex_roles.py generate`. Add no prohibition (prompt_lint budget).
