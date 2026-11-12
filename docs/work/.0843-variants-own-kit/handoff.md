---
id: T-0843
title: "Port component-variants off base-ui onto a trimmed own kit"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0841]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`component-variants` builds its review page from a trimmed kit it owns, with geometry from `ui-geometry`, and no longer needs `base-ui` beside it.

## Intent
- Do: move into `component-variants` only what `scripts/build.mjs` uses from `base-ui/scripts/api.mjs` (`compileControls`, `getAssetBundle().foundationCSS`, `validateUI` token membership, `describeKit` identity), and generate its geometry CSS from `ui-geometry/scripts/derive.mjs`.
- Non-goals: changes to other skills; new features.
- Done when: the criteria below hold.

## Context
- Skill: `plugins/design/skills/component-variants/` (`scripts/build.mjs`, `scripts/check-build.mjs`, `assets/`, `ui-kit.lock.json`, `references/template-contract.md`, SKILL.md).
- Kit today: `plugins/design/skills/base-ui/scripts/api.mjs` and what it reads (`compile-controls.mjs`, `token-index.mjs`, `token-inspection.mjs`, `lib/font-css.mjs`, the foundation CSS sources). Copy only the pieces build.mjs needs; drop the lock and identity check, since the kit now ships inside the skill.
- Geometry: `plugins/design/skills/ui-geometry/scripts/derive.mjs --json` (T-0841). Write a small generator script in this skill that emits its geometry custom properties from derive output, so geometry is never hand-typed. Colours and type stay as copied from base-ui.
- Plugin guidance: `plugins/design/AGENTS.md` (Rules on sibling paths and `ui-kit.lock.json`).

## Do
1. Vendor the trimmed kit under `component-variants/` and generate its geometry CSS from `ui-geometry`.
2. Point `build.mjs` at it, remove `ui-kit.lock.json`, and update `check-build.mjs` so its negative control removes the vendored kit (or `ui-geometry`) instead of `base-ui`.
3. Update SKILL.md, the template contract, the design AGENTS.md Rules line and a CHANGELOG `[Unreleased]` Changed line.

## Acceptance criteria
- `cd plugins/design/skills/component-variants && node scripts/check-build.mjs` exits 0, including its negative control.
- With `base-ui` and `mathematical-design-system` moved out of the tree (in a temporary copy of `plugins/design/skills/`), `node scripts/check-build.mjs` there still exits 0.
- `! grep -rnE "base-ui|mathematical-design-system|differential-forms|local\.base-ui" plugins/design/skills/component-variants` exits 0.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills. Geometry values come from `derive.mjs`, never copied numbers.

## Outcome

## Outcome

2026-11-12 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: f17a11427538
- Changed: see commits
- Commits: ddfa899 T-0843: component-variants builds from its own trimmed kit
- Check: 1 check-build.mjs exits 0 including negative control: pass
- Check: 2 passes with base-ui and mathematical-design-system removed: pass
- Check: 3 forbidden-name grep: pass
- Check: 4 packaging and diff check: pass
- Follow-up: note: plugins/design/skills/component-variants/scripts/geometry.mjs:11... -> notes.md
- Follow-up: note: the head is merge commit b3c44154 main merged into the lane; the... -> notes.md
