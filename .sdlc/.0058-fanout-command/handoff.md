---
id: T-0058
title: "/fanout command for parallel lanes, with per-lane board view"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0055, T-0056, T-0059]          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Running ticket lanes in parallel needs no hand-written driver.

## Intent
- Do: add `/fanout <lane>=<ids>...`: a script (`scripts/fanout.sh` or .py) that makes one worktree per lane, starts one headless conductor per lane (`claude -p --agent sdlc-lite:conductor ...`), syncs each lane from the integration branch before each ticket, runs /chain and /file, then merges each lane into an integration branch `fanout/<date>` under a lock, runs the gates there, reverts the merge on red, and closes tickets there. Add `board.py --lanes`, a per-lane view read from `git worktree list`.
- Non-goals: committing to or fast-forwarding main (the user approves that once at the end); changing the default board.
- Done when: a selftest or live run on a throwaway repo shows two lanes merging into `fanout/<date>`, a red gate reverting its merge, main unchanged, and `board.py --lanes` listing both lanes; check.sh passes.

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

Today each conductor rebuilds: one worktree per lane, sync from main before each ticket, /chain, /file, merge into main under a lock, gates on main, revert on red, close on main. Suggested: `/fanout <lane>=<ids>...` in the plugin, plus board.py showing each lane.

## Constraints
- All code changes go in this worktree's `plugins/sdlc-lite/` (repo root: /Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets12). Do not edit the installed plugin at /Users/kimba/Projects/nonoun/sdlc-agents.
- The default `board.py` output must not change.
- No role commits, pushes, or publishes (except a builder on a merge step, per the merge-step template). The selftest must run in throwaway repos under a temp dir and never touch this repo's branches.
- Keep CLAUDE.md, `.claude/agents/sdlc-lite-author.md`, and the skill docs in step with any new script or flag; `scripts/check.sh` must pass.

## Decisions (user, 2026-09-25; were open)
All three recommendations below were chosen: integration branch with one user-approved main fast-forward; a script running one headless conductor per lane; `board.py --lanes`.

## Options as raised
1. Unattended commits on main. The suggested driver merges each lane into main, reverts on red gates, and closes on main with no per-merge approval. The conductor contract says a commit happens only after an AskUserQuestion approval, and the merge-step template makes the builder commit only inside a lane. Recommended: /fanout merges into an integration branch (e.g. `fanout/<date>`) with no approval, and the user approves the single fast-forward of main at the end.
2. How lanes run in parallel. Options: one headless conductor (`claude -p --agent sdlc-lite:conductor`) per lane worktree, driven by a script; or one interactive session that backgrounds run.sh per lane. Recommended: a script that starts one headless conductor per lane, since role runs cannot outlive the session otherwise.
3. Scope of the per-lane board: a lane column in board.py read from `git worktree list`, or a separate `board.py --lanes` view. Recommended: `--lanes`, leaving the default board unchanged.
