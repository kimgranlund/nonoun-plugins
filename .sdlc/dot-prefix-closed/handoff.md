---
id: T-0050
title: "Dot-prefix closed ticket folders"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0049]          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
In numbered mode, closing a ticket renames `.sdlc/NNNN-slug/` to `.sdlc/.NNNN-slug/` so Finder and `ls` hide finished work, and every tool still treats it as a closed ticket.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Requested by the setup-sdlc-lite-generative-ui session for gen-ui-system-svelte-lite; that user chose this over a done/ subfolder. Today tickets.py skips any dir starting with `_` or `.` (line 96 in 0.4.2), so a dot folder drops out of the roadmap, a `depends` on it looks unresolved, and the next id can reuse its number. Expected: tickets.py (new, close, roadmap, check, depends), board.py and steps.py treat `.NNNN-*` as a closed ticket; `_templates` and `.board-state.json` stay skipped; `check` fails on a dot folder whose status is not done or dropped; a one-shot `tickets.py archive` renames existing done folders. Numbered mode only, opt-in; plain mode unchanged. Build after T-0049, which changes how the same scripts read task dirs.

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: build now; T-0049 has landed.
