## 2026-10-21 — Unified label padding, compensation retired

The current contract supersedes all earlier half/full exposed-label compensation: every Control label uses L=n/2 on both inline sides, zero internal slot gaps and no extra compensation. Outer m remains density-dependent. The visualizer and Base UI now match UI-KIT-neue's shared label rule. Earlier decisions below are historical only; use geometry-contract.md for new consumers.

> HISTORICAL: superseded revisions, not the active contract. See geometry-contract.md.

> Active radius policy: see **Adopted margin reference and retained-parent floor** below. Endpoint dials and earlier radius profiles are historical compatibility models.

## 2026-10-21: product shoulders and folded separation

- Product tier coefficients changed from [8, 2, 2, 1] to [8, 1, 2, 0]. Old product units: scale sm 5·6·7, md 6·8·10, lg 7·10·13 (Regular heights 20/24/28, 24/32/40, 28/40/52). New: 5·7·9, 6·8·10, 7·9·11 (20/28/36, 24/32/40, 28/36/44). Product md/md stays n = 8. `legacy-scale.mjs` keeps the old row; `check-geometry.mjs` compares product contexts by unit.
- Content and brand were confirmed unchanged: size steps 1, 2, 3 by scale.
- E stopped being a CSS gap between Control wrappers. Buttons: label padding is W+E on an occupied side and W+C on an exposed side; wrapper gap 0. Resolved positions and widths are unchanged (verified by rendered checks). Rows (menu, listbox, table) still use E as a gap. Adjacent non-label wrappers keep E as the trailing wrapper's margin.

# Mathematical geometry contract

This is the formula authority for the adopted proportional model. Numerical
implementations live in `../scripts/lib/`. The model is a design convention;
its coefficients can be adapted explicitly. UI recipes and browser presentation
are owned by the consuming project, not this contract.

## Context and units

Tier expresses purpose, scale regional sizing, size a local adjustment, and density
spacing. Defaults are product/md/md/regular. Scale and size use sm/md/lg, encoded
as s,z ∈ {−1,0,1}. Resolve the content unit:

`n = n₀ + a·s + b·z + g·s·z`

| Tier | n₀ | a | b | g |
| --- | ---: | ---: | ---: | ---: |
| widget | 6 | 1 | 1 | 0 |
| product | 8 | 2 | 2 | 1 |
| content | 11 | 3 | 2 | 1 |
| brand | 15 | 4 | 2 | 1 |

Supported resolved n is 4–24. Lengths use a consistent unit (CSS pixels in the
reference implementation). Preserve fractional results. Presentation rounding
must not affect calculations.

`c = n/4`; `d = q·c`, where q is 2/3/4/5/6 for
tight/compact/regular/spacious/loose. Density changes spacing and frames, never n,
content typography, intrinsic clearance or media size.

## Frames, slots and borders

- Media slot I = 2n; glyph mark G = I−2c = 3n/2.
- Standard nominal frame H = 2n+2d; compact Hc = 2n+d.
- The frame ladder is F(k) = 2n+k·d, with k=2,1,0. Adjacent frames differ by d,
  giving d/2 clearance at each nesting edge.
- If outer margin is M and border width B, interior padding is max(0,M−B).
- Text nominal content height T = max(2n,1.2f), where f is text size.
  Centering within H gives vertical padding max(0,(H−T)/2−B).
- Nominal frames are not universal maximum heights. Intrinsic content may require
  larger frames; fixed-frame rendering is a consumer decision.

For standard controls, outer margin d plus text-slot allowance d/2 gives a 1.5d
text edge. Compact chip-like controls use d/2+d/4=3d/4. Nested listbox-like rows
use d/2+d=1.5d. Count each spacing contribution once. Border thickness belongs
inside the declared edge budget.

## Composed control elements

Container siblings use `G = M` (margin:gutter 1:1). Closely related elements
inside a composed control use `G = M/2` (margin:gutter 2:1, gutter:margin 1:2).
`composeControl(M)` accepts a finite nonnegative border-inclusive margin and
returns `{margin:M,gutter:M/2}`. Zero is an explicit flush setting, not a density.
The resolver exposes `composition.control` (M=d, G=d/2) and
`composition.compactControl` (M=d/2, G=d/4).

