# Inspector panel reference implementation

Formerly the standalone `inspector-panels` skill, now an example of [ui-kit-inspector](../../SKILL.md). It is one plain-DOM panel with schema-driven controls, validation, persistence and an element inspector. It predates the jig contract: it has no `data-jig` markers and no `window.jig` change set, so add them before running `scripts/check-jig.mjs` on a jig built from it.

An inspector panel lets someone tune a parametric system and watch the result change. It has three parts:

- **Panel (inputs):** controls generated from a typed schema over one config object.
- **Status (checks):** validation runs on every change. A failing contract check stops rendering and is shown in the panel.
- **Inspector (outputs):** rendered elements carry `data-spec`. Hovering or focusing one shows the values it was built from.

Use it for design tokens, type scales, layout or grid rules, animation curves, chart styling, physics or simulation constants: anything that is `render(config)`. Don't use it for an end-user settings form; that is a different product with different needs.

## Workflow

1. **Model the system as `defaults + render(cfg) + validate(cfg)`.** The config is plain JSON: numbers, strings, booleans, nested objects and fixed-length arrays. Write the defaults first; they define the only shape the panel will accept.
2. **Write the schema.**
   - Add one param per tunable leaf.
   - Group params by concept and order the groups by influence.
   - Give each group a `hint` stating the rule its params drive, such as `n = n0 + a·s + k·z`.
   - Never expose derived values as inputs. Show them in the output, the readout or the hints.
3. **Write `validate(cfg)`.** It returns checks of two kinds:
   - **Contract** checks must hold for the output to mean anything. A failure blocks rendering.
   - **Property** checks describe the current choice, such as "matches the reference examples". A failure is only reported.
   - Give each check a short id, a title that states the rule, and a detail that shows the offending values.
4. **Write `render(cfg, ctx)`.**
   - It must synchronously draw into the detached `ctx.root` supplied by the panel. Set styles and attributes on its children; only the children are committed to `outputRoot`. Do not mutate the live output or external state. DOM measurements on this detached root do not reflect live layout.
   - Put `data-spec="Name · key value · key value"` on every meaningful element, listing the values it actually used.
5. **Mount the panel with `createInspectorPanel`** (section 6).
   - Supply separate `mount` and `outputRoot` elements. `inspectRoot` defaults to `outputRoot`.
   - Choose a `storageKey`.
   - Start at `version: 1`. Bump it whenever a path changes meaning or shape, so old saved configs are dropped instead of misread.
6. **Run the test checklist** (section 7) before handing it over.

## 1. Schema

```js
const schema = [
  { group: "Spacing", hint: "padding = base × steps", params: [
    { type: "number", path: ["spacing", "base"], label: "Base", unit: "px", min: 1, max: 16, step: 1 },
    { type: "range",  path: ["spacing", "steps"], label: "Steps", min: 1, max: 8 },
  ] },
  { group: "Tiers", params: [
    { type: "matrix", label: "Tiers", rows: [["widget", ["tiers", "widget"]], ["brand", ["tiers", "brand"]]],
      cols: [["n0", 0], ["a", 1], ["k", 2], ["g", 3]], step: 1 },
  ] },
  { group: "Look", params: [
    { type: "select", path: ["look", "ratio"], label: "Ratio", options: [["9:8", 9 / 8], ["5:4", 1.25], ["4:3", 4 / 3]] },
    { type: "toggle", path: ["look", "rounded"], label: "Rounded" },
    { type: "color",  path: ["look", "accent"], label: "Accent" },
    { type: "text",   path: ["look", "label"], label: "Label" },
  ] },
];
```

| type | value | use when |
|---|---|---|
| number | number | an exact value matters, or the range is open |
| range | number | the value is bounded and continuous, and scrubbing helps; shows its value |
| select | any (option value, type kept) | a few named choices: ratios ("9:8"), modes, presets |
| toggle | boolean | on/off |
| color | "#rrggbb" | colours |
| text | string | labels, sample text, short expressions |
| matrix | numbers at `[...rowPrefix, colKey]` | a table of coefficients: tiers × parameters, breakpoints × values |

