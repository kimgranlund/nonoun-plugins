---
id: T-0845
title: "Remove base-ui and mathematical-design-system from design"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0842, T-0843, T-0844]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The design plugin no longer ships `base-ui` or `mathematical-design-system`, and no record still points at them.

## Intent
- Do: delete both skill folders and repair every live reference.
- Non-goals: rewriting dated reports or closed tickets; changes to skill behaviour.
- Done when: the criteria below hold.

## Context
- Folders: `plugins/design/skills/base-ui/` and `plugins/design/skills/mathematical-design-system/`.
- Live references: `plugins/design/AGENTS.md` (skill table, Rules, Checks), root `README.md`, design and root `CHANGELOG.md` (add a Removed line under `[Unreleased]`, keep history), `scripts/check-packaging.py` if it names them, and any design skill text left after T-0842 to T-0844. Find them with `git grep -nE "base-ui|mathematical-design-system"` excluding `docs/reports/`, closed `.NNNN-*` tickets and CHANGELOG history.

## Do
1. `git rm -r` both folders.
2. Repair each live reference found by the grep.
3. Add the CHANGELOG `[Unreleased]` Removed lines.

## Acceptance criteria
- `test ! -e plugins/design/skills/base-ui -a ! -e plugins/design/skills/mathematical-design-system` exits 0.
- `git grep -nE "base-ui|mathematical-design-system" -- . ':!docs/reports' ':!docs/work/.[0-9]*' ':!*CHANGELOG.md' ':!docs/work/084*' ':!plugins/design/skills/ui-kit-inspector/examples/maison-jig'` prints nothing.
- `node scripts/check-build.mjs` in `component-variants`, `npm test` in the inspector-panel example and `node --test` in `ui-geometry` all exit 0.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Touch only reference lines; no behaviour change.

## Outcome
