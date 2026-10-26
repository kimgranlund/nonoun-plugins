# Using this model in another project

Read [the current contract](geometry-contract.md) first. Resolve every path in
this skill relative to the directory containing its SKILL.md, not the consumer's
working directory. Do not assume a particular username, checkout or local server.

## Load the current API

The current modules are self-contained ES modules with no package dependencies:

- `scripts/lib/scale.mjs`
- `scripts/lib/curvature.mjs`

For local analysis, import their absolute file URLs. For a deployed application,
copy these two files together into a consumer-owned module directory, record the
source location and file hashes in the project's provenance, and import the local
copies. Synchronize snapshots deliberately after model updates. Never import a
user's absolute skill path from browser code or copy the visualizer as the model.

```js
// Paths below are relative to the consuming application's chosen module folder.
import {
  resolveGeometry, resolveControlSurface, resolveSpacingRoles,
} from './model/scale.mjs';
import {resolvePercentageRadiusGroup} from './model/curvature.mjs';

const geometry = resolveGeometry('product', 'md', 'md', 'regular');
const control = resolveControlSurface(geometry.n, 'regular', 25);
const roles = resolveSpacingRoles(geometry.containers.card.margin, {
  pagePercent: 100, containerPercent: 75, groupPercent: 50,
  controlPercent: 25, controlUnit: geometry.n, controlMargin: control.margin,
});
// control: H32, inner24, margin4, icon/glyph budget2/side, label4/side, wrapperGap0.
// roles: page gap24, container gap18, group gap12 (zero group edges).
```

`resolveGeometry().surface` is the default Control geometry. Use
`resolveControlSurface` when the Control wrapper percentage is configurable.
Layout references and Control margins are different quantities; `d` is not the
Control's outer margin. Avoid the ambiguous word “gutter” in consumer tokens:
prefer `wrapperInset`, `slotGap`, `containerGap` and `groupGap`.

## Map geometry to components

Treat icon, label and glyph wrappers as internal anatomy of one Control. They
are implementation slots, not Container or Group instances. Apply W and E from
the owning Control, with no new margin tier or radius scope. Explicit nested
surfaces (such as a listbox frame and its row surfaces) are a separate concern;
wrapping text or artwork in a DOM node does not create such a surface.


| Component quantity | Resolver field |
| --- | --- |
| Outer control height / edge budget | `control.height` / `control.margin` |
| Wrapper height / icon/glyph budget / label inline padding | `control.slotHeight` / `control.slotPadding` / `control.labelPadding` |
| Internal slot gap / collection row gap | `control.wrapperGap` = 0 / `control.slotGap` = m/2 |
| Icon / glyph artwork dimensions | `control.icon` / `control.glyph` |
| Icon / glyph wrapper widths | `control.iconSlotWidth` / `control.glyphSlotWidth` |
| Tile / Card / Section margin | `geometry.containers[level].margin` |
| Page / Container / Group sibling gaps | `roles[role].gutter` |

Icon and glyph wrappers are square 3n × 3n. Icon artwork is 2n; glyph
artwork matches Control typography (`geometry.type.control = n + 6`). Both
artwork sizes remain independent of density. At product md/md, wrappers are
24px square, the icon is 16px, and the glyph and Control text are 14px; do not shrink
artwork or expand the wrapper to accommodate excessive W. Icon padding fits
only when 2W+2n ≤ 3n; glyph padding fits when 2W+(n + 6) ≤ 3n.

Keep square wrapper dimensions fixed even when W is infeasible. One implementation
is a fixed-size relative wrapper with absolutely centered artwork: reserve W as
an internal spacing budget rather than allowing CSS padding to enlarge the box.
Guide measurement and conflict detection must then read the declared W token,
not computed padding=0. Include wrapper-budget conflicts in the inspector's
conflict count; checking radius caps alone does not validate wrapper geometry.
Report 2W+artwork > 3n as a conflict; never shift or shrink artwork to hide it.

