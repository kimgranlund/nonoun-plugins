# Current mathematical geometry contract

This is the sole current formula authority. The model is an adopted design
convention, not a perceptual law. Historical revisions are archived in
[geometry-history.md](geometry-history.md); they do not override this contract.
Lengths are CSS pixels in the reference implementation. Preserve fractions in
calculations and round only displayed values.

## Context and typography

Purpose (tier), scale, size and density are independent. Defaults are
product/md/md/regular. Scale and size sm/md/lg map to s,z = −1,0,1.

`n = n₀ + a·s + b·z + g·s·z`

| Purpose | n₀ | a | b | g |
| --- | ---: | ---: | ---: | ---: |
| widget | 6 | 1 | 1 | 0 |
| product | 8 | 1 | 2 | 0 |
| content | 11 | 3 | 2 | 1 |
| brand | 15 | 4 | 2 | 1 |

The size step inside one scale is b + g·s. Product keeps a constant step of 2 at every scale, so its shoulders stay evenly spaced: control heights at Regular are 20/28/36 (scale sm), 24/32/40 (md) and 28/36/44 (lg). Content and brand step by 1, 2 and 3 for scale sm, md and lg. Product changed from [8, 2, 2, 1] on 2026-10-21; see history.

Supported n is 4–24. Density q is 2/3/4/5/6 for
Tight/Compact/Regular/Spacious/Loose. Define c=n/4 and d=nq/4.
Density changes spacing, never n or typography.

Body size = n+7; control = n+6; field label and group kicker = n+5;
small control = n+4. Heading ratio Q = 1.25+(n−5)/32.
Display/heading/subhead = body × Q³/Q²/Q. Section kicker = body × 9/8.
Title = body + 0/1/2 for sm/md/lg size. All values are unrounded.

## Control geometry

Icon, label and glyph wrappers are internal Control anatomy, not additional
spacing roles. Their DOM nesting does not make them Containers, Groups or new
radius scopes. They inherit the owning Control's n, density and wrapper settings.
Only explicitly modeled nested surfaces participate in Nested radius resolution;
an artwork/label wrapper alone is not a surface requiring radius inheritance.
Do not apply Page/Container/Group gap percentages or margin factors to these slots.


Use lowercase m for a Control margin, uppercase M for a layout margin reference.

- Inner surface and every icon/label/glyph wrapper height S = 3n.
- Outer margin m = (q−2)n/4; outer height H = 3n+2m.
- Icon artwork = 2n; glyph artwork = control font size = n + 6 (density-independent).
- Icon/glyph wrapper budget per horizontal side W = n × controlPercent/100.
- Label inline padding per side L = n/2, independent of W and density.
- Internal Control wrapper gap is zero. Do not fold E into label padding or add
  margins between adjacent non-label wrappers. Collection rows and table columns
  retain E=m/2; this is separate from slot separation.
- Icon wrapper is square: width = height = 3n, with centered 2n artwork.
  Its artwork inset is n/2; glyph wrapper is also square 3n × 3n with centered (n + 6) artwork.
  Glyph artwork inset is (3n − (n + 6))/2; label–glyph separation is L+(3n − (n + 6))/2.
  Icon–label artwork separation is n/2+L. Media–label separation is L.
  W remains the configured icon/glyph budget; extra centering space is not W.
  If 2W+artwork size exceeds 3n, the square padding budget cannot fit the artwork;
  preserve the square/artwork dimensions and expose this conflict.
- Label width is intrinsic or flexible and includes 2L. Labels may ellipsize.

Default controlPercent=25. At n=8, wrappers stay 24px high, artwork stays
16px/14px, icon/glyph budgets stay 2px per side and label padding is4px per side.

| Density | Outer H | Margin m | Internal slot gap | Icon–label separation |
| --- | ---: | ---: | ---: | ---: |
| Tight | 24 | 0 | 0 | 8 |
| Compact | 28 | 2 | 0 | 8 |
| Regular | 32 | 4 | 0 | 8 |
| Spacious | 36 | 6 | 0 | 8 |
| Loose | 40 | 8 | 0 | 8 |

Declared edge margins include borders. For border width B, padding is M−B
(or m−B). If B exceeds the budget, report a conflict; do not silently enlarge
the component. Decorative inset strokes can avoid consuming layout space.

### Fixed wrapper budgets and physical conflicts

For square wrappers S=3n and centered artwork size I, the declared horizontal
padding requirement W fits only if 2W+I ≤ S. Icon I=2n; glyph I=n+6.
The actual artwork inset is (S−I)/2 regardless of W. Feasible horizontal extra
centering is (S−I)/2−W. A negative result is a spacing-budget conflict, not a
negative space to draw or an instruction to change the frame.

