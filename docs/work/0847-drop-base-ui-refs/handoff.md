---
id: T-0847
title: "Drop base-ui and mathematical-design-system references from other plugins and wireframe-review's catalog check"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: [T-0845]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
branch: lane/T-0847-t0847
worktree: ../sdlc-lite.worktrees/T-0847-t0847
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
No live skill or check outside the dated records still names `base-ui` or `mathematical-design-system` as a current skill.

## Context
- Found by the T-0845 solo after both skills were removed:
  - `plugins/dev-tools/skills/skill-report-card/**`: a `base-ui` skill id, an argparse choice, the `local.base-ui` packageId and test fixtures.
  - `plugins/context/skills/context-fog-of-war/**`: an embedded `base-ui-source` bundle in `shell.html`, `build_shell.py --kit` and references.
  - `plugins/context/skills/generative-systems/resources/*.md`: historical split specs (may stay as history; say so in the report).
  - `plugins/design/skills/wireframe-review/scripts/check-catalog-boundary.mjs:9` asserts the data-driven owner `base-ui`.
- Leave records alone: `docs/reports/`, closed tickets, `docs/work/NOTES.md`, CHANGELOG history, `docs/README.md` release lines.

## Acceptance criteria
- `git grep -nE "base-ui|mathematical-design-system" -- plugins ':!*CHANGELOG.md' ':!plugins/design/skills/ui-kit-inspector/examples/maison-jig'` prints only lines the report names as history.
- Each touched skill's own tests exit 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Outcome