Use border-box sizing and count the border inside the edge budget. Decorative
inset strokes do not consume layout space. Label padding L=n/2 is independent of icon/glyph budget W. Internal Control wrappers abut; never fold a gap into labels or add margins between non-label slots.
Individual buttons use `resolveButtonPadding({margin: control.margin,
wrapperInset: control.labelPadding, height: control.height, hasLeading,
hasTrailing})`. Outer inlinePadding stays m. Apply labelStart and labelEnd to
the label wrapper's logical inline padding. Every side receives L=n/2, independent of occupancy; no extra compensation or gap is added. Artwork remains centered, so
actual artwork edge spacing includes `iconInset` or `glyphInset`, not just W.
Determine presence from actual siblings before/after the label. Omit absent slots
entirely; reserve blank slots only for explicit alignment such as listbox checks.

A Group has no edge padding or painted radius surface. Its gap is computed from
the borrowed margin reference, never another gap. Preserve art sizes within the
3n wrappers; labels can flex and ellipsize.

For menus/listboxes, the adopted row surface is 3n; outer padding is control.margin
and row gap is control.slotGap. A listbox's radius reference is control.height,
not the entire multi-row height. Scope retention to the actual component owner,
never sequential sibling rows. The existing table/data-list recipe is explicitly
separate; do not silently apply it to ordinary Controls.

The visualizer's shell spacing, sample content sizes, colors, sticky tables,
inspector dimensions and guide overlays are presentation choices, not formulas
that every consuming project must adopt. Its formula summaries are explanatory
consumers; compute values from resolvers rather than copying their strings.

## Radius application

Pass actual measured border boxes `{x,y,width,height}` to
`resolvePercentageRadiusGroup`, with `family`, `amount`, `retained` and
`mode: 'standalone' | 'nested' | 'pill'`. Supply `rootMargin` for Containers;
use explicit `referenceHeights` for listbox frames/rows when required.
Percentages are numbers 0…100, not fractions. Defaults are Sharp (amount0,
retained0). `parentRadius` is only for a child with an explicit owning parent.

The result contains per-layer required radii, candidates, floors and physical
caps, plus whole-scope `valid` and `issues`. Validate before applying border-radius:
CSS may normalize an impossible radius silently. Show conflicts in a diagnostic
view with dashed required geometry; do not clamp or enlarge examples to conceal
them. For production components, report the infeasible inputs and choose a
product-appropriate resolution explicitly.

## Verify from any working directory

Replace `<skill-root>` with the discovered directory containing SKILL.md:

```sh
node <skill-root>/scripts/check-geometry.mjs
node <skill-root>/scripts/check-curvature.mjs
```

These commands resolve imports relative to their own files. The checks include
current numerical invariants and historical regression coverage; a historical
PASS does not make that API current. In the consumer, check all supported axes,
wrapper percentage changes, zero Tight margin, nested radius retention, physical
conflicts, and rendered border-box sizes. Keep typography independent of density.
If browser verification is unavailable, state that limitation separately from
numerical results.

## Compatibility boundary

Only existing historical callers should import `legacy-scale.mjs` or
`legacy-curvature.mjs`; historical rationale lives in geometry-history.md.
New callers use `resolveGeometry`, `.surface.height`, `.surface.icon`,
`.surface.glyph`, and `.groupMarginReference`. The current radius mode is
`nested`, not `interpolated`. Do not reintroduce legacy aliases into the current
resolver or use historical amendments as current design instructions.

## Spacing guide semantics

These are diagnostic categories, not additional spacing roles or independent
formula inputs. Visibility changes must not change geometry or radius validity.
The retained visualizer places four contribution switches and one Slot boundaries
switch in the Spacing section:

| Toggle | Measured contribution | Visualizer key / color |
| --- | --- | --- |
| Margins | Outer edge-to-wrapper clearance m or layout M | `marginGuides` / pink |
| Wrapper padding | Icon/glyph W and label L=n/2 | `wrapperGuides` / blue |
| Centering | Empty space between padded wrapper bounds and centered icon/glyph artwork | `centeringGuides` / green |
| Gaps | Layout sibling, collection-row and table-column gaps only; internal Control slot gaps are zero | `gutterGuides` / gray |
| Slot boundaries | Fixed wrapper frames; no extra spacing contribution | `slotBoundaries` / purple dashed |

For an icon, horizontal extra centering per side is n/2−W; for a glyph it is
(3n−(n+6))/2−W when feasible. Vertical artwork centering is n/2 and
(3n−(n+6))/2 respectively; there is no prescribed vertical W. Label padding L is shown under Wrapper padding. No compensation region exists. Flexible label width is not artwork-centering
space, and font bearing inside an icon's artwork box is not measured empty space.

