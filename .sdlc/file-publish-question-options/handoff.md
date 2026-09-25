---
id: T-0067
title: "/file step 4 publish question exceeds AskUserQuestion's 4-option limit"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
The /file publish question is valid on the first call.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Live T-0047 run: the step 4 AskUserQuestion failed twice with `Invalid tool parameters` (5 options, then a 1-option question) before a 4-option multiSelect worked. Fix: step 4 names at most 4 options (commit, push, PR, changelog), with the GitHub-issues item folded in or asked separately only when it applies.

## Constraints
The failing test lands before or with the fix, never after.
