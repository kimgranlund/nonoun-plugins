# Current standalone geometry contract

The standalone kit projects [the mathematical contract](../../mathematical-design-system/references/geometry-contract.md). Its portable resolver is `assets/geometry/scale.mjs`; curvature is `assets/geometry/curvature.mjs`. `control.mjs` composes the public control APIs and reports internal spacing conflicts. These snapshots ship with consumers: no home-directory imports are required. Maintainer generation imports the sibling mathematical source. The separate ui-kit project does not automatically receive these updates.

## Control anatomy

For resolved unit n, density q = 2/3/4/5/6 (Tight/Compact/Regular/Spacious/Loose): S=3n, M=(q−2)n/4, H=S+2M. At n=8, H=24/28/32/36/40px. Icon artwork=2n; glyph artwork=control font size=n+6. Icon and glyph wrappers are fixed 3n squares, with centered artwork. Label wrappers are 3n high and flexible in width. All are internal Control anatomy, never Groups or new Container/radius scopes.

Icon/glyph wrapper budget W=n×Control ratio (default25%). Internal Control slot gaps are zero; collection rows and table columns retain E=m/2. Never expand the square or shift its art to satisfy excessive W: 2W+art>S is a conflict. Label inline padding is L=n/2 per side, independent of W. Omit absent media slots and their gaps. Buttons of every shape use exactly L on both label edges, with no extra compensation. Slot occupancy does not change this padding. Use explicit label markup; bare text remains a compatibility fallback. Outer button padding stays m. Border paint is inside the requested frame and must not expand zero-margin Tight controls.

## Spacing and radius

Page, Container and Group gutters are reference M times independent ratios 100%,75%,50%. Groups have no surface/edge padding and do not compound a parent gutter. Control wrapper ratio defaults25%. CSS ratios use fractions, resolver arguments percentages.

Container radii use margin×amount; Control radii use half reference height×amount. Both default Sharp (amount0). A Nested child takes max(its candidate, immediate parent required radius×retained); each family owns its amount and retention. Listboxes are Controls; their reference height is H, independent of row count. Composition stops at component/family boundaries. Standalone/Nested/Pill are explicit modes. Use the measured-frame radius resolver for validation; do not clamp individual layers, enlarge examples, or treat browser radius normalization as success. Expose invalid required geometry with dashed outlines and issue text.

CSS inputs: --page-gutter-ratio, --container-gutter-ratio, --group-gutter-ratio, --control-gutter-ratio; --container-radius-amount, --control-radius-amount, --control-radius-retained. Container nested retention requires the measured resolver. Geometry tokens include --g-d, --g-control-margin (Control M); --g-margin remains the legacy d alias, --g-slot-height, --g-wrapper-padding (W), --g-label-padding (L), --g-wrapper-gap (0), --g-slot-gap (collection E=m/2). Container margins remain 2d/3d/4d; tables and data-lists use the Control-derived row contract below.

## Guides and compatibility

