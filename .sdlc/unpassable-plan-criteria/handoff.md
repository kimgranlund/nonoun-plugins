---
id: T-0060
title: "Plan acceptance criteria that cannot pass reach the builder"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A plan criterion that cannot pass is caught before any build, and a plan defect goes to replan instead of a rebuild.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), 2026-09-24.

T-0029 step 1's criterion grep had a stray `'`, so it printed 0 whatever the file held. Builder and verifier both judged the work correct, yet /chain ran fail, fail, blocked. T-0002 step 15 had criteria that couldn't all be true at once (solution == HEAD with base == HEAD~1). Suggested: (a) the planner, or a lint step after it, runs each criterion's command once on the current tree to prove it parses and can go both ways (red now, green once done); and/or (b) when the verifier says the defect is in the plan, /chain goes straight to replan instead of rebuilding and raising the level.

## Constraints
The failing test lands before or with the fix, never after.
