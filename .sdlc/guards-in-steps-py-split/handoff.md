---
id: T-0083
title: "Guards in steps.py split --only N really execute, so a guard..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0062
---

## Goal
`steps.py split --only N` refuses, with a `plan defect:` last line, when running a step's `(guard)` criteria changed the git work tree (tracked or untracked files), so a side-effecting guard is caught by code, not only by the planner prompt. The selftest proves the refusal fires and that a guard which changes nothing still passes.

## Context
Follow-up from T-0062 (criteria-that-contradict-each-other/filer-L1.md):

Guards in `steps.py split --only N` really execute, so a `(guard)` criterion with side effects now changes the tree before the build; only the planner prompt forbids that, and no code check does.

## Constraints
- Full `split` and `lint` still execute nothing; the existing `(n)` selftest cases keep passing.
- Detection compares the tree before and after the guards (for example `git status --porcelain --untracked-files=all` from the git toplevel); outside a git work tree (the selftest's task dir) behave as today, with no new refusal.
- A tree that was already dirty before the guards is fine; only a change caused by the guards refuses. Do not try to undo the guard's change: report it (the paths) and refuse, writing no step handoff.
- Keep the docs that describe `split --only N` in step: steps.py usage text, CLAUDE.md Layout and Decisions, `.claude/agents/sdlc-lite-author.md` if it describes guards, `skills/chain/SKILL.md`, and `agents/planner.md` where it tells the planner guards must be side-effect free.
- `scripts/check.sh` stays green. Never commit, push, or publish.

## Clarify (unattended)
Gap named, not blocked: the ticket left the Goal blank; the conductor filled it from the Context. Undo is out of scope (refuse and report only).
