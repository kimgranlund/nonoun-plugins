---
id: T-0073
title: "A verifier result with no verdict is counted as a fail and burns a retry"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A verifier output with no pass/fail verdict is reported as an error (no verdict), reruns the verifier, and never counts as a build fail.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui (T-0044 step 5, 0.7.0): verifier L2 returned only "Nothing to do until the test gate reports." and /chain recorded it as fail 1, burning a retry and moving toward a level bump. Ask: run.sh or /chain treats a verifier result without a verdict line as `no verdict`.

## Constraints
The failing test lands before or with the fix, never after.
