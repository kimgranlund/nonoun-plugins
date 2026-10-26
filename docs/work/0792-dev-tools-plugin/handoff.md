---
id: T-0792
title: "new dev-tools plugin from the user-level machine and harness skills"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0789]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A new `dev-tools` plugin ships the machine, repo and harness care skills for Claude Code and Codex.

## Intent
- Do: create `plugins/dev-tools/` with `closed-loop-run`, `flaky-gates`, `port-zombie-sweep`, `git-bare-repo-setup`, `macos-build-and-verify`, `author-cross-harness-plugins` and `skill-report-card`, plus an `AGENTS.md` for the plugin.
- Non-goals: the duplicates T-0789 names for fold or retire; content rewrites.
- Done when: `python3 scripts/check-packaging.py` passes and every relative link inside the moved skills resolves, including `closed-loop-run/references/ui-feedback.md` that `base-ui` (T-0791) links to.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Sources are the user-level skill folders, merged 2026-10-25 so every copy of a shared skill is identical: `~/.claude/skills/<name>` and `~/.codex/skills/<name>` on this Mac, and the same paths on the share mounted at `/Volumes/kimba`. A skill found only on the share is read from `/Volumes/kimba/.codex/skills/<name>`. Pre-merge backups: `~/skill-backups/2026-10-25-pre-merge/`. Each plugin ships for both hosts: `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, a row in `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` (parity), and passes `python3 scripts/check-packaging.py` (it checks skill routes and sizes). `closed-loop-run` was three-way merged on 2026-10-25 (this Mac's 10-17 edits plus the share's 10-24 `ui-feedback` page). `macos-build-and-verify` exists only on the share. `flaky-gates` and `port-zombie-sweep` reference each other by name.

## Constraints
None.
