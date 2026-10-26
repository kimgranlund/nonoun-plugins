---
name: base-ui
description: Build and adapt interfaces with Differential Forms components, composition recipes and appearance rules, aligned with mathematical-design-system. Use for application UI and component implementation; wireframe-review owns alternatives and feedback.
---
# Base UI — Differential Forms

Use **Differential Forms** for new UI. [mathematical-design-system](../mathematical-design-system/SKILL.md) owns the adopted geometry model and portable source; this skill owns how to consume it in semantic UI. The name base-ui is unrelated to `@base-ui/react`.

## Source and routing

The shared source root is `../mathematical-design-system/assets/differential-forms/`, resolved relative to this skill directory. Snapshot paths below are relative to that source root; current-project paths come from that project’s entry point. Do not resolve them against the calling project or a personal checkout. Existing project instructions and explicit user decisions take precedence over the bundled baseline.

For current development, start at the consuming project’s `AGENTS.md` and follow its registry and package routes. Read the relevant manifest fields and linked governing documents; do not assume filenames, field names or package locations. Use the project’s shared terminology and construction conventions rather than introducing synonyms. Evaluate `avoidWhen` and `useInstead`, implemented availability, registration dependencies and the public component API. The bundled v0.2.2 snapshot is a frozen historical geometry/specimen baseline, not the current custom-component distribution; do not export it as a current component starter. Use a verified current project export for new component adoption.

Identify intent, semantic component, geometry family and parent context separately. Follow the registry’s resolved contract, parts and composition references before creating markup, including generated markup. For standalone examples as well as routed applications, discover and import the project’s shared CSS foundation before component companions; do not reconstruct it from selected token files. Verify its readiness, typography and motion dependencies through the chosen delivery path.

- Sizing/spacing: [geometry integration](references/geometry-spacing.md), then the relevant `geometry/resolve-*.ts` and geometry-family contract.
- Composition: `docs/composition.md` and only the relevant `recipes/*.json`.
- Appearance: `docs/appearance.md`.
- Keyboard, naming and state: `docs/interaction.md`.
- Unsupported components/behaviors: `docs/exceptions.md`; add the smallest explicit experimental extension. Do not silently import old kit geometry.

The source snapshot includes working examples in `specimens/source.html`; it is evidence, not a production component API or accessibility certification. Its accumulated overrides and document-level keyboard-mode listener need deliberate integration.

## Implement

Use implemented custom-element components and supported public composition APIs. Components own custom-part anatomy and text nodes; do not introduce native component interiors without explicit user authorization. Preserve semantic roles, accessible names and keyboard behavior. Use neutral input compositions, chip adornments and named selector/clear/stepper actions. Never nest interactive controls inside buttons or put interactive descendants inside options. Existing consumers may retain native comparisons during verification; do not silently replace unsupported compositions.

Public component attributes configure geometry and state. All component styling and token mapping belongs in `components/{component}/{component}.css`; companion CSS resolves lengths. TypeScript supplies behavior and reflects public input/state attributes only. Never generate styles, inline declarations or stylesheets at runtime. Pure geometry resolvers are numerical references; use `box-sizing:border-box` and preserve CSS pixels. Templates may construct owned anatomy. Node 24+ runs numerical references; browser applications use their normal build. Keep appearance independent of geometry.

Use the current project’s declared geometry defaults. The frozen v0.2.2 snapshot defaults are u4, border0, composite inset0u, Soft curvature and label edge1.5u; they are not overrides for current consumers. Compact/default/loose are family-specific. Chips use half the control label edge. Preserve slots, typography and label compensation across density changes. Transparent borders consume their owner's interior once. Cards and collections preserve descendant control density; multiline rows use collection geometry. The zero-inset child-radius rule belongs to attached composites, not arbitrary nesting or composed-input adornments.

Use system-ui for interface text, IBM Plex Mono 400 for specimen captions, and pinned Phosphor CDN icons for HTML demos. Preserve paired light/dark surface roles; use subtle surface levels without redundant divider lines. Do not substitute the legacy Bricolage font or percentage-curvature tokens.

