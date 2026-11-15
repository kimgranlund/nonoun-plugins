# Framework targets

Spec 8. Written on 2026-11-13 for the first target after the Web Components: React. It says what a framework target renders, where its files live and how it is proved equal to the Web Components target. Svelte and Solid follow the same rules when they are built.

A target is one framework (B2). It shares the manifests, the recipes, the tokens and the behaviours with the Web Components (D12, D13, D16, D17) and is not a wrapper around them.

## The proof set

React is built first for the four families of the spike: button, checkbox, tabs (tabs, tab list, tab, tab panel) and menu button (menu button, menu, menu item). They hold a form control, a coordinating composite and an overlay, which is what the contract has to carry. Every other component stays `planned` for React (D98).

## What a component renders

| Component | Root | Notes |
|---|---|---|
| button | `button` | `type` as the manifest's attribute; no hidden submit part, the native button submits |
| checkbox | `label` | Holds a native `input type="checkbox"` marked `data-part="input"`, which takes focus and takes part in the form. The root mirrors its state. |
| tabs, tab list, tab panel | `div` | With the role the manifest gives |
| tab | `button` with `role="tab"` | |
| menu button | `span` | |
| menu | `div` with `role="menu"` and `popover` | |
| menu item | `div` with `role="menuitem"` | |

## Rules

| # | Rule | Basis | Check |
|---|---|---|---|
| X1 | A root shall be the native element the table gives and carry `data-ui="<component id>"`. A variant shall be the attribute `data-<variant name>`. A part shall be marked `data-part` with the manifest's name. | C23, D17 | Parity test |
| X2 | A state shall be written in a form its condition in `references/states.json` already selects: the native attribute or pseudo-class where the root has it, otherwise the ARIA attribute where the role of the root allows it, otherwise the author attribute, and `data-focus-visible`, `data-hover` or `data-active` on a root whose focus, hover or press happens on a part. No recipe and no condition shall change for a target. | D26, D62 | Parity test; the recipes are the rewritten ones, byte for byte |
| X3 | A target's recipe shall be the Web Components recipe rewritten by `scripts/rewrite-recipe.mjs` and nothing else, written to `kit/<target>/<id>/<id>.css` by `node scripts/targets.mjs`, which also writes `kit/<target>/styles/kit.css`. With `--check` it writes nothing and fails when a file is stale. | C24, D62 | Generator check; Node test |
| X4 | A component shall mount the behaviours its manifest lists, the same functions the Web Components call, in an effect whose cleanup is the behaviour's cleanup. It shall copy none of their logic. | D12 | Mutation: a behaviour is not mounted |
| X5 | A component's props shall be the manifest's attributes, in camel case, with the defaults and the enum values read from the generated `<id>.props.js`. A value the component holds shall be controlled (`checked` with `onChange`) or uncontrolled (`defaultChecked`), as React's own inputs are. Events of the manifest are `on<Name>` props. Any other prop goes to the root. | D13 | Test per component |
| X6 | A component shall be a plain JavaScript module with JSDoc types that calls `createElement`, needs no build step and imports only `react` and `react-dom`, the behaviours, its own props and another component of its family (for the family's context). One component per file, `kit/react/<id>/<id>.js`, with a named export in Pascal case. No barrel file. | B14, D24 | Size test; import test |
| X7 | A component shall render the same markup on the server and in the browser: `renderToString` followed by `hydrateRoot` shall report no recoverable error, and the server markup alone shall be painted as the hydrated one is. | D17, U1, U2 | Parity test in three engines |
| X8 | For each state of the manifest, the React component and the Web Component, side by side with the same content, shall have the same box and the same computed paint on the root and on every part, in three engines. | D17 | Parity test in three engines |
| X9 | The keyboard and pointer rules of the pattern shall hold for the React component as they do for the Web Component. Its tests cite the pattern's own rule ids. | D17 | Behaviour test in three engines |
| X11 | A target's index stylesheet shall load `kit/styles/native.css` after the reset: it removes what a native `button` root brings of its own, and hides the native input a checkbox or radio root holds, leaving it focusable. No recipe changes for it. | D101; the React proof | Parity test: the tests load the target's `kit.css` and nothing else |
| X10 | A target marked `built` in a manifest shall have its component file and its recipe. | H11, D83 | The checker |

## Files

```text
kit/react/<id>/<id>.js     the component
kit/react/<id>/<id>.css    the recipe, generated
kit/react/styles/kit.css   every built React recipe behind the shared sheets, generated
tests/browser/react.<family>.test.js
tests/mutations/react.mjs
```

## What the proof found

Built on 2026-11-13: nine components, 78 tests in each of three engines, 63 mutations caught. Fixed since: the native reset (X11). Still open:

- **A menu rendered open on the server paints closed until hydration.** Its open state is `:popover-open`, and no attribute opens a popover. X7 holds because the proof renders its menus closed.
- **A `label` root cannot carry ARIA states,** so the checkbox mirrors `checked`, `indeterminate`, `disabled` and `invalid` as plain attributes, which the conditions select. X2's order reads "the ARIA attribute where the root's role allows it".
- **A disabled fieldset does not reach the checkbox's label:** the input is disabled, the label is not painted so.
- **A menu button's trigger gets its ARIA after hydration,** because the trigger belongs to another family.
- **A tab or panel without a `value`** gets its position only as a direct child of its list.

## Not in this spec

- **Svelte** has no sequence yet. **Solid 2.0** cannot be built here: the only Solid at hand is 1.9 (D99).
- **The Panda preset** is in the [CSS contract](css-contract.md), C25 to C27.