This is the effective separation between adjacent content slots, including
icon–label and icon–icon pairs. Existing text-slot allowances may supply it;
do not add an explicit gap on top of an allowance that already supplies G.
Frame height, intrinsic media size and typography retain their own rules.
Compact repeated-row gaps, listbox text rails and table cell clearances below
are separately defined and are not replaced by this composition rule.

| Density | d / n | Standard control M | Composed G | Container G at M=d |
| --- | ---: | ---: | ---: | ---: |
| tight | 0.5 | n/2 | n/4 | n/2 |
| compact | 0.75 | 3n/4 | 3n/8 | 3n/4 |
| regular | 1 | n | n/2 | n |
| spacious | 1.25 | 5n/4 | 5n/8 | 5n/4 |
| loose | 1.5 | 3n/2 | 3n/4 | 3n/2 |

## Repetition and containment

For compact repeated rows: parent margin Mp=d/2, row nominal height Hc, gap g=d/4.
With N rows, `height = 2Mp + N·Hc + (N−1)g` for N≥1. Content growth may exceed
that nominal result. A physical inset i yields `Rchild=max(0,Rparent−i)`.

| Level | Margin | Gutter | Legacy base radius |
| --- | ---: | ---: | ---: |
| widget | d/2 | d/2 | — |
| button/control | d | d | — |
| group | 5d/4 | 5d/4 | n+c |
| tile | 2d | 2d | 2n |
| card | 3d | 3d | 3n |
| section | 4d | 4d | 4n |

These six containment levels use a 1:1 margin:gutter ratio: `M = G`.
Existing Group/Tile/Card/Section margins remain 5d/4, 2d, 3d and 4d.
Widget uses d/2 and Button/control uses d; gutters match at every density.
The resolver exposes this ladder as `containers.widget`, `containers.control`,
`containers.group`, `containers.tile`, `containers.card` and `containers.section`.
Containment Widget is independent of the Widget purpose tier. The legacy top-level
`widget` alias still resolves to Tile; use `containers.widget` for the small level.
Button/control describes the outer spacing budget; existing control text-slot
allowances still apply. The widget level does not redefine compact listbox gutters.
Compact repeated-row spacing and tabular cell clearance retain their separate rules.
An aligned inner rail has offset `parent rail − child internal rail`; a negative
result requires an explicit consumer choice rather than silent clamping.

Tabular base geometry: cell inline margin 5d/4, block clearance d/4, legacy
nominal row 2n+2.5d. Compact content rows use 2n+d where selected by a consumer.
The pure resolver exposes base quantities; it does not prescribe DOM structure.

## Typography

Type derives from n independently of density. Let Q=(n+35)/32.

| Role | Size |
| --- | --- |
| smallControl | n+4 |
| fieldLabel / groupKicker | n+5 |
| control | n+6 |
| body | n+7 |
| title | body + size bump (sm:0, md:1, lg:2) |
| subhead | body·Q |
| heading | body·Q² |
| display | body·Q³ |
| sectionKicker | body·9/8 |

The supported model guarantees a 9-unit minimum except smallControl, whose
minimum is 8 at n=4. These are domain invariants, not post-calculation rounding.
Font family, weight, tracking, casing and semantic markup belong to consumers.

## Curvature

The current API is `resolveEndpointRadiusGroup`, schema v11. Inputs are independent
nonnegative finite `innerRadius`, `outerRadius`, measured `frames` (outer to inner,
x/y/width/height border boxes), and `mode`: standalone, interpolated or pill.

- **Interpolated:** x is cumulative outward inset from the inner frame, L the
  total inset to the outer frame. R(x)=Inner+(Outer−Inner)×x/L. Inner and Outer
  may increase, decrease or match; neither is a floor or ceiling. Preserve both
  endpoints exactly and never clamp intermediate radii. The scalar model checks
  equal offsets on all four edges, ordered containment, and actual dimensions.
  L ≤ measurement tolerance (default 0.05px) with different endpoints reports
  ambiguous geometry. Intermediate radii and t are null rather than invented;
  known endpoints are retained. Equal endpoints need no division and remain
  valid for otherwise well-formed coincident geometry. Positions must be ordered
  and in [0,1] with no tolerance-based extrapolation or position clamping.
  This is coordinated interpolation, not necessarily concentric geometry.
