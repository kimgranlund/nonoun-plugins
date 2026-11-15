# Fills: the base every material starts from

With every setting at its plainest (`lighting: none`, `transmission: opaque`, `delineation: fill`, `chroma: colour`),
which is the Flat preset, a part is painted by its fill alone. Get this right first. If a design only works when lit,
its reliefs are wrong.

## Role colours per relief × face

Read ui-colors roles through the palette inputs (the base block below). With ui-colors' 12-step ramp (1–2 backgrounds,
3–5 interactive fills, 6–8 borders, 9–10 solids, 11–12 text):

| Part | Fill | Note |
|---|---|---|
| ground (base layer) | `--bg` (ui-colors `bg`, the ground family, step 1) | the page or device body |
| raised · neutral | `--element` (ui-colors `surface`, or `bg` in a system with one neutral; `bg-muted` in the dark scheme) | must be lighter than its ground. In the light scheme with one neutral it has the base ground's own colour, so it needs a ground one step off, or a ui-colors system generated with `neutrals` |
| pressed | `--element-pressed` (ui-colors `bg-muted-active`; `bg-subtle` in the dark scheme) | a key held down keeps its own fill in every material: darker than the key at rest |
| etched · neutral | `--etch` (ui-colors `neutral-3`; `neutral-2` in the dark scheme) | a shown value: one step off its ground, and distinct from both the recessed and the disabled fill |
| recessed · neutral | `--recess` (ui-colors `bg-muted`; `bg` in the dark scheme) | fields, wells, tracks, trays: darker than its ground |
| recessed · display | `--display` (ui-colors `black`); marks on it use `--on-display` (ui-colors `white`) | a screen reads light-on-dark in every scheme. `black` and `white` are ui-colors' endpoints, the same in every mode; `bg-inverse` is not used, because it turns light in a dark scheme |
| ground (overlay layer) | `--overlay` (ui-colors `bg-overlay`; `--element` in a system with one neutral), **opaque** | it must hide what's under it while opaque. In the dark scheme an overlay face must stand off a resting card by its fill, because its cast does not show there: ui-colors puts `bg-overlay` two neutral steps above the card with `neutrals`, which clears its raised gate. Put a recess inside the overlay on `bg-overlay-muted`, and measure each level against the next with ui-colors' `separation`. A one-neutral system has no `bg-overlay`: set `--overlay` to a step that stands off its cards |
| solid (raised or recessed) | `--accent` (ui-colors `primary-solid`, the primary solid) or a charcoal neutral; marks use `--on-solid` | primary keys, latched keys, an on track, a filled range |
| solid, held down | `--accent-pressed` (ui-colors `primary-solid-active`); marks keep `--on-solid` | a primary key held down keeps its own colour, one step further from its rest fill than hover, never the neutral pressed fill, which turns it grey under its light label. A latched key held down takes it too; a part on the selected face held down keeps `--selected-face`. Neither takes the neutral pressed fill. Where a bright solid sits at ui-colors' `apca.ui` limit, its active step is clamped and barely moves from the solid (ui-colors reports the hover → active ΔE). There the pressed shadow tells a held part apart where a table draws one; an unlit material shows no difference |
| solid, selected (chosen alone) | `--select` (ui-colors `bg-inverse`); marks use `--on-selected` (ui-colors `fg-inverse`) | a current page, a single-select option: raised on a control, flat on a row; never the primary solid, which stays the action's. The thumb of a segmented control or tabs is not this face (construction.md) |
| tint (a row chosen among several) | `--tint` (ui-colors `bg-selected-multiple`, a neutral tint held to `apca.ui` against a resting row) | no relief; the checked box in its leading slot carries the selection |
| emissive | `--signal` (ui-colors `primary-solid` by default) | the only face whose colour means "live" |
| hole (emissive off) | `--hole` (ui-colors `neutral-6`) | an unlit lamp is a hole |

**The two neutral inputs trade roles in the dark scheme.** ui-colors' neutral steps get darker with their number in a light
scheme and lighter in a dark one. A raised face must be lighter than its ground and a recess darker in every scheme, so in
the dark scheme `--element` reads `bg-muted` and `--recess` reads `bg`. The base block does it with `light-dark()`, which
follows the `color-scheme` property: ui-colors sets it in every mode block, and another palette must set it wherever its
scheme changes. A recess that sits directly on the base ground in the dark scheme has the ground's own fill, so it
separates by its ring or its inner shadow. The pressed fill moves as well: in the dark scheme `--element-pressed` reads
`bg-subtle`, which is darker than the key at rest and lighter than a recess. No step of the neutral is darker than the base
ground, so that is the one fill left between the two. On a ground that is itself `bg-subtle`, an unlit pressed part has
the ground's own fill and takes the even ring that Separating reliefs without edges prescribes.

A palette may instead lift a recess one step off its ground in the dark scheme; in an unlit material it then reads by its
step, in a lit one by its inward shadow.

## Separating reliefs without edges

- Neighbours of different relief must differ in fill. Neighbours of the same relief separate by **space** (ui-geometry's
  gaps), not by lines.
