# Maison Jig prototype

`prototype-maison-jig.html` is one system jig for one system. It is not a template to copy.

It was built to tune the constants of one design system, with that system's names, formulas and rules written into it. Open it to see how the larger patterns behave when they are all present. Build your own jig from the host you are working in, following the skill's workflow.

## What does not apply to it

It predates the jig contract and uses its own change set format, `maison.jig.changeset/2`.

- `scripts/validate-changeset.mjs` does not apply. Its change sets are not `jig.changeset/1`, so the validator rejects them.
- `scripts/check-jig.mjs` does not apply. The page has none of the three `data-jig` attributes and no `window.jig`.
- Its controls are written by hand, and its canvas is a drawn specimen. A jig built with this skill uses the host's own components.
- Several of its constants (colour, elevation, motion, layout) were the prototype's own proposals and not tokens of the system. In a jig built with this skill, each of those is a proposal with `home: null`.

For a jig that meets the contract, see `../minimal-system-jig/jig.html`.

## Where it came from

| | |
|---|---|
| Source | `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0525-token-jig-preview-panel/prototype-maison-jig.html` |
| Version | Prototype version 9 |
| Copied | 2026-10-13, byte for byte |
| sha256 of the copy | `580dd8d19625bbb6a770428af9b99b40fce68fa0ce9470871f7ab98189716e53` |

Confirm the copy with `shasum -a 256 prototype-maison-jig.html`. Do not edit the file. If the source moves on, copy it again and update this table.

## Where to look

Open the file in a browser. The canvas is on one side and the panel, titled Jig, on the other.

| Pattern | Where to see it |
|---|---|
| Pick, element to constants | Hover any part on the canvas for a preview, and click to keep it. The panel marks what the part reads (solid), what its containers read (dashed) and what its contents read (dotted), opens the group that holds the first hit, and switches tab if it needs to. A tooltip on the page names the part with its path. Esc, or a click on the page background, releases it. |
| Pick, constant to elements | Click or hover a field label in the panel. Every element that reads that constant is outlined on the canvas, and the on-page tooltip says how many it drives. The same label, Esc or a click outside releases it. Dragging a label scrubs the value and is not a pick. |
| Before and after | The "Before (base system)" checkbox in the row of toggles above the canvas. It draws the canvas from the base values and keeps your edits. |
| Undo and redo | In the actions menu, and on Ctrl or Cmd Z. |
| Presets | The System tab, Presets group. Name the current state and save it, then load or delete it from the list. Presets stay in the browser. |
| Tabs | Four tabs under the context row: Space, Type, Style and System. Context (Tier, Scale, Size, Density) stays above them. A dot marks each tab that holds a hit from a pick. |
| Actions menu | The button labelled "Jig actions" at the end of the panel header. It holds Copy JSON, Copy as prompt, Import a change set, Undo, Redo and Reset all. |

Also worth a look: the health mark in the header that opens the System tab, the help button on each group, the "Every rung" matrix that jumps the context when a cell is clicked, and the toggles for Focus ring, Elevation, Long labels and Right to left.

One thing it does that this skill now teaches differently: its presets are snapshots of the whole state. The skill teaches presets as saved change sets against a base, so a stale preset is refused on load.
