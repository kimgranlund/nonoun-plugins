# Review shell foundations

The shell bundles byte-for-byte snapshots of Maison's generated `geometry.css` and `layout.css` in `assets/foundation/maison/`. `provenance.json` records upstream relative paths and SHA-256 hashes. Builds inline these assets, so neither host needs Maison installed or network access. These files cover active geometry and layout only; historical `--md-sys-size-*` snapshots and density classes are not aliases and are not bundled.

## Authoring the shell

- Root defaults: `data-tier="product" data-scale="md" data-size="md" data-radius="round"`.
- Each axis resolves independently from its nearest declaration. Change data attributes, not resolved `--g-*` properties or compound ancestor selectors. The bundled resolver recomputes geometry on every element.
- Controls consume `--g-height`, `--g-inset`, `--g-text`, `--g-icon`, and `--r-control`. Product/md/md gives 32px height, 8px inset, 14px text, and 16px icons. Labels use `--g-caption-text`; label gaps use half the inset. Every element also exposes `--g-micro-*` for the same scale/size.
- Radius modes are default, round, sharp, pill. Cards use `--r-card`, inset surfaces `--r-inset`, and icon marks can use `--r-mark`. Do not replace these with a separate radius ladder.
- Layout uses `--m-space-*`, `--m-inset-*`, `--m-gap-*`, border and focus roles. Color, editorial typography, and shell viewport widths use authored `--wr-*` tokens in `shell.css`.
- Each wireframe iframe embeds its own copy of the same geometry/layout foundations, followed by token-based artifact defaults and manifest CSS. Axes and theme overrides inside a preview are independent of the shell. The artifact's preview viewport dimensions and feedback schema remain separate from geometry. A shell-only update does not require migrating design revision IDs.
- Compare, Inspect, and My selection remain distinct. Inspect and My selection expose a visible Back to compare control.

## Box and slot model

All shell elements use border-box. Controls reserve a constant thin border in every state; borderless appearances set border-color to transparent rather than removing the border. Height includes that border. While the focus-visible ring is displayed, component border color becomes transparent and border width stays occupied. Pointer focus without a ring retains its ordinary boundary. Buttons have minimum inline size equal to height and maximum 100%; labels truncate within half-inset padding. Fixed icon containers use icon geometry, contextual glyphs use icon size, and indicators use text-size glyphs. Native selects retain native behavior with a decorative custom indicator. Native input text includes the outer inset plus half-inset text padding.

## Artifact containers

Use a softly contrasting outer review card for title, rationale and actions, with a separate white preview surface nested inside it. Outer headers use 2.5 times the geometry inset; the preview well keeps one inset around the preview sides and bottom. The inner surface uses the inset radius and a constant thin border. Only the preview surface clips its content; the outer container leaves control focus rings visible. Frame scaling measures the inner content width and includes the occupied border in the wrapper height. This structure applies to page overview, comparison and inspect views without changing the iframe's design content.

## Spacing invariants

Every text-bearing button, including quiet navigation actions and disclosure headers, keeps the root geometry inset and the label slot half-inset padding. Quiet appearance changes paint, never occupied geometry. Do not zero button or label padding to align text with adjacent prose; align their enclosing layout instead. Internal control gaps stay half the inset. Compact badges use chip height, chip inset, chip text, and half-chip-inset gaps. Panel/layout gaps and insets use the public layout roles; these are distinct from control slot geometry. Zero padding is appropriate for structural wrappers whose children own the inset, not for text-bearing controls.

The optional rendered `scripts/check-shell.mjs` checks actual controls, including hover, selected, disabled, and ghost appearances, at different geometry sizes. Preserve this check when adding control variants.

## Refreshing the snapshot

Read Maison's styling reference, geometry contract, CSV, and definition before changing foundations. The CSV and tier formula are authoritative. Generate upstream leaves only with `node scripts/generate.mjs` in Maison under its own workflow and required Node version (v24.18.0 for this snapshot). Never hand-edit generated CSS, component.md, manifests, dist, gen-ui, or package.json; do not run generate-all for this task.

After upstream outputs are ready, copy the two generated CSS files unchanged into this skill and update their provenance hashes. Keep the artifact self-contained. Verify all 27 tier/scale/size combinations and all four radius modes with nested independent axes, then run the skill's runtime checks and inspect desktop/mobile renders. If adding shadow-root controls, include the geometry resolver within those roots as required by Maison's host contract.

## Scrollbars

Hide scrollbar chrome throughout the shell and iframe previews with `scrollbar-width: none` and the WebKit scrollbar selector. Preserve scrolling and keyboard access; do not use overflow hidden to hide scrollbars on scrollable panels, dialogs, or fields.

## Color foundation and scheme

`assets/foundation/ultimate-tokens/colors.css` is an actual `exportCSS` output, using `source-state.json` with Neutral, Primary, and Danger palettes and `colorPrefix: "md-color"`. Provenance records the exporter and role sources. It is embedded into the shell and every preview. Refresh it by calling the exporter with the saved state, never by inventing Material role names. Builds remain independent of the source repository.

