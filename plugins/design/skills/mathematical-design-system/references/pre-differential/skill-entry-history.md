---
name: mathematical-design-system
description: Derive and validate proportional system formulas for geometry, typography, spacing and curvature. Use for mathematical model design, coefficients, invariants and numerical evaluation; site implementation and UI recipes belong to their consuming project.
---
# Mathematical design system

Use this skill to reason about a mathematically derived system: identify independent
inputs, derive dependent quantities, state units and domains, and verify invariants.
The supplied model is an adopted design convention, not a perceptual law or a
universal requirement for every interface.

Read [geometry formulas](references/geometry-contract.md) for the adopted model.
For use from another project, read [consumer integration](references/consumer-integration.md)
for portable imports, CSS mapping, radius ownership and verification. Resolve
relative resources from this SKILL.md directory, never the caller’s working
directory. Do not assume the author’s machine paths or local dev server.

The contract also explains the independent density axis. Executable
numerical references are in `scripts/lib/`:

- `scale.mjs`: current `resolveGeometry`, Control surfaces and independent spacing roles.
- `curvature.mjs`: current Standalone / Nested / Pill radii, scoped families and physical validation (`resolvePercentageRadiusGroup`).
- `legacy-scale.mjs` and `legacy-curvature.mjs`: frozen compatibility formulas only; never use for new consumers. Historical decisions live in `references/geometry-history.md`, not the current contract.
- `tier-mapping.mjs`: equivalent coefficient-table representation and validation.

