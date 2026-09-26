---
id: T-0117
title: "fanout.py closes tickets with a plain close <slug>, so in a..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0113
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0113 (close-rename-breaks-refs/filer-L1.md):

`fanout.py` closes tickets with a plain `close <slug>`, so in a numbered-mode repo a reference hit ends the ticket as `merged, close refused` and leaves it open until someone reruns with `--rewrite-refs`.

## Constraints
What must not change. "None" if none.
