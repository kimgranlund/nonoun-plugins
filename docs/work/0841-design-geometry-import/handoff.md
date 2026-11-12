---
id: T-0841
title: "Import the hct-palettes update and the ui-geometry skill into design"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The design plugin ships the MacBook's current `hct-palettes` and a new `ui-geometry` skill, both loadable in Claude Code and Codex.

## Intent
- Do: replace `plugins/design/skills/hct-palettes/` with the MacBook copy and add `plugins/design/skills/ui-geometry/`.
- Non-goals: any change to `base-ui`, `mathematical-design-system` or their dependents (T-0842 to T-0845).
- Done when: the criteria below hold.

## Context
- Sources (read-only share, never write there): `/Volumes/kimba/.claude/skills/hct-palettes/` and `/Volumes/kimba/.claude/skills/ui-geometry/`. `ui-geometry` is its own git repo; record its `git -C <src> rev-parse --short HEAD` in the CHANGELOG line. Copy without `.git`, `.gitignore` and `.DS_Store`.
- The local `hct-palettes` came in with T-0791 and has no repo-side edits since; the MacBook copy is a superset (adds `evals/`, `references/system*.md`, `references/showcase.md`, `scripts/system*`, `scripts/check.mjs`, `scripts/preset.mjs`, `scripts/presets.json`).
- `ui-geometry` has no `agents/openai.yaml`; add one shaped like `hct-palettes/agents/openai.yaml`. Its description is long: if `check-packaging.py` rejects its length, shorten the frontmatter description only, keeping its trigger phrases and NOT clause.
- Plugin guidance: `plugins/design/AGENTS.md` (skill table, Checks line). Packaging rules: `docs/specs/doc-standards/plugins.md`. Changelog: `plugins/design/CHANGELOG.md` `[Unreleased]`.

## Do
1. Copy both skills as above and add `ui-geometry/agents/openai.yaml`.
2. Add a `ui-geometry` row to the design AGENTS.md skill table, update the `hct-palettes` row if its scope grew, and add its test commands to the Checks paragraph.
3. Add CHANGELOG `[Unreleased]` Added and Changed lines.

## Acceptance criteria
- `diff -rq -x .git -x .gitignore -x .DS_Store /Volumes/kimba/.claude/skills/hct-palettes plugins/design/skills/hct-palettes` prints nothing, and the same for `ui-geometry` apart from `agents/` and any shortened SKILL.md description (named in the report).
- `cd plugins/design/skills/ui-geometry && node --test scripts/` exits 0, and each `hct-palettes` check script the skill names exits 0.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills.

## Outcome
