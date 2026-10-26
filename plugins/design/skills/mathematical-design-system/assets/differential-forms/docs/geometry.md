# Geometry reference

All variables below are lengths in CSS pixels unless explicitly marked as unit coefficients. u defaults to 4; supported range 3..6. B defaults to 0 and is restricted to 0..u/2. Computations retain fractional pixels. Jig increments are editing affordances, not mathematical quantization requirements.

## Controls
S=6u. Density compact/default/loose chooses I=[.5,1,2]u and G=[0,1,2]u. P=I-B; H=S+2I. Because B<=u/2, P remains nonnegative. Border-box height includes both borders. Label wrapper and slot height are S. Icon sm/md/lg nominal artwork is 4u/5u/6u; cap at S-2B. The slot owns this internal border; an avatar filling the slot has no second border.

At u=4, heights are 28/32/40 and gaps 0/4/8. Control text F=2u+6px; line height=5u. Fonts at u=3/3.5/4/4.5/5 are 12/13/14/15/16px.

L=labelEdgeUnits*u, default 1.5u. Without slots, start=end=L. With leading only, start=0/end=2L; with trailing only, start=2L/end=0; with both, 0/0. Optical doubling applies to buttons, chips and the choice label pattern. Editable input wrappers use L, not 2L, on an exposed edge. These margins are additional to outer inset.

For an intrinsic-width single-line control: W=2I + sum(part widths) + (partCount-1)G + labelEdgeStart + labelEdgeEnd. Text width is measured by the browser; do not guess from character count. For full-width inputs, the label/input takes remaining width with min-width:0; fixed parts do not shrink. Multiline content uses auto height.

## Chips and badges
Chip slot=4u; inset and gap use the control density; Hchip=4u+2I. Label edge is L/2, with the same slot-presence rules. Default text-only margins are .75u each; one-slot opposite margin is 1.5u. Chip text=2u+4px. Chip icon space=4u-2B. Chip radius uses its own height for the softest pill.

Text badge H=4u; minimum W=4u; inline edge budget J=.5u; CSS padding=max(0,J-B). W=max(4u, measured content width + 2J). Text=2u+2px. A short count badge is circular. Density does not alter badge dimensions. Prefixes, suffixes and currency selectors instead use chip geometry, described below.

## Composites
Listbox, segmented control and attached groups share the same rules. Let Q be requested composite inset, default 0u, range 0..1.5u. Effective outer edge distance D=max(B,Q). Parent CSS padding=D-B. Parent gap=Q. Child inset Ic=max(B,I-D); child padding=Ic-B; child height Hc=S+2Ic. Choose S=6u for control options or 4u for chip options, with the corresponding parent radius. Preserve S and text metrics.

A one-row composite height is Hc+2D. It matches the ordinary control height when I-D>=B; otherwise it grows. Vertical list height is 2D + sum(child heights) + (n-1)Q. A wrapped segmented group requires layout-derived height.

Example u=4, default density, B=0, Q=2: D=2, Ic=2, Hc=28, one-row composite=32. Extreme compact, B=2, Q=6: D=6, Ic=2, Hc=28, composite=40. Old shrinking logic yielded a 12px label wrapper for 20px text and is deprecated.

At Q=0, gap=0 and child radius=0, including when a transparent parent border creates a nonzero physical edge distance. This is an explicit semantic override.

## Curvature
Default curvature is Soft for both controls and containers. Control/chip requests are sharpest=0u, sharp=1u, default=2u, soft=3u, softest=own height/2. Clamp to half actual height and width. Container requests use 0/1/2/3/4u; no pill mode. CSS performs final fitting to actual boxes. Nested child radius=max(0,Rparent-D), capped to half child height; Q=0 overrides to zero.

Checkbox radius=1u independent of curvature. Radio remains a circle. Switch track remains capsule and thumb circle. Artwork is 4u; alignment slot is 6u. Switch width=9u, height=5u, edge inset=.5u; padding=.5u-B and thumb diameter=4u. These are identity-bearing shape exceptions.

## Collections and tables
Collection density chooses T=[1,2,3]u. Record inset and gap=T, padding=T-B; row separation=.5u. Table cells use block padding T-B; interior inline padding T/2-B on each side, giving a full T between content boxes after adjacent border budgets. First and last outer edges use T-B. Shared column widths come from the table layout, not per-row flex layouts. Native border-spacing may also appear at the table's outer block edges.

Rows use container curvature; nested controls keep their control geometry. The specimen reserves a checkbox column of S+1.5T and action column of H+1.5T. These are recipe widths, not global minimum table column widths.

## Cards and multiline
Cards use inset=gap=[3,4.5,6]u, padding=inset-B. Width and height follow layout and content. Container curvature is independent of controls. Do not subtract card inset from child control inset.

Multiline rows belong to the collection family: inset=gap=T, padding=T-B, minimum height=6u+2T, content-driven final height, title minimum height=6u and description gap=1u. Copy has no exposed label margins. Use collection density and container curvature independently of the Controls jig. The list of rows has .5u separation and no composite surface/inset.

## Composed inputs and chip selectors
Prefixes/suffixes are chip-sized spans with real chip label wrappers. The currency selector is a chip-sized button with label plus trailing 4u caret slot. Chip exposed-edge rules apply: text-only gets L/2 each side; trailing-slot-only gets L on the opposite label edge. These margins do not vary with density.

For inputs containing chips, Hinput=max(Hcontrol,Hchip+2I). Parent min-width=Hinput; each adornment min-width=Hchip. At u4, compact/default/loose yields chip heights 20/24/32 and input heights 28/32/48. Fixed parts do not shrink; the editable part takes remaining width.

Resolve parent radius using Hinput. Let Dx=I and Dy=(Hinput-Hchip)/2 be actual outer-edge distances. Nested chip radius is elliptical: Rx=max(0,Rparent-Dx), Ry=min(Hchip/2,max(0,Rparent-Dy)); CSS fits to actual width. Border is already included in these edge distances; do not subtract it again. This uses physical nesting, not the zero-inset composite override.

The currency popup uses chip composite geometry: 4u option slots, half label edge, residual inset Ic=max(B,I-max(B,Q)), gap Q, and zero option curvature when Q=0. Popup radius comes from the standalone chip radius, not the nested trigger's radius. Overlay offset is 1u in this recipe; popup minimum width 100px is a specimen-specific affordance, not a system constant. Escape returns focus, arrows/Home/End move focus, Enter/Space commits, Tab and outside pointer dismiss.
