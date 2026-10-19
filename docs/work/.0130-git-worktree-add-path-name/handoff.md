---
id: T-0130
title: "git worktree add <path> <name> where <name> exists only as a remote..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0107
---

## Goal
Inside a role run, `hooks/block-stray-worktree.sh` denies every `git worktree add` form that can create a local branch, including the DWIM forms where git creates one implicitly (a `<name>` that exists only as a remote-tracking branch, and, per git docs, an omitted commit-ish, which auto-creates a branch named after the path basename), while the explicit detached form under `$SDLC_TMP_WORKTREES` still passes.

## Context
Follow-up from T-0107 (role-throwaway-worktrees-created-outside/filer-L1.md):

`git worktree add <path> <name>` where `<name>` exists only as a remote branch can make git create a local tracking branch, but block-stray-worktree treats `<name>` as a commit-ish and allows it; close this gap, or require `--detach`.

## Constraints
- The hook cannot see refs reliably before git runs, so prefer a purely textual rule (for example: require `--detach`, or allow only a commit-ish git cannot DWIM into a branch) over one that queries the repo; the planner picks and states why.
- Existing passing forms that still pass must keep passing: the detached form with a path under the prefix. Nothing changes when `SDLC_ROLE` is unset. Fail closed on unparseable commands stays.
- New fixtures in `scripts/hook-selftest.sh` for each newly denied form and the allowed form; `scripts/check.sh` green.
- Docs that describe this hook (plugin CLAUDE.md layout bullet at repo root `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md` if it describes it, `agents/builder.md` or other prompts that tell roles how to add a worktree) are updated in the same change so no role is told to use a form the hook now denies.
- Never commit, push, or publish.

## Notes from the conductor
- Prompts that show a worktree add today: `agents/builder.md` and `agents/verifier.md` use `--detach`; `agents/planner.md` (rules 3, 8, 11) and the `merge-step` template (in `agents/planner.md` and `skills/handoff-format/SKILL.md`, kept identical by `check.py`) show `git worktree add <tmp> HEAD` / `HEAD^1` without `--detach`. If the chosen rule denies those forms, update them in step, keeping the two merge-step copies identical.