- Proximity groups: ui-geometry's spacing ladder (groups farther apart than their members) makes most rules unnecessary.
- An operable boundary (a field's extent, a button's extent, an unchecked box, a switch track) must meet ui-colors' APCA threshold for
  non-text (`apca.ui`) against its neighbour. ui-colors reports that contrast for `border-strong` on the page
  (`system.json` › `contrast`) and never fixes a miss. This skill states no contrast ratio of its own and does not claim
  WCAG's non-text contrast criterion: ui-colors lists the WCAG ratio only as information (`ratio`). If fill can't do it, give the part an even 1px ring of the strong line (`--field-shadow: inset 0 0 0
  1px var(--line-strong)`), or use `delineation: line`. Never use `border` for it, and never mark only one side: a baseline
  under a field or a highlight along its top reads as a 3D lip, however faint, and an unlit material has no light direction.
  Row dividers inside a list or table are the exception, because they separate rows, not edges.
- An opaque overlay sits on the same colour as raised parts. Where its fill equals what it floats over, keep ui-geometry's
  cast at its level, unshifted, as `--overlay-shadow` in the unlit tables, in the cast paint roles or, in a system without
  them, ui-colors' `shadow` role: it is the only cue left, and unshifted it leans to no side. A modal adds a scrim
  (ui-colors `bg-backdrop`). A scrim is an overlay-layer fill, not a shadow.
- Lines stay only where they divide content inside one shape (row rules, separators, seams) or carry state (focus,
  invalid).

## States in colour only

| State | Paint |
|---|---|
| hover | the face one step nearer the text colour (step n → n + 1 on its ramp); where that step measures under ΔE 4 (OKLab × 100) against the rest face, as one step from the lightest neutral can, take the next step that clears it; a ghost changes its ink instead, never its fill |
| pressed | the pressed fill (raised → recessed); a solid part keeps its own colour, `--solid-pressed-face` |
| selected / latched | the solid fill, or the selected face for a part chosen alone; a row chosen among several takes the tint; never the pressed fill (a selected part is not recessed) |
| live | an emissive face on the indicator only |
| review / read-only | the etched fill |
| disabled | marks and emissive faded (ui-colors `fg-disabled`); a solid or tinted face becomes the neutral face of its relief (ui-colors `bg-disabled` where the part has no neutral face of its own); layer and relief unchanged |
| focus | a ring outside the box, identical in every material |

## Base block

Every material token gets its base value here; the other passes only override. Palette inputs default to ui-colors roles.
`--element` carries a fallback, because ui-colors emits `surface` only for a request that sets `neutrals`
([terms.json](terms.json) › `inputs` › `fallback`). `--element`, `--recess` and `--element-pressed` choose by scheme with
`light-dark()` ([terms.json](terms.json) › `inputs` › `dark`).

```css
:root {
  /* palette inputs (terms.json › inputs) */
  --bg: var(--colors-bg);                 --display: var(--colors-black);
  --element: light-dark(var(--colors-surface, var(--colors-bg)), var(--colors-bg-muted));   /* light, dark */
  --overlay: var(--colors-bg-overlay, var(--element));
  --element-pressed: light-dark(var(--colors-bg-muted-active), var(--colors-bg-subtle));
  --recess: light-dark(var(--colors-bg-muted), var(--colors-bg));
  --etch: light-dark(var(--colors-neutral-3), var(--colors-neutral-2));
  --accent: var(--colors-primary-solid);  --accent-pressed: var(--colors-primary-solid-active);  --signal: var(--colors-primary-solid);  --hole: var(--colors-neutral-6);
  --select: var(--colors-bg-inverse);     --tint: var(--colors-bg-selected-multiple);
  --line: var(--colors-border);           --line-strong: var(--colors-border-strong);

  /* material tokens (terms.json › tokens) */
  --ground-face: var(--bg);               --ground-shadow: none;
  --raised-face: var(--element);          --raised-shadow-1: none;  --raised-shadow-2: none;
  --pressed-face: var(--element-pressed); --pressed-shadow: none;
  --etched-face: var(--etch);             --etched-shadow: none;
  --recessed-face: var(--recess);         --recessed-shadow: none;  --field-shadow: none;
  --display-face: var(--display);         --display-shadow: none;   --display-cover: none;
  --overlay-face: var(--overlay);         --overlay-shadow: none;   --overlay-backdrop: none;
  --solid-face: var(--accent);            --solid-shadow: none;     --on-solid: var(--colors-primary-on-solid);
  --solid-pressed-face: var(--accent-pressed);
  --selected-face: var(--select);         --on-selected: var(--colors-fg-inverse);  --tint-face: var(--tint);
  --emissive: var(--signal);              --emissive-shadow: none;
  --hole-face: var(--hole);               --hole-shadow: none;
  --ink: var(--colors-fg);                --ink-muted: var(--colors-fg-muted);  --ink-faint: var(--colors-fg-subtle);
  --on-display: var(--colors-white); --data-1: var(--colors-data-1);       /* … one per series */
  --media-filter: none;
}
```

Where the operable boundary needs it in an unlit material, set `--field-shadow: inset 0 0 0 1px var(--line-strong)`.

A raised control is an operable boundary as well, and its neighbour is the ground. ui-colors reports that pair as
`system.json › modes.<id>.separation`: `dE` passes at one just-noticeable difference, which tells two colours apart side by
side but does not make a button read as a part; `lc` is its APCA contrast. When `lc` is below `apca.ui` in a mode (a
`neutrals` system with the default surface lift is: Lc ≈ 5 against a threshold of 15), the unlit fill table gives raised
controls an even ring as well: `--raised-shadow-1: inset 0 0 0 1px var(--line-strong)`. Resting cards and overlays take no
ring: they are not operable, so they separate by fill (`separation.dE` at least one just-noticeable difference) and, where
an overlay's fill equals what it floats over, by its cast (Separating reliefs without edges). Lit materials need no ring:
the bevel and the cast separate them.
