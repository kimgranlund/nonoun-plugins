---
id: T-0013
title: "close cuts follow-up titles mid-word with ..."
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Follow-up tickets created by `tickets.py close` keep a readable title: cut at a word boundary, or keep the full bullet as the title and put detail in Context.
## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
T-0007..T-0012 all have titles cut mid-word with "..." (see .sdlc/roadmap.md). The full bullet text survives in each ticket body.

## Constraints
The failing test lands before or with the fix, never after.
