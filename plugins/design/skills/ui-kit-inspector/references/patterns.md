# Interaction patterns

The named patterns a jig is built from. Build the core loop first (canvas, constants, change set, checks). Add a pattern from this file when the work asks for it, and run the checker after each. Sources for the precedents named here are in [prior-art.md](prior-art.md).

## Scrub

A number field whose label can be dragged to change the value. The term is Bret Victor's: drag sideways on a number and the result updates at once.

The keyboard path is complete on its own. Dragging is the extra.

| Input | Step |
|---|---|
| Up or Down arrow | 1 |
| Shift with an arrow | 10 |
| Alt with an arrow | 0.1 |
| Drag on the label | The same steps, by distance, with the same modifiers |
| Typing a value and leaving the field | Sets it, clamped to the allowed range |

- These steps are the ones Chrome DevTools and Firefox DevTools document for numbers in their style editors, so they are what people's hands expect. The 0.1 step is Alt on a Mac, and Ctrl in Firefox on Windows and Linux; accept both.
- Chrome has deprecated its own drag-to-change on length values (as of Chrome 123). That is one more reason the keyboard path stands on its own.
- One gesture is one history entry. Update the canvas on every move, and commit to the undo history and the change count once, when the drag ends or the key is released. lil-gui makes the same split between `onChange`, which fires on every change, and `onFinishChange`, which fires once the change is done.
- A drag on a label is a scrub, never a pick. Decide which it was when the pointer comes up: no movement means a click.
- Give the field a spinbutton role or a native number input, a visible label, and its range. The checker's `edit` check presses ArrowUp in the first one it finds.
- Round to the step, so a value never exports as 4.000000001.

## Changed marks and reset

A row whose value differs from the base shows the old value, the new value and a reset for that row. Put the reset inside the field as its leading part, in a slot that stays reserved while hidden, so the field keeps one border and the value never shifts. The panel header shows the count of changes. One action resets everything to the base.

## Pick: from an element to its constants

Hovering an element on the canvas previews, and clicking keeps, a highlight in the panel of what that element reads. Three relations, each with its own mark:

| Relation | What it shows | Mark |
|---|---|---|
| Its own | The constants the element itself reads | Solid |
| Its containers | The constants its ancestors read, up to the page | Dashed |
| Its contents | The constants its descendants read | Dotted |

- The panel opens the group that holds the first direct hit and scrolls it into view. With tabs, it switches to the tab that holds the hit and puts a dot on every tab that has one.
- On the canvas, the picked element, its ancestors and its descendants get matching outlines.
- A tooltip on the page, anchored to the element, names the selection with its path (for example "Button label in Button, Toolbar, Card, Page") and says how to keep it and how to release it. The explanation belongs on the page, beside the thing picked, and not in a bar inside the panel.
- Release on Esc, or on a click on anything that is not a pickable element, the panel, a help popover or a control.

Where the links come from: draw a link only where the host's source shows the element reading the constant, for example a `var()` in its rule, a token named in its component, or an entry in a manifest. An element with no link found gets a tooltip that says the jig could not trace it, and the report lists it as a finding.

This direction is well established. The Firefox Computed view expands a property to the rule that set it, a `var()` in Chrome DevTools links to the declaration, and Figma's Inspect lists the variables on a selected layer.

## Reverse pick: from a constant to what it drives

Clicking or hovering a field label in the panel outlines every element on the canvas that reads that constant.

- The same on-page tooltip names the constant and says "Drives N elements" in the current context, and how to release.
- Release with the same label again, Esc, or a click elsewhere.
- A constant that nothing reads directly, such as a limit or a range, says so in the tooltip.
- When the constant drives nothing in the current context but would in another, the tooltip says which context to switch to.

This direction is the jig's own. The research behind this skill found it in none of the tool pages it read. Build it; there is no borrowed behaviour to copy, so test it with people.

## Before and after

One toggle draws the canvas from the base values and leaves the edits in place, so a person flips between the two without losing work. Precedents are the Chrome DevTools Changes panel, which shows a diff of edits with a revert, and Figma's Compare changes. Where the width allows, draw both side by side.

## Undo and redo

- Keep a history of whole states. One snapshot shape serves undo, presets and a saved session.
- Undo and Redo sit in the actions menu, and on Ctrl or Cmd Z.
- While a text field has focus, leave the shortcut to the field's own undo.
- An import is one history entry, and so is a reset of everything.

## Presets

A preset is a saved change set against a base, with a name. Loading one goes through `importSet`, so a stale preset is refused. Always offer a reset to the base. The reasoning and the storage rule are in [change-set.md](change-set.md).

## Whole-system view

A view that shows everything the system can produce at once: every step of a scale, every variant of a component, every breakpoint range, or every colour role. A click on a cell moves the context to that step. A health mark in the panel header shows whether the checks pass and opens the checks when clicked.

Canvas toggles that stress the system belong near this view: long labels, right to left, focus ring on, elevation on, reduced motion, and before.

## Panel structure

- Context stays visible above everything else, whichever tab is open. It is the viewpoint, and every number in the panel is read against it.
- Group concepts in tabs when the panel has more than a few groups, for example space, type, style and system. Tabs take arrow keys, Home and End.
- Fold actions into one menu in the header: Copy JSON, Copy as prompt, Import, Undo, Redo, Reset all. Esc closes the menu and returns focus to its button.
- Checks sit beside the controls, in two groups that cannot be confused: the host's contract, and the jig's proposals.
- The note field for the reason is always one step away.
- Every field has a label, works from the keyboard and shows focus.
- At a viewport 360 px wide, the page does not scroll sideways. The panel stacks under or over the canvas.

## Labels, glossary and help

- Each field shows a plain name first, and the letter or token name second as a hint. The path in the change set uses the token name or letter, so the two stay linked.
- A tooltip on a field gives one line about that one field.
- Keep a glossary: one row per letter or token name, with its plain name and meaning. Take each plain name from the host's own docs and comments. A constant the host never names in plain words is labelled with its token name, and the report lists a suggested plain name for the owner to approve.
- Each group header carries a help button that opens a popover. It opens on click or from the keyboard, holds rich text, closes on Esc or a click outside, and leaves focus on the button. Unlike a hover tooltip, people on touch screens and screen readers can read it.

What goes where:

| Place | Content |
|---|---|
| Help popover | Static, read once: the group's definitions, its formula in words, the glossary rows it uses, what moves and what does not, which checks guard it, what an override or a copy action means |
| Panel | Live, used every time: fields, values, changed marks, check results, warnings. At most one short hint per group. |
| Field tooltip | One line about that field |

## What the host's component library should supply

A jig needs six controls.

| Control | Used for |
|---|---|
| Number field with scrub | Every numeric constant |
| Segmented choice | Context axes and small sets of options |
| Tabs | Groups of concepts |
| Menu | The one actions menu |
| Popover | Group help, and the on-page tooltip for a pick |
| Disclosure | Groups that open and close |

Use the host's own components when they exist, so the jig is itself a test of the system it tunes. Use plain elements when they do not: a native input with a label, radio inputs in a fieldset, buttons with tab roles, a button with a list of menu items, the popover attribute or a positioned element, and `details` with `summary`.

When the host's library lacks one of the six, or has it without the behaviour a jig needs (a number field that cannot scrub, a popover that traps focus), build the plain version for the jig and report the gap as a finding.
