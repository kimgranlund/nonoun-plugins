# System jig

A system jig tunes the constants a whole UI system derives from, and shows the whole system moving. Read [change-set.md](change-set.md) for the export and [patterns.md](patterns.md) for the interactions.

## What it tunes

The small set of values everything else is computed from. Typical families, each present only when the host has it:

| Family | Examples of a constant |
|---|---|
| Size and space | A base unit, the step between sizes, the range of allowed sizes |
| Type | The size of body text at a reference point, the ratio between heading steps, the smallest text allowed |
| Shape and stroke | A corner radius or radius factor, a border width, a focus ring width |
| Motion | Durations and easings |
| Elevation | Offset, blur and strength of a shadow |

A system jig does not tune one component (that is a component jig), page structure (a layout jig) or colour roles (a theme jig). When the host keeps one of those families among its system constants, a system jig may carry it. The change set's `kind` stays `system`.

## Discover first

Look in this order, and write down what you find before building.

1. Token source files: CSS custom properties on the root, a tokens JSON file, a theme object, a config module.
2. The code that derives values: `calc()` expressions, a scale function, a build script. Each derived value has a formula there. Copy the formula in the host's own terms.
3. The rules the system states about itself: a README, a contract file, a test suite, a lint rule.
4. The components that read the tokens, for the canvas.

Then sort every value into one of three lists.

| List | Test | What the jig makes |
|---|---|---|
| Constant | It is written as a literal in the source | A control, with `home` set to where the literal is |
| Derived | It is computed from other values | A read-only row with its formula, and at most an override |
| Proposal | The work asks for a knob and the source has no literal for it | A control with `home: null`, shown in a group labelled as proposals |

Where the host uses DTCG token files, use the token's path and its `{alias}` syntax as the `home`. DTCG has no formulas, so the formulas still come from the host's code.

## Context, constants and overrides

- Context is the viewpoint: which size, density, theme or tier the canvas shows, how wide it is, how long its content is. It changes nothing and exports under `context`. Keep it above the tabs, always visible.
- Constants are the real knobs. Each one carries `data-jig-constant="<path>"` and exports under `changes` with the value it replaced.
- Overrides pin one derived value at one spot. Show the row as off its formula, with the formula beside it. It exports under `overrides` with `target`, `at`, `formula`, `from`, `to` and a `reason`. An override never becomes a change.

A changed row shows the old and the new value and a reset. The panel has a reset for all.

## Canvas

- Draw the host's own components by loading its styles and using its markup. Size nothing by hand.
- Show a strip of representative parts: a control in each size, a text sample for each type role, a card or container at each level.
- Add a whole-system view: a matrix of every step the system can produce at once, where a click on a cell moves the context to that step.
- Mark the canvas root with `data-jig-canvas`.
- Write edits where the derived values are computed. In a CSS system that is the element that declares the derived custom properties, usually the root, so every `calc()` picks up the new input.

## Checks to offer

- Contract: every rule the host states, run on every edit. A failure names the rule and the step that broke it.
- Proposed, kept in a separate group and exported under `checks.proposed`:
  - a control is not shorter than a minimum the host or the team names;
  - the radius fits inside the control;
  - a border and a focus ring fit and stay visible;
  - durations rise from short to long;
  - a font weight the type scale asks for exists in the font.
- A finding that is worth saying and breaks no rule goes in `notes`, for example how many steps fall under a touch target.

When the host states no rule, `checks.contract` is null. Say so in the panel.

## Edges to stress

- The smallest and the largest step of every scale.
- Each constant at the two ends of its allowed range.
- Long labels, and right to left.
- Focus ring and elevation switched on.
- Two constants moved together that share a derived value.

## Done when

- Every control maps to a constant found in the source, or sits in the proposals group with `home: null`.
- Moving a constant moves every part on the canvas that derives from it, with no rebuild.
- A derived value can be pinned, and the pin exports under `overrides` and nowhere else.
- The host's rules and the jig's proposed checks show in separate groups.
- The panel root carries `data-jig="system"`, and `node scripts/check-jig.mjs <page>` exits 0 with no `skip` line.
- The exported change set passes `node scripts/validate-changeset.mjs <file.json>`.

The worked example in [../examples/README.md](../examples/README.md) is a system jig of this shape.
