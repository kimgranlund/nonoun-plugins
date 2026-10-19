---
id: T-0017
title: "Board order matches the roadmap"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
/board can list tasks in the same order as the roadmap (by ticket id, or by folder name) instead of by recency.

## Intent
- Do: add `--sort {recent,id,name}` to `plugins/sdlc-lite/scripts/board.py`. `recent` is today's st_mtime order. `id` orders ticketed tasks by ticket id (numeric part of `T-NNNN`, read with the existing front matter parser), then tasks with no ticket id by folder name. `name` orders by folder name. Cover each mode in `board.py selftest`, and document the flag in `skills/board/SKILL.md` (argument-hint and step 2, pass `--sort` through when given).
- Non-goals: changing the default order (stays `recent`; making `id` the default when tickets exist is a later call for the user); dependency (roadmap) ordering; `--summary` behavior.
- Done when: `board.py --sort id` lists T-0002 before T-0003 regardless of mtime; `--sort name` lists folders alphabetically; no flag gives the same output as before; `board.py selftest` covers all three modes and passes; `scripts/check.sh` passes.
- Gap (unattended, decided conservatively): the default. Kept as `recent` so /chain and the statusline see no change.

## Context
Requested by the setup-sdlc-lite-generative-ui session. `scripts/board.py` sorts task dirs by `st_mtime`, so with numbered folders the board reads 0002, 0003, 0005, 0008 (recency) while the roadmap reads by id. Suggested: a sort option (id or name), possibly the default when tickets exist. Relates to T-0015 (board hides closed tickets).

## Constraints
Default board output unchanged. Board stays render-only (no hand tables). Python stdlib only.
