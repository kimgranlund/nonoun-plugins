---
id: T-0564
title: "Worktree root guidance for Claude Code and Codex"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0563]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A fresh Claude Code or Codex session in any SDLC Lite repo learns where lanes live, and how to run lane operations, from the file it reads at start. Nothing still states the old in-repo root as current.

## Intent
- Do:
  1. Add one line to this repo's root `AGENTS.md` and to the managed block that onboarding writes into consumer repos. Example: `Worktrees: lanes live in ../<repo>.worktrees/ (scripts/wtroot.py root); lane open, land and close write .git, so under Codex run them with full access, not the workspace-write sandbox.`
  2. Replace `.claude/worktrees` as the current root in the plugin docs, references and skills. About 36 files name it; `grep -rln 'claude/worktrees' plugins/sdlc-lite docs/references docs/specs` lists them. The "Lanes" section of `plugins/sdlc-lite/AGENTS.md` is the authoritative statement. Drop the watcher and test-exclusion requirement it carries for the nested root. Regenerate the Codex agent TOMLs with `scripts/codex_roles.py` if their source text changed.
  3. Sweep and stray-worktree reporting (`lanes.py sweep`, `wtroot.py sweep`, `dispatch.py` stray report) name `~/.codex/worktrees/*` and Claude Code's `.claude/worktrees/agent-*` as host-owned and never list them for removal.
- Non-goals: the root change itself (T-0563).
- Done when: the criteria below pass.

## Context
Depends on T-0563, which moves the default root to `<main checkout parent>/<repo>.worktrees/` and adds `migrate-worktrees.sh`. Claude Code reads `CLAUDE.md`, which imports `AGENTS.md` here; Codex reads `AGENTS.md` directly. Codex's `workspace-write` sandbox keeps `.git` read-only, so `git worktree add` and commits fail there; see `docs/references/codex-role-execution.md:94`.

## Constraints
One authoritative statement of the root: the `plugins/sdlc-lite/AGENTS.md` "Lanes" section plus the `wtroot.py` docstring. Every other file links to those or uses the root as an example, without restating the rule.

## Acceptance criteria
1. `grep -rn 'claude/worktrees' plugins/sdlc-lite docs/references docs/specs AGENTS.md` prints only lines that call it legacy or host-owned (Claude `agent-*` trees).
2. Root `AGENTS.md` and the onboarding managed-block template each contain the worktree line naming `wtroot.py` and the Codex full-access note.
3. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0. Its new case shows a `~/.codex/worktrees` worktree and a `.claude/worktrees/agent-x` worktree registered on the repo, absent from the sweep's removal list; that case failed before the change.
4. `python3 scripts/check-packaging.py` and `python3 plugins/sdlc-lite/scripts/codex_roles.py --check` (or its parity check) exit 0, and `git diff --check` exits 0.
