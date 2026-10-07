---
id: T-0352
title: "dispatch.py record: unmatched error stdin yields to the transcript, and a solo dispatch file ignores agent id, tool uses and duration"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
dispatch.py record treats any non-result stdin as a failure when it is not a heading-bearing report, and records agent id, tool uses and duration for a solo dispatch.

## Intent
- Do: Second verifier pass findings 2 and 4 (.sdlc/verify-maisonfix/verdict-pass2.md). (2) Error stdin that matches neither LIMIT_RE nor `^(API )?Error:` (example 'Agent terminated unexpectedly') still yields to a transcript with a complete final message and is recorded as done: widen the rule so that stdin with no declared sections is a failure unless the transcript's final message is the same text, or add an explicit `--stdin-is-notice` mode; pick the smaller change and say why. (4) `dispatch.py record` on a solo dispatch file silently ignores stdin, --agent-id, --tool-uses and --duration-ms: pass them through to `solo_run.complete` so the solo runs.jsonl row carries agent_id and duration. Also: `skills/agent/SKILL.md` step 3 (the solo row) should name the closing `dispatch.py record` step (finding 3).
- Non-goals: model or effort changes.
- Done when:
  - Selftests for error variants r6 and r6b (observed failing first) and for the solo row carrying agent_id and duration.
  - check.py, tickets.py check, dispatch, solo_run, fanout selftests and both generate --check pass.

## Context
Non-blocking findings of the second verification pass of 2026-10-07; the release shipped without them or waits per the maintainer.

## Constraints
No em or en dashes. No push or publish.
