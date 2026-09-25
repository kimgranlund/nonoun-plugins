---
id: T-0039
title: "A defined name for superseded step dirs"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A step replaced by a replan has a defined dir name that board.py and the scripts treat as superseded, not as another step.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. /chain says to replan and continue from the blocked step but defines no convention for the old step dir. Renaming it step-15-blocked made board.py (which globs step-*) render a second "15." row, and loops that use `ls step-*` counted an extra step. Suggested: a reserved name such as step-<n>.superseded-<k>/ that board.py skips or shows as superseded, and /chain documents it. Pairs with the replan-overwrites-plan ticket.

## Constraints
What must not change. "None" if none.
