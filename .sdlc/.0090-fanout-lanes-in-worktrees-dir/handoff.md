---
id: T-0090
title: "fanout default lanes dir becomes <toplevel>/.worktrees/fanout/<lane>"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A repo's fanout lane worktrees live inside it, under a gitignored `.worktrees/fanout/<lane>`, not in a sibling `<toplevel>-fanout` dir.

## Intent
- Do: change fanout.py's default lanes dir to `<toplevel>/.worktrees/fanout` (integration worktree at `<lanes-dir>/integration`, lanes at `<lanes-dir>/<lane>`), keep `--lanes-dir` as the override, add a preflight refusal (exit 2, naming the fix: add `.worktrees/` to .gitignore) when `git check-ignore -q .worktrees/x` fails and the default dir is used, update the selftest's default-dir expectations and add a refusal case, and repair stale docs (plugins/sdlc-lite/skills/fanout/SKILL.md, CLAUDE.md, .claude/agents/sdlc-lite-author.md) including the caveat that .gitignore does not exclude `.worktrees/` from vitest, tsc or file watchers and that Node module resolution walks up into the main tree's node_modules.
- Non-goals: editing the user-level git-bare-repo-setup skill (outside this repo; list any stale line for the user in the final report); changing lane branch naming, merge, gate or close behavior.
- Done when: `scripts/check.sh` passes; the fanout selftest proves the new default dir and the unignored-`.worktrees/` refusal; no doc in the repo still names `<toplevel>-fanout` as the default.

## Context
User request relayed 2026-09-25, following the ultimate-tokens convention. Requirements:
- fanout.py's default `--lanes-dir` becomes `<toplevel>/.worktrees/fanout`, and `--lanes-dir` stays as the override.
- Preflight refuses, naming the fix, when `.worktrees/` is not ignored (`git check-ignore -q .worktrees/x`).
- The docs (skills/fanout, CLAUDE.md) say that .gitignore does not exclude `.worktrees/` from vitest, tsc or file watchers, and that Node module resolution walks up into the main tree's node_modules.
- Update anything left stale by the sibling convention: CLAUDE.md, the sdlc-lite-author agent, and the fanout selftest's default-dir expectations. The user-level git-bare-repo-setup skill lives outside this repo, so note any stale line for the user instead of editing it.

## Constraints
What must not change. "None" if none.
