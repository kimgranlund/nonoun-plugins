---
id: T-0156
title: "Keep gate logs per attempt, never overwrite"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
A retried gate keeps every attempt's log, so the first failure survives.

## Intent
- Do: write gate output to <step-dir>/gate-<attempt>.log (or equivalent) instead of one overwritten file.
- Non-goals: gen-ui's own merge train script.
- Done when: a selftest runs a gate twice and both logs exist with distinct content.

## Context
From gen-ui batch 3 item 5 (T-0365 at 07:40 lost its first failure). fanout currently names gate logs `gate-<lane>-<id>-<k>.log`, where `<k>` numbers gates, not attempts; check whether a retry overwrites the same path. The lifecycle runner preserves role logs but does not own gate logs. If no sdlc-lite script overwrites them, close as not-sdlc. Prerequisite for T-0157.

## Constraints
None.