`path` is an array of keys into the config. Array indices are numbers.

Every param must point at a default of the matching type, and a select's default must be one of its options. Otherwise building the panel throws an error that names the path.

## 2. The contract

These are the guarantees the reference implementation keeps. Keep them if you adapt it to a framework.

1. **One source of truth.** The config is the state; the controls only display it. View state such as tabs or scroll position is stored separately.
2. **One change pipeline.** A change goes through these steps in order:
   1. The control is parsed. A half-typed number is marked `aria-invalid` and not applied.
   2. The value is written to its path.
   3. Updates are batched into one animation frame.
   4. `validate` runs.
   5. `render` runs, only if no contract check fails.
   6. The controls are synced to the config.
   7. The config is persisted.
3. **The panel survives any config.** If a contract check fails, `validate` throws, or `render` throws, a banner lists the failures, the output keeps its last valid render, and every control keeps working.
4. **Differences from the defaults are visible.** Changed controls are marked, the header shows a "N changed" count, and Reset returns everything to the defaults.
5. **Configs round-trip.**
   - Copy JSON falls back to selecting the text when the clipboard is blocked.
   - Apply JSON uses a shape-safe merge: unknown keys and values of the wrong type are dropped.
   - Persistence stores `{ v, cfg }`. A saved config from another version is ignored, and a storage failure doesn't stop the panel.
6. **The panel's style doesn't depend on the system being tuned.** A broken config can't make the panel unreadable. The panel defines private, mount-time geometry tokens and never reads the live system’s size or typography tokens. Keep any deliberate panel theme separate from the config being tuned.
7. **Accessible.**
   - Every control has a label.
   - Focus outlines are visible.
   - The status line has `role=status` and the banner has `role=alert`.
   - The inspector responds to focus as well as hover.
8. **Fast.** An update takes under 16ms. If validation measures the DOM, batch the reads into one style pass rather than reading in a loop.

## 3. Layout and density

- **Desktop:** the panel is a sticky column 280–340px wide, beside the output (`.ip-layout`).
- **Under 900px:** it stacks above the output.
- **Collapsible:** the panel is a `<details>`, so it can be closed.
- **Differential Forms geometry:** consume the current shared typed resolvers through `panel-geometry.js`. Defaults are u4, border0, Soft curvature and label edge1.5u. Controls are 28/32/40px for compact/default/loose; their 24px slots and 14px text remain fixed at u4.
- **Independent families:** `geometry.controlDensity`, `geometry.collectionDensity`, and `geometry.cardDensity` are separate. Panel geometry is independent of the inspected config. Border is deducted once by the owner; keep its transparent width in all states.
- **Parts:** action buttons contain `.ip-label`; text/number fields use neutral `.ip-field` wrappers and native editable parts. JSON editing uses content-driven collection geometry. Groups and the panel do not subtract geometry from nested controls.
- **Focus:** keyboard focus paints a 3px solid ink outline at offset0; text fields paint on the wrapper, other controls individually. Preserve space for outline paint and raise focused siblings without changing dimensions.
- **Typography:** system-ui interface text; IBM Plex Mono400 for specimen hints/captions. HTML examples load pinned Phosphor2.1.1 when icons are used.
- **Order inside the panel:** status and actions first, then groups, then the Config JSON section last.
- **Hints** state the formula. Keep them to one or two lines.
- **Readout:** with Inspect on, a hovered element gets a dashed outline, and the readout repeats its `data-spec`.
- **Size tokens:** `panelGeometry()` maps resolver pixels once into private `--ip-*` properties. Never connect them to the config being tuned or inherited system tokens.

## 4. Writing good checks and specs

