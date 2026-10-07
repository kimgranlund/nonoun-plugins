---
id: T-0113
title: "close's dot-prefix rename breaks committed references to the ticket folder"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Closing a ticket in numbered mode never leaves main with broken references to its folder.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite): `tickets.py close` renamed `.sdlc/0171-naming-symmetry/` to `.sdlc/.0171-naming-symmetry/`. A spec doc delivered by that same ticket cited the old path, so the repo's doc-path lint failed on main and every merge was red until the reference was fixed by hand. Options:
1. `close` lists tracked files that reference the old path (`git grep -lF`), and refuses without `--force`, or rewrites them.
2. Tools that resolve ticket paths accept both forms.
3. At minimum, the planner or filer warns when a deliverable cites the ticket's own `.sdlc` folder.
Recommended: 1, listing and refusing (never a silent rewrite), with a `--rewrite-refs` opt-in.

## Constraints
The failing test lands before or with the fix, never after.
