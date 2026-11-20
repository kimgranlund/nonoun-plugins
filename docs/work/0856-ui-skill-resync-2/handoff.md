---
id: T-0856
title: "Resync five ui-* skills from the MacBook copies"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
branch: lane/T-0856-t0856
worktree: ../sdlc-lite.worktrees/T-0856-t0856
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`ui-geometry`, `ui-frameworks`, `ui-explore-variants`, `ui-materials` and `ui-content` in the design plugin match the user's current MacBook copies, and everything that leans on them still passes.

## Intent
- Do: sync the five skills, rerun their tests and the dependents' checks, fix the broken-link allowlist, record the change.
- Non-goals: skills whose repo copy is the newer one (`ui-kit-inspector`, `component-variants`, `wireframe-review`, `context-fog-of-war`, `generative-systems`, `closed-loop-run`, `skill-report-card`); editing synced files.
- Done when: the criteria below hold.

## Context
- Sources under `/Volumes/kimba/.claude/skills/`: `ui-geometry` (SKILL.md, `references/equations.md`, `scripts/derive.mjs` and its test changed), `ui-frameworks` (about 165 changed files; the source dropped `checks/`), `ui-explore-variants` (SKILL.md, `assets/feedback.js`), `ui-materials` (SKILL.md, `scripts/check.mjs`), `ui-content` (new `scripts/`). Record each source's `git log --format=%h -1` at sync time. Targets: `plugins/design/skills/<name>/`.
- Copy each with `rsync -a --delete --exclude .git --exclude .gitignore --exclude .DS_Store --exclude node_modules --exclude __pycache__ --exclude agents <source>/ <target>/` (`--exclude agents` keeps the repo-only `ui-geometry/agents/openai.yaml`). `/Volumes/kimba` is read-only: never write under it. The user may commit to a source during the run: run the diff criterion last and resync a skill that moved.
- Dependents of `ui-geometry/scripts/derive.mjs`: `ui-kit-inspector/examples/inspector-panel` (`npm run build` refreshes its browser copy and `provenance.json`; `npm test`), `component-variants` (`node scripts/check-build.mjs`), `wireframe-review` (`node scripts/generate-geometry.mjs --check`, `node scripts/selftest.mjs`). Make the smallest repair in a dependent that breaks and say so; if it is not small, report blocked with the output.
- `docs/reports/broken-links-allowlist.md` holds rows for `ui-frameworks` docs links (T-0853). `python3 plugins/sdlc/scripts/check.py` fails on a stale row and on an unlisted broken link: run it, delete rows it calls stale, and add a row (wording of the existing T-0853 rows, naming T-0856) only for a link still broken in the source.
- `scripts/check-packaging.py` limits SKILL.md to under 18000 characters. If it flags a synced file, do not trim it: report blocked with the output.
- Record: update the five rows in `plugins/design/AGENTS.md` (source commits, and each skill's test command if it changed or is new, such as `ui-content/scripts`), and add `### Changed` lines under `## [Unreleased]` in `plugins/design/CHANGELOG.md`.

## Do
1. Sync the five skills.
2. Run their tests and the dependents' checks; repair small breaks; fix the allowlist.
3. Update the plugin guidance and changelog.

## Acceptance criteria
- For each of the five, `diff -rq --exclude .git --exclude .gitignore --exclude .DS_Store --exclude node_modules --exclude agents /Volumes/kimba/.claude/skills/<name> plugins/design/skills/<name>` prints nothing, and `test -f plugins/design/skills/ui-geometry/agents/openai.yaml` exits 0.
- `node --test` exits 0 in `ui-geometry`; `node scripts/check.mjs` exits 0 in `ui-materials`; `node scripts/manifests.mjs --check` and `node scripts/lint-recipes.mjs` exit 0 in `ui-frameworks` (or the commands its synced SKILL.md now names, stated in the report); any test `ui-content/scripts` ships exits 0.
- `node scripts/check-build.mjs` exits 0 in `component-variants`, `npm test` exits 0 in `ui-kit-inspector/examples/inspector-panel`, and `node scripts/generate-geometry.mjs --check` exits 0 in `wireframe-review`.
- `SDLC_ALLOW_STALE_PLUGIN=1 python3 plugins/sdlc/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check $SDLC_BASE_SHA -- . ':!plugins/design/skills/ui-frameworks'` is clean (replan: two synced `ui-frameworks` source files end in a blank line, and synced files are not hand-edited).

## Constraints
- Never write under `/Volumes/kimba`.
- Do not hand-edit synced files.
