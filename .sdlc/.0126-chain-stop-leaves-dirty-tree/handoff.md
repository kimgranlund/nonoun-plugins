---
id: T-0126
title: "A chain that stops mid-step leaves the tree dirty and blocks the next sync merge"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
A stopped chain never blocks the next sync.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui, overnight lanes on 0.11.1 (ids in parentheses are gen-ui's).

Uncommitted builder output blocked the next sync merge twice ("commit your changes before you merge"). Proposal: when /chain or fanout stops mid-step, it leaves a WIP commit on the lane branch (never on main), or a tagged stash. It must match the builder no-commit rule, since the chain commits, not the builder.

## Constraints
The failing test lands before or with the fix, never after.

## Intent
Literal ask: "when /chain or fanout stops mid-step, it leaves a WIP commit on the lane branch (never on main), or a tagged stash. It must match the builder no-commit rule, since the chain commits, not the builder."
Root goal: a lane whose chain stopped mid-step never blocks the next sync merge into that lane, and the stopped work is kept for inspection.
Deltas:
- Repro/Expected/Actual blank: defaulted: in `scripts/fanout.py` `run_ticket`, a nonzero driver exit returns `driver failed rc=N` and leaves the builder's uncommitted edits in the lane worktree; any later `git merge --ff --no-edit <integration>` in that lane (a resync, a rerun on the lane, a manual sync) refuses with "commit your changes before you merge". Expected: the lane tree is clean after any stop.
- WIP commit vs tagged stash: defaulted: WIP commit on the lane branch. The git stash stack is shared by every worktree and session, so a stash can be popped by another lane; a commit on the lane branch is isolated and inspectable. (gap: user preference unrecorded; default: WIP commit.)
- Who commits: defaulted: fanout.py (the script, running as the lane's chain owner) makes the WIP commit, never the builder or the headless conductor; the builder no-commit rule and the conductor's "never commit" prompt stay unchanged.
- Which stops: defaulted: every lane outcome after the driver ran that is not `merged` and leaves the lane tree dirty (driver nonzero exit at minimum). Also, before each sync, a lane tree that is already dirty is WIP-committed first rather than failing the merge.
- WIP commit is never merged: defaulted: the stop outcome stays a stop (lane marks the rest `skipped`, exit 1), the WIP commit is never merged into the integration branch, the report names its short sha, and the message is `wip(<id>): <outcome>`.
- Plain /chain outside fanout (on main or a user branch): defaulted: out of scope for code; no commit on main ever. The /chain and /fanout skill text and CLAUDE.md fanout description are updated to say where stopped work lands.
Do: in `scripts/fanout.py`, after a driver stop (and before a sync when the lane is dirty), `git add -A` and commit `wip(<id>): <outcome>` on the lane branch in the lane worktree only, record the sha in the report, never merge it; add selftest cases (failing first): a stub driver that edits a file and exits nonzero leaves a clean lane tree with a `wip(` commit on the lane branch, the integration branch and main untouched; update the module docstring, `skills/fanout/SKILL.md`, and the CLAUDE.md fanout bullet (and `.claude/agents/sdlc-lite-author.md` if it restates it) to match.
Non-goals: stash-based capture; changing builder or conductor commit rules; committing on main or the integration branch; auto-resuming a stopped lane.
Done when: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` passes with the new cases (which fail on the pre-change code), and `plugins/sdlc-lite/scripts/check.sh` passes.
