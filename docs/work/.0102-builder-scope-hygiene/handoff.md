---
id: T-0102
title: "Builders format only changed files and never pkill by pattern"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Builders never touch files or processes outside their own work.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui, 2026-09-25: about 20 builder stops across 12 gen-ui-system-svelte-lite lanes in one day. Each class cost a stop plus a conductor decision. Ticket ids in parentheses are gen-ui's.

1. Formatters run only on files the builder changed. A repo-wide `prettier --write` dirtied generated files (T-0104).
2. Builders never `pkill` or `killall` by pattern; they stop only the PIDs they started. A pattern kill took down another session's `vite dev` (T-0009). This could also be enforced in a hook, like block-publish.

## Constraints
The failing test lands before or with the fix, never after.
