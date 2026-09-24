---
id: T-0018
title: "Recommend ignoring .sdlc/.board-state.json"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Projects that commit their .sdlc/ trail don't get a dirty tree from /board.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Requested by the setup-sdlc-lite-generative-ui session. `board.py` rewrites `.sdlc/.board-state.json` on every render; in /Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite that dirtied the tree and made a verifier fail a step's "git diff lists only docs" criterion. `skills/handoff-format` recommends ignoring all of `.sdlc/` but gives no lines for projects that commit the trail. Add recommended .gitignore lines there (at least `.sdlc/.board-state.json`, `*.running`, `*.log`), matching this repo's own .gitignore. Consider also moving the cache out of the tree.

## Constraints
What must not change. "None" if none.