Use the current project’s focus token and outline contract for keyboard focus. The frozen snapshot uses a 3px solid ink outline with 0px offset; do not carry that color or geometry into a project with a different contract. Text fields indicate focus on their neutral wrapper; sibling actions show their own ring. Avoid clipping or sibling occlusion of focus paint. Do not add tab stops to passive content. Hover, selected, invalid and focus states must not change geometry. Preserve accessible names, native keyboard operation and sensible focus return.

## Metadata and shared-style maintenance

When changing a public input, reconcile its manifest with the actual class and CSS owner. Writable JavaScript accessors belong in `properties`; attribute-only inputs belong in `attributes`. An observed attribute does not prove reflection, and an internal popup's CSS input is not a public host API without forwarding. Verify inherited APIs before adding or removing entries.

Reuse the consuming project's canonical typography, spacing and icon owners; keep family-specific geometry local when required by its contracts. Repeated CSS selectors alone are not defects: remove only demonstrated obsolete/conflicting declarations, checking the resulting computed geometry. Follow the project's scoped browser-verification policy for affected consumers; build/type/unit success does not imply browser interaction coverage.

## Export and alignment

To validate or export the frozen v0.2.2 historical baseline (not the current component package), run:

```sh
node <base-ui-root>/scripts/differential-forms.mjs --check
node <base-ui-root>/scripts/differential-forms.mjs --export <new-directory>
```

The helper reads the sibling mathematical-design-system snapshot directly, validates its declared files and authored-source hash, and copies it into a new directory. It refuses existing destinations. This is a portable specimen starter, not an application generator. Adapt its components to the user's requested application rather than treating the geometry jig as the application. No install or hosting connection is required.

There is no second mutable formula copy inside base-ui. Updates to the shared snapshot are picked up by subsequent checks/exports. Previously exported projects remain independent; synchronize them intentionally and verify their local changes. Formula changes must update contracts, numerical resolvers, companion CSS, relevant recipes and tests together. Current specimens consume the shared system rather than maintaining independent formula copies. Edit source.html and regenerate index.html, never hand-edit the generated preview.

## Verification and delivery

For an exported Differential Forms project, run `npm test`, then `npm run build`; use `npm run dev` when a local preview is needed. Refresh the specimen hash and provenance after authored changes, following docs/local-project.md. For other consumers, run their relevant checks and test actual rendered component behavior.

Inspect relevant cases from `verification/visual-cases.json`, including keyboard completion/focus, narrow layouts, light/dark states and the geometry boundaries affected by the change. Preserve content/slot sizes when budgets are tight; permit documented container growth. Report numerical, browser and accessibility evidence separately. Read the chosen project’s current exceptions before making production-readiness claims; historical snapshot limitations do not describe every current API.

When UI feedback exposes a composition defect or a missed issue after a claimed pass, use Closed Loop Run’s UI feedback procedure (the `dev-tools:closed-loop-run` skill, page `references/ui-feedback.md` in that skill's folder) to diagnose both the artifact and the acceptance gap.

For ordinary edits use targeted checks and fresh visual inspection. Broader review tooling is optional unless requested or required by the consuming project; legacy kit review gates do not certify this new model. Do not publish or synchronize other consumers solely because a maintenance workflow exists.

## Legacy compatibility boundary

The older `scripts/api.mjs`, `build.mjs`, `build-page.mjs`, component-context commands, `assets/geometry/`, CSS/token bundles, old recipes and other pre-existing references implement the previous UI kit. `kit.json` and its sealing script identify that compatibility package; they do not establish Differential Forms conformance. Do not use those builders or assets for new Differential Forms UI.

For explicit maintenance of an existing old-kit consumer, consult [the historical entry](references/pre-differential/skill-entry-history.md); its original relative links were written from the base-ui root and must be resolved from that original location. Follow the consuming project's current instructions. Migration requires intentional component/API mapping. This skill update does not migrate the separate UI-KIT repository, wireframe-review compatibility copies, or deployed sites.
