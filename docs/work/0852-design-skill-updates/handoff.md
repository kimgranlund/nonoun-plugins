---
id: T-0852
title: "Update ui-geometry and ui-colors from the MacBook copies"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`ui-geometry` and `ui-colors` in the design plugin match the user's current MacBook copies, and the skills that consume them still pass their checks.

## Intent
- Do: sync both skills from the source, keep the repo-only host files, rerun their tests and the dependents' checks, record the change.
- Non-goals: importing new skills (T-0853); redesigning dependents; editing the synced files beyond what packaging requires.
- Done when: the criteria below hold.

## Context
- Sources: `/Volumes/kimba/.claude/skills/ui-geometry` (git `62d0cda`) and `/Volumes/kimba/.claude/skills/ui-colors` (git `e9ff385`). Targets: `plugins/design/skills/ui-geometry/` and `plugins/design/skills/ui-colors/`. Copy with `rsync -a --exclude .git --exclude .gitignore --exclude .DS_Store --exclude node_modules --exclude __pycache__ <source>/ <target>/`. `/Volumes/kimba` is read-only: never write, touch or create anything under it. Add `--delete` so files the source dropped go away, but keep `plugins/design/skills/ui-geometry/agents/openai.yaml` (repo-only, `--exclude agents` for ui-geometry) and check `git status` for any other repo-only file before deleting it.
- New in the source: ui-geometry gains `references/{archetypes,dimensions,terms}.json` and scripts `archetypes`, `dimensions`, `docs`, `observe`, `terms`, `knowledge.test.mjs`; ui-colors gains `references/terms.json` and a pressed solid role (`-solid-active`).
- Dependents of `ui-geometry/scripts/derive.mjs`: `ui-kit-inspector/examples/inspector-panel` (browser copy `geometry-runtime/derive.js`, `npm test`), `component-variants` (`scripts/geometry.mjs`, `node scripts/check-build.mjs`), `wireframe-review` (`scripts/generate-geometry.mjs --check`, `scripts/selftest.mjs`). If a derive change breaks one, make the smallest repair in the dependent (regenerate its derived output or refresh its copy) and say so; if the repair is not small, report blocked with the failing output.
- `scripts/check-packaging.py` limits SKILL.md to under 18000 characters. If a synced SKILL.md fails it, do not trim the file: report blocked with the count.
- Record: update the two rows and source notes in `plugins/design/AGENTS.md` (source commit ids), and add `### Changed` lines under `## [Unreleased]` in `plugins/design/CHANGELOG.md`. T-0853 edits the same two files later; keep edits to these two skills' lines.

## Do
1. Sync both skills.
2. Run their tests and the dependents' checks; repair small breaks.
3. Update the plugin guidance and changelog.

## Acceptance criteria
- `diff -rq --exclude .git --exclude .gitignore --exclude .DS_Store --exclude agents /Volumes/kimba/.claude/skills/ui-geometry plugins/design/skills/ui-geometry` and `diff -rq --exclude .git --exclude .gitignore --exclude .DS_Store /Volumes/kimba/.claude/skills/ui-colors plugins/design/skills/ui-colors` print nothing, and `test -f plugins/design/skills/ui-geometry/agents/openai.yaml` exits 0.
- `node --test` exits 0 in `plugins/design/skills/ui-geometry`, and `node scripts/check.mjs` exits 0 in `plugins/design/skills/ui-colors`.
- `node scripts/check-build.mjs` exits 0 in `component-variants`, `npm test` exits 0 in `ui-kit-inspector/examples/inspector-panel`, and `node scripts/generate-geometry.mjs --check` exits 0 in `wireframe-review`.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Never write under `/Volumes/kimba`.
- Model and geometry values come from the synced source; do not hand-edit them.