Preserve the S×S wrapper and artwork size. Do not let CSS's minimum padding box
expand the square, move the artwork off center, or shrink it to satisfy W.
A consumer can center artwork absolutely inside a fixed relative wrapper and
represent W as a declared internal budget. In that implementation computed CSS
padding is not the authority for W; use the resolver/token value.

Report wrapper-budget conflicts alongside physical radius conflicts, with dashed
wrapper outlines in the visualizer. Do not feed clipped guide widths back into
model calculations. In a conflict, guides show only actual empty space up to the
artwork boundary; retain the original requested W in readouts and validation.
Guide regions must not overlap artwork or one another. This diagnostic clipping
is not a clamp on required geometry or an indication that the configuration fits.

Icon/label/glyph wrappers do not enter Nested radius validation merely because
they are children. Validate the owning Control's Standalone frame; only explicitly
modeled surface composition creates a Nested radius scope.

## Button content and inline padding

Omit absent leading/trailing wrappers entirely. An absent wrapper contributes
neither W nor E. Preserve an empty alignment slot only when explicitly requested
by a component such as a listbox checkmark column.

For all button shapes and slot arrangements, outer inline padding remains m and every label wrapper uses L=n/2 on both inline sides. No compensation or occupancy-dependent extra padding is added. Omitted slots create no padding and no gap. Internal wrappers abut, including adjacent non-label wrappers. Radius never changes padding or natural width.

At Regular n=8, L=4 and H=32: m=4. Label-only buttons have 4px label padding per side and 8px edge-to-text inset. A side occupied by one 24px icon/glyph/media wrapper has 32px edge-to-text inset (4+24+4); its opposite exposed side stays 8px. Edge-to-artwork inset is m+n/2=8 for the icon and m+(3n−(n+6))/2=9 for the glyph; configured artwork padding remains W=2.

Pass `surface.labelPadding` as `wrapperInset` to `resolveButtonPadding({margin,wrapperInset,height,hasLeading,hasTrailing})`; this input is L, not W. The resolver returns outer `inlinePadding` m, `labelStart`=`labelEnd`=L and `exposedLabelInset`=m+L. `edgePadding` and `compensation` remain zero-valued compatibility fields. Presence flags remain accepted but cannot change padding. Apply logical inline-start/end padding and preserve physical conflicts without clamping.

## Layout spacing roles

Use M for the layout margin reference and G for its sibling gutter. Reserve
lowercase m for the Control outer margin, W for the icon/glyph internal budget,
L=n/2 for label inline padding and E=m/2 for collection-row/table-column spacing.
Internal Control wrappers abut with zero gap; E is not folded into L. These are separate quantities,
not interchangeable instances of a single gutter.

Tile/Card/Section margin references are 2d/3d/4d. The Group specimen may borrow
1.25d; an actual Group normally borrows its owning layout's reference. It adds
zero edge padding and has no painted surface or radius scope.

| Role | Default percentage | Reference | Result |
| --- | ---: | --- | --- |
| Page | 100 | Its layout margin M | G=M |
| Container | 75 | Its margin M | G=.75M |
| Group | 50 | Borrowed margin M | G=.5M; edge padding 0 |
| Control | 25 | Content unit n | Wrapper inset W=.25n; separation E=m/2 held by the label wrapper |

All four percentages are independently adjustable 0…200; UI step is 5.
Ratios never multiply another gutter. Controls are not a container margin tier.
The small Widget and Button/control specimens use their respective purpose's
Control geometry. Groups organize components rather than introduce surfaces.

Tables and data-lists use Control-derived minimum rows: S=3n, m=(q−2)n/4, H=S+2m; cell padding P=m+W and column gap E=m/2. Center the growing inner slot and allow multiline content to increase row height. Use resolveDataRowGeometry; details below.
The visualizer's inner chip uses 3n and its badge uses a nominal 2n minimum;
neither is the standard outer Control frame. The old 2n+d compact frame is
compatibility-only and must not determine current specimen geometry.

## Radius families and modes

Each family has Amount A and minimum retained F, each 0…100%.
Both default to 0 (Sharp). Presets Sharp/Crisp/Balanced/Round set A to
0/25/50/100 and F to 0. Percentages below are divided by 100.

**Standalone:** each component starts a scope, with no inherited floor.
Container candidate = A × component margin M.
Control candidate = A × reference height / 2.

**Nested:** composition is scoped to an explicitly nested component.
At cumulative actual inset x from the root, Container candidate
C = A × max(0, root margin M − x).
Control candidate C = A × reference height / 2 at that surface.
Then Rchild = max(Cchild, F × immediate-parent required radius).
Use the parent's computed requirement even if it does not physically fit.
An explicitly supplied parentRadius allows a real child to use its owner,
without treating sibling rows or their virtual envelope as its parent.