- **Standalone:** R=Inner for each frame; Outer is irrelevant.
- **Pill:** R=min(width,height)/2 independently for each frame. Both endpoints
  are irrelevant. A zero-sized frame resolves to zero.

Validate physical caps over the complete group without modifying the computed
radii. Valid-but-infeasible geometry returns issues and the required radii;
malformed/nonfinite inputs throw. The 0.05px tolerance detects ambiguous inset spans and compares edge-offset
measurements; it does not permit physical-cap excess. Any positive excess is a
conflict and is returned as physicalExcess, with withinMeasurementTolerance
metadata distinguishing tiny excesses from larger failures. Containment and
position ordering are strict.
The visualizer renders conflicts as exact dashed quarter-circle arcs over solid
frame bounds, without browser normalization, clamping or frame enlargement.

The controls are **Inner radius** and **Outer radius**, independent 0…8n sliders
in 1/16n steps. Bounds follow n (purpose/scale/size), not density. Density affects
measured inset distances and frame sizes. Presets are endpoint pairs only:
Sharp (0,0), Crisp (0.1875,0.5), Balanced (0.375,1), Round (1,2), with executable
source `radiusEndpointPresets`. Sharp is simply both endpoints zero; Pill still
uses its measured dimensions. Comparison frames retain their normal control
height H=2n+2d, with d/2 and d surrounding spacing. Legacy profile, ceiling,
concentric and offset APIs remain for compatibility, not new consumers.

## Coefficient-table equivalence

For a tier polynomial at fixed scale s, baseline=n₀+a·s and size step=b+g·s.
Then n=baseline+z·step. `tier-mapping.mjs` provides this equivalent representation
and validates finite positive steps, the supported n domain and monotonic scales.
Changing the representation must not introduce a second model.

## Validation

`node scripts/check-geometry.mjs` checks the supported tier/scale/size cells, role ordering,
size bumps, type floors, density relationships and finite geometry.
`node scripts/check-curvature.mjs` checks endpoints, reversed/equal legacy bounds,
physical caps, profile units, nested offsets and invalid modes/parameters.
Consumer rendering requires separate browser and visual verification.

Preset calibration covers all 180 purpose/scale/size/density combinations and
three comparison modes (2,160 cases including four presets), using the retained
comparison frame width 217px and H=2n+2d inner height. This is not a promise that
the presets fit arbitrary narrower components; actual geometry is always checked.
Round is a moderate endpoint pair, distinct from dimension-derived Pill.

### Specimen integration

The retained visualizer routes buttons and badges through Standalone using their
measured border boxes. Menu/listbox frames and container-tier frames are explicit
Interpolated groups. Their sibling rows/tiles define an inner content envelope
(the union of their actual border boxes), not a fictitious chain through siblings.
The frame-to-envelope pair validates all four insets; the frame receives Outer
and every terminal child receives Inner. Each child's own dimensions are also
validated with the same resolver. A failure marks the complete group and draws
required geometry without CSS normalization. Widgets and controls use their own
purpose-tier n; other container examples use the current purpose context.

Selected/hover listbox paint uses the resolved row-radius variable. Diagnostic
SVGs live outside menu/listbox children, have pointer-events:none, and do not
alter roving focus order or measured component sizes. Readouts identify the mode,
resolved endpoints, content inset and any conflicts.

### Radius families and component scopes

Container and Control are independent semantic families, not size tiers or nesting
depths. Each owns an Inner/Outer pair in units of its component context n, with
Sharp (0,0) as the default. Presets assign a pair only to the chosen family.
Scale and size change n; density does not change either endpoint.

Containers cover structural widgets, layout groups, tiles, cards and sections.
Controls cover buttons, badges, menus, listboxes and their options, including the
Button/control tier specimen. A widget's role can be Control in a product; the
visualizer's structural widget specimen belongs to Container.