Measure rendered wrapper and artwork boxes. Partition empty regions without
painting over artwork or counting overlap twice; split top/bottom strips from
side strips. If padding cannot fit the artwork, show the physical conflict rather
than claiming a negative centering space. Guides may depict only the remaining
empty area; that depiction must not change the required geometry.

Hover readouts identify the category and measured width × height in pixels.
Hidden regions must not intercept hover inspection. Clear an existing hover
readout whenever guides are repainted or their visibility changes, so a hidden
contribution cannot leave a stale value visible. Measure horizontal gaps from
physical left-to-right wrapper order, even when DOM order is visually reversed;
label padding still uses logical leading/trailing sides. Guides are non-layout,
non-interactive overlays; controls retain their ordinary keyboard/click behavior.
The global `guides` setting is a master visibility gate, while all active category
preferences remain independently saved, resettable and exportable in configuration
JSON. Turning off Gaps must not hide wrapper or centering guides.
When every guide switch is off, hide diagnostic boxes and required-radius arcs as
well as spacing paint. Keep conflict counts and textual details available; guide
visibility must not alter validation. Say that dashed geometry is available when
guides are enabled rather than claiming it is visible when diagnostics are hidden.

For older visualizer configurations without wrapper/centering category keys,
initialize supported categories from the former `gutterGuides` value. Preserve
explicit supported values. Ignore the retired `compensationGuides` key; importing
it must not restore a switch, overlay or extra padding. Preserve the configuration
version migration supported by the consuming implementation.

A different project may choose different guide colors/UI. Preserve the category
meanings and arithmetic; do not mistake the visualizer's colors or inspector
layout for mandatory production component styling.

## Role and tier example fidelity

The Four spacing roles Controls column uses real Control anatomy: fixed 3n icon/glyph squares, L=n/2 label padding per inline side, and zero internal gaps. Bind the resolved inner height and artwork budget on that example itself; do not rely on a variable inherited from another specimen. The Controls percentage changes W, never L. Widget and Button/control tier examples contain label wrappers, so their inline padding is L, not W, and their sibling slot gap is zero. Layout Page/Container/Group gutters keep their own role ratios.

At n=8, Tight/Compact/Regular/Spacious/Loose keep L=4px and slot gap=0px; outer m is 0/2/4/6/8px. Occupied icon-to-label and label-to-glyph content separation stays 8px and 9px respectively, including artwork centering. Readouts must describe those actual quantities rather than label collection E as a slot gap.

A zero CSS gap alone is insufficient: remove obsolete adjacent-wrapper margins and reset gap variables consumed by pseudo-elements or SVG guides. Abutting wrappers must paint no gray gap band. Show L under Wrapper padding, artwork centering separately, with no compensation toggle or region. Turning guides off changes no dimensions. Keep real layout/collection gaps and conflict diagnostics independent.

## Visualizer audit regression checks

Run these by absolute skill-root path from any working directory:

```sh
node <skill-root>/assets/proportion-lab/tests/spacing-guides.mjs
node <skill-root>/assets/proportion-lab/tests/inspector-state.mjs
```

The guide test covers empty-space area, disjoint regions, no artwork overlap,
infeasible wrapper budgets and all leading/trailing label arrangements. Inspector
checks cover independent guide persistence and old Gutters migration. These
complement the geometry and radius checks; they do not replace rendered checks
of square border boxes, centering, logical label padding and toggle visibility.
Run `tests/rendered-geometry.mjs` from the retained preview project with the installed Playwright module and served URL (optional browser executable as its third argument). It also checks measured adjacent-slot gaps, role/tier label padding and obsolete pseudo-element gap bands across all five densities. Inspect screenshots with guides on and off; include role/tier examples, not only the button grid.

## Full-size media slots

`mediaSize = mediaSlotWidth = 3n`: avatars, logos and thumbnails fill a fixed square Control wrapper. `mediaPadding = mediaInset = 0`, independent of the Control gutter percentage. Do not apply W to media: its content already consumes the whole square. It remains internal Control anatomy, not a new Container/Group or inherited radius scope. An avatar may crop with `cover` and use its own circular mask; a logo normally uses `contain` and preserves its own silhouette. Transparent or letterboxed asset pixels are asset content, not wrapper padding.

