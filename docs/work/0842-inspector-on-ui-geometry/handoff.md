---
id: T-0842
title: "Port the ui-kit-inspector example onto ui-geometry"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0841]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
branch: lane/T-0842-t0842
worktree: ../sdlc-lite.worktrees/T-0842-t0842
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `ui-kit-inspector` inspector-panel example takes its geometry from `ui-geometry` and no longer reads `mathematical-design-system`.

## Intent
- Do: rewire `examples/inspector-panel/scripts/build.mjs`, `examples/geometry.test.mjs` and the example README onto `../../../../ui-geometry/scripts/derive.mjs`.
- Non-goals: changes to `ui-geometry` itself or to other skills.
- Done when: the criteria below hold.

## Context
- Example: `plugins/design/skills/ui-kit-inspector/examples/inspector-panel/` (`npm test`, Node 24 or later). It now imports `resolveControl` and copies `mathematical-design-system/assets/differential-forms/`.
- `ui-geometry` (T-0841): `scripts/derive.mjs` exports the preset and derive functions; its identities are in its SKILL.md `## Identities` and `references/equations.md`. Values will differ from the Differential Forms snapshots: assert ui-geometry identities (for example `h = S + 2I`, concentric radii within a tier), not old numbers.
- The MacBook `ui-kit-inspector` has no `inspector-panel` example and edits SKILL.md and `examples/README.md`; do not import those, keep the local example.
- Plugin guidance: `plugins/design/AGENTS.md` (Rules paragraph names the sibling paths; update it).

## Do
1. Replace the Differential Forms imports and asset copy with `ui-geometry` derive calls.
2. Rewrite the geometry test to assert ui-geometry identities.
3. Update the example README, the design AGENTS.md Rules line and a CHANGELOG `[Unreleased]` Changed line.

## Acceptance criteria
- `cd plugins/design/skills/ui-kit-inspector/examples/inspector-panel && npm test` exits 0.
- `! grep -rnE "mathematical-design-system|differential-forms|base-ui" plugins/design/skills/ui-kit-inspector` exits 0.
- The geometry test fails when one asserted identity is broken (an observed negative control, named in the report, then reverted).
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills.

## Outcome
