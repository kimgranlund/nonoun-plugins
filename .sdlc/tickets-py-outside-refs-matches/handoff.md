---
id: T-0128
title: "tickets.py outside_refs matches folder paths by fixed-string..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0116
---

## Goal
`tickets.py` close and archive (numbered mode) report and rewrite only citations of the ticket's own folder: a literal `<rel>/<slug>` that continues into a longer folder name (for example `.sdlc/0001-a` inside `.sdlc/0001-ab`) is neither reported by `outside_refs` nor rewritten by `rewrite_files`. Done when a selftest case proves a file citing only `.sdlc/0001-ab` does not block or get rewritten when `0001-a` closes, and a file citing both gets only the `0001-a` cite rewritten.

## Context
Follow-up from T-0116 (tickets-py-archive-renames-done/filer-L1.md):

`tickets.py outside_refs` matches folder paths by fixed-string prefix, so `.sdlc/0001-a` also matches `.sdlc/0001-ab`. `close` and `archive` can report or rewrite a citation of a different folder that shares the prefix.

## Constraints
All existing tickets.py selftest cases and `scripts/check.sh` stay green. Keep the documented reference forms (literal `<rel>/<slug>` followed by `/`, end of token, or punctuation; toplevel-relative, file-relative, and absolute path tokens). Update the tickets.py docstrings and the CLAUDE.md / sdlc-lite-author notes on the scan in the same change if their wording changes.
