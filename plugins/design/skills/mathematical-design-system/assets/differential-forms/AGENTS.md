# Agent entry point

## Required workflow
1. Read system.manifest.json and docs/principles.md.
2. Identify intent, semantic component, geometry family and parent context separately.
3. Read that component in contracts/components.json, its parts and composition relationships.
4. Resolve geometry using geometry/*.ts. Keep CSS `box-sizing:border-box`; resolved values are CSS pixels.
5. Compose only supported parts. Use semantic HTML and native inputs where possible.
6. Apply appearance independently of geometry. Follow docs/interaction.md.
7. Run `npm test`. For UI changes, inspect the relevant cases in verification/visual-cases.json; do not claim visual or accessibility checks from numerical tests.
8. Report changed rules, verification performed and remaining exceptions.

## Non-negotiable constraints
- Do not invent spacing constants, inherit every density into descendants, or subtract borders twice.
- Do not shrink text, icon slots or label wrappers to force nested content into a fixed outer height.
- Label edge compensation is independent of density. Chips use half the control label edge.
- Composite gap equals requested inset; zero requested inset means zero child curvature.
- Checkbox radius is 1u; radio and switch shapes remain circular/capsule.
- Transparent borders occupy their owner's interior in every state.
- Do not nest interactive controls inside buttons. Input compositions use a neutral wrapper.
- Use system-ui for UI, IBM Plex Mono 400 for specimen captions, Phosphor icons via CDN in HTML demos.
- Use subtle surface levels and no divider lines where surface color already identifies boundaries.

## Context routing
Geometry task: foundations + families + geometry.md + relevant resolver.
New component: parts + components + composition + interaction.md.
New layout: collection/card geometry + recipes; do not apply composite subtraction to ordinary cards.
Visual styling: appearance.md; preserve geometry.
Unspecified behavior: consult exceptions.md, keep the smallest explicit extension, record it as experimental.

Never infer that the frozen specimen is a reusable API or an accessibility certification. Do not publish, send messages or change access just because this document describes a workflow; follow the user's task authorization.

## Local project workflow
Run `npm test`, `npm run build`, then `npm run dev` (http://localhost:4173). Node 24+; no install step. Edit specimens/source.html and rebuild; do not hand-edit generated specimens/index.html. The source snapshot calculates its own CSS variables: when changing geometry, update the relevant contract, pure resolver, tests and specimen together. Read docs/local-project.md for the entry prompt and file ownership.

Current defaults: u4, border0, composite inset0u, Soft control/container curvature. Composed inputs use chip adornments and resolveComposedInput; multiline rows use collection geometry. The zero-inset child-radius rule applies to attached composites, not arbitrary nested components. Keep this distinction explicit.
