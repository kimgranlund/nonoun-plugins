---
id: T-0844
title: "Port wireframe-review off base-ui onto a trimmed own kit"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0841]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`wireframe-review` generates and checks wireframes from a trimmed kit it owns, with geometry from `ui-geometry`, and no longer needs `base-ui` or `mathematical-design-system` beside it.

## Intent
- Do: make the mirrored kit files in `wireframe-review` authoritative, move in only the base-ui script modules its scripts call, regenerate its geometry from `ui-geometry`, and delete forwarders to checks that only base-ui owned.
- Non-goals: changes to other skills; redesigning wireframes or their markup.
- Done when: the criteria below hold.

## Context
- Skill: `plugins/design/skills/wireframe-review/`. `ui-compatibility.json` lists 135 mirrored kit files already held locally (foundation CSS, icons, control markup). `scripts/ui-kit.mjs` `loadUI` and `scripts/sync-ui-kit.mjs` check the base-ui lock and mirrors; `ui-kit.lock.json` pins the identity.
- Base-ui calls used by its scripts: `api.readSource`, `getAssetBundle`, `describeKit`, `createIndex`, `updateIconCSS`, `collectCatalog` (from `plugins/design/skills/base-ui/scripts/api.mjs` and the modules it imports). 48 scripts are one-line "Compatibility entry; base-ui owns this check" forwarders routed by `scripts/run-ui-check.mjs`.
- Geometry today: `assets/foundation/maison/geometry.{css,json}` and `layout.css`, generated from `mathematical-design-system/scripts/lib/scale.mjs` (see its `provenance.json`). Replace the generator with one driven by `plugins/design/skills/ui-geometry/scripts/derive.mjs --json` (T-0841); keep the custom property names the CSS consumers use, and record the ui-geometry source in `provenance.json`.
- References naming the old owners: `SKILL.md`, `references/ui-kit-dependency.md`, `references/geometry-spacing.md`, `references/workflows/{build-core,reference-sheets}.md`, `references/migration/*`.
- Plugin guidance: `plugins/design/AGENTS.md`.

## Do
1. Vendor the needed base-ui script modules under `wireframe-review/scripts/` and make `loadUI` load the local kit with no lock or mirror check; remove `ui-kit.lock.json`, `ui-compatibility.json` and `sync-ui-kit.mjs`.
2. Delete each compatibility forwarder whose check is not vendored, and remove its route from `run-ui-check.mjs`; keep any check the generation or revision flow runs.
3. Replace the geometry generator with a `ui-geometry` driven one and regenerate `assets/foundation/maison/`.
4. Update SKILL.md and the references above, the design AGENTS.md Rules line and a CHANGELOG `[Unreleased]` Changed line.

## Acceptance criteria
- In a temporary copy of `plugins/design/skills/` with `base-ui` and `mathematical-design-system` removed, the skill's documented generation command builds the example manifest (`assets/example.manifest.json`) into a fresh directory and exits 0; the report names the command.
- `! grep -rnE "\.\./base-ui|mathematical-design-system|local\.base-ui|differential-forms" plugins/design/skills/wireframe-review --include='*.mjs' --include='*.js' --include='*.md' --include='*.json'` exits 0 (provenance history lines excepted only if named in the report).
- Regenerating the geometry with the new generator is byte-identical to the committed `assets/foundation/maison/geometry.css`, and changing one derive dial changes it (an observed negative control, then reverted).
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills. Geometry values come from `derive.mjs`, never copied numbers.

## Outcome

## Outcome

2026-11-12 · lane: solo L3 · verdict: closed by reason (delivered by the solo agent (level L3); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: ab93a5738ddc
- Changed: see commits
- Commits: baa87ac T-0844: wireframe-review builds from its own trimmed kit with ui-geometry geometry
- Check: 1 Generation without base-ui and mathematical-design-system: pass
- Check: 2 Forbidden-name grep: pass
- Check: 3 Geometry regeneration byte-identical and dial-sensitive: pass
- Check: 4 Packaging and diff hygiene: pass
- Follow-up: decide: plugins/design/skills/wireframe-review/assets/fonts/ibmplexmono/OFL... -> notes.md
- Follow-up: decide: plugins/design/skills/wireframe-review/assets/foundation/maison/geo... -> notes.md
- Follow-up: decide: The builder lists several suites as already red at baseline... -> notes.md
