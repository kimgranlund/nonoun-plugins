---
id: T-0155
title: "Attempt id on lane and gate log lines"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
Every lane and gate log line names the attempt that wrote it, so a line from an earlier attempt never reads as a new failure.

## Intent
- Do: use the existing `SDLC_ATTEMPT_ID` from the lifecycle runner and prefix it on lane and gate log lines. Define a separate identifier only for fanout lines that have no role attempt.
- Non-goals: rewriting old logs.
- Done when: a selftest resumes a stopped run and shows the old STOPPED line and the new lines carry different attempt ids.

## Context
From gen-ui batch 3 item 14. `run_lifecycle.py` already records `attempt_id` in `*.attempt.json` and normal `runs.jsonl` rows. Prerequisite for review-sdlc-traces (T-0157), which joins events by attempt id.

## Constraints
None.