Diagnostic overlays separately expose margins, icon/glyph budget W and label padding L, remaining centering space, gaps. Supporting role/tier examples use the same L=n/2 and zero internal gaps as real controls; see [role/tier fidelity](../../mathematical-design-system/references/consumer-integration.md#role-and-tier-example-fidelity). Zero-gap slots must not retain adjacent margins or pseudo-element gap bands. Gray gap guides belong only to actual layout/collection separation. Independent toggles must not change geometry. Clip diagnostic paint to actual empty areas; report the full requested values and conflicts separately. See [consumer integration](../../mathematical-design-system/references/consumer-integration.md).

Legacy Chip/Badge/control-ladder and historical native recipes are compatibility implementations, not examples of current Control anatomy. Their historical geometry assertions are not current-model verification. See [historical formulas](../../mathematical-design-system/references/geometry-history.md). Existing consumers need an explicit kit sync and visual review; regenerating this kit does not silently update vendored copies.

## Full-size media slots

`mediaSize = mediaSlotWidth = 3n`: avatars, logos and thumbnails fill a fixed square Control wrapper. `mediaPadding = mediaInset = 0`, independent of the Control gutter percentage. Do not apply W to media: its content already consumes the whole square. It remains internal Control anatomy, not a new Container/Group or inherited radius scope. An avatar may crop with `cover` and use its own circular mask; a logo normally uses `contain` and preserves its own silhouette. Transparent or letterboxed asset pixels are asset content, not wrapper padding.

Media occupies a real leading or trailing slot without changing label padding L. Internal Control wrappers abut: media-to-label content separation is L=n/2 (`mediaContentSeparation`), and media-to-media separation is zero. Do not add E as a gap, label padding or media margin. Omit absent media entirely. Guide toggles show no wrapper-padding or centering contribution inside full media; they still expose outer margins and label padding L. Validate the fixed frame and occupied content; never shrink media to accommodate an unrelated icon/glyph padding budget. At n=8, media is24px square across every density; at n=4/24 it is12/72px square.

For `resolveControlAnatomy`, pass occupied `slots` (e.g. `["media","label"]`) so validation checks only present icon/glyph budgets. Media requires no padding budget.

### Opt-in Control shape for media

Media defaults remain asset-owned: avatars use `circle`, logos use `intrinsic` (no added curvature). Explicit `shape: 'control'` opts a media frame into Control curvature without making its wrapper a Container or Group. Use `resolveMediaRadius({shape,frame,amount,retained,parentRadius})` from curvature.mjs. Supply the actual media border box and the immediate row/button's **required** radius, never a normalized or clamped CSS radius.

For Control media, candidate = amount/100 × measured media height/2; floor = retained/100 × immediate parent radius; required R = max(candidate,floor), except amount0 forces Sharp0. Validate R against min(width,height)/2. A retained floor can exceed a 3n media cap in a larger button: preserve the requested result and show a dashed geometry conflict, rather than enlarging or shrinking the frame. No uniform concentric inset is required: media is an internal child beside a label. Existing parent-scope conflicts remain visible independently.

Base UI: `data-slot="media" data-media-shape="control"` opts into clipping; set `--media-required-radius` from the measured resolver. `data-media="avatar"` remains circular when the opt-in is absent; logos remain unchanged. Clear the opt-in and its resolved style to restore defaults. On conflict, expose issue text and required dashed geometry; CSS alone is not validation. Zero padding and 3n square dimensions do not change.

The visualizer has separate avatar and logo inheritance toggles under Inspector → Radius. Both default off, persist in saved configurations, and reset off. With inheritance on, Control Sharp makes media square; Container settings do not affect it.

The current Control slot model has been adopted by UI-KIT as of 2026-10-18. [Integration record](../../mathematical-design-system/references/ui-kit-integration.md) documents typed Select slots, exports, separate build ownership and verification scope. Future changes still require explicit synchronization.

Wrapper shape ownership: Control slot wrappers own any resolved border radius and overflow clipping. Icon/glyph artwork and media img/SVG children retain their authored radius, overflow, and shape styles; do not reset or inherit these properties through parent selectors. Circular avatar defaults belong on the media wrapper. Keep sizing/placement rules separate from shape ownership. For physical conflicts, keep the fixed wrapper and render dashed diagnostics outside the clipping layer; never alter artwork styles to make a requested radius fit.

Icon/glyph/indicator wrappers in current Buttons and Listbox options inherit Control shape using the same candidate and immediate-parent retained floor as opted-in media; Sharp amount0 forces zero even with retention. CSS amounts/retention are fractions (0–1), resolver inputs percentages. Preserve fractional amounts; do not round before resolving. `--media-required-radius` is the wrapper-local measured override for these slots. CSS fallback supplies paint only, not physical-size validation. Standalone Base UI has no automatic media binding: consumer code must measure/validate each wrapper against its own immediate row/button, recompute on owner/context changes, and remove or restore the override and owned `data-geometry-conflict` on opt-out, replacement, destroy, and abort. Never carry a row's measured override into a cloned Select trigger; resolve the new owner independently. Restore authored prior styles/diagnostics rather than erasing consumer-owned values. Keep overflow clipping during conflicts; use an external diagnostic layer for required geometry. No child artwork radius or overflow reset is permitted.

Control-shaped wrappers and circular media defaults explicitly use `corner-shape:round`; inherited superellipse/bevel paint must not change the scalar-radius contract or turn a circular avatar into a squircle. This reset belongs on the wrapper only; artwork keeps its authored corner shape.

Painted buttons own an outer content-clipping boundary matching their resolved radius. Clip descendant slots at that boundary, including intrinsic logos; keep slot dimensions, label padding and artwork-authored styles unchanged. This is separate from optional media-wrapper shape inheritance. Keep focus rings on the button and required-geometry conflict diagnostics in an external, unclipped layer.

Containment uses 0.05 CSS px tolerance consistently for edge equality, negative inset and parent bounds. Physical radius excess uses a separate 0.001 CSS px noise threshold; preserve exact requested radii and excess. Group validity is diagnostic, not a command to square every layer: paint each parent/row from its own physical validity, and retain containment and sibling failures separately. A failing child must not erase feasible parent or sibling radii. Keep genuine conflicts visible in consumer diagnostics even when overlays are hidden.

For the portable resolver, `group.valid` includes containment and all layer failures. For one layer’s paint eligibility, test `layer.physicalExcess <= 0.001`; retain `group.issues` for reporting. Resolve sibling rows as separate single-frame groups using their own actual dimensions and the immediate parent’s required radius. Base UI does not supply an automatic binding: consumers own repaint and cleanup.

## Menu rows versus selection-list rows

Command-menu items use `button.button__root` with role `menuitem`, `menuitemcheckbox` or `menuitemradio`. Each is a full Control: `H=3n+2m`, `m=(q−2)n/4` on all four edges. At md/md n=8, row heights are 24/28/32/36/40px; slots remain 24px. Menu outer padding is a separate surface inset. Icon/glyph budget W is unchanged; internal slot gaps are zero. Menu labels receive L=n/2 without extra compensation; missing slots are omitted. Use `resolveControlSurface` for the row and its own measured height for radius validation and immediate-parent wrapper inheritance. Keep outer surface and sibling row validation independent. Ordinary Listbox selection rows remain 3n; this change does not resize all listbox options or alter native select popups.

## Tables and data-lists

Rows use the Control minimum H=3n+2m, with m=(q−2)n/4. At md/md (n=8), Tight/Compact/Regular/Spacious/Loose resolve to 24/28/32/36/40px. Center a minimum 3n content slot vertically; multiline content grows both slot and row without clipping or fixed heights. Native table row height is a minimum. Use `.table__slot` for composed/multiline cells; bare native text has a 3n line box. Data-list dt/dd provide the same minimum slot.

Cell inline padding P=m+W, W=n×Control gutter ratio; block padding=m. Column gutter E=m/2 is additional. Native collapsed tables reserve E/2 on each internal facing cell edge, with no extra outer-edge gutter; grid data-lists use column-gap E. Content-to-content separation is 2P+E. Regular defaults: P=6px, E=2px, H=32px, S=24px. `--g-table-cell-margin`, `--g-table-clearance`, `--g-table-column-gap`, and `--g-table-row-height` project these values.

A single non-layout row inset divider consumes `--ui-data-divider` (default `--ui-divider`); cells have no duplicate border or shadow. Keep native table semantics and scoped headers. Existing compact/tabular row aliases use this same minimum; explicit data-inline-spacing=none remains a consumer opt-out. Narrow stacked data-lists grow for both labelled values.

### Five-density data-row comparisons

Use identical single-line and multiline content in Table and Data-list examples across Tight, Compact, Regular, Spacious and Loose. Keep column widths and content consistent so wrapping differences reflect spacing, not different examples. At Product md/md the single-line minimum heights are 24/28/32/36/40px; multiline rows grow without clipping. Resolve each column against its own density, even when the inspector highlights another density.

Show H, S, m, P and E plus the actual measured multiline heights for both structures. Measure after layout and refresh on font, viewport and configuration changes; display rounded values without feeding rounded values into geometry. Data guides show cell edge padding and reserved intercell gaps separately, based on actual bounds. Toggles must change overlays only, never row dimensions. A table’s E is split across facing cell edges; a data-list uses real grid gap E. Do not double-count P as an additional column gap.

Keep density headings visible, expose previous/next scrolling controls and a named focusable comparison region, and retain hidden scrollbars. Teaching readouts stay outside the specimens. Verify all five density minima, multiline growth, one divider per row, guide-on/off geometry invariance, narrow-width scrolling and keyboard navigation. UI-KIT owns its recipe/site examples; installed Base UI provides the portable geometry and styling contract. Do not import an author’s project path.

`resolveButtonPadding({height, margin, wrapperInset, hasLeading, hasTrailing})` uses `wrapperInset=surface.labelPadding` (L). Labels receive L on both sides for every occupancy and radius; extra `edgePadding` and `compensation` are compatibility zeros. At n=8, label padding is4px per side across all densities; at Regular m=4, exposed edge-to-text inset is8px. Shape does not change natural width.

### Sharp/Pill comparisons and specimen cards

Show leading and trailing **Label padding** beneath each arrangement pair: L=n/2 on both sides, excluding outer margin m. At n=8 every arrangement shows4px /4px. Values are independent of density, radius, icon/glyph budget W and slot occupancy. Use logical sides and resolved values; never feed rounded readouts back into layout.

For a button shape comparison, pair identical content in explicit Sharp (R=0) and Pill (R=min(width,height)/2) examples across all five densities. Include label-only, icon + label, label + glyph, avatar + label and label + logo arrangements. Both shapes use identical L=n/2 label padding; do not stretch buttons to manufacture equal widths. Measure and display each pair's actual widths after layout, refreshing for font and context changes. Fixed comparison shapes override the Control radius dial only within those examples; explain that distinction. Inherited icon/glyph wrapper shape follows the local example's shape, while media keeps its per-asset defaults or opt-in behavior.

Specimen cards are Container surfaces, separate from the Controls they demonstrate. Resolve their card margin from the current purpose/scale/size and each column's density, their sibling gutter from that margin and the Container ratio, and their radius from the Container family. Do not leave fixed square corners or hard-coded padding/gaps on these cards. Container settings must not change button slot sizes, padding or widths. A card containing Controls has no Container child-radius retention relationship with those Controls. Teaching labels/readouts are not extra Control slots.

Verify natural equal widths for all 25 pairs, fixed Sharp/Pill radii, and card margin/gutter/radius response without changes to button widths. Keep real conflicts visible separately, density headings sticky, scrollbars hidden, and comparison navigation keyboard-accessible.
