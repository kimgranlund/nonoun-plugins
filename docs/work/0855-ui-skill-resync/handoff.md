---
id: T-0855
title: "Resync four ui-* skills from the MacBook copies"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-15
claimed_by: nonoun-author 2026-11-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`ui-geometry`, `ui-frameworks`, `ui-explore-variants` and `ui-interaction-dev` in the design plugin match the user's current MacBook copies, and everything that leans on them still passes.

## Intent
- Do: sync the four skills, rerun their tests and the dependents' checks, drop allowlist rows the sync makes stale, record the change.
- Non-goals: the other `ui-*` skills (`ui-colors`, `ui-content`, `ui-materials`, `ui-showcase-bento` already match; `ui-kit-inspector` is newer here than on the MacBook and stays); editing synced files.
- Done when: the criteria below hold.

## Context
- Sources under `/Volumes/kimba/.claude/skills/` with git commits: `ui-geometry` (`2b1500a`: `references/equations.md`, `scripts/derive.mjs`, `scripts/derive.test.mjs` changed), `ui-frameworks` (`2cf5ee1`: new `checks/` folder, 5 changed files), `ui-explore-variants` (`79ce3f9`: SKILL.md and three assets), `ui-interaction-dev` (`ba2f4c4`: `references/spec.json` and `spec.md`). Targets: `plugins/design/skills/<name>/`.
- Copy each with `rsync -a --delete --exclude .git --exclude .gitignore --exclude .DS_Store --exclude node_modules --exclude __pycache__ --exclude agents <source>/ <target>/` (`--exclude agents` keeps the repo-only `ui-geometry/agents/openai.yaml`). `/Volumes/kimba` is read-only: never write under it.
- Dependents of `ui-geometry/scripts/derive.mjs`: `ui-kit-inspector/examples/inspector-panel` (`npm run build` refreshes its browser copy `geometry-runtime/derive.js` and `provenance.json`; `npm test`), `component-variants` (`node scripts/check-build.mjs`), `wireframe-review` (`node scripts/generate-geometry.mjs --check`, `node scripts/selftest.mjs`). Make the smallest repair in a dependent that breaks (regenerate derived output) and say so; if it is not small, report blocked with the output.
- `docs/reports/broken-links-allowlist.md` holds 18 rows for `ui-frameworks` docs links (T-0853) that were broken because the source lacked `checks/` and other files. `python3 plugins/sdlc/scripts/check.py` fails on a stale row and on an unlisted broken link: run it, delete rows it calls stale, and add a row (same wording as the existing T-0853 rows, naming T-0855) only for a link still broken in the source.
- Record: update the four rows' source commit ids in `plugins/design/AGENTS.md` and add `### Changed` lines under `## [Unreleased]` in `plugins/design/CHANGELOG.md`.
- If `scripts/check-packaging.py` flags a synced file, do not trim it: report blocked with the output.

## Do
1. Sync the four skills.
2. Run their tests and the dependents' checks; repair small breaks; fix the allowlist.
3. Update the plugin guidance and changelog.

## Acceptance criteria
- For each of the four, `diff -rq --exclude .git --exclude .gitignore --exclude .DS_Store --exclude node_modules --exclude agents /Volumes/kimba/.claude/skills/<name> plugins/design/skills/<name>` prints nothing, and `test -f plugins/design/skills/ui-geometry/agents/openai.yaml` exits 0.
- `node --test` exits 0 in `ui-geometry` and in `ui-interaction-dev`; `node scripts/manifests.mjs --check` and `node scripts/lint-recipes.mjs` exit 0 in `ui-frameworks`.
- `node scripts/check-build.mjs` exits 0 in `component-variants`, `npm test` exits 0 in `ui-kit-inspector/examples/inspector-panel`, and `node scripts/generate-geometry.mjs --check` exits 0 in `wireframe-review`.
- `SDLC_ALLOW_STALE_PLUGIN=1 python3 plugins/sdlc/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Never write under `/Volumes/kimba`.
- Do not hand-edit synced files.
