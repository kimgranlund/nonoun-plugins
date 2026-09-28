---
id: T-0155
title: "Run id on every lane and gate log line"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
Every lane, fanout, and gate log line names the run that wrote it, so a line from an earlier run never reads as a new failure.

## Intent
- Do: generate a run id per run.sh and fanout invocation, export it as SDLC_RUN_ID, and prefix it on each log line those scripts write.
- Non-goals: rewriting old logs.
- Done when: a selftest resumes a stopped run and shows the old STOPPED line and the new lines carry different run ids.

## Context
From gen-ui batch 3 item 14. Prerequisite for review-sdlc-traces (T-0157), which joins events by run id.

## Constraints
None.
