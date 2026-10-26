# Theme jig

A theme jig tunes colour: the palette, its light and dark modes, contrast, and brand variants. Read [change-set.md](change-set.md) for the export and [patterns.md](patterns.md) for the interactions.

## What it tunes

| Family | Examples of a constant |
|---|---|
| Palette sources | An accent hue, chroma and lightness, a neutral tint |
| Mode values | A role's value in light and its value in dark, when each is written as a literal |
| Brand variants | The source colours that differ between brands |

Roles computed from a source colour are derived values: a hover shade mixed from the accent, a border taken from the neutral ramp. Show them with their formula and offer an override. Shape, spacing and type belong to the other kinds.

## Discover first

1. Find the colour tokens and how they are layered: source colours, ramps, and semantic roles such as text, surface, border and accent.
2. Find how modes are selected: a class or attribute on the root, a media query, separate token files. Where the host keeps modes in DTCG resolver files or in Figma variables, use the mode names written there.
3. Find how brand variants are selected, when the host has them.
4. Find the formulas: where a role is computed from a source (a colour function, a mix, a ramp generator), copy the formula in the host's own terms.
5. Find the contrast rule the host states, and which pairs of roles it applies to.
6. Find the components and screens that show the roles in use. These are the canvas.

Sort what you found.

| Found | It is | In the jig |
|---|---|---|
| The mode and the brand being viewed | Context | A choice above the tabs |
| A source colour or a role written as a literal | Constant | A control, with `home` set to where the literal is |
| A role computed from a source | Derived | A read-only swatch with its formula, and at most an override |
| A colour hard-coded in a component, with no token | Proposal | A control with `home: null` and a `hint` that says where the literal is written, in a group labelled as proposals |

A role with one literal per mode is one constant per mode. Give each its own path, for example `/accent/light` and `/accent/dark`, so a change says which mode it moved.

## Context, constants and overrides

- Context: the mode shown, the brand shown, and the screen or parts shown. These export under `context`.
- Constants: the source colours and literal role values. Each control carries `data-jig-constant="<path>"`. Split a colour into number fields in the colour space the host writes it in (for example hue, chroma and lightness), so each channel scrubs and steps from the keyboard, and so the checker's `edit` check has a number field to press.
- Overrides: a wish for one derived role in one mode ("the dark border a little lighter"). Export it under `overrides` with the mode in `at` and the formula beside it.

Export colour values as the host writes them. A change's `from` must equal the literal in the source, so keep the host's notation and precision.

## Canvas

- Draw real components from the host that use the roles: text on surfaces, buttons, fields, borders, a focus ring, a status message.
- Show light and dark side by side when the width allows, each under its own mode selector, so one edit is judged in both.
- Add a role sheet as the whole-system view: every role as a swatch with its name, its value, and the contrast of each declared pair.
- Offer a before and after toggle. Colour is judged by comparison.
- Mark the canvas root with `data-jig-canvas`.

## Checks to offer

- Contract: the host's own contrast rule and any other colour rule it states, run in every mode on every edit.
- Proposed, in a separate group:
  - each text and surface pair meets a contrast level, in both modes;
  - the focus ring is distinguishable from the surface behind it, in both modes;
  - status colours stay distinguishable from one another;
  - a role's value in one mode is not left equal to its value in the other by accident.
- When the host states no contrast rule, propose one, name the level in the check's text, and report it under `proposed`. A failure names the pair and the mode.

Measure contrast from the colours the browser computes on the canvas, so the check sees what a person sees.

## Edges to stress

- Both modes for every edit, and every brand variant.
- The lightest and darkest step of each ramp.
- Text on every surface it can sit on, including tinted and raised surfaces.
- Disabled, selected and focused states.
- A forced high-contrast or reduced-transparency setting, when the host supports one.
- Small text and thin borders, where a low contrast shows first.

## Done when

- Every control maps to a colour found in the source, or sits in the proposals group with `home: null`.
- Moving a source colour moves every derived role on the canvas, in every mode shown.
- The mode and the brand are context, and the change set's `context` records them.
- Contrast is reported per pair and per mode, with the host's rule and the jig's proposals in separate groups.
- The panel root carries `data-jig="theme"`, and `node scripts/check-jig.mjs <page>` exits 0 with no `skip` line.
- The exported change set passes `node scripts/validate-changeset.mjs <file.json>`.