- **Checks** state the rule in the title and show the actual values in the detail. For example: `M8 · A control fits in every container · card offset 2 < 3`.
- **Contract vs property.** If the output would be wrong or unreadable when the check fails, it's a contract check. If the check only describes the current choice, it's a property check.
- **Specs** name what the element is, then the values it used, in the order a person reads them. For example: `Button · product/md/sm · h28 inset 7 icon 14 r7`.

## 5. Adapting to a framework

Keep the same schema and the same contract. In React, hold the config in `useReducer`. Validate before committing a candidate output and preserve the last successful subtree if validation or rendering fails. If wrapping this DOM implementation, give it an output root that React does not manage, and call `destroy()` in effect cleanup. Persist in an effect. Attach the inspector with delegated listeners on the output root and remove them on cleanup.

## 6. Reference implementation

Use the bundled [JavaScript](inspector-panel.js) and [CSS](inspector-panel.css). Copy `panel-geometry.js` and `geometry-runtime/` alongside them. There are no third-party runtime dependencies; rebuild the generated browser modules with Node24+ using `npm run build`. The build reads mathematical-design-system’s bundled source in this plugin directly, strips TypeScript and records source hashes. Renderers must use `render(cfg, { root })` and receive a separate `outputRoot` at mount time; migrate older renderers that wrote directly to the live DOM.

Minimal use:

```html
<link rel="stylesheet" href="inspector-panel.css">
<div class="ip-layout"><aside class="ip-mount" id="panel"></aside><main id="out"></main></div>
<script type="module">
  import { createInspectorPanel } from "./inspector-panel.js";
  const defaults = { spacing: { base: 4, steps: 4 }, look: { accent: "#3366ff", rounded: true } };
  const schema = [
    { group: "Spacing", hint: "padding = base × steps", params: [
      { type: "number", path: ["spacing", "base"], label: "Base", unit: "px", min: 1, step: 1 },
      { type: "range", path: ["spacing", "steps"], label: "Steps", min: 1, max: 8 } ] },
    { group: "Look", params: [
      { type: "color", path: ["look", "accent"], label: "Accent" },
      { type: "toggle", path: ["look", "rounded"], label: "Rounded" } ] },
  ];
  const validate = (c) => [{ id: "C1", level: "contract", pass: c.spacing.base * c.spacing.steps <= 64, title: "Padding ≤ 64px", detail: `${c.spacing.base * c.spacing.steps}px` }];
  const render = (c, { root }) => {
    const pad = c.spacing.base * c.spacing.steps, r = c.look.rounded ? 2 * c.spacing.base : 0;
    root.innerHTML =
      `<div style="padding:${pad}px;border-radius:${r}px;background:${c.look.accent}" data-spec="Card · padding ${pad} · radius ${r}">Card</div>`;
  };
  createInspectorPanel({ mount: document.getElementById("panel"), title: "Jig", schema, defaults, render, validate,
    outputRoot: document.getElementById("out"), version: 1, storageKey: "my-jig", inspectRoot: document.getElementById("out") });
</script>
```

ES modules don't load from `file://` in Chromium, so serve the folder over http. For a single-file artifact, bundle the module and its geometry imports with the host project’s normal build.

The returned object has `get()`, `set(path, value)`, `reset()`, `inspect(on)`, `checks()` and `destroy()`.

## 7. Test checklist

Run these in a real browser (Playwright or similar) before handing the panel over. The runnable suite is [examples/test.mjs](examples/test.mjs), using [examples/demo.html](examples/demo.html). Serve this folder over HTTP, then run `node examples/test.mjs http://localhost:8000/examples/demo.html /tmp/inspector-panel-results`. Install `playwright-core` and a compatible Chromium first; optionally set `PLAYWRIGHT_MODULE` to its absolute module entrypoint and `CHROMIUM` to the browser executable. Test failures produce a nonzero exit status.

