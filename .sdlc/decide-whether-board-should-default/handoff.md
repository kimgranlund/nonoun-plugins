---
id: T-0021
title: "Decide whether /board should default to --sort id when tasks have..."
type: idea            # feature | bug | chore | spike | idea
status: ready
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0017
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0017 (board-order-by-id/filer-L1.md):

Decide whether `/board` should default to `--sort id` when tasks have tickets (T-0017 kept `recent` to leave /chain and the statusline unchanged)

## Constraints
What must not change. "None" if none.

## Decision
2026-09-24, user: yes. When at least one rendered task has ticket front matter, /board sorts by ticket id by default (tasks without a ticket keep recency order after them); `--sort` still overrides. Build this.
