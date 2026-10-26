---
name: mathematical-design-system
description: "Derive and validate UI geometry using the Differential Forms model: family-specific density, border budgets, exposed label edges, nested curvature and composition. Use for formula design, geometry contracts and numerical verification; follow the consuming project's rules for implementation."
---
# Mathematical design system

The adopted model is **Differential Forms**. The bundled portable snapshot is the frozen **v0.2.2** geometry/specimen baseline captured 2026-10-22; it is not the current custom-component package. Current implementation work must use the consuming project’s verified registry, manifests and component docs. It replaces the earlier n/tier/percentage model for new work. These are design conventions, not universal perceptual laws. Explicit user instructions and a consuming project's confirmed contracts take precedence over this bundled snapshot.

## Start and route

Identify **intent**, **semantic component**, **geometry family**, and **parent context** separately. A DOM wrapper does not automatically establish a geometry family.

For current work, follow the consuming repository’s entry point to its authoritative contracts, resolvers and companion CSS. For historical baseline work, read the [frozen v0.2.2 baseline](references/geometry-contract.md), then only the relevant files in [the portable source snapshot](assets/differential-forms/system.manifest.json):

- Geometry: `contracts/foundations.json`, `contracts/geometry-families.json`, `docs/geometry.md`, and the relevant `geometry/resolve-*.ts`.
- Components/composition: `contracts/components.json`, `contracts/parts.json`, `contracts/composition.json`, relevant `recipes/`.
- Appearance or behavior: `docs/appearance.md`, `docs/interaction.md`.
- Unspecified behavior: `docs/exceptions.md`; use the smallest explicit experimental extension.
- Integration: [consumer integration](references/consumer-integration.md).

The listed contracts/, docs/, geometry/, recipes/, specimens/ and verification/ paths are relative to `<skill-root>/assets/differential-forms/`. Markdown reference links are relative to the file containing them. Resolve the skill root from this SKILL.md location, never the caller's working directory. The snapshot runs independently of the originating checkout and has no deployment credentials.

For current component work, public attributes configure geometry/state; companion `components/{component}/{component}.css` owns every style and token mapping. TypeScript reflects inputs/state and implements behavior only. Never generate inline styles or stylesheets at runtime. Pure resolvers remain numerical references, not a runtime CSS transport. Shared templates may construct custom-part anatomy. Start component selection at `registry.json`, check implemented availability and `avoidWhen`/`useInstead`, and register required parts explicitly.

## Operating constraints

- Keep CSS `box-sizing:border-box`. Resolver outputs are CSS pixels; preserve fractions and round only display values.
- Defaults: u=4px, border=0px, composite inset=0u, Soft control/container curvature, label edge=1.5u. Chip label edge is half the control edge.
- Density is a family lookup: compact/default/loose. Typography, icon slots and label-edge compensation do not shrink with density. Collections/cards do not overwrite descendant control density.
- Distinguish outer inset, internal gap, exposed label edge and independent layout gutter. Deduct an owner's border once from its own inset. Transparent borders occupy interior space in every state.
- Preserve readable text and slots. When composite budgets cannot fit the nominal size, allow the containing composite to grow; do not shrink wrappers or artwork to force a fit.
- Composite gap equals requested inset. Zero requested inset means zero child curvature **for attached composites**, not arbitrary nested components or composed-input adornments.
- Inputs use neutral wrappers; adornments use chips. Never nest interactive controls inside buttons. Multiline rows use collection geometry, not composite residual subtraction.
- Checkbox radius is 1u; radio and switch shapes stay circular/capsule. Container Softest is 4u, not a pill.
- Appearance is independent of geometry. Keyboard focus is a 3px solid ink outline, 0px offset for all focusable components. Text fields paint it on their neutral wrapper; sibling actions own their ring. Contain attached/segmented child paint within the group contour while keeping keyboard focus fully visible; use the verified current component focus treatment without changing dimensions.
- UI uses system-ui, specimen captions IBM Plex Mono 400, HTML demo icons pinned Phosphor CDN. Prefer subtle surface levels; omit divider lines where surface color identifies boundaries.

## Change and verify

Change confirmed contracts, numerical resolvers, companion CSS, relevant recipes and tests together when changing geometry. Current component CSS resolves geometry from public attributes; editing only a resolver does not update rendered lengths. The historical bundled specimen predates this architecture and is not a current implementation template. For current projects, follow their manifest and build workflow for authored specimen sources and generated output; do not assume a `specimens/index.html` target. The bundled snapshot retains its own historical output paths. Appearance-only changes leave geometry formulas alone.

For the bundled snapshot only: use Node 24+, no install step. From `assets/differential-forms` run `npm test` and `npm run build`; use `npm run dev` only when a preview is needed. For authored-source edits, refresh `source.fragmentSHA256`, record local provenance, increment version and update the changelog. The original source commit identifies the published baseline, not later local modifications.

Check finite/domain-valid results, border conservation, fixed slots, density-independent typography/label edges, zero-inset composites, curvature endpoints and growth under tight budgets. Inspect relevant `verification/visual-cases.json` cases for UI changes. Numerical passes do not establish visual quality, accessibility, contrast or responsiveness. Report verified behavior and remaining exceptions separately.

For consuming projects, use their scoped browser-verification policy and output locations. Reconcile geometry contracts, implementation and attribute/property metadata together, but do not synchronize a frozen bundled snapshot merely because the live project changed. Preserve snapshot provenance unless explicitly updating that snapshot.

## Superseded resources

`references/pre-differential/`, `references/geometry-history.md`, existing `scripts/lib/*.mjs`, `scripts/check-geometry.mjs`, `scripts/check-curvature.mjs` describe or execute the older model. They remain only for explicit maintenance of existing consumers. Do not use them as current formula authority or claim their tests validate Differential Forms. The Proportion study in `assets/proportion-lab/` is now an explicit Differential Forms consumer with authored source and shared-resolver builds; its retained old runtime files and `tests/` remain historical. Use its `AGENTS.md`, `docs/MIGRATION.md` and current `verification/` checks for maintenance. Do not publish it unless requested. Existing UI-KIT integrations likewise do not update automatically.
