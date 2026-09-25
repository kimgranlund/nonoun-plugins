---
id: T-0042
title: "Document long role runs in interactive sessions"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S
priority: P1
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
The docs for /chain, /bench and the conductor say how to run a role that takes longer than the Bash tool's 10-minute cap in an interactive session.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. skills/chain, skills/bench and agents/conductor say to run every role in the foreground with timeout 600000 and never end the turn, but a bench task's full /chain takes 15 to 30 minutes. `scripts/bench.sh` raises BASH_DEFAULT_TIMEOUT_MS/BASH_MAX_TIMEOUT_MS for headless runs, but an interactive session can't. Suggested: foreground only in headless sessions; in interactive sessions run in the background and wait for the completion notification (never poll with sleep), with both cases documented.

## Constraints
The failing test lands before or with the fix, never after.
