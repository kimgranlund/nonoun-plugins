---
id: T-0789
title: "repository charter for four plugins"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The repository guidance describes four plugins (sdlc-lite, progressive-context, design, dev-tools) instead of two, so the plugin tickets T-0790 to T-0792 land against a charter that allows them.

## Intent
- Do: update `AGENTS.md` (line 3 "two peer plugins", line 16 "the two plugins", the Purpose and ownership list, and the Read for the task table) to name all four plugins and what each owns: design owns UI construction, geometry, palettes and design review; dev-tools owns machine, repo and harness care; progressive-context also owns context routing and system mapping.
- Non-goals: creating the plugins or moving any skill.
- Done when: `grep -n 'two peer plugins\|the two plugins' AGENTS.md` prints nothing, each new plugin has one ownership line, and `git diff --check` exits 0.

## Context
User decision 2026-10-25: three plugin homes for the user-level skills (progressive-context extended, new design, new dev-tools). Fold or retire, not move: `checks-that-bite` (sdlc-lite ships it), `rag-board` (replaced by `sdlc-lite:board`), `import-to-claude-code` (a Claude Code built-in). Stay user-level: `unslop`, `i-have-adhd`. Stay in its project: `lg-thinq-integration`.

## Constraints
Keep one authoritative location per fact: link to each plugin's own `AGENTS.md` once it exists instead of copying its details.
