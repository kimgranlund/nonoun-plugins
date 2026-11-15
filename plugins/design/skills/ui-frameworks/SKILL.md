---
name: ui-frameworks
description: Creates a UI kit in a project - light-DOM custom elements (or React) with plain CSS recipes, built on a signals foundation, covering the WAI-ARIA APG patterns (button, checkbox, switch, radio group, tabs, menu and menubar, listbox, combobox, tree, dialog, tooltip, slider, spinbutton, splitter, grid and treegrid, feed, carousel, text field, form field and more), each with a manifest, overridable tokens such as --button-face, every ARIA and native state styled, and forced-colours rules. Tokens come from ui-colors, ui-geometry and ui-materials. Use for "create a UI kit", "add a tabs component", "give me accessible web components", "a component library with our palette", "a Panda preset for the kit", or to extend or restyle a kit this skill made. NOT for colours or palettes (ui-colors), lengths and radii (ui-geometry), paint and materials (ui-materials), one-off interaction code (ui-interaction-dev), a showcase page (ui-showcase-bento), or components for another design system's own kit.
---

# UI frameworks

A kit is a folder of components that load alone: a shared `reset.css` and `tokens.css`, then per component one class, one defining module, one recipe (CSS) and one manifest. Nothing is bundled and nothing needs a build step. The kit in `kit/` is complete and tested; creating a kit means copying the parts a project needs and regenerating its tokens.

Contents: [Route](#route) · [Create a kit](#create-a-kit) · [Use a component](#use-a-component) · [Restyle](#restyle) · [Extend](#extend) · [Commands](#commands) · [Files](#files)

## Route

| The request | Read | Then |
|---|---|---|
| Create a kit, or add components to one | `kit/registry.json` | [Create a kit](#create-a-kit) |
| How one component is used: markup, attributes, keys, tokens | `kit/components/<id>/<id>.manifest.json` | [Use a component](#use-a-component) |
| Change colours, density, font size or icons | `kit/styles/kit.config.json` | [Restyle](#restyle) |
| Override one component's look | The `tokens` list of its manifest | Set the public token on any ancestor: `--button-face: …` |
| A new component or recipe | `docs/specs/css-contract.md`, `docs/specs/foundation.md`, `docs/specs/manifest.md` | [Extend](#extend) |
| React | `docs/specs/targets.md` | `create-kit.mjs --target react` |
| Panda CSS | `kit/panda/preset.js` | Add it to `presets`, and load `styles/kit.css` as it is |
| Why something is the way it is | `docs/decisions.md` (D1 onwards) | |

## Create a kit

1. Read `kit/registry.json`: every component with its family, role, summary and the targets it is built for. Choose ids. A component brings its family.
2. Copy: `node scripts/create-kit.mjs <project>/kit --components button,tabs,dialog` (omit `--components` for all; `--target react` for React). Add `--tokens used` to trim `tokens.css` to the custom properties the copied components reach (about a quarter of the file), and `--keep --colors-bg,--colors-fg*` for names the project's own CSS reads; leave it out when the project will style its own parts with the kit's colour ramps. The copy keeps this folder's layout, so imports resolve as they are. Without Node, copy this skill's whole `kit/` folder into the project instead: it is the same kit with every component and target, and loads as it is.
3. In the page, link `kit/styles/kit.css` ahead of any script, then load each component's defining module: `<script type="module" src="kit/components/button/button.js">`. A component is styled before its script runs, and moves nothing when it does. Two rules for a project with CSS of its own: the kit's sheet comes before any other sheet that names cascade layers (Tailwind 4's among them), and a reset of the project's goes in a layer, `@import url(reset.css) layer(base);`, because an unlayered rule beats every recipe. A bundler tree-shakes the kit as it is (esbuild, Rollup, Rolldown and webpack were measured). If the project puts the kit in a package with a `sideEffects` field, it must be `["./components/*/*.js", "**/*.css"]` and never `false`, which drops every element's definition. `tokens.css` is required: the recipes read its tokens without fallbacks. `reset.css` is not: each recipe makes its own boxes border boxes.
4. If the project has its own palette, density or font size, [restyle](#restyle).

Markup is the API: `<ui-button variant="primary">Save</ui-button>`. State is an attribute (`checked`, `open`, `disabled`), and the component keeps the ARIA attribute in step. Text entry is always the author's own `<input data-part="input">` inside the component.

## Use a component

Open its manifest. `attributes` are its API, `parts` the children it expects (`author`) or creates (`element`), `keys` its keyboard, `events` what it dispatches, `tokens` what can be overridden, `guidance` and `notYet` its limits. Style-only items (link, card, badge, table) have `kind: "recipe"`: a native element carrying `data-ui="<id>"`.

## Restyle

Edit `kit/styles/kit.config.json` (font size `n`, densities, the ui-colors request, the icon folder and names), then run `node scripts/tokens.mjs` and `node scripts/icons.mjs`. They read ui-colors, ui-geometry and ui-materials from `~/.claude/skills` (or `SKILLS_DIR`) and rewrite `tokens.css` and `icons.css`. Never edit those two files by hand. Dark mode, contrast modes and density are attributes or media queries the tokens already answer; a recipe never changes for them.

## Extend

A new component starts as a manifest (schema: `references/manifest.schema.json`), then its files beside it. The rules it must follow are the specs in `docs/specs/`: the CSS contract for the recipe, the foundation for the class, the state matrix (`references/states.json`) for every state selector, copied unchanged. Then run the commands below until they pass. Copy from a family that is close: tabs for a coordinating element, menu button for an overlay, checkbox for a form control, meter for a value shown as a share.

## Commands

Run from the kit's parent folder (this folder, or a project that copied `scripts/` and `references/` too).

- `node scripts/manifests.mjs`: checks every manifest, writes `kit/registry.json` and `kit/styles/kit.css`. `--check` writes nothing.
- `node scripts/lint-recipes.mjs`: holds every recipe to the CSS contract and names the rule it finds broken.
- `node scripts/props.mjs`: writes each `<id>.props.js` from its manifest.
- `node scripts/tokens.mjs`, `node scripts/icons.mjs`: write `tokens.css` and `icons.css`.
- `node scripts/targets.mjs`: writes the React recipes; `node scripts/panda.mjs`: writes the Panda preset.

## Files

- `kit/registry.json`: the index of every component. Generated.
- `kit/foundation/`: the signals kernel, `UIElement`, `UIFormElement`. `kit/behaviours/`: roving focus, grid focus, typeahead, dismiss, press, active descendant, as plain functions any framework can mount.
- `kit/components/<id>/`: class, defining module, generated props, recipe, manifest.
- `kit/react/<id>/`: the React components that exist. `kit/panda/preset.js`: the Panda preset.
- `kit/styles/`: `reset.css`, `tokens.css`, `icons.css`, `kit.css`, `kit.config.json`.
- `docs/specs/`: vocabulary, state matrix, foundation, CSS contract, manifest, icons, patterns (the rules of every component, J1 onwards), targets. `docs/decisions.md`: why.
- `references/`: `manifest.schema.json`, `states.json`, `terms.json`.

Browser floor: Chrome 129, Firefox 147, Safari 26.4.