Media occupies a real leading or trailing slot without changing label padding L. Internal Control wrappers abut: media-to-label content separation is L=n/2 (`mediaContentSeparation`), and media-to-media separation is zero. Do not add E as a gap, label padding or media margin. Omit absent media entirely. Guide toggles show no wrapper-padding or centering contribution inside full media; they still expose outer margins and label padding L. Validate the fixed frame and occupied content; never shrink media to accommodate an unrelated icon/glyph padding budget. At n=8, media is24px square across every density; at n=4/24 it is12/72px square.

### Opt-in Control shape for media

Media defaults remain asset-owned: avatars use `circle`, logos use `intrinsic` (no added curvature). Explicit `shape: 'control'` opts a media frame into Control curvature without making its wrapper a Container or Group. Use `resolveMediaRadius({shape,frame,amount,retained,parentRadius})` from curvature.mjs. Supply the actual media border box and the immediate row/button's **required** radius, never a normalized or clamped CSS radius.

For Control media, candidate = amount/100 × measured media height/2; floor = retained/100 × immediate parent radius; required R = max(candidate,floor), except amount0 forces Sharp0. Validate R against min(width,height)/2. A retained floor can exceed a 3n media cap in a larger button: preserve the requested result and show a dashed geometry conflict, rather than enlarging or shrinking the frame. No uniform concentric inset is required: media is an internal child beside a label. Existing parent-scope conflicts remain visible independently.

Base UI: `data-slot="media" data-media-shape="control"` opts into clipping; set `--media-required-radius` from the measured resolver. `data-media="avatar"` remains circular when the opt-in is absent; logos remain unchanged. Clear the opt-in and its resolved style to restore defaults. On conflict, expose issue text and required dashed geometry; CSS alone is not validation. Zero padding and 3n square dimensions do not change.

The visualizer has independent avatar/logo inheritance toggles in Radius; both default off, persist and reset off. With inheritance on, Control Sharp makes media square; Container settings do not affect it.

For package-specific imports, typed rich Select anatomy, sync boundaries and verification scope, see [UI-KIT integration](ui-kit-integration.md).

### Visualizer media comparison

The retained study offers independent avatar and logo Control-shape toggles; defaults remain circular avatars and intrinsic logos. Listbox density specimens support **None selected**, **All selected**, and **Actual selection** comparison states under **Listbox appearance**. These are comparison settings, not changes to the geometry contract. Slot boundaries are outline-only paint and expose measured dimensions and inline padding through tooltips. Conflict details magnify the required arcs separately from the actual-size specimen and report required radius, physical cap, and excess. Never enlarge or clamp the actual media to make a diagnostic fit. Legacy saved global media inheritance is migrated to both asset settings when individual settings are absent.

Run `tests/media-comparison.mjs <installed-playwright-module> <served-url>` from the retained project for independent settings, selection parity, persistence, unchanged slot dimensions, diagnostics, and narrow-layout checks.

In the retained visualizer, icon and glyph wrappers automatically use the Control shape resolver with their actual square frame and immediate parent required radius. They clip artwork with overflow hidden, preserving fixed wrapper/artwork dimensions and spacing. Sharp stays square; infeasible retained radii retain dashed diagnostics outside the clipped wrapper. Avatar/logo inheritance remains separately optional.

Shape and clipping belong to the slot wrapper, not its artwork. Do not impose border-radius or overflow on icon/glyph artwork or media img/SVG children. Preserve authored artwork styles; avatar defaults are implemented by the circular wrapper.

Spacing guides clip their internal regions to each wrapper’s displayed radius. Their hover hit testing excludes clipped-away corners. These overlays remain outside layout; required radius conflicts retain separate dashed geometry and do not change slot/artwork sizes. The same wrapper resolution applies to the Four spacing roles Control examples.

### Wrapper inheritance and cleanup

Icon/glyph (and equivalent indicator) wrappers use Control candidate `A/100 × slotHeight/2` and floor `F/100 × immediateParentRequiredR`; required R is their maximum, with Sharp A=0 forcing zero. Keep fractional percentages intact. Validate against the actual square frame, and report excess without changing geometry. Mathematical circular/round wrapper shapes explicitly use `corner-shape: round`; a global superellipse must not silently turn a circle into a squircle. Never force corner-shape, radius, overflow, or clip-path on the artwork child.

