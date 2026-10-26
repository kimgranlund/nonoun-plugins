---
id: T-0789
title: "repository charter for four plugins"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The repository guidance describes four plugins (sdlc-lite, context, design, dev-tools) instead of two, so the plugin tickets T-0790 to T-0792 land against a charter that allows them.

## Intent
- Do: update `AGENTS.md` (line 3 "two peer plugins", line 16 "the two plugins", the Purpose and ownership list, and the Read for the task table) to name all four plugins and what each owns: design owns UI construction, geometry, palettes and design review; dev-tools owns machine, repo and harness care; context (the renamed progressive-context plugin, T-0793) also owns context routing and system mapping.
- Non-goals: creating the plugins or moving any skill.
- Done when: `grep -n 'two peer plugins\|the two plugins' AGENTS.md` prints nothing, each new plugin has one ownership line, and `git diff --check` exits 0.

## Context
User decision 2026-10-25: three plugin homes for the user-level skills (progressive-context extended and renamed `context`, new design, new dev-tools). Fold or retire, not move: `checks-that-bite` (sdlc-lite ships it), `rag-board` (replaced by `sdlc-lite:board`), `import-to-claude-code` (a Claude Code built-in). Stay user-level: `unslop`, `i-have-adhd`. Stay in its project: `lg-thinq-integration`.

## Constraints
Keep one authoritative location per fact: link to each plugin's own `AGENTS.md` once it exists instead of copying its details.

## Outcome
`AGENTS.md` now names four peer plugins. Intro line, Purpose and ownership list (Progressive Context extended with context routing and system mapping and marked "to be renamed `context`, T-0793"; new one-line ownership for design (T-0791) and dev-tools (T-0792)), the map line ("holds the plugins"), and the Read for the task table (renamed row plus one row for the planned plugins, no links to files that do not exist).

Checks:
- `grep -n 'two peer plugins\|the two plugins' AGENTS.md` prints nothing (exit 1)
- `git diff --check` exit 0
- `python3 scripts/check-packaging.py` exit 0
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0
