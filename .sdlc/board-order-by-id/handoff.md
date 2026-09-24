---
id: T-0017
title: "Board order matches the roadmap"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
/board can list tasks in the same order as the roadmap (by ticket id, or by folder name) instead of by recency.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Requested by the setup-sdlc-lite-generative-ui session. `scripts/board.py` sorts task dirs by `st_mtime`, so with numbered folders the board reads 0002, 0003, 0005, 0008 (recency) while the roadmap reads by id. Suggested: a sort option (id or name), possibly the default when tickets exist. Relates to T-0015 (board hides closed tickets).

## Constraints
What must not change. "None" if none.
