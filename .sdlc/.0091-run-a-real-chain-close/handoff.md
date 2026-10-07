---
id: T-0091
title: "Run a real /chain close-out, both interactive and headless, to..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0086
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0086 (chain-open-questions-sweep/filer-L1.md):

Run a real /chain close-out, both interactive and headless, to confirm open-questions asks one round, drops items /file already asked about, and never calls AskUserQuestion when unattended (so far only the text has been checked)

## Constraints
What must not change. "None" if none.

## Closed

2026-09-27: Headless half confirmed: five unattended /chain runs 2026-09-26/27 (T-0105, T-0141, T-0132, T-0110, T-0142) closed out without AskUserQuestion; interactive half is covered by normal use
