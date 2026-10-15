---
id: T-0562
title: "Role sub-agents that background a Bash call go idle and never wake when it finishes"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role sub-agent cannot stall by backgrounding a Bash call: the call is refused or run in the foreground, so the role never sits idle waiting for a notification that does not reach it.

## Repro
1. Spawn a role sub-agent (solo, builder, or verifier) whose work includes a long check.
2. The agent runs Bash with `run_in_background: true` and then ends its turn "waiting on the notification".

## Expected
The role keeps working until it reports.

## Actual
The role goes idle; the parent must nudge it (T-0553 builder, 21 min idle, 2026-10-14; T-0558 solo, 2026-10-15), even though the brief says "Run every command in the foreground".

## Context
Brief wording did not hold twice, so a structural guard is needed. Candidate: a PreToolUse hook on Bash that, for a role session (`SDLC_ROLE` set or a role `agent_type`), denies `run_in_background: true` with a message to rerun in the foreground (long checks fit within the Bash timeout or go through `gate_lock.py run`). Mirror it in the role contracts' one line. Codex: note only.

## Constraints
The failing hook selftest (role + background denied; main session + background allowed) lands with the fix. Target 0.23.1.
