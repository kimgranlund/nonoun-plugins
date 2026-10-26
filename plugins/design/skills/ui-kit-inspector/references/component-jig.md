# Component jig

A component jig tunes the tokens one component reads, and shows that component across its props, states and variants. Read [change-set.md](change-set.md) for the export and [patterns.md](patterns.md) for the interactions.

## What it tunes

The constants one component reads: its heights, paddings, gaps, radius, border, type size and colours, each as the token behind it.

It differs from a story with controls in what moves. A story's controls change the arguments of one rendering. A component jig changes tokens, and a token is usually shared. So the jig shows the component in every variant at once, and names the other components that read the same token.

## Discover first

1. Find the component's source and its styles. List every token its rules read, for example each `var()` in its stylesheet or each theme key in its style object.
2. Find each token's `home`: the file and the place where its literal value is written.
3. List the component's props, variants and states from its own API: its prop types, its variant map, its documented states.
4. Find which other components read each of those tokens. A search of the source for the token name is enough.
5. Find the rules that apply to it: a minimum size, a contrast rule, an accessibility test.

Sort what you found.

| Found | It is | In the jig |
|---|---|---|
| A prop, a variant, a state | Context | A choice that changes what the canvas shows |
| A token with a literal value | Constant | A control, with `home` set to where the literal is |
| A token computed from others | Derived | A read-only row with its formula, and at most an override |
| A value hard-coded in the component, with no token | Proposal | A control with `home: null` and a `hint` that says where the literal is written, in a group labelled as proposals |

## Context, constants and overrides

- Context: the props, the variant, the state, the content and the size the canvas shows. They export under `context` and change nothing. A person switching from the primary to the secondary variant has changed their viewpoint, not the system.
- Constants: the tokens. Each control carries `data-jig-constant="<path>"`. Beside each one, show how many other components read it, because moving it moves them too.
- Overrides: a wish that this one component differ from its token ("this button, 2 px less padding"). Export it under `overrides` with the component and variant in `at`. The receiving agent decides whether it becomes a new token, a component-level exception or nothing.

## Canvas

- Render the host's real component, imported or loaded the way the host's own screens do it.
- Show a matrix: variants across, sizes or states down. Every cell is the live component at true pixels.
- Give states a control that forces them (hover, focus, active, disabled, invalid, loading), so a state can be held still and inspected.
- Show the component once inside a real neighbour, for example a button inside the host's toolbar or form row, so spacing against siblings can be judged.
- Mark the canvas root with `data-jig-canvas`.

## Checks to offer

- Contract: the host's own rules for this component, when it states any.
- Proposed, in a separate group:
  - the smallest size meets a minimum target the host or the team names;
  - the focus ring is visible in every variant;
  - text and background in every variant and state meet the contrast rule the host states;
  - the radius fits the smallest size;
  - a label does not clip at the longest content setting.
- When the host states no contrast rule or minimum target, propose one, name it in the check's text, and report it under `proposed`.

## Edges to stress

- Empty, one character, and very long content. With and without an icon.
- The smallest and largest size.
- Every state in every variant, including disabled with focus and invalid with hover.
- Right to left.
- Inside a narrow container, where the component must wrap, truncate or shrink.
- Many instances in a row.

## Done when

- Every control maps to a token the component reads in its source, or sits in the proposals group with `home: null`.
- The matrix shows every variant and state the component's API declares.
- Moving a token moves every cell that reads it, and the panel says which other components read that token.
- A per-component wish exports under `overrides`, never under `changes`.
- The panel root carries `data-jig="component"`, and `node scripts/check-jig.mjs <page>` exits 0 with no `skip` line. At least one constant is a number field, so the `edit` check runs.
- The exported change set passes `node scripts/validate-changeset.mjs <file.json>`.