Listboxes use the density-dependent Control reference H for the outer frame
and 3n for rows, independently of row count. Other Controls use measured height
unless an explicit reference is supplied. Family/component boundaries start
new scopes. Container floors never flow into Controls.

**Pill:** R = min(measured width, measured height)/2, exempt from A and F.
Otherwise A=0 always forces Sharp, including with a nonzero parent floor.

Validate finite nonnegative measured border boxes and all four nested edge
insets. The uniform-inset comparison allows .05px measurement tolerance for
edge equality. The shared current radius resolver retains exact required radii
and physicalExcess=max(0,R−min(width,height)/2). Physical excess at or below
0.001 CSS px is measurement noise; larger excess is a conflict. This acceptance
threshold does not clamp the radius or change the measured frame. Validate the
entire scope; show required geometry as dashed outlines when diagnostics are
visible, without enlarging frames. Keep conflict text available when guides are off.
The retained floor is intentionally dependent on the immediate hierarchy.

For portable application integration, see [consumer integration](consumer-integration.md).

## Resolver API and migration

`scale.mjs` exports:

- `resolveGeometry(tier,scale,size,density)`: context, n/d/c, surface, typography,
  Tile/Card/Section margin references, Group margin reference and table recipe.
- `resolveControlSurface(n,density,controlPercent=25)`: current Control geometry.
  `slotPadding` is icon/glyph W; `labelPadding` is L=n/2; `slotGap` retains E for collection-row/table-column spacing; `wrapperGap` is 0 (the CSS gap between Control wrappers);
  `contentSeparation` retains the compatibility 2W+E quantity; do not use it for current label or artwork spacing.
- `resolveButtonPadding({margin,wrapperInset,height,hasLeading,hasTrailing,slotGap=margin/2})`: outer `inlinePadding` m,
  `edgePadding`/`compensation` 0 (compatibility), `labelGap` 0, `wrapperGap` 0, and `labelStart`/`labelEnd` = L for every occupancy.
  `iconInset`/`glyphInset` are the actual centered artwork insets;
  `iconContentSeparation`/`glyphContentSeparation` include those insets plus L.
  `gutter` is a compatibility spelling of W within this result, never E.
- `composeContainer(M,percent=75)`: preserved margin and derived gap.
- `resolveSpacingRoles(M,options)`: independent role percentages; Groups have
  zero edges. Supply controlUnit=n and controlMargin=m for Control results.
- `CFG`, `CONTAINER_FACTORS`, `DENSITIES`, `SPACING_ROLES`: current coefficients.

`curvature.mjs` exports `resolveMediaRadius`, `resolvePercentageRadiusGroup` and
`radiusPercentagePresets`. Current mode names are `standalone`, `nested`, `pill`.
The default is `nested`. `interpolated` is not a current mode.

Historical imports must explicitly use `legacy-scale.mjs` or
`legacy-curvature.mjs`. Those frozen compatibility modules preserve old output
shapes, aliases and mode names for old callers and regression checks. The
visualizer imports only current modules. Migrate `resolve` to
`resolveGeometry`, `.h` to `.surface.height`, `.icon`/`.glyph` to the corresponding
`.surface` fields, and `.containers.group.margin` to `.groupMarginReference`.
No compatibility module is bundled into the visualizer.

Run `node scripts/check-geometry.mjs` and `node scripts/check-curvature.mjs`.
They include historical regression checks and current API parity/invariant
checks. Numerical checks do not establish visual or accessibility quality.

## Full-size media slots

`mediaSize = mediaSlotWidth = 3n`: avatars, logos and thumbnails fill a fixed square Control wrapper. `mediaPadding = mediaInset = 0`, independent of the Control gutter percentage. Do not apply W to media: its content already consumes the whole square. It remains internal Control anatomy, not a new Container/Group or inherited radius scope. An avatar may crop with `cover` and use its own circular mask; a logo normally uses `contain` and preserves its own silhouette. Transparent or letterboxed asset pixels are asset content, not wrapper padding.

Media occupies a real leading or trailing slot without changing label padding L. Internal Control wrappers abut: media-to-label content separation is L=n/2 (`mediaContentSeparation`), and media-to-media separation is zero. Do not add E as a gap, label padding or media margin. Omit absent media entirely. Guide toggles show no wrapper-padding or centering contribution inside full media; they still expose outer margins and label padding L. Validate the fixed frame and occupied content; never shrink media to accommodate an unrelated icon/glyph padding budget. At n=8, media is24px square across every density; at n=4/24 it is12/72px square.

### Opt-in Control shape for media

