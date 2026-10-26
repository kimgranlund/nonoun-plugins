# Examples

Three examples ship with the skill. They do different jobs.

| Folder | What it is | Use it for |
|---|---|---|
| [minimal-system-jig](minimal-system-jig/jig.html) | The worked example. A small system jig over a small host, and it meets the jig contract. | The shape to build to: the core loop, the contract, the change set |
| [maison-jig](maison-jig/README.md) | One system jig for one system. It predates the jig contract. | Seeing the larger patterns at work: pick in both directions, before and after, undo and redo, presets, tabs, the actions menu |
| [inspector-panel](inspector-panel/README.md) | A reusable plain-DOM panel: schema-driven controls, validation, persistence and an element inspector, on Differential Forms geometry. It predates the jig contract. | A tested panel to start from when the host has no components of its own; add the jig markers and change set |

## minimal-system-jig

| File | What it is |
|---|---|
| [minimal-system-jig/host/README.md](minimal-system-jig/host/README.md) | The host: a stand-in for a real project, with its two rules |
| [minimal-system-jig/host/tokens.css](minimal-system-jig/host/tokens.css) | Five constants and four derived values |
| [minimal-system-jig/host/components.css](minimal-system-jig/host/components.css), [minimal-system-jig/host/index.html](minimal-system-jig/host/index.html) | A card, a text field and a button |
| [minimal-system-jig/jig.html](minimal-system-jig/jig.html) | The jig: one page, no build step, nothing loaded from the network |
| [minimal-system-jig/changeset.json](minimal-system-jig/changeset.json) | A change set exported from the jig: one change, one override, one failing proposed check and a note |

What to read in `jig.html`:

- It loads the host's CSS by relative link and draws the host's own markup, so the canvas is the real thing.
- Context (canvas width, label length) sits apart from the five constants.
- A number constant steps by 1 on the arrow keys, by 10 with Shift and by 0.1 with Alt, and scrubs when its label is dragged.
- A changed row shows the old and the new value with a reset.
- One derived value has an override row. It exports under `overrides`, never under `changes`.
- The host's two rules report under `contract`, and the jig's own checks under `proposed`, in separate groups.
- One actions menu holds Copy JSON, Copy as prompt, Import and Reset all.

It builds the core loop only. Pick, before and after, undo and redo, and presets are taught in [../references/patterns.md](../references/patterns.md).

Check it from a project that has Playwright installed, with paths relative to the skill folder:

```
node scripts/check-jig.mjs examples/minimal-system-jig/jig.html
node scripts/validate-changeset.mjs examples/minimal-system-jig/changeset.json
```

Two things in it are specific to a page opened from disk. It holds the hash of `host/tokens.css` as a constant, because a page opened as a file cannot read another file to hash it. If you change `tokens.css`, update that constant. And it writes edits on the root element, because that is where the host declares its derived values.

## maison-jig

Read [maison-jig/README.md](maison-jig/README.md) before opening it. It is not a template, and the two scripts do not apply to it.

## inspector-panel

Read [inspector-panel/README.md](inspector-panel/README.md). It was the `inspector-panels` skill. Its own tests run from its folder with `npm test` (Node 24 or later); the two scripts above apply only once a jig built from it has the markers and the change set.