Resolve endpoints from the component's explicit family, then call the same
resolveEndpointRadiusGroup computation. Standalone uses that family's Inner;
Interpolated uses its Inner/Outer and actual insets; Pill remains frame-derived.
Composition ends at the component boundary: a listbox within a card starts its
own Control scope and never inherits or interpolates through the card's Container
endpoints. Internal menu/listbox rows stay in their owning Control scope. No
cross-family interpolation is implicit. Whole-group physical validation and
dashed conflicts are unchanged. The comparison selector changes only the family
being inspected, never either family's stored settings.

## Adopted half-height percentage model (supersedes endpoint dials)

Each component has an explicit Container or Control family with a radius amount
A in [0,100] percent. Both default to Sharp, A=0. Presets are Sharp 0%, Crisp
25%, Balanced 50%, Round 100%. Each family also has a minimum retained percentage; see the revision below.

`resolveControlSurface(n,density)` defines inner H=3n, icon=2n, glyph=1.5n,
margin M=(q−2)n/4, and outer H=3n+2M, where q is 2/3/4/5/6 for
Tight/Compact/Regular/Spacious/Loose. At n=8 this gives outer heights
24/28/32/36/40, fixed inner24/icon16/glyph12 and margins0/2/4/6/8.
The old d spacing axis and structural Container margins remain unchanged.
Legacy compactHeight and composition fields remain compatibility values; new
control surfaces consume `surface` or `resolveControlSurface`, not those fields.

`resolvePercentageRadiusGroup` computes R=A/100 × H/2 per surface. Container candidates now use root margin minus cumulative inset (see revision below);
a listbox uses reference outer
control height for its frame and fixed3n for its rows, independent of row count.
Standalone uses each component height. Interpolated validates nested geometry;
for equal edge insets x its radii are equivalently A/100 × (Houter/2−x).
Pill remains min(width,height)/2 independent of A. Physical width/height caps
are validated without clamping, including reference-height listboxes. Zero
inset has no division and equal heights yield equal radii. Border paint at zero
clearance must not consume layout space. No implicit cross-family composition.
The old endpoint resolver is retained for compatibility, not the active visualizer.

### Adopted margin reference and retained-parent floor

This revision supersedes Container half-height radii. Each family owns amount A
and minimum retained F, both 0…100%. Defaults are A=0, F=0 (Sharp). Presets set
amount as above and reset retained to zero. Custom retained settings are explicit.

Container root R = A/100 × component root margin M. For a nested surface at
cumulative actual inset x from the scope root, candidate C = A/100 × max(0,M−x).
Control candidate C = A/100 × reference half-height, retaining the fixed 3n row
surface and density-dependent reference outer height for listboxes.
For every immediate parent→child edge, Rchild=max(Cchild,F/100 × Rparent).
Use the parent's required computed radius even if physically infeasible; never
clamp and feed a different value downstream. A three-level container with M=24,
insets0/24/30, A=100%, F=50% gives 24→12→6, not24→12→12.

Standalone components have no parent floor. Sibling rows share their actual
owning frame as parent, never each other or the virtual sibling envelope.
Cross-family/component boundaries start new scopes. Sharp amount0 forces zero;
Pill ignores amount/floor and remains physical-cap-derived. Validate the whole
scope, preserving required geometry as dashed outlines on physical conflicts.
The visualizer reports candidate and floor for comparison layers, and retained
percentage plus child floor in the live component summaries.

### Container gutter percentage

`composeContainer(M,p)` preserves margin M and derives gutter G=M×p/100.
p defaults to100 (1:1), with visualizer range0…200%, step5%. This supersedes
fixed1:1 for Container-family sibling spacing only. Widget, group, tile, card
and section specimens, card content/button-row gaps and container spacing
comparisons use this setting. The Button/control tier, listbox rows and composed
Control gutters retain their Control spacing rules. Radius bases remain margins;
changing gutters never changes the margin or crosses component scopes.

### Adopted spacing roles (supersedes default 1:1 Container gutters)

