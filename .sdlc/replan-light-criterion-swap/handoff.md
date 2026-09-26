---
id: T-0123
title: "Plan defects: criteria stable across main syncs, and apply the verifier's replacement criterion without a full replan"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P1         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
Plan defects stop fewer lanes.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui, overnight lanes on 0.11.1 (ids in parentheses are gen-ui's).

Plan defects were the #1 stop cause overnight, 8 in total. (a) Literal criteria go stale after a main sync: T-0152 required an exact `children: [..]` line that main later extended. The planner should prefer membership or structure checks for generated or shared files. (b) Guards that can't go red: a wrong cache dir (T-0163), `vitest list` without `--filesOnly` (T-0197), and a runtime check whose red state doesn't reproduce. (c) The verifier's `plan defect:` note usually proposes a replacement criterion. The conductor could apply it to the step handoff and rebuild, without a full planner L3 replan. That needs a rule for when a swap is safe.

## Constraints
The failing test lands before or with the fix, never after.
