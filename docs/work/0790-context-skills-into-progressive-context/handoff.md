---
id: T-0790
title: "move the context skills into the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0789, T-0793]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `context` plugin (renamed from progressive-context by T-0793) ships the context skills, so every repo and both machines load one version instead of drifting user-level copies.

## Intent
- Do: add `context-fog-of-war`, `context-routing-review`, `generative-systems`, `system-atlas` and `icm-architect` under `plugins/context/skills/`; update the plugin's `AGENTS.md`, manifests and version; record which user-level copy each came from.
- Non-goals: rewriting the skills' content; deleting the user-level copies (the user does that after install).
- Done when: `python3 scripts/check-packaging.py` passes, each skill's description routes (no duplicate trigger with `context:progressive-context`), and every relative link inside the moved skills resolves.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Sources are the user-level skill folders, merged 2026-10-25 so every copy of a shared skill is identical: `~/.claude/skills/<name>` and `~/.codex/skills/<name>` on this Mac, and the same paths on the share mounted at `/Volumes/kimba`. A skill found only on the share is read from `/Volumes/kimba/.codex/skills/<name>`. Pre-merge backups: `~/skill-backups/2026-10-25-pre-merge/`. Each plugin ships for both hosts: `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, a row in `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` (parity), and passes `python3 scripts/check-packaging.py` (it checks skill routes and sizes). `generative-systems` carries a large `resources/reports/` tree (739 differing files in the 2026-10-25 comparison) and one dangling symlink (`resources/reports/split-consumption-followup-2026-10-11/main-evidence/author/evaluator-alias`); decide what ships and what stays out of the package. Read `plugins/context/AGENTS.md` first.

## Constraints
The plugin's existing skill behavior does not change.
