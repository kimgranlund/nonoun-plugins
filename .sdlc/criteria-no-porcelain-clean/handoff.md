---
id: T-0125
title: "Criteria use git diff plus untracked files, never a clean porcelain status"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
Criteria never require a clean porcelain status, which a no-commit builder can't meet.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui, overnight lanes on 0.11.1 (ids in parentheses are gen-ui's).

T-0232 staged 538 baselines, and its `git status` criterion could never be clean, because builders never commit. Rule for the rubric and the planner: criteria check `git diff` plus untracked files. A steps.py lint can refuse `git status --porcelain` emptiness criteria.

## Constraints
The failing test lands before or with the fix, never after.
