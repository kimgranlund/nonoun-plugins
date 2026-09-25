---
id: T-0050
title: "Dot-prefix closed ticket folders"
type: feature        # feature | bug | chore | spike | idea
status: done
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0049]          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
In numbered mode, closing a ticket renames `.sdlc/NNNN-slug/` to `.sdlc/.NNNN-slug/` so Finder and `ls` hide finished work, and every tool still treats it as a closed ticket.

## Intent
- Literal ask: in numbered mode, `close` renames `.sdlc/NNNN-slug/` to `.sdlc/.NNNN-slug/`; every tool keeps treating it as a closed ticket.
- Do: tickets.py (`new` id allocation, `close`, `roadmap`, `check`, `depends` resolution), board.py, and steps.py recognize `.NNNN-<slug>` dirs (dot, 4 digits, dash) as closed tickets. `close --numbered` (or config numbered) renames after setting done. `check` fails on a dot ticket folder whose status is not done or dropped. New one-shot `tickets.py archive` renames existing done/dropped numbered folders to the dot form (supports `--dry-run`). Selftests cover each new check failure and the rename paths. Update docs that describe this behavior (CLAUDE.md Layout tickets.py line, handoff-format SKILL.md, ticket SKILL.md, sdlc-lite-author agent if it lists tickets.py behavior).
- Non-goals: plain (unnumbered) mode behavior; a `done/` subfolder; renaming non-ticket dot dirs.
- Done when: in a numbered temp root, `close` produces `.NNNN-slug/`, `roadmap` still lists it, a `depends` on it resolves, `new` does not reuse its id, `board.py` shows or hides it per its existing done rules, `check` fails on a dot folder with status ready; `_templates` and `.board-state.json` stay skipped; `scripts/check.sh` passes.
- Gaps (unattended, not blocking): whether `/file` should pass `--numbered` explicitly (default: config line decides); whether `archive` also moves `dropped` (default: yes, both are closed).

## Context
Requested by the setup-sdlc-lite-generative-ui session for gen-ui-system-svelte-lite; that user chose this over a done/ subfolder. Today tickets.py skips any dir starting with `_` or `.` (line 96 in 0.4.2), so a dot folder drops out of the roadmap, a `depends` on it looks unresolved, and the next id can reuse its number. Expected: tickets.py (new, close, roadmap, check, depends), board.py and steps.py treat `.NNNN-*` as a closed ticket; `_templates` and `.board-state.json` stay skipped; `check` fails on a dot folder whose status is not done or dropped; a one-shot `tickets.py archive` renames existing done folders. Numbered mode only, opt-in; plain mode unchanged. Build after T-0049, which changes how the same scripts read task dirs.

## Constraints
Plain mode unchanged. `_templates`, `.board-state.json`, and other non-ticket dot/underscore entries stay skipped. Existing selftests keep passing. Never commit or push.

## Triage
2026-09-24, user-approved: build now; T-0049 has landed.
