---
id: T-0853
title: "Import six ui-* skills into design"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0852]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The design plugin ships six new skills copied from the user's MacBook share: `ui-materials`, `ui-content`, `ui-interaction-dev`, `ui-frameworks`, `ui-explore-variants` and `ui-showcase-bento`.

## Intent
- Do: copy the six skills, register them, run the tests they ship, pass packaging.
- Non-goals: retiring or changing existing design skills (`component-variants`, `wireframe-review` and the rest stay); changing imported behaviour; `ui-geometry` and `ui-colors` (T-0852, already landed).
- Done when: the criteria below hold.

## Context
- Sources under `/Volumes/kimba/.claude/skills/`, with their git commits for the record: `ui-materials` (`ec1743a`), `ui-content` (`1aafd92`), `ui-interaction-dev` (`de8f3a9`), `ui-explore-variants` (`c7d3ac9`), `ui-showcase-bento` (`f3fbd78`), `ui-frameworks` (no git, 283 files). Target: `plugins/design/skills/<name>/`. Copy with `rsync -a --exclude .git --exclude .gitignore --exclude .DS_Store --exclude node_modules --exclude __pycache__ <source>/ <target>/`. `/Volumes/kimba` is read-only: never write, touch or create anything under it.
- These skills name each other and `ui-geometry` and `ui-colors` (same plugin). Leave their text as authored.
- Register: one row per skill in `plugins/design/AGENTS.md` (use from the SKILL.md description, source path and commit), an `### Added` line each under `## [Unreleased]` in `plugins/design/CHANGELOG.md`, and add them wherever the design plugin's skills are listed for users (root `README.md`, both `plugin.json` descriptions and both marketplace files if they enumerate skills; keep the two hosts in parity).
- Tests: run what each skill ships (`node --test`, a `scripts/check.*` or `scripts/*.test.mjs`, an `evals/` runner) and list in your report which skills ship none.
- `scripts/check-packaging.py` limits SKILL.md to under 18000 characters and checks relative links. `ui-materials/SKILL.md` is 18042 bytes and may sit near the limit. If packaging flags an imported file, do not trim or rewrite it: report blocked with the exact output. A missing `agents/openai.yaml` that packaging requires may be added, matching the form of `plugins/design/skills/ui-geometry/agents/openai.yaml`.

## Do
1. Copy the six skills.
2. Register them in the guidance, changelog and listings.
3. Run their tests and packaging.

## Acceptance criteria
- `for s in ui-materials ui-content ui-interaction-dev ui-frameworks ui-explore-variants ui-showcase-bento; do test -f plugins/design/skills/$s/SKILL.md || exit 1; done` exits 0, and `find plugins/design/skills -name .git -o -name .DS_Store -o -name node_modules -o -name .gitignore` prints nothing.
- For each of the six, `diff -rq --exclude .git --exclude .gitignore --exclude .DS_Store --exclude node_modules --exclude agents /Volumes/kimba/.claude/skills/<name> plugins/design/skills/<name>` prints nothing.
- `grep -c -E 'ui-materials|ui-content|ui-interaction-dev|ui-frameworks|ui-explore-variants|ui-showcase-bento' plugins/design/AGENTS.md` prints 6 or more, and each name appears in `plugins/design/CHANGELOG.md`.
- Every test a skill ships exits 0, named in the report.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Never write under `/Volumes/kimba`.
- Do not edit other skills.
