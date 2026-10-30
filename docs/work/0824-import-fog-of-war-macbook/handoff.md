---
id: T-0824
title: "Import MacBook context-fog-of-war changes into the context plugin"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: nonoun-author 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/context/skills/context-fog-of-war/` carries the general improvements made to the skill on the MacBook since the repo copy (2026-10-25), and nothing project-specific.

## Context
- The user asked (2026-10-30) to bring MacBook skill updates back into the repo, one ticket per skill.
- Source, read-only over SMB: /Volumes/kimba/.codex/skills/context-fog-of-war (2026-10-29 05:27) and /Volumes/kimba/.claude/skills/context-fog-of-war (2026-10-26 20:05); the two differ in 15 files, so take the newer Codex copy as the base and check the Claude copy for changes the Codex one lacks.
- Differences found by a file-level diff: 20 files differ from the repo, including a new `scripts/delivery.py` and edits to diagnostics, engineering, hydration, investigation, the learnings and `session.schema.json`.
- The repo copy is the shipped source; the MacBook copy was edited in place, so some changes may be general improvements and some may be Maison or machine specific.

## Do
1. Diff the source against `plugins/context/skills/context-fog-of-war/` file by file.
2. Take every change that is general to the skill. Leave out anything specific to one project (Maison, a single repo, machine paths), any nested `.git`, `.openai` or `.DS_Store`, and anything that would break the skill's Codex adapter line or the packaging rules in `docs/specs/doc-standards/plugins.md`.
3. In the report, list each file taken, each file left out and why.
4. Never write to `/Volumes/kimba`.

## Acceptance criteria
- the skill's own selftests or validator if it ships one (state which), and `python3 scripts/check-packaging.py` exits 0.
- `! find plugins/context/skills/context-fog-of-war -name .git -o -name .DS_Store | grep -q .`
- `git diff --check` is clean.