A measured binding owns only the wrapper properties it writes. On media opt-out, removal, scope transfer, destroy or abort, restore prior authored radius/diagnostic state and stop reusing the old parent’s measurements. Observe relevant shape/context changes; ignore internal measurement probes to avoid observer loops. Keep clipping on the wrapper when reporting conflicts, with separate external dashed diagnostics. Recompute against the new immediate parent after cloning into a Select trigger.

### Button stroke paint

Filled buttons have no box-shadow stroke, including their active state. Outlined buttons use an explicit border-color token (`--ui-control-border` in Base UI and the visualizer; `--button-border-color` in UI-KIT), independent of text color. The visualizer paints outlines with an inset stroke and zero layout border: this consumes none of m, S, wrapper padding or gaps. Keep focus indicators and explicit pressed-state affordances separate from the resting stroke. Changing appearance must preserve resolved dimensions and slot geometry across all five densities.

A painted button also clips its content to its own outer radius. A logo may keep an intrinsic square wrapper while being cropped where it reaches the rounded button edge. This outer content boundary is independent of optional media-wrapper radius inheritance; neither boundary changes authored SVG/image styles or slot dimensions. Render conflict diagnostics outside the clipped control.

Radius diagnostics display values to two decimal places. The current radius resolver preserves exact radii and physical excess, but excess at or below 0.001 CSS px is treated as browser measurement noise, not a physical-size conflict. Larger excess still produces a conflict; no radius is clamped.


## Readout and comparison presentation

Use layout M/G and Control m/W/E consistently in headings, readouts, legends and
formula summaries: M is the layout margin reference, G its sibling gutter, m the
Control outer margin, W wrapper padding per side, and E the separation between wrappers (held in label padding).
Expand symbols near their first use. Avoid calling both W and E “Control gutter.”
API compatibility field names remain unchanged; this is presentation terminology.

Show the primary resolved values first: Height, Radius, Margin and Gap. Identify
which surface a value describes; list the separate outer/child radii for nested
surfaces. Put formula derivations, wrapper/centering/label-edge-padding breakdowns and
per-layer conflict details in disclosures. Format pixel values to at most two
decimal places and group repeated conflicts, while retaining exact values in the
resolver. Never feed display-rounded values back into validation.

Keep comparison configuration in the inspector. The body contains actual-size
examples and their resolved values. Hidden scrollbars must not make overflow
comparisons undiscoverable: provide visible directional controls and a focusable,
labelled scroll region with keyboard scrolling. Preserve sticky density/role
headers, and keep navigation labels and section numbering aligned. Use restrained
formula summaries instead of oversized decorative formula banners.

Explain both clipping boundaries when relevant: a slot wrapper owns its resolved
shape, and the painted button clips its descendants at the outer button edge.
Turning off media inheritance restores the asset wrapper's default shape; it does
not disable the outer button's clipping. Artwork-authored styles remain untouched.

Containment comparisons use the same 0.05 CSS px measurement tolerance for edge equality, negative insets and parent bounds. Larger overflow remains a reported containment issue. Physical radius excess keeps its separate 0.001 CSS px threshold. Validate nested parent and each actual row independently for radius painting: a sibling radius failure or scope containment issue must not erase an otherwise feasible radius. The visualizer lists real conflicts and links to affected examples in Inspector → Issues; comparison-slot diagnostic diagrams live there, and empty diagnostics are hidden.

Menu command rows use resolveControlSurface directly: fixed inner slots S = 3n; row clearance m = (q − 2)n/4 on all edges; outer row height H = S + 2m. At n=8, Tight/Compact/Regular/Spacious/Loose rows are 24/28/32/36/40px while slots remain24px. Label padding L=n/2 and icon/glyph budget W are internal anatomy; internal slot gaps are zero. Collection row spacing remains E=m/2. No extra compensation applies to any Control label. Menu-frame outer padding is separate; a three-item frame is 2m + 3H + 2E. Menu row radius uses H/2; ordinary selection-listbox rows retain S height and S/2 radius reference. Do not apply this menu change to selection rows.