The exported vocabulary is `--md-color-{palette}-{role}` (for example neutral-surface, neutral-on-surface, neutral-outline, primary, danger-on-surface), plus raw ramp stops and fixed system constants such as md-color-dialog-backdrop. Component aliases `--wr-*` and `--ui-*` reference these foundation roles; keep literal colors confined to the exported foundation. The exported `light-dark()` semantics follow CSS color-scheme.

The header scheme button sits immediately left of Decisions and cycles System, Light, Dark. It initializes from the system, saves the explicit preference separately from feedback, and synchronizes current and newly created previews without rerendering or changing decisions. System continues to follow OS preference. Custom artifact CSS may override roles intentionally; literal custom colors will not automatically become mode-aware.

Mobile previews keep a 390px logical viewport but scale to the entire wrapper content width, both up and down. Do not cap mobile scale at 1: it leaves unused horizontal space in wide cards. Wrapper height must track the scaled content plus its border. Desktop previews retain their 1200px viewport and scale-down cap.

The scheme trigger is icon-only: desktop for System, sun for Light, moon for Dark. Use bundled Phosphor regular SVGs pinned to @phosphor-icons/core 2.1.1; compiled local masks inherit currentColor within an icon-sized slot. Keep square geometry, zero icon-only inline padding and an accessible mode/next-mode name. A browser title may supplement that name; it is not a custom tooltip implementation or the sole explanation. Icon rendering does not require runtime network access.

## Corner shape

Use `corner-shape: superellipse(1.5)` with a 1.5 presentation radius scale where supported. This softer curve replaces literal `squircle` (`superellipse(2)`), which remained visually tight on short controls even with increased radii. Feature detection selects the treatment; do not sniff browser names.

Fallback engines use the original foundation radius with scale 1 and factor 1. Do not reduce the fallback radius. The former 0.543214 compensation is retired. The two curves are intentionally approximate, not geometrically identical. Radius clamping means larger numeric values alone cannot guarantee softer corners.

Continue consuming foundation radius roles. Zero radius remains square, and control dimensions and insets stay unchanged. Verify rendered examples, not only computed radii. Do not edit generated foundation files. See [CSS corner shapes](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/corner-shape-value).

## Viewport shell and scroll ownership

Use a viewport-height flex column (`100dvh`, with `100vh` fallback). Header, notices and toolbar use intrinsic height and do not shrink. The workspace receives the remaining space with `flex: 1 1 0` and `min-height: 0`. Its grid uses `minmax(0,1fr)` rows and columns. The document has `overflow: hidden`; canvas main and review panel own `overflow: auto` and `overscroll-behavior: contain` independently. Header stays stationary because it is outside both scroll regions; no guessed header-height subtraction is needed.

On narrow screens the remaining workspace uses a 3:2 vertical split between canvas and review panel, retaining independent scrolling and access to both. The panel toggle sticks within its own scroller. Dialogs retain their separate scrolling. Preserve canvas-main scroll offset across renders and asynchronous iframe loads. Hidden scrollbars do not remove wheel, touch or keyboard scrolling.

## Icons and native selects

Use regular Phosphor icons by default from the bundled @phosphor-icons/core 2.1.1 assets. The artifact builder compiles `.ph-icon[data-ph]` to local SVG presentation before delivery; unsupported names fail the build. Standalone UI must embed the local SVG or its compiled mask. Identity text, content illustrations and review-state text are not automatically converted to icons. Accessible names remain independent from decorative glyphs. No runtime network access is required for icons.

Keep selects as actual HTML `select` elements, with native options, focus, keyboard and selection behavior. Decorate using `.select__root` with non-interactive leading icon and trailing indicator slots inside its bounds; never put a separate actionable chevron beside a partial focus ring. `data-select-icon` is build-time shorthand for a bundled leading Phosphor glyph. Authored anatomy works without JavaScript; see [the static recipe](../assets/recipes/native-select.html). The artifact builder compiles bare selects before delivery and preserves existing wrappers; copied standalone markup must contain the anatomy. Geometry supplies height, inset, icon slot and glyph size; center slot contents and reserve corresponding text padding. The control owns border/focus paint and the icons use `pointer-events: none`. Preserve the available text width and native disabled semantics.

## Scripts-disabled preview

The builder includes native disclosure sections for every raw proposal, including each page's declared composition. With scripts disabled, these replace the inactive review chrome. Each preview is a titled, sandboxed, scrollable iframe with the same bundled foundations and manifest CSS. This mode does not apply imported choices, persist feedback or run application simulations; its visible notice states those limits. Native disclosure and navigation remain available. CSS is repeated for iframe isolation and offline portability, so measure artifact size when extending large manifests. `check-shell-fallback.mjs` verifies both script modes and composition fidelity across three engines.
