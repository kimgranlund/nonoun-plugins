---
id: T-0120
title: "block-publish.sh: an option that takes a separate value word before..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0097
---

## Goal
hooks/block-publish.sh scans the raw command whenever an interpreter runs inline code, even when options that take a separate value word (for example `python3 -X dev -c '...'`, `python3 -W ignore -c`, `node --require x -e`, `perl -I lib -e`, `ruby -I lib -e`) come before the inline-code flag, so a publish call inside that code is blocked inside a role run.

## Context
Follow-up from T-0097 (block-publish-sh-no-longer/filer-L1.md):

block-publish.sh: an option that takes a separate value word before the inline-code flag (for example `python3 -X dev -c '...git push...'`) stops the interpreter match, so that command keeps the masked scan and a publish call can slip through

## Constraints
`python3 script.py` (no inline-code flag) keeps the masked scan; an interpreter word inside quotes stays masked away; existing hook-selftest fixtures stay green; the CLAUDE.md and sdlc-lite-author descriptions of the hook stay accurate.