Media defaults remain asset-owned: avatars use `circle`, logos use `intrinsic` (no added curvature). Explicit `shape: 'control'` opts a media frame into Control curvature without making its wrapper a Container or Group. Use `resolveMediaRadius({shape,frame,amount,retained,parentRadius})` from curvature.mjs. Supply the actual media border box and the immediate row/button's **required** radius, never a normalized or clamped CSS radius.

For Control media, candidate = amount/100 × measured media height/2; floor = retained/100 × immediate parent radius; required R = max(candidate,floor), except amount0 forces Sharp0. Validate R against min(width,height)/2. A retained floor can exceed a 3n media cap in a larger button: preserve the requested result and show a dashed geometry conflict, rather than enlarging or shrinking the frame. No uniform concentric inset is required: media is an internal child beside a label. Existing parent-scope conflicts remain visible independently.

Base UI: `data-slot="media" data-media-shape="control"` opts into clipping; set `--media-required-radius` from the measured resolver. `data-media="avatar"` remains circular when the opt-in is absent; logos remain unchanged. Clear the opt-in and its resolved style to restore defaults. On conflict, expose issue text and required dashed geometry; CSS alone is not validation. Zero padding and 3n square dimensions do not change.

The visualizer has separate avatar and logo inheritance toggles under Inspector → Radius. Both default off, persist in saved configurations, and reset off. With inheritance on, Control Sharp makes media square; Container settings do not affect it.

Implementation ownership and the completed package sync are recorded in [UI-KIT integration](ui-kit-integration.md).

Wrapper shape ownership: Control slot wrappers own any resolved border radius and overflow clipping. Icon/glyph artwork and media img/SVG children retain their authored radius, overflow, and shape styles; do not reset or inherit these properties through parent selectors. Circular avatar defaults belong on the media wrapper. Keep sizing/placement rules separate from shape ownership. For physical conflicts, keep the fixed wrapper and render dashed diagnostics outside the clipping layer; never alter artwork styles to make a requested radius fit.

### Wrapper inheritance and cleanup

Icon/glyph (and equivalent indicator) wrappers use Control candidate `A/100 × slotHeight/2` and floor `F/100 × immediateParentRequiredR`; required R is their maximum, with Sharp A=0 forcing zero. Keep fractional percentages intact. Validate against the actual square frame, and report excess without changing geometry. Mathematical circular/round wrapper shapes explicitly use `corner-shape: round`; a global superellipse must not silently turn a circle into a squircle. Never force corner-shape, radius, overflow, or clip-path on the artwork child.

A measured binding owns only the wrapper properties it writes. On media opt-out, removal, scope transfer, destroy or abort, restore prior authored radius/diagnostic state and stop reusing the old parent’s measurements. Observe relevant shape/context changes; ignore internal measurement probes to avoid observer loops. Keep clipping on the wrapper when reporting conflicts, with separate external dashed diagnostics. Recompute against the new immediate parent after cloning into a Select trigger.

Containment comparisons use the same 0.05 CSS px measurement tolerance for edge equality, negative insets and parent bounds. Larger overflow remains a reported containment issue. Physical radius excess keeps its separate 0.001 CSS px threshold. Validate nested parent and each actual row independently for radius painting: a sibling radius failure or scope containment issue must not erase an otherwise feasible radius. The visualizer lists real conflicts and links to affected examples in Inspector → Issues; comparison-slot diagnostic diagrams live there, and empty diagnostics are hidden.

Menu command rows use resolveControlSurface directly: fixed inner slots S = 3n; row clearance m = (q − 2)n/4 on all edges; outer row height H = S + 2m. At n=8, Tight/Compact/Regular/Spacious/Loose rows are 24/28/32/36/40px while slots remain24px. Label padding L=n/2 and icon/glyph budget W are internal anatomy; internal slot gaps are zero. Collection row spacing remains E=m/2. No extra compensation applies to any Control label. Menu-frame outer padding is separate; a three-item frame is 2m + 3H + 2E. Menu row radius uses H/2; ordinary selection-listbox rows retain S height and S/2 radius reference. Do not apply this menu change to selection rows.

Tables and data-lists use resolveDataRowGeometry(n,density,controlPercent): inner slot minimum S=3n, block clearance m=(q−2)n/4, row minimum H=S+2m, cell inline padding P=m+W (W=n×Control percentage), and column gap E=m/2. At md/md Regular: S24px, H32px, m4px, P6px, E2px. Vertically center slots; allow both slots and rows to grow with multiline content. Native collapsed tables reserve E/2 on each facing cell edge, excluding the two outer edges; data-lists use grid gap E. Content separation across cells is 2P+E. Paint one row divider through an explicit color token, without adding layout thickness or duplicate cell borders/shadows. This replaces the previous 1.25d cell padding / d/4 clearance / 2n+2.5d row convention for current data rows; legacy formulas remain historical only.
