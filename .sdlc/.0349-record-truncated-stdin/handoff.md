---
id: T-0349
title: "dispatch.py record uses the transcript's final message when stdin is truncated, and keeps error stdin as a failure"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Verifier findings 3 and 4

## Intent
- Do: Verifier findings 3 and 4. In record, the transcript is consulted only when stdin has no '## ' heading, so (3) a notice truncated after its first heading is recorded as the artifact, and (4) stdin that is an error (for example 'Error: session limit reached') is overridden by any transcript message with a heading, so a 429 after an interim '## Status' message closes the attempt as done and writes no .limit marker (v0.21.1 recorded a failed attempt and the marker). Fix: compare stdin with the transcript's final text message: use the transcript when stdin is empty, is a strict prefix or truncation of it, or lacks the declared sections; treat stdin that matches an error pattern (session limit, rate limit, 429, Error:) as a failure with the .limit marker as before. Add the missing selftests (truncated stdin, error stdin plus an interim heading transcript, and a transcript with tool-use turns before the final text), each failing on the current main.
- Non-goals: model or effort changes; anything outside the named scripts and skills.
- Done when:
  - record handles complete stdin, empty stdin, truncated stdin and error stdin correctly (observed, failing on the current main first).
  - check.py, tickets.py check, fanout, dispatch and solo_run selftests and `codex_roles.py generate --check` pass.

## Context
Independent verifier verdict on T-0343 to T-0348 (.sdlc/verify-maisonfix/verdict.md, Fable, 2026-10-07), findings numbered there.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
