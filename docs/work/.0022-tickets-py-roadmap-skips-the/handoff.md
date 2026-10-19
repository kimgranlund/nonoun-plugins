---
id: T-0022
title: "tickets.py roadmap skips the numbered prefix/id check, so with..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0016
---

## Goal
`tickets.py roadmap` refuses to write the roadmap whenever `check` would fail on a ticket problem, including the numbered-mode NNNN-/id prefix rule, so the two commands never disagree on what a valid ticket set is.

## Context
Follow-up from T-0016 (ticket-numbered-folders/filer-L1.md):

tickets.py `roadmap` skips the numbered prefix/id check, so with `ticket_folders: numbered` set it can rebuild the roadmap while `check` fails

Code facts (conductor, from reading the source):
- `plugins/sdlc-lite/scripts/tickets.py` `cmd_roadmap(root)` (~line 450) calls `problems(ts)` with no `numbered`, while `cmd_check` uses `numbered = numbered or config_numbered(root)` and `problems(ts, numbered)`. `new` and `close` already take `--numbered` and read `<root>/config`.
- The usage docstring (top of tickets.py) says roadmap "refuses on any ticket problem"; the argparse subparser for `roadmap` (~line 882) takes no flags.
- `selftest` (~line 489 on) covers numbered mode; a block near line 677 renames folders and regenerates the roadmap, so check it still holds.
- Docs that describe the roadmap/numbered behavior: `plugins/sdlc-lite/skills/ticket/SKILL.md` (argument-hint and body), repo-root `CLAUDE.md` (Layout, tickets.py bullet), `.claude/agents/sdlc-lite-author.md`. Stale docs are a defect: update any that the change makes wrong.
- Gate: `plugins/sdlc-lite/scripts/check.sh` must pass (it runs the tickets selftest).

## Constraints
- Plain-slug mode (no `--numbered`, no config line) behaves exactly as today.
- `tickets.py` stays the only writer of roadmap.md; no new dependencies.
- The roadmap output format does not change.
- Never commit, push, or publish.