**Loading**
- The page loads with no errors.
- There is one control per schema leaf, and every control has a label.
- The status shows the counts and the header says "defaults".

**Controls**
- Each control type writes its path with the right type: number, number, the option's own value, boolean, string.
- Each matrix cell writes `[...prefix, key]`.
- The output follows each change. Focus a range and change it with the keyboard; its numeric readout must follow immediately.
- An empty or half-typed number is not applied and is marked invalid.

**Changed marks**
- After a change, the control is marked changed and the count is right.
- Reset returns to "defaults".

**Failure handling**
- When a contract check fails, `render` isn't called, the output is unchanged, the banner is shown and the status is marked bad.
- Fixing the value clears the banner and renders again.
- If `render` writes a partial staging tree then throws, the live output retains its node identities and event handlers; the error is reported and the panel recovers.
- If `validate` throws, the error is reported and the next valid change recovers.
- A property check that fails is reported but doesn't block rendering.

**Persistence and JSON**
- The config survives a reload.
- A saved config from another version is ignored.
- Merging saved or pasted configs recursively preserves nested objects and fixed-length arrays, including objects within arrays. Null, wrong container types, unknown keys and mistyped leaves cannot corrupt the shape.
- Apply JSON takes the valid values, drops the rest and syncs the controls.
- Apply with bad JSON reports the error and changes nothing.
- Copy reports "Copied" or selects the text.

**Inspector**
- Hovering an element shows the spec of the nearest `[data-spec]` element.
- Turning Inspect off removes the outlines and hides the readout.

**Schema errors**
- A missing path, a wrong type, a select default that isn't an option, and an unknown param type each throw an error naming the path.

**Lifecycle**
- Destroy with an update pending: no later render or page error occurs.
- Destroy twice safely, then remount on the same element: no old handlers fire.

**Layout and speed**
- Set hostile system tokens on an ancestor (`--h:0px`, `--type-control:0px`, huge spacing); panel dimensions and typography remain unchanged.
- At 390px wide there is no horizontal scroll, in both light and dark mode.
- One update takes under 16ms.

## Differential Forms integration and exceptions

Component mapping: the panel is a card; groups are collections; actions are standalone controls; text/number fields are neutral input wrappers; booleans remain native checkbox semantics with 1u artwork curvature. The JSON editor is a content-driven collection surface. Native disclosure summaries retain their keyboard behavior. There are no attached composites, chip adornments, currency selectors, radios or switches in this implementation; do not manufacture them to match the reference specimen.

Small experimental extensions preserve existing native functionality: select and color inputs use control-family outer geometry with browser-owned popup/swatch internals; ranges retain native track/thumb behavior in a fixed control slot; the JSON textarea uses collection inset and content-driven height; details summaries use control minimum height and allow heading wrapping. Native number steppers remain browser-owned. These internals are not certified Differential Forms parts. Checkbox forced-colors mode delegates artwork to the native control. The demo output is deliberately arbitrary `render(config)` content: its existing padding, shadow and aspect-ratio experiment remains intact, separate from the inspector chrome.

`geometry` is an optional mount-time object: `{unit:4, border:0, controlDensity:'default', collectionDensity:'default', cardDensity:'default', controlCurvature:'soft', containerCurvature:'soft', labelEdgeUnits:1.5}`. Changing panel geometry requires remounting; reset/import/persistence affect the inspected config only.

Run `npm run build` and `npm test`, then the browser suite above. Verify unit/border/density boundaries, text and label preservation, wrapper versus action focus, pointer/keyboard transitions, light/dark and narrow layouts. Numerical checks, browser assertions, visual inspection and assistive-technology audits are separate evidence. No full screen-reader or contrast audit is claimed. Shared contracts/resolvers are consumed unchanged: this consumer has no `specimens/source.html` or generated `specimens/index.html` to edit. `geometry-runtime/provenance.json` records the baseline and per-source hashes; do not hand-edit generated modules.