Tables and data-lists use resolveDataRowGeometry(n,density,controlPercent): inner slot minimum S=3n, block clearance m=(q−2)n/4, row minimum H=S+2m, cell inline padding P=m+W (W=n×Control percentage), and column gap E=m/2. At md/md Regular: S24px, H32px, m4px, P6px, E2px. Vertically center slots; allow both slots and rows to grow with multiline content. Native collapsed tables reserve E/2 on each facing cell edge, excluding the two outer edges; data-lists use grid gap E. Content separation across cells is 2P+E. Paint one row divider through an explicit color token, without adding layout thickness or duplicate cell borders/shadows. This replaces the previous 1.25d cell padding / d/4 clearance / 2n+2.5d row convention for current data rows; legacy formulas remain historical only.

### Five-density data-row comparisons

Use identical single-line and multiline content in Table and Data-list examples across Tight, Compact, Regular, Spacious and Loose. Keep column widths and content consistent so wrapping differences reflect spacing, not different examples. At Product md/md the single-line minimum heights are 24/28/32/36/40px; multiline rows grow without clipping. Resolve each column against its own density, even when the inspector highlights another density.

Show H, S, m, P and E plus the actual measured multiline heights for both structures. Measure after layout and refresh on font, viewport and configuration changes; display rounded values without feeding rounded values into geometry. Data guides show cell edge padding and reserved intercell gaps separately, based on actual bounds. Toggles must change overlays only, never row dimensions. A table’s E is split across facing cell edges; a data-list uses real grid gap E. Do not double-count P as an additional column gap.

Keep density headings visible, expose previous/next scrolling controls and a named focusable comparison region, and retain hidden scrollbars. Teaching readouts stay outside the specimens. Verify all five density minima, multiline growth, one divider per row, guide-on/off geometry invariance, narrow-width scrolling and keyboard navigation. The retained visualizer example is `assets/proportion-lab/dist/index.html#data-densities`; UI-KIT owns its corresponding recipe/site examples rather than importing this path.

### Sharp/Pill comparisons and specimen cards

Show leading and trailing **Label padding** beneath each arrangement pair: L=n/2 on both sides, excluding outer margin m. At n=8 every arrangement shows4px /4px. Values are independent of density, radius, icon/glyph budget W and slot occupancy. Use logical sides and resolved values; never feed rounded readouts back into layout.

For a button shape comparison, pair identical content in explicit Sharp (R=0) and Pill (R=min(width,height)/2) examples across all five densities. Include label-only, icon + label, label + glyph, avatar + label and label + logo arrangements. Both shapes use identical L=n/2 label padding; do not stretch buttons to manufacture equal widths. Measure and display each pair's actual widths after layout, refreshing for font and context changes. Fixed comparison shapes override the Control radius dial only within those examples; explain that distinction. Inherited icon/glyph wrapper shape follows the local example's shape, while media keeps its per-asset defaults or opt-in behavior.

Specimen cards are Container surfaces, separate from the Controls they demonstrate. Resolve their card margin from the current purpose/scale/size and each column's density, their sibling gutter from that margin and the Container ratio, and their radius from the Container family. Do not leave fixed square corners or hard-coded padding/gaps on these cards. Container settings must not change button slot sizes, padding or widths. A card containing Controls has no Container child-radius retention relationship with those Controls. Teaching labels/readouts are not extra Control slots.

Verify natural equal widths for all 25 pairs, fixed Sharp/Pill radii, and card margin/gutter/radius response without changes to button widths. Keep real conflicts visible separately, density headings sticky, scrollbars hidden, and comparison navigation keyboard-accessible.

The former Label edge padding/compensation guide is retired. Legacy `compensationGuides` configuration and `compensation` diagnostic names may be accepted for migration but are ignored: they create no switch, overlay, spacing or validation input. Show the actual L contribution with Wrapper padding.

### Total edge-to-text insets

Alongside each arrangement's label padding L, show total logical leading/trailing edge-to-text inset and its contributions. An exposed side totals m+L. An occupied side totals m+Σslot widths+L; internal gaps and extra compensation are zero. Media counts as an occupied slot. Use rendered border-box slot widths, not artwork insets. At Regular n8/L4, label-only is8px each; icon + label is32px leading and8px trailing (4+24+4 and4+4). Label + glyph reverses those totals. Count borders within m once. Readouts are non-layout and update with context; never feed rounded values back into geometry. Sharp/Pill pairs retain equal widths.