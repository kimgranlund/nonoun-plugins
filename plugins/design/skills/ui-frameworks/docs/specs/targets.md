# Framework targets

Spec 8. Written on 2026-11-13 for the first target after the Web Components: React. It says what a framework target renders, where its files live and how it is proved equal to the Web Components target. Svelte and Solid follow the same rules when they are built.

A target is one framework (B2). It shares the manifests, the recipes, the tokens and the behaviours with the Web Components (D12, D13, D16, D17) and is not a wrapper around them.

## The proof set

React was built first for the four families of the spike: button, checkbox, tabs (tabs, tab list, tab, tab panel) and menu button (menu button, menu, menu item). They hold a form control, a coordinating composite and an overlay, which is what the contract has to carry (D98). Every other component followed on 2026-11-14, by family, to authoring-react.md (D112). The ten style-only recipes have no React component: their root is a native element with `data-ui` in every target.

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
| switch | `label` | Holds a native `input type="checkbox" role="switch"` marked `data-part="input"`; the native input reports the checked state, so the root carries no `aria-checked` |
| radio group | `div` with `role="radiogroup"` | Gives its radios one `name`; after `rovingFocus` moves focus it clicks the native radio, so the browser's own check and events follow |
| radio | `label` | Holds a native `input type="radio"` |
| disclosure, accordion | `div` | `open` is the author attribute on the root |
| breadcrumb | `nav` | |
| alert | `div` with `role="alert"` | |
| meter, progress | `div` with the role | The share goes to the recipe through `style`; a progress with no value renders no `value` attribute |
| icon | `span` | The icon sheet gives each glyph on `[data-ui="icon"][name]` as well as on the custom element |
| toolbar, menubar | `div` with the role | The menubar opens the next menu by a click on its trigger |
| menu group, checkable items | `div` with the role | A group reaches its radio items through context |
| submenu | `div` | |
| listbox, option | `div` with the role | The listbox renders one hidden input per submitted value; neither renders an attribute a holder writes |
| combobox | `div` | Around the author's input and popup |
| select | `div` with `role="combobox"` | Renders the value part and a hidden input |
| tree, tree item | `div` with the role | Level is rendered from context; set size and position are written after render |
| tooltip, popover | `span` | The content and the control are the author's children, found in the DOM |
| dialog | `div` | Around the author's native `dialog` panel |
| toast | `div` with `role="status"` or `alert` | |
| toaster | `div` with `role="region"` and `popover` | |
| text field | `span` | Around the author's input |
| form field, file field | `div` | Around the author's label and control, or file input |
| tag group | `div` with `role="group"` | |
| slider | `div` with `role="slider"` | Renders a hidden input |
| range slider | `div` with `role="group"` | Renders two `span` thumbs and two hidden inputs |
| spinbutton | `span` | Around the author's input; renders the two buttons |
| splitter | `div` | Renders the bar with `role="separator"` |
| grid | `div` | Around the author's native `table`; the treegrid's keys run in the capture phase, ahead of `gridFocus` |
| feed | `div` with `role="feed"` | |
| carousel | `div` with `role="region"` | |
| calendar | `div` with `role="group"` | Renders a hidden input; its keys run in the capture phase, ahead of `rovingFocus`; takes `today` as a prop; watches `value`, `min` and `max` written on its root by a holder |
| date field | `span` | Around the author's input and popup; renders a hidden input and the toggle; hands the calendar it finds in the popup `value`, `min` and `max` as attributes |

## Rules

| # | Rule | Basis | Check |
|---|---|---|---|
| X1 | A root shall be the native element the table gives and carry `data-ui="<component id>"`. A variant shall be the attribute `data-<variant name>`. A part shall be marked `data-part` with the manifest's name. | C23, D17 | Parity test |
| X2 | A state shall be written in a form its condition in `references/states.json` already selects: the native attribute or pseudo-class where the root has it, otherwise the ARIA attribute where the role of the root allows it, otherwise the author attribute, and `data-focus-visible`, `data-hover` or `data-active` on a root whose focus, hover or press happens on a part. No recipe and no condition shall change for a target. | D26, D62 | Parity test; the recipes are the rewritten ones, byte for byte |
| X3 | A target's recipe shall be the Web Components recipe rewritten by `scripts/rewrite-recipe.mjs` and nothing else, written to `kit/<target>/<id>/<id>.css` by `node scripts/targets.mjs`, which also writes `kit/<target>/styles/kit.css`. With `--check` it writes nothing and fails when a file is stale. | C24, D62 | Generator check; Node test |
| X4 | A component shall mount the behaviours its manifest lists, the same functions the Web Components call, in an effect whose cleanup is the behaviour's cleanup. It shall copy none of their logic. | D12 | Mutation: a behaviour is not mounted |
| X5 | A component's props shall be the manifest's attributes, in camel case, with the defaults and the enum values read from the generated `<id>.props.js`. A value the component holds shall be controlled (`checked` with `onChange`) or uncontrolled (`defaultChecked`), as React's own inputs are. Events of the manifest are `on<Name>` props. Any other prop goes to the root. | D13 | Test per component |
| X6 | A component shall be a plain JavaScript module with JSDoc types that calls `createElement`, needs no build step and imports only `react` and `react-dom`, the behaviours, its own props, another component of its family (for the family's context), and a module of pure routines both targets read, `kit/components/<id>/<id>.<word>.js`, never a class (D113). One component per file, `kit/react/<id>/<id>.js`, with a named export in Pascal case. No barrel file. | B14, D24 | Size test; import test |
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

## What the full build found

Built on 2026-11-14: the other 40 components, each with a report in reports/ named `react.<family>.md`. What holds for all of them:

- **Another family is reached through the DOM.** A combobox, a select, a date field, a menubar and a toaster find the components they hold by role and write on them what their manifests say. The held component renders none of those attributes, so React never undoes a holder's write. X6 needed no exception for it.
- **A component's own keys run before the behaviours when they must win.** React hears a bubbling `onKeyDown` at its root container, after a behaviour's native listener on the component. The treegrid, the listbox, the combobox, the select and the calendar therefore take their keys in `onKeyDownCapture` and prevent the default, which `rovingFocus` and `gridFocus` pass over (D111).
- **What a component writes on the author's parts appears after hydration:** roles, ids and ARIA on a content part, a panel, a label or a control. None of it paints. A state that only the top layer gives (an open dialog, menu or popup) is closed in server markup.
- **What only `ElementInternals` gives is not built:** a form control with no native control renders a hidden input for its name and value, so `required` on a listbox, a select, a slider or a calendar is `aria-required` and blocks no submit; there is no restored form state, and a `label for` does not focus a `div` root. The switch, the radio, the spinbutton, the text field and the date field keep the browser's own validity, through their native input.
- **Events are props.** `onChange(value, event)` and the like are called; no DOM `change` is dispatched from a root that is not a native control, except where another family has to hear it (the calendar, the tag group's `remove`, the popover's `toggle`, the toast's `close`).
- **Parts a component renders cannot be renamed:** the thumbs of a range slider, the bar of a splitter, the buttons of a spinbutton and the toggle of a date field carry fixed names.

## Svelte

Svelte is the second framework target (D119). X1 to X3 and X8 to X11 hold for it as they are written, with `kit/svelte` for `kit/react`: the same roots as the table above, the same forms of each state, the same rewritten recipes and the same parity with the Web Components. X4 to X7 are React's; Svelte has these in their place.

| # | Rule | Basis | Check |
|---|---|---|---|
| V1 | A component shall be one file, `kit/svelte/<id>/<id>.svelte`, for Svelte 5 in runes mode, with `<script lang="ts">` and no `<style>` block. It shall import only `svelte` and its subpaths, the behaviours, its own generated props, another component of its family, its family's context module (`<id>.context.js` or `<id>.context.svelte.js`, beside the coordinating component), and a module of pure routines (D113). No barrel file. | B14, D24, D119 | Node test |
| V2 | A component's props shall be the manifest's attributes, in camel case, read with `$props()`, with the defaults and the enum values from the generated `<id>.props.js`. A value the component holds shall be `$bindable`, so `bind:checked` controls it and a plain `checked` only starts it. An event of the manifest shall be a callback prop in lower case, `on<name>`, called with the value and the DOM event; the DOM shall already show the new state when it is called. Children are the `children` snippet. Any other prop goes to the root. One exception: the tab has no `selected`, because the server cannot honour it; the tabs element's `value` chooses the tab (D121). | D13, D121 | Node test; test per component |
| V3 | A component shall mount the behaviours its manifest lists, the same functions, in an effect or an attachment that returns the behaviour's cleanup. It shall copy none of their logic and add no native key listener: its own keys go through `onkeydown`, or `onkeydowncapture` where they must run before a behaviour. | D12, D111 | Node test; mutation: a behaviour is not mounted |
| V4 | A family shall coordinate through Svelte context, whose key and types live in the family's context module. A component of another family shall be found in the DOM by its role, and a component shall not render an attribute another component writes on it. | D112 | Behaviour test |
| V5 | Ids shall come from `$props.id()`. `data-ready` shall be written one frame after mount. | U1, U2 | Parity test |
| V6 | A form control with no native control of its own shall render a native `input type="hidden"` part with its name and value. | D112 | Behaviour test |
| V7 | `render` from `svelte/server` followed by `hydrate` shall report no warning and no error, and the server markup alone shall be painted as the hydrated one is. | D17, U1, U2 | Parity test in three engines |

A Svelte component is source for the project's own Svelte compiler; a Svelte project always has one, so "no build step" (B14) means here that the kit adds none of its own. The tests compile each file as it is served and render on the server in Node (`tests/serve.mjs`).

```text
kit/svelte/<id>/<id>.svelte   the component
kit/svelte/<id>/<id>.css      the recipe, generated
kit/svelte/styles/kit.css     every built Svelte recipe behind the shared sheets, generated
tests/browser/svelte.<family>.test.js
tests/browser/svelte/<family>.<word>.svelte    fixtures: a snippet can only be written in a .svelte file
tests/mutations/svelte.<family>.mjs
```

### What the Svelte proof found

Built on 2026-11-15: the same nine components as React's, with a report each in the reports folder named `svelte.<family>.md`.

- **The server renders in one pass.** A component cannot know its later children while it renders its earlier ones. A tab marked `selected` after an enabled tab was rendered selected on the server only when the tabs element had a `value`, which is why the Svelte tab lost that prop (D121); `aria-controls` names the generated panel id until the browser corrects it; with every tab disabled and no value, no tab is selected. All three hold in the browser.
- **Position is creation order.** A tab or panel with no `value` takes the order in which it was created, which is document order on the server and at mount. One inserted later between others needs a `value`.
- **Svelte repairs server markup that differs and reports nothing.** V7 is therefore held by comparing the markup straight after hydration with the server's, as the browser parses it.
- **An attachment runs during hydration,** so code that writes the DOM when it mounts goes in an effect; an attachment is for a behaviour that only listens.
- **`$derived` keeps its first value on the server,** so a value that later children change is read through a function.
- **The menu and the menu item held only what the menu button needs** until the menu's other families were built, the same day.
- **Not checked:** a project's own Svelte build (SvelteKit or Vite), `bind:ref` on each root, and function bindings.

### What the full Svelte build found

Built on 2026-11-15: the other 40 components, each with a report named `svelte.<family>.md`. What holds for all of them:

- **There is no controlled mode.** React's controlled value is `bind:`; its `default…` is a plain prop, which only starts the component. An owner that refuses a change is a function binding whose setter keeps its value; the callback is then not called, where React calls it as the ask.
- **A parent's new props reset an unbound value,** even an equal one, when they arrive as one spread. A value the user chose is kept by `bind:`.
- **What the server cannot know, it leaves out.** A select's chosen text is blank until hydration, with its box at full height (D121). A tree item has no `aria-expanded` until it knows it has a group. A combobox around a disabled input paints enabled unless its root is given `aria-disabled`. A tabs element with no `value` selects the first tab that is not disabled.
- **An effect that mounts a behaviour mounts it inside `untrack`,** and an effect that sets something up on the root reads `ref` inside `untrack`. Without either, the set-up runs again at every change it happened to read.
- **A holder writes on another family as in React.** The listbox, the option and the calendar render none of the attributes a combobox, a select or a date field writes on them.
- **A Svelte parent does not render again when only its children change,** so a toast tells its toaster to look again through the family's context module; the toaster still decides from the DOM.
- **A page's change to the author's markup is seen a microtask later,** by an observer, not in the same task as in React.
- **`all: unset` on a native button root took the raise C20 gives a part holding focus;** `native.css` gives it back, for React and Svelte alike.
- **Not checked:** a SvelteKit or Vite build. `node tests/svelte-build.mjs` compiles every component for production, bundles it for the browser and renders it on the server, with nothing installed.

The proof set is the same nine components as React's; every other component followed the same day. How to build one is in authoring-svelte.md.

## Not in this spec

- **Solid 2.0** cannot be built here: the only Solid at hand is 1.9 (D99).
- **The Panda preset** is in the [CSS contract](css-contract.md), C25 to C27.