Page: G=M (100%). Container: G=.75M (75% default, existing slider may override).
Group: G=.5M (50%). Controls: component-specific margins and gutters, unchanged.
`resolveSpacingRoles(M, options)` derives every role directly from M, never from
a parent gutter. `composeContainer` now defaults to75%. Groups borrow a margin
reference but have zero actual edge margin, no painted surface and no radius
scope. At reference24, Page/Container/Group gaps are24/18/12px.

The retained card is Container → heading/description Group, listbox Control,
button Group containing Controls, feedback text. Both Groups use half the card
margin reference. Container gaps separate these siblings. The standalone Group
tier specimen is likewise unpainted with zero edges; its children keep Control
radius scopes. Page workbench gaps equal its own page margin reference.

### Independent role sliders and Control 25% default

Page, Container and Group percentages are independently adjustable0…200%,
step5%, with defaults100/75/50. `resolveSpacingRoles` accepts pagePercent,
containerPercent and groupPercent; each multiplies the supplied margin reference
directly. Groups still add no edge padding or radius scope. Page applies its
ratio to its own page margin. Changing any one ratio does not change the others.

Control default gutter is25% of its own control margin, exposed as
`resolveControlSurface(...).gutter`. The visualizer uses it for listbox/menu row
gaps, button icon/label gaps, the Control tier and composed-control examples.
Component-specific controlGutter overrides remain supported; no Control slider
is introduced here. Legacy composeControl remains compatibility-only at1/2.

### Four independently tunable spacing roles

Controls now also have a0…200% gutter slider, step5%, default25%. All four
role defaults remain100/75/50/25. `resolveControlSurface(n,density,p)` accepts
the Control percentage; `resolveSpacingRoles` accepts controlPercent (and still
permits an explicit controlGutter override). Control gaps derive from their own
margin, never the enclosing Container or Group reference. The setting affects
menu/listbox row gaps, button internal gaps, Control-tier examples and density
comparisons. It does not alter Control heights, margins, icons or glyphs.

## Composed control slots (adopted)

Icon, label and glyph slots each have fixed height 3n across densities and horizontal padding n/4 on each side. Icon artwork is 2n; glyph artwork is 1.5n. Their border-box slot widths are 2.5n and 2n respectively. The label width is intrinsic or flexible, including its 2 × n/4 padding. Center artwork and text vertically within the slot; do not stretch artwork to slot height.

Control gutter G = M × Control percentage remains additional between slot border boxes. Content-edge separation between adjacent slots is n/4 + G + n/4 = n/2 + G. Slot padding does not replace or compound the margin reference. Outer frame H = 3n + 2M. At n=8, slots are 24px high, padding is 2px per side, icon slot width is 20px, glyph slot width is 16px; at Regular with G=1px, content separation is 5px. Tight has zero outer clearance and zero default gutter, but retains 2px slot padding per side. Guides distinguish outer margins, slot padding, and additional gutters.

### Control gap default revision
Control gutter now defaults to 0%. Slot padding remains n/4 per side, so default adjacent-content separation is n/2 at every density (4px at n=8). The Control gutter slider remains available for explicit experiments; nonzero values add to slot padding. This supersedes the earlier 25% default and 5px Regular example.

### Wrapper gutters (current; supersedes the additional-gap convention)
The Control percentage uses n as its reference and is realized as horizontal padding inside each icon, label and glyph wrapper: G = n × Control% / 100. Default Control%=25 gives n/4 per side. Slot height stays 3n; icon/glyph artwork stays 2n/1.5n. Flex gap is always zero. Adjacent content separation is 2G. Thus Control0% removes wrapper insets, Control25% gives 2px per side at n=8, and Control50% gives 4px per side. The global Gutters toggle controls wrapper guides. Outer margin guides remain separate. Page/Container/Group spacing roles retain their margin references.

### Inter-wrapper gap (current amendment)
Wrapper gutters remain G=n×Control%/100. Inter-wrapper gap is E=M/2 at every density. At n=8, Tight/Compact/Regular/Spacious/Loose gaps are 0/1/2/3/4px. Content separation is 2G+E (4/5/6/7/8px at the default Control25%). E is independent of the wrapper gutter percentage and scales with n. This supersedes the prior always-zero flex gap; there is no threshold at Regular.
