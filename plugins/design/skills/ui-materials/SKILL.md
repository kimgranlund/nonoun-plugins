---
name: ui-materials
description: Paint UI parts in any material (Flat, Physical, Frosted glass, Glass, Outline, or any mix of four settings) and build components that render correctly in all of them. A part is described by layer, relief and face; a material is a preset of lighting, transmission, delineation and chroma. Covers the light model, frosted and clear glass with refraction, line and mono rendering, the material-token contract and its palette inputs, component construction, and the material brief for a showcase. Use when designing or extending a material system, adding a material, or building a component that must work across materials. Every length comes from ui-geometry; this skill owns paint only. NOT for colours or palettes (ui-colors), lengths, radii or shadow geometry (ui-geometry), the showcase canvas and its packing (ui-showcase-bento), or one system's token names (that system's skill, e.g. instrumental-modernism).
---

# UI materials

A material is how a part is painted: fill, bevel, cast shadow, texture, and what it does to the content behind it.
**A material never changes a length.** Geometry (heights, insets, radii, gaps, cast-layer lengths) comes from
**ui-geometry** and is identical in every material, so switching material is a set of token overrides and nothing moves.

Contents: [Route](#route) · [Division of labour](#division-of-labour) · [The taxonomy](#the-taxonomy) · [Settings and materials](#settings-and-materials) · [The token contract](#the-token-contract) · [Procedure](#procedure-building-a-component) · [Invariants](#invariants) · [Commands](#commands)

## Route

Read the row whose question is open. Paths are relative to this file.

| Unresolved question | Read | Load when |
|---|---|---|
| Which layer, relief and face does each part of my component get? Which states move it? | [references/construction.md](references/construction.md) | Building or reviewing a component |
| What is a part's colour with no light, line or glass? | [references/fills.md](references/fills.md) | Building Flat, or any part's base colour |
| How does lit paint work: face shading, bevel, cast, recesses, lamps? | [references/lighting.md](references/lighting.md) | `lighting: lit` |
| How do frosted and clear glass, cover panes and the lens work? | [references/transmission.md](references/transmission.md) | `transmission` is not `opaque`, or a lens misbehaves |
| How do line and mono rendering work? | [references/line-and-mono.md](references/line-and-mono.md) | `delineation: line` or `chroma: mono` |
| How do the settings combine, and how are the CSS tables laid out? | [references/composition.md](references/composition.md) | Writing the token tables, or a combination looks wrong |
| Which shade, lit and glass colours does lit paint use, and how are they generated? | [references/paint.json](references/paint.json); `node scripts/request.mjs` prints it as a ui-colors request | Generating a colour system for Physical, Frosted or Glass |
| What must a material showcase show? | [references/showcase.md](references/showcase.md); the canvas itself is **ui-showcase-bento** | Planning a showcase or a specimen sheet |
| What does a word mean here, and which skill owns it? | [references/terms.json](references/terms.json) | A term is disputed, or a word appears in two skills |

## Division of labour

| Question | Owner |
|---|---|
| How tall, how far in, how round, how far apart; a cast's layers and its elevation level | **ui-geometry** (run its calculator, quote its symbols) |
| What a part is (layer, relief, face), how each setting paints it, how states move it | **this skill** |
| Which colours fill the faces | the palette, **ui-colors** by default: a material reads them only through its palette inputs |
| The showcase canvas, its packing and its checks | **ui-showcase-bento**; this skill supplies the material brief |
| One system's token names, recipes and components | that system's skill; **instrumental-modernism** is a reference implementation |

When asked to generate any UI, derive the geometry with ui-geometry first, then paint it with this skill. Words the
siblings own keep their meaning here: surface, ink, role, accent, mode, scheme and theme are ui-colors'; edge, tier
and elevation levels are ui-geometry's; specimen and group are ui-showcase-bento's ([terms.json](references/terms.json) › `foreign`,
and its scheme and elevation-level concepts). The one exception is `ground`: ui-colors' word for the page's neutral family
is this skill's relief value, a public name ([terms.json](references/terms.json) › ground).

## The taxonomy

Two independent descriptions meet: **what a part is**, which the component author decides, and **how the material paints**,
which the settings decide. Neither knows about the other.

### What a part is: three attributes

| Attribute | Values | Question it answers |
|---|---|---|
| **layer** | `base` · `overlay` | Does it sit in the content, or float above it (menus, popovers, dialogs, toasts, sheets, floating and tab bars)? |
| **relief** | `ground` · `raised` · `etched` · `recessed` | Is it the part others sit on, does it stand out of its ground, sit level in it, or cut into it? |
| **face** | `neutral` · `solid` · `emissive` · `display` | What is the face made of: the neutral fill, a strong fill, light, or a screen you read through? |

**Marks are not parts.** Ink (labels, scales, ticks, legends, rules) and data (series, values) are printed on a face. They
have no relief, and every material draws them the same, apart from chroma.

Rules that bind the attributes:

1. **Choose by job.** *Print what you read, etch what you show, recess what holds, raise what you move, light what is
   live.* A scale is ink. A shown value (a field in review) is etched.
   A field, track, well or tray is recessed. A control is raised: a trigger pressed to open a list is a control, and a
   field typed into holds. Live state is an emissive face.
2. **Grounds nest.** An overlay's body is the `ground` of its own layer: a dialog's field is `recessed` relative to the
   dialog, not to the page. A raised part that casts at the popup level or higher and holds parts (a card, a device
   housing) is the ground for them.
3. **Relief alternates.** A control (cast at the raised level: a key, a button, a thumb) never holds raised parts. To group
   raised parts, put them in a recessed tray first.
4. **Compatible pairs only.** A `display` face is always `recessed`. An `emissive` face is a lamp in a hole: `recessed`,
   and when it is off it is a `neutral` recessed hole. A `solid` face may be raised (a primary button, a selected key or item) or recessed (a
   switch track that is on, a filled range).
5. **States move attributes, never paint.** Pressed: raised → recessed, keeping its face, only while it is held.
   Selected or latched: a `solid` face that is never recessed: a control stays raised, a row takes no relief. Live: emissive. Dragged: base → overlay.
   Review: a field or trigger → etched. Disabled: fade the marks and drop the tone (a solid face → neutral); never etched. Focus is a ring outside the box, the same in every material.

Rule 4 is checked by the classifier in [construction.md](references/construction.md), in the consuming project; rules 1–3
and 5 are judgement, against its anatomy and state tables.

Casts use **ui-geometry's elevation levels**: controls `raised`, resting cards and popovers `popup`, floating bars
`floating`, dialogs `modal`.

## Settings and materials

| Setting | Values | What it does |
|---|---|---|
| **lighting** | `none` · `lit` | `lit` adds one light from above: face shading, bevels, casts, inward recess shadows. `none` is colour only. |
| **transmission** | `opaque` · `frosted` · `clear` | What overlay bodies and cover panes do with what's behind them: hide it, soften it (an 8px blur), or keep it legible (a 3px blur, plus the lens where it runs). |
| **delineation** | `fill` · `line` | `line` replaces every fill with an even 1px line inside each box. Line and text weight carry state. |
| **chroma** | `colour` · `mono` | `mono` maps the primary solid, emissive faces, data and media to one neutral ink. |

**The lens is not a material.** It is refraction added to `clear`: an SVG displacement map in `backdrop-filter`, which only
Chromium applies. Where it doesn't run, `clear` stays clear and never becomes `frosted`, unless the system offers the lens
on `frosted` (transmission.md). An engine check is not enough (a frame can pass it and draw nothing): confirm the lens by
rendering ([transmission.md](references/transmission.md)).

### Material presets

| Material | lighting | transmission | delineation | chroma |
|---|---|---|---|---|
| **Flat** | none | opaque | fill | colour |
| **Physical** | lit | opaque | fill | colour |
| **Frosted glass** (`frosted`) | lit | frosted | fill | colour |
| **Glass** | lit | clear | fill | colour |
| **Outline** | none | opaque | line | mono |

Glass adds the lens where it runs. Any other combination is valid and needs no new code: Flat + frosted (flat UI with
blurred bars), Physical + mono, Outline in colour. Name a preset only for a combination a product ships, so the
list stays the materials in use (a judgement: no check holds it).

**Names.** A material's id is lowercase (`data-material="frosted"`) and its display name is title case. Frosted glass keeps the id `frosted`, the same word as the transmission value it sets; its display name says "glass" so the two never read as one control. "Material" here means a preset of the four settings (what it is not: terms.json › material). Use one attribute name per system for the preset (`data-material` here), so every stylesheet and script finds it.

### Which parts each setting touches

| Setting | Touches |
|---|---|
| lighting | every neutral and solid face (shading), every raised part (bevel + cast), every recessed part (inward shadow), emissive faces (glow) and holes |
| transmission | **overlay** bodies with a neutral face (a glass body), and, when lit, **display** faces (a cover pane over a screen). Never ground, raised, solid or emissive faces, and never a neutral recess: a field, well, track or tray stays cut into its ground (a cover pane on it reads as a raised glass panel). |
| delineation | every face (fill → the base ground's colour) and every shadow (→ an even line ring). A solid face becomes a heavier ring in its ink. |
| chroma | the primary solid, solid and emissive colours, data marks, media. Neutral greys stay. |

The settings compose in five passes, in a fixed order: **fills → delineation → lighting → transmission → chroma**. Each pass
rewrites only the tokens it owns ([composition.md](references/composition.md); owners per token in [terms.json](references/terms.json) › `tokens`).

## The token contract

Components paint with **material tokens** only, never raw colours or shadows. They are named by relief, face and layer:

```
ground     --ground-face        --ground-shadow
raised     --raised-face        --raised-shadow-1   --raised-shadow-2       (neutral face; -1 raised level, -2 popup level)
pressed    --pressed-face       --pressed-shadow    --solid-pressed-face    (raised → recessed, keeps its face)
etched     --etched-face        --etched-shadow
recessed   --recessed-face      --recessed-shadow   --field-shadow          (field: an operable boundary, at ui-colors' apca.ui threshold in every unlit material)
display    --display-face       --display-shadow    --display-cover
overlay    --overlay-face       --overlay-shadow    --overlay-backdrop      (always used together)
solid      --solid-face         --solid-shadow      --on-solid
selected   --selected-face      --on-selected       --tint-face             (chosen alone; tint: among several)
emissive   --emissive           --emissive-shadow   --hole-face  --hole-shadow  (lamp on / off)
marks      --ink  --ink-muted  --ink-faint  --on-display  --data-<n>  --media-filter
scheme     --shade  --shade-k  --lit-k  --glass-k                           (scheme constants; the first three are retired, see lighting.md)
```

Material tokens read colour only through **palette inputs**, each defaulting to a ui-colors role (`--colors-<role>`):

```
--bg → bg    --element → surface    --overlay → bg-overlay    --element-pressed → bg-muted-active    --recess → bg-muted
--etch → neutral-3 (neutral-2 in the dark scheme)
--display → black    --hole → neutral-6
--accent → primary-solid    --accent-pressed → primary-solid-active    --signal → primary-solid
--select → bg-inverse    --tint → bg-selected-multiple
--line → border    --line-strong → border-strong
```

In a system with one neutral `--element` and `--overlay` fall back, and in the dark scheme the neutral inputs trade
roles so a raised face stays lighter than its ground and a held key darker than the key at rest: [fills.md](references/fills.md).

Lit and transmissive tables also read **paint roles** (`--colors-paint-<use>`), declared in [paint.json](references/paint.json)
and generated by ui-colors as literals from the fragment `node scripts/request.mjs` prints ([lighting.md](references/lighting.md)).
Flat and Outline use none and work on any colour system; Physical, Frosted glass and Glass need one generated with it.

Each setting is a token table under its own attribute (`data-lighting`, `data-transmission`, `data-delineation`,
`data-chroma`). The preset attribute expands to the four, by a line of script or by hand. `data-lens` (`on` · `off`) is
an engine flag, not a setting. Scheme, size and shape are further attributes that compose with all of these. The
catalogue of every token and input, with its writers and defaults, is [terms.json](references/terms.json); `scripts/check.mjs` keeps these blocks, the references and the catalogue in step.

## Procedure: building a component

1. **Geometry.** Get tier, height, insets, radius, nesting and elevation level from **ui-geometry**. Put no lengths in the paint.
2. **Anatomy.** List the parts. Give each one a layer, relief and face, by job (rule 1). Anything that only informs is a mark.
3. **Check the rules.** Grounds nest (2), relief alternates (3), pairs are compatible (4).
4. **States** as attribute moves (rule 5), using the state table in [construction.md](references/construction.md).
5. **Paint** each part with the material tokens its attributes name, and nothing else.
6. **Verify** across the material presets × schemes (and at least one off-preset combination): identical boxes, attributes
   consistent with tokens, glass text legible, fallbacks working (the checklist in [construction.md](references/construction.md)).

## Invariants

Each names its check. "Render" means the verification matrix in [showcase.md](references/showcase.md) or ui-showcase-bento's `uiBentoCheck()`.

| Invariant | Check |
|---|---|
| Every part's box is identical in every material. Lines and borders are inset rings or shadows, never `border`. | Render (box diff across materials) |
| A material token's relief, face and layer are declared, and every token, input and attribute value used is declared. | `check.mjs`: `tokens`, `closure`, `selectors` |
| An overlay always uses face + shadow + backdrop filter together. | Render (construction.md classifier in the consuming project) |
| Transmission writes only overlay tokens, the display shadow, the display cover and `--glass-k`. | `check.mjs`: `reach`, `reachRow` |
| Every material preset uses only declared setting values, and every copy of the sets matches terms.json. | `check.mjs`: `presets`, `paintPasses`, `bento`, `bentoWords` |
| Without lighting, adjacent reliefs separate by fill or line, operable boundaries meet ui-colors' APCA threshold for non-text (`apca.ui`), and lines are even rings on all sides, because an unlit material has no light direction. This skill states no contrast ratio of its own. | ui-colors' contrast report (`system.json` › `contrast`), render, judgement; `check.mjs`: `ratios` |
| Text over a transmissive body meets its contrast target over the worst backdrop it can sit on. | Render, judgement |
| `prefers-reduced-transparency` makes transmission `opaque`; `forced-colors` and `prefers-contrast: more` switch to `line` (ui-colors' contrast modes apply as well). | Render with the media emulated |
| Marks are drawn identically in every material apart from chroma, and never take a shadow. | Render, judgement |
| One word, one meaning: no avoided word or hedge in a rule doc, no alias that names another concept, a value or a sibling's word, and every word listed as a sibling's is in that sibling's vocabulary. | `check.mjs`: `words`, `hedges`, `aliases`, `foreign` |
| A sibling's value is cited, never copied: no doc here states a canvas size. | `check.mjs`: `canvas` |
| No table derives a colour: every shade, lit and glass colour is a paint role declared in paint.json, used by a doc, and present at its alpha in a system that ui-colors generates from the request. | `check.mjs`: `derived`, `paint`, `request` |

## Commands

```sh
node ~/.claude/skills/ui-materials/scripts/check.mjs     # every check above, then its negative controls; exits 1 on any failure
node ~/.claude/skills/ui-materials/scripts/request.mjs   # the ui-colors request fragment for the paint roles; its header lists the options
```

Run it after editing this file, a reference or terms.json. It reads the three siblings' vocabularies, ui-geometry's
SKILL.md and ui-showcase-bento's source when installed beside this skill, and says when they are not.