Icon, label, glyph and media wrappers are internal anatomy of their owning Control.
They are not independent Containers, layout Groups, or new component/radius
scopes merely because they are DOM elements. Use Control wrapper spacing and
zero occupied-slot gaps. Label inline padding is L=n/2 per side; no E is folded into it. Do not apply Container/Group percentages to these wrappers.
Use M/G for layout margin/sibling gutter, and m/W/L for Control outer margin,
icon/glyph budget and label inline padding. E=m/2 remains collection-row/table-column spacing. These names distinguish existing quantities;
they do not change the formulas.
Role and tier examples must obey the same anatomy; see [role/tier fidelity](references/consumer-integration.md#role-and-tier-example-fidelity) for resolved padding, zero-gap overlays and audit coverage.
For diagnostic views, keep wrapper padding (including label L), artwork centering
and layout/collection gaps separately inspectable; see [guide semantics](references/consumer-integration.md#spacing-guide-semantics).

Current component invariants: icon and glyph wrappers are square `3n × 3n`.
Icon artwork is `2n`; glyph artwork matches Control typography, `n + 6`, and
is density-independent. Use the resolver's artwork insets when explaining
visible spacing; square wrappers include centering space beyond their padding.
The square border box and artwork dimensions remain fixed even when the declared
wrapper budget W cannot fit. W is an internal spacing requirement, not permission
to expand the wrapper, shift artwork, or silently reduce it. Report infeasible
budgets separately from radius conflicts. Guides partition measured empty space;
they do not redefine the required geometry.
Omit absent slots. Every label wrapper has L=n/2 padding on both inline sides,
regardless of occupancy or shape; no extra compensation is added. Outer padding
remains the Control margin. See the contract for exact equations and physical-conflict handling.

Changes adopted 2026-10-21: product coefficients [8, 1, 2, 0] (even shoulders, Regular heights
20/28/36, 24/32/40, 28/36/44; content and brand keep steps 1/2/3 by scale), and L=n/2 label inline padding with zero internal wrapper gap. Menu, listbox
and table rows still use E as a row or column gap. See the contract and history.

When adapting a system, distinguish existing coefficients from proposed changes.
Keep tier, scale, size and density independent. State whether a bound is nominal,
minimum or a physical cap. Preserve floating-point values through derivation;
round presentation only, never feed formatted values back into the model.

For coefficient/formula changes, update the contract and numerical implementation
together. Run `node <skill-root>/scripts/check-geometry.mjs` and
`node <skill-root>/scripts/check-curvature.mjs`, replacing `<skill-root>` with the
discovered skill directory.
Check monotonicity, finite results, dimensional consistency, density independence
of typography, and endpoint/degenerate cases. Numerical passes do not establish
visual quality, accessibility or browser behavior.

The interactive **Proportion** study is kept in
[`assets/proportion-lab/dist/index.html`](assets/proportion-lab/dist/index.html).
Edit this retained project in place; its `.openai/hosting.json` preserves the
published Site identity. To preview locally, serve `assets/proportion-lab/dist`
with an HTTP server (the study uses JavaScript modules). The bundled numerical
resolver is a snapshot of `scripts/lib/scale.mjs` and `scripts/lib/curvature.mjs`; synchronize it when adopting
formula changes. After changing wrapper/guide behavior, also run
`node <skill-root>/assets/proportion-lab/tests/spacing-guides.mjs` and
`node <skill-root>/assets/proportion-lab/tests/inspector-state.mjs`.
For rendered slot and media regression checks, run `node <skill-root>/assets/proportion-lab/tests/rendered-geometry.mjs <installed-playwright-module> <served-visualizer-url>`. It checks narrow/wide inheritance and guide toggles as well as slot/label-edge-padding geometry. Full responsive browser review remains incomplete.

The study is a consumer of the mathematical model, not a second formula authority.
Reusable component CSS, DOM anatomy and interaction guidance remain with base-ui.
Use the consuming project’s UI kit and repository instructions for component
implementation. This skill does not require a particular external kit checkout.
Do not modify or publish the retained visualizer when the task only concerns a
different consumer project.

Full-size `media` (avatars/logos/thumbnails) is internal Control anatomy: fixed `3n × 3n`, zero padding and zero centering inset. It occupies a leading/trailing slot and has no additional slot gap. Do not apply the icon/glyph wrapper budget to media. See the current geometry contract for media-to-label spacing and guide semantics.

Media shape is asset-owned by default (circular avatar, unchanged logo). Explicit Control-shape inheritance uses `resolveMediaRadius` with actual media size and the immediate row/button required radius; Sharp overrides retained floors. Report physical conflicts without clamping. See the media opt-in contract.

For the adopted UI-KIT sync, package exports, typed Select slots and implementation-specific limits, read [UI-KIT integration](references/ui-kit-integration.md). This is a consumer integration record; future edits do not propagate automatically.

Wrapper shape ownership: Control slot wrappers own any resolved border radius and overflow clipping. Icon/glyph artwork and media img/SVG children retain their authored radius, overflow, and shape styles; do not reset or inherit these properties through parent selectors. Circular avatar defaults belong on the media wrapper. Keep sizing/placement rules separate from shape ownership. For physical conflicts, keep the fixed wrapper and render dashed diagnostics outside the clipping layer; never alter artwork styles to make a requested radius fit.

Icon/glyph wrappers automatically follow the owning Control’s radius amount and retained-parent floor, using their actual fixed square frame. Media inheritance remains per-asset opt-in. Resolve against the immediate parent’s required radius; never inherit a raw parent pixel radius blindly. See the current contract for shape ownership and opt-out cleanup.

After editing the retained preview, run `node <skill-root>/assets/proportion-lab/scripts/refresh-assets.mjs` to version its CSS/module graph, then reload and inspect the actual open preview. A fresh test-browser pass does not prove a long-lived browser tab loaded the new assets. `--check` verifies the revision matches current source.

Painted buttons own an outer content-clipping boundary matching their resolved radius. Clip descendant slots at that boundary, including intrinsic logos; keep slot dimensions, label padding and artwork-authored styles unchanged. This is separate from optional media-wrapper shape inheritance. Keep focus rings on the button and required-geometry conflict diagnostics in an external, unclipped layer.

In the retained study, hide diagnostic overlays when all guides are off; keep conflict text available. Preserve exact resolver values: physical radius excess at or below 0.001 CSS px is measurement noise, not a conflict, and never clamp a radius to its cap. Present compact resolved values first and disclose formula and conflict detail; see consumer integration for presentation and comparison navigation.

Containment uses 0.05 CSS px tolerance consistently for edge equality, negative inset and parent bounds. Physical radius excess uses a separate 0.001 CSS px noise threshold; preserve exact requested radii and excess. Group validity is diagnostic, not a command to square every layer: paint each parent/row from its own physical validity, and retain containment and sibling failures separately. A failing child must not erase feasible parent or sibling radii. Keep genuine conflicts visible in consumer diagnostics even when overlays are hidden.

Menu command rows use resolveControlSurface directly: fixed inner slots S = 3n; row clearance m = (q − 2)n/4 on all edges; outer row height H = S + 2m. At n=8, Tight/Compact/Regular/Spacious/Loose rows are 24/28/32/36/40px while slots remain24px. Label padding L=n/2 and icon/glyph budget W are internal anatomy; internal slot gaps are zero. Collection row spacing remains E=m/2. No extra compensation applies to any Control label. Menu-frame outer padding is separate; a three-item frame is 2m + 3H + 2E. Menu row radius uses H/2; ordinary selection-listbox rows retain S height and S/2 radius reference. Do not apply this menu change to selection rows.

Tables and data-lists use resolveDataRowGeometry(n,density,controlPercent): inner slot minimum S=3n, block clearance m=(q−2)n/4, row minimum H=S+2m, cell inline padding P=m+W (W=n×Control percentage), and column gap E=m/2. At md/md Regular: S24px, H32px, m4px, P6px, E2px. Vertically center slots; allow both slots and rows to grow with multiline content. Native collapsed tables reserve E/2 on each facing cell edge, excluding the two outer edges; data-lists use grid gap E. Content separation across cells is 2P+E. Paint one row divider through an explicit color token, without adding layout thickness or duplicate cell borders/shadows. This replaces the previous 1.25d cell padding / d/4 clearance / 2n+2.5d row convention for current data rows; legacy formulas remain historical only.

When comparing data-row geometry, use matching single-line and multiline examples across all five densities, each resolved in its own context. Show measured growth and separate padding/gap guides without changing geometry. See [five-density comparisons](references/consumer-integration.md#five-density-data-row-comparisons).

For Sharp/Pill comparison views and responsive specimen cards, follow [comparison scope and verification](references/consumer-integration.md#sharppill-comparisons-and-specimen-cards). Fixed comparison shapes are explicit local overrides; surrounding cards follow Container settings independently. Per-arrangement readouts show leading/trailing label padding L and total edge-to-text inset, separating outer m and occupied slot widths.

For per-arrangement spacing readouts, show label padding L and the [total edge-to-text breakdown](references/consumer-integration.md#total-edge-to-text-insets). Include occupied slot widths on occupied sides; internal gaps are zero, and m+L describes exposed sides.
