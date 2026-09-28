---
id: T-0021
title: "Decide whether /board should default to --sort id when tasks have..."
type: idea            # feature | bug | chore | spike | idea
status: done
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0017
---

## Goal
With no `--sort` flag, `scripts/board.py` orders by ticket id whenever at least one rendered task has ticket front matter; tasks without a ticket id follow, in recency (mtime) order. With no ticketed task the default stays recency. An explicit `--sort recent|id|name` still overrides and behaves exactly as today. Done when the selftest proves both default branches and the docs describe the new default.

## Context
Follow-up from T-0017 (board-order-by-id/filer-L1.md):

Decide whether `/board` should default to `--sort id` when tasks have tickets (T-0017 kept `recent` to leave /chain and the statusline unchanged)

## Constraints
- Explicit `--sort id` keeps its current order (unticketed after, by folder name); `--sort recent` and `--sort name` unchanged.
- `--summary` output (statusline) and `--task` renders (/chain) unchanged.
- Records that describe the default must be updated in the same change: `skills/board/SKILL.md` (and its argument-hint if needed), repo `CLAUDE.md` Feed bullet, `.claude/agents/sdlc-lite-author.md` if it mentions the sort default.
- `scripts/check.sh` passes, including `board.py selftest`.

## Decision
2026-09-24, user: yes. When at least one rendered task has ticket front matter, /board sorts by ticket id by default (tasks without a ticket keep recency order after them); `--sort` still overrides. Build this.
