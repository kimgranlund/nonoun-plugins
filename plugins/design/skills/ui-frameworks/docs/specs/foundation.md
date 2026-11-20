# Foundation

Spec 3 of 4. Accepted on 2026-11-12.

The Web Components foundation: the signals kernel, `UIElement`, `UIFormElement`, parts, behaviours, and how a component is defined. It says what each piece must do and how that will be checked. It does not hold code; the spike writes the code and the tests named here.

Terms such as root, part, behaviour, author attribute and managed attribute are defined in the [vocabulary](vocabulary.md). States and conditions are in the [state matrix](state-matrix.md).

Not in this spec: recipes and stylesheets (spec 4, the CSS contract), and the manifest schema, which is extracted from the spike.

## How to read the rules

Each rule has an id, a basis and a check. The check column names the test the rule needs. [Coverage](#coverage) says which of those tests exist and pass today. Eleven rules went beyond the decisions that existed when this spec was written. They were confirmed as D38 to D48 and are listed [at the end](#decisions-this-spec-introduced).

The platform facts this spec leans on were tested on 2026-11-12 in Chromium 156, Firefox 157 and WebKit 27.2. They are in [checks.md](../checks.md), and the form facts in [the last section there](../checks.md#check-6--forms-and-the-accessibility-tree).

## Modules

```text
signals.js              the kernel; imports nothing
element.js              UIElement; imports signals
form.js                 UIFormElement; imports element
behaviours/<name>.js    one behaviour each; imports nothing from the three above
<id>/<id>.class.js      a component class; imports element or form, and behaviours
<id>/<id>.props.js      the component's prop schema; generated from its manifest
<id>/<id>.js            defines the element; imports the class
```

| # | Rule | Basis | Check |
|---|---|---|---|
| M1 | A module shall import only from modules above it in the list. | D5; agent-ui's layering | Import-graph test |
| M2 | A behaviour shall import nothing from `signals.js`, `element.js` or `form.js`. | D12: every target mounts the same behaviours | Import-graph test |
| M3 | The foundation shall have no runtime dependencies. | B9 | The package manifest lists none |
| M4 | Source shall be JavaScript with JSDoc types that pass the TypeScript compiler's check. | D24 | `tsc --checkJs` in the spike |
| M5 | `signals.js` shall be at most 1 KB, and `element.js` with `form.js` at most 3 KB, minified and gzipped. | B9, D47 | A size test that fails over budget |

## Signals kernel

The surface is `signal`, `computed`, `effect`, `scope`, `untracked` and `settled`. A signal is read and written through `.value`, and read without subscribing through `.peek()`.

| # | Rule | Basis | Check |
|---|---|---|---|
| K1 | When a computed or an effect reads a signal's `.value`, the kernel shall subscribe it to that signal. A read through `.peek()` or inside `untracked()` shall not subscribe. | Both earlier kits | Unit test |
| K2 | When a signal is written a value that `Object.is` equal to its current one, the kernel shall notify nothing. | agent-ui | Unit test |
| K3 | A computed shall be lazy and cached. It shall recompute only when one of its sources has changed since it last ran, and an effect shall never see a computed that is out of date. | agent-ui; gen-ui-kit's kernel could run an effect once with a stale computed | Unit test with a diamond of dependencies |
| K4 | An effect shall run once, synchronously, when it is created. Later runs shall happen in a microtask, at most once per flush however many of its sources changed. | agent-ui | Unit test |
| K5 | Before an effect runs again, and when it is disposed, the kernel shall call the function its last run returned. | agent-ui; gen-ui-kit ignored the return value | Unit test |
| K6 | After each run, the kernel shall unsubscribe an effect or computed from every source it did not read in that run. | gen-ui-kit never unsubscribed | Unit test with a conditional read |
| K7 | A scope shall own every computed and effect created while it is active. When the scope is disposed, no signal shall keep a reference to any of them. | agent-ui | Leak test: after dispose, every signal reports no subscribers. Negative control: a kernel that skips K6 fails it |
| K8 | When an effect throws, the kernel shall report the error and still run the other effects of that flush. | agent-ui drops the rest of the flush | Unit test |
| K9 | When a flush has not settled after 100 rounds, the kernel shall stop it and throw an error that names the effect's owner. | Both earlier kits | Unit test with two effects that write each other |
| K10 | When a computed reads itself, the kernel shall throw. | agent-ui | Unit test |
| K11 | `settled()` shall return a promise that resolves when the current flush has finished. | agent-ui's `whenFlushed` | Used by every component test |

There is no `batch()`. K4 already groups writes made in one task. There is also no store, controller or inspection API; gen-ui-kit carries three overlapping state patterns and the port drops them.

## UIElement

### Props and attributes

A component's props come from a schema that is generated from its manifest (D13) and imported by its class. A prop has one of four types: `boolean`, `string`, `number` or `enum`.

| # | Rule | Basis | Check |
|---|---|---|---|
| E1 | For each prop, `UIElement` shall define a property on the class's prototype, backed by one signal per element. | agent-ui | Unit test |
| E2 | The attribute name of a prop shall be the prop's name in lowercase with hyphens. | N5 | Schema generator test |
| E3 | When an attribute changes, the element shall set the prop to the value parsed by the prop's type. | B11 | Unit test per type |
| E4 | When a prop changes through its property, the element shall write the attribute, and the two shall not echo each other. | S4, D39 | Unit test that counts attribute writes |
| E5 | The element shall write no attribute for a prop that holds its default value. When a property write returns a prop to its default, the element shall remove the attribute. | D39; gen-ui-kit: stamping defaults flips attribute selectors | Unit test |
| E6 | When an attribute is removed, the prop shall return to its default. | gen-ui-kit | Unit test |
| E7 | When an `enum` attribute holds a value outside the set, the prop shall take its default and the attribute shall stay as written. | D39 | Unit test |
| E8 | A property set on the element before it was defined shall be kept, and shall win over the attribute. | Both earlier kits | Test that sets a property, then defines |

E4 makes every author attribute live, not only the state attributes that S4 requires. A recipe selects variants by attribute as well, so a variant set from script has to reach the attribute too.

### Lifecycle

| # | Rule | Basis | Check |
|---|---|---|---|
| L1 | When the element connects, it shall open a connection scope and an `AbortController`, then apply E8, write its managed defaults, ensure its parts, call the component's `connected()` hook without tracking, and start its bindings. | agent-ui; gen-ui-kit's untracked `connected()` | Order test with a recording component |
| L2 | The element shall offer `effect(fn)`, `listen(target, type, handler)` and `use(behaviour, options)`. Each shall end when the element disconnects. | agent-ui | Leak test |
| L3 | When the element disconnects, it shall dispose the scope and abort the controller, and shall leave no listener and no subscriber behind. | agent-ui | Leak test: connect and disconnect 100 times, then count listeners and subscribers. Negative control: a component that calls `addEventListener` directly fails it |
| L4 | When a disconnect arrives while the element's own connect is still running, the element shall finish connecting and then tear down. | agent-ui `dom/element.ts:63-92` | Test that moves a child during its parent's connect |
| L5 | When the element connects again after a move, it shall not add a second copy of any part or managed attribute. | gen-ui-kit's move-stability test | Move test over every component |
| L6 | One frame after it first connects, the element shall write `data-ready`. | State matrix: ready | Unit test |
| L7 | A component that coordinates child components shall work whichever of them is defined first. | agent-ui: upgrade order is not insertion order | Tabs test that defines the four elements in several orders |

A binding is an effect that writes one thing: a part's text, one attribute or one ARIA value. There is no render pass, and no effect replaces an element's children (D8).

### Managed attributes

| # | Rule | Basis | Check |
|---|---|---|---|
| A1 | When it connects, the element shall write its ARIA `role` and `tabindex` only if the author wrote none. | D9 | Unit test with and without authored values |
| A2 | The element shall never change or remove `aria-label`, `aria-labelledby` or `aria-describedby`. | D9 | Unit test |
| A3 | For each state the component has, a binding shall keep the managed attribute in step with the author attribute. | S5 | Test per component |
| A4 | Only `UIFormElement` shall call `attachInternals()`. | D46; gen-ui-kit attaches on every element | Unit test: a plain component has no internals |

### Parts

| # | Rule | Basis | Check |
|---|---|---|---|
| P1 | The element shall never move, wrap or remove a child the author wrote. | D8, D40 | Test that compares the author's nodes before and after connect, by identity |
| P2 | For each part the component needs, the element shall use a child the author marked with that `data-part`, and shall create the default only when there is none. | D8, D30 | Unit test both ways |
| P3 | A part the element creates shall be added at the start or at the end of the root, as the component's manifest states. | D40 | Unit test |
| P4 | A part the element creates shall be a plain HTML element, never another component. | D41 | Import-graph test: a class imports no defining module |
| P5 | When the element looks for a part, it shall ignore parts that belong to a component nested inside it. | gen-ui-kit's ownership walk | Test with a component inside a component |
| P6 | A binding shall look a part up each time it runs and shall not keep a reference between runs. | gen-ui-kit: a cached part is lost when the children are replaced | Test that replaces a part, then changes state |

P1 means a part never wraps author content. `<ui-button>Save</ui-button>` keeps its text node as it is; a checkbox adds its mark beside the author's label text. Where a wrapper is needed, for example to truncate a label, the author writes it and marks it with `data-part`.

P4 keeps tree-shaking exact: importing a class never defines another element. A component that needs another one beside it, such as an icon in a button, gets it from the author's markup.

### Before the script has run

| # | Rule | Basis | Check |
|---|---|---|---|
| U1 | Defining a component shall not change the size or the position of its root. | B9, D43 | Layout test: measure the root's box before and after `define`, for every variant |
| U2 | A state the author set in markup shall be painted before the component is defined. | S3 | The state matrix fixtures, plus a screenshot test per component |
| U3 | The kit shall not hide a component that is not yet defined. | D43; D11: its stylesheet is already loaded | No kit stylesheet contains `:not(:defined)` |
| U4 | A component that is not yet defined is not operable. The documentation shall say so, and shall say that a form submitted before its custom controls are defined omits their values. | Platform limit | Documentation check |

gen-ui-kit hides elements until they are defined, because its styles can arrive after its script. With one stylesheet path loaded ahead of the script (D11), an undefined component is already styled and already shows its state, so hiding it would only add a flash. U1 is the rule that makes that safe: space for a part the element will create is reserved by the recipe.

## UIFormElement

Every form control that can be disabled extends `UIFormElement`, button included (D20). A root that can be disabled but holds no form value, such as a tab, extends `UIElement` (D69).

| # | Rule | Basis | Check |
|---|---|---|---|
| F1 | `UIFormElement` shall be form-associated and shall declare the props `name` and `disabled`. | D20 | Unit test |
| F2 | When a prop that feeds the form value changes, the element shall update the form value before the property setter returns. | D44; maison-ui: publish the value synchronously | Test: set the property, read `FormData` in the same task |
| F3 | The element shall report validity through `setValidity`, with itself or one of its parts as the anchor. | Check 6: on submit the form moves focus to an invalid root | Unit test |
| F4 | The element shall treat itself as disabled when its own `disabled` prop is set or when the platform reports it disabled through a fieldset. It shall never write the `disabled` attribute because of a fieldset. | gen-ui-kit `core/form.js:130-136` | Fieldset test: disable, then enable |
| F5 | The element shall mark itself as "the user is due to be told" when the user has changed it, when it loses focus after a change, or when it receives an `invalid` event. From then on it shall write `aria-invalid="true"` while it is invalid and remove it while it is valid. | D33; check 6: an invalid root receives one `invalid` event on submit | Test: untouched, changed, submitted |
| F6 | When the form resets, the element shall restore each value and state prop to what it held when it first connected, and shall clear the mark of F5. | S4; gen-ui-kit's reset snapshot | Reset test |
| F7 | When the platform restores form state, the element shall restore its value from it. | Platform feature | Unit test of `formStateRestoreCallback` |

### Activation

Space and Enter do nothing on a custom-element root unless the component handles them (check 1). The `press` behaviour does this for every component that can be activated.

| # | Rule | Basis | Check |
|---|---|---|---|
| F8 | While the root is not disabled, `press` shall activate it on Enter at key down and on Space at key up, and shall prevent the default action of both. | D45; agent-ui: an unprevented Enter lands on whatever takes focus next | Keyboard test in three engines |
| F9 | While Space or Enter is held, `press` shall keep `data-active` on the root. | S9, D35 | Keyboard test |
| F10 | Activation shall dispatch one `click` event. A pointer click and a label click already do. | Check 1: label activation dispatches `click` on a form-associated root | Test that counts `click` events from pointer, keys and label |

### Submitting

| # | Rule | Basis | Check |
|---|---|---|---|
| F11 | A button whose `type` is `submit` shall have a part named `submit`: a native `<button type="submit">` that is hidden and out of the tab order. | D19 | Unit test |
| F12 | The button shall keep that part's `name`, `value` and disabled state equal to its own. | Check 6 | Unit test |
| F13 | When the button is activated, it shall call `requestSubmit` on its form with that part. | Check 6: the form then has a submitter and the data carries the button's name and value | Form test in three engines |
| F14 | The button shall not set a form value of its own. | Check 6: otherwise the name would be submitted twice | Form test |
| F15 | A button whose `type` is `reset` shall reset its form when activated. | Native button behaviour | Form test |

### The form tests of D18

Button and checkbox must pass all of these in three engines before the core set starts:

1. Clicking a submit button submits; the `submit` event has a submitter; the data holds the button's name and value once.
2. Pressing Enter in a text input submits a form that has two inputs and a custom submit button.
3. A disabled submit button blocks both.
4. A checked checkbox contributes its name and value; an unchecked one contributes nothing.
5. Resetting the form restores the checkbox to its first state.
6. Clicking a `<label for>` toggles the checkbox and focuses it.
7. Disabling a surrounding fieldset disables both, and enabling it again enables both.
8. A required, unchecked checkbox blocks submission, receives focus, and from then on is invalid in the state matrix's sense.

## Behaviours

| # | Rule | Basis | Check |
|---|---|---|---|
| B1 | A behaviour shall be a function that takes a root and an options object and returns a cleanup function. | D12 | Type check |
| B2 | A behaviour shall take a value that can change as a function in its options, not as a signal. | M2 | Type check |
| B3 | After its cleanup has run, a behaviour shall have left no listener and no observer. | D12 | Leak test per behaviour |
| B4 | A behaviour shall write only the managed attributes its documentation lists, and no author attribute. | D9 | Test per behaviour |
| B5 | A component shall mount a behaviour through `use()`, never by copying its logic. | gen-ui-kit's components hand-roll what its traits already do | Review; the manifest lists each behaviour a component uses, and a test checks the import exists |

The spike needs four: `press`, `rovingFocus`, `dismiss` and `typeahead`. All four exist. Positioning needs no behaviour for basic placement (check 4).

### Roving focus

`rovingFocus` makes a set of items one stop in the Tab order. It is mounted on the element that holds the items: a tab list today; a toolbar, a menu or a radio group later. These five rules were written with the tabs; the decision behind them is D70.

| # | Rule | Basis | Check |
|---|---|---|---|
| B6 | `rovingFocus` shall keep one item that can take focus in the Tab order, with `tabindex="0"`, and every other such item out of it, with `tabindex="-1"`. | APG: roving tabindex; ui-interaction-dev `focus.one-stop` | Keyboard test in three engines |
| B7 | While focus is inside the root, that one item shall be the item that has focus. While focus is outside, it shall be the item the component names as current, when it names one. | APG tabs: Tab lands on the selected tab | Keyboard test |
| B8 | The arrow keys of the root's orientation shall move focus to the next or the previous item and wrap at the ends, and in a horizontal root they shall follow the writing direction. Home and End shall move focus to the first and the last item. The behaviour shall prevent the default action of a key that moved focus and shall leave every other key alone, a key whose default action another handler has already prevented among them: the component that mounts it can then take a key for itself without hiding it from the page (D111). | APG | Keyboard test, with a root that runs right to left |
| B9 | An item the component tells it to skip, such as a disabled tab, shall have no `tabindex` and shall take no focus from the keys. | Without a tabindex a click does not focus it either | Keyboard and pointer test |
| B10 | When an item is added, is removed or changes a watched attribute, the behaviour shall bring the tabindex values up to date without being called, and shall write an attribute only when its value differs. | D70, D12: a behaviour returns only its cleanup, so the DOM is its source | Test that adds and removes items, and one that counts attribute writes |

### Dismissal and typeahead

`dismiss` tells a component when the user wants an open layer closed; the component closes it. `typeahead` hands a component the item that matches what the user types; the component moves to it. Both were written with the menu button.

| # | Rule | Basis | Check |
|---|---|---|---|
| B11 | When Escape is pressed inside the root of an open layer, `dismiss` shall ask the component to close it, and shall stop the event so that no layer around it closes as well. | ui-interaction-dev `overlay.escape-innermost` | Keyboard test in three engines |
| B12 | When a pointer goes down outside the root, `dismiss` shall ask the component to close the layer. A press on an element the component names, such as the button that opened the layer, shall be left to the component. | A press on the opener has to reach it as one click, which closes the layer | Pointer test |
| B13 | When focus moves from the root to an element outside it, `dismiss` shall ask the component to close the layer. | APG menu: Tab closes the menu | Keyboard test, forwards and backwards |
| B14 | When a printable key is pressed inside the root, `typeahead` shall hand the component the next item whose text starts with what was typed, whatever its case. The same letter typed again shall step through the items that start with it. What was typed shall be forgotten after a pause. | APG menu and listbox | Keyboard test |
| B15 | `typeahead` shall prevent the default action of a key that found an item. It shall leave alone Space, a key pressed with Control, Alt or Meta, and a key that found no item. | Space activates an item | Keyboard test |

### Active descendant

`activeDescendant` is the other way to move among items: focus stays on the root, or on a text field that drives the list, and one item is marked as highlighted. A listbox uses it, and a combobox will. The decision behind it is D90.

| # | Rule | Basis | Check |
|---|---|---|---|
| B16 | `activeDescendant` shall keep at most one item highlighted: that item has `data-highlighted`, and the element that has focus names its id in `aria-activedescendant`. It shall give an item an `id` only when the item has none, and write no other attribute. | State matrix: highlighted; APG: managing focus with aria-activedescendant | Test that counts attribute writes |
| B17 | ArrowDown, ArrowUp, Home and End, pressed on the element that has focus, shall move the highlight among the items that are not skipped, and prevent the key's default action. Whether the arrows wrap is the component's choice. The highlighted item shall be scrolled into view. | APG listbox | Keyboard test in three engines |
| B18 | The component shall be able to set the highlight by writing `data-highlighted` on an item, and the behaviour shall then bring `aria-activedescendant` and the other items in step. When the highlighted item is removed or becomes skipped, the highlight shall move to an item the component names, or be cleared. | D70: the DOM is a behaviour's source | Test that writes the attribute, and one that removes the item |

### Focus in a grid

`gridFocus` is roving focus in two directions, for a grid and a treegrid.

| # | Rule | Basis | Check |
|---|---|---|---|
| B19 | `gridFocus` shall keep one cell of the grid in the Tab order and every other cell out of it. The arrow keys shall move focus one cell and stop at the edges; Home and End go to the ends of the row, with Control to the corners of the grid; PageDown and PageUp move by a number of rows the component gives. It shall prevent the default action of a key that moved focus. | APG grid | Keyboard test in three engines |
| B20 | The component gives the rows, and for each row its cells, as functions read again at every event. A cell that holds exactly one focusable control shall be represented by that control, unless the control takes text or uses the arrow keys itself; such a cell, and a cell with several controls, is represented by itself and entered as J79 says. When rows or cells are added, removed or hidden, the behaviour shall keep one stop without being called, and write an attribute only when it differs. | D70, B10 | Test that hides a row and removes a cell |

## Coordinating components

Some patterns are several components that work as one: a tabs element, its tab list, the tabs and the panels. One of them coordinates the others. These rules were written with the tabs, and the decisions behind them are [D65 to D72](#decisions-the-tabs-introduced). G1 to G6 hold for any such component; G7 to G9 are the tabs' own.

| # | Rule | Basis | Check |
|---|---|---|---|
| G1 | A component that coordinates others shall find them by their ARIA role, among its descendants that belong to no component of its own kind nested inside it. Its class shall name no tag. | D66; R3; D17: the other targets have the same roles and no tags | Test with tabs nested in a panel |
| G2 | It shall bring the others up to date when one of them is added, is removed or is defined later, with no call from that component. | L7; agent-ui: upgrade order is not insertion order | Tests that define the elements in several orders, and that add and remove a tab |
| G3 | It shall set a state on another component through that component's own author attribute, and shall write an attribute only when its value differs. | D67, D39; an observer then sees nothing when nothing changes | Test that counts attribute writes once the elements have settled |
| G4 | It shall give another component an `id` only when that component has none, and shall name a panel after its tab only when the author gave the panel no name. | D68, A2; ARIA relations are made of ids | Test with and without authored ids and names |
| G5 | When the user changes the selection, it shall write the others' author attributes before it dispatches `change`. It shall dispatch nothing when a script changes the value. | D44's reason: a listener reads the result in the same task. A managed attribute such as `aria-selected` follows in its own binding, a microtask later, as on every component | Test that reads the tabs and panels inside the listener |
| G6 | When a script or the author marks one of the others as selected, it shall take that component's value as its own. | D39: every author attribute is live | Test that sets `selected` on a tab |
| G7 | With `activation="automatic"`, the tabs element shall select a tab when the tab takes focus. With `activation="manual"`, it shall select a tab only when the tab is activated. | D71; APG tabs: both are allowed, and automatic is recommended when the panels are already in the page | Keyboard test in three engines |
| G8 | A disabled tab shall not be selected by the pointer, by a key or by focus. | State matrix: disabled | Pointer and keyboard test |
| G9 | The tabs element shall show the one panel whose value is the selected tab's, and hide the others. With no value written, it shall select the tab the author marked as selected, or else the first tab that is not disabled. A value that names no tab shall select no tab and show no panel. | APG tabs | Test of each case |

## Defining

| # | Rule | Basis | Check |
|---|---|---|---|
| R1 | Importing `<id>.class.js` shall define no element and have no other side effect. | B14; gen-ui-kit's split | Bundle test: importing one class adds no other class to the bundle |
| R2 | Importing `<id>.js` shall define the element under its tag, and shall do nothing if that tag is already defined. | gen-ui-kit's `defineIfFree` | Unit test that imports twice |
| R3 | The tag shall appear only in `<id>.js` and in the recipe, so that the kit prefix can be changed when the files are copied. | D23 | Copy test with another prefix |
| R4 | There shall be no module that re-exports several components. | B14 | Repository check |

## Coverage

Which rules have a check that runs today. A test names the rule it covers at the start of its title, and this table is generated from those titles by `node scripts/docs.mjs`.

<!-- generated:coverageTotal:start -->
99 of 100 rules have a check that runs today. U4 waits for what it describes.
<!-- generated:coverageTotal:end -->

<!-- generated:coverage:start -->
| Rules | Checked | Not yet |
|---|---|---|
| Modules (M1 to M5) | M1, M2, M3, M4, M5 · 4 tests | none |
| Signals kernel (K1 to K11) | K1, K2, K3, K4, K5, K6, K7, K8, K9, K10, K11 · 15 tests | none |
| Props and attributes (E1 to E8) | E1, E2, E3, E4, E5, E6, E7, E8 · 10 tests | none |
| Lifecycle (L1 to L7) | L1, L2, L3, L4, L5, L6, L7 · 89 tests | none |
| Managed attributes (A1 to A4) | A1, A2, A3, A4 · 38 tests | none |
| Parts (P1 to P6) | P1, P2, P3, P4, P5, P6 · 44 tests | none |
| Before the script has run (U1 to U4) | U1, U2, U3 · 54 tests | U4 |
| UIFormElement (F1 to F15) | F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15 · 96 tests | none |
| Behaviours (B1 to B20) | B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20 · 118 tests | none |
| Coordinating components (G1 to G16) | G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, G11, G12, G13, G14, G15, G16 · 221 tests | none |
| Defining (R1 to R4) | R1, R2, R3, R4 · 5 tests | none |
<!-- generated:coverage:end -->

How to run them. The last argument of each is the path of any project whose `node_modules` holds that tool.

```bash
node --test kit/foundation/
```

```bash
node tests/run.mjs <project-with-playwright>
```

```bash
node tests/mutate.mjs <project-with-playwright>
```

```bash
node tests/size.mjs <project-with-esbuild>
```

`tests/mutate.mjs` is the negative control for the tests themselves: it breaks one rule at a time in a copy of the source and fails if the tests still pass.

### The gate of D18

All eight form tests pass in Chromium 156, Firefox 157 and WebKit 27.2, on the real button and checkbox, with the browser's own keyboard and pointer. They are in `tests/browser/d18.test.js`. No exception to B10 was needed beyond the two already decided: the native input of D1 and the native submit part of D19.

## Decisions this spec introduced

All eleven were confirmed on 2026-11-12 and are recorded in [decisions.md](../decisions.md).

| # | Decision | Why |
|---|---|---|
| D38 | The kernel has no `batch()`. An effect runs once when created, then at most once per microtask flush (K4). | Deferred effects already group writes. One less concept in a kernel meant to be minimal. |
| D39 | Every author attribute is live, and a prop at its default writes no attribute (E4, E5). | Recipes select variants and states by attribute. A stamped default would change which selectors match. |
| D40 | A part never wraps, moves or removes author content. A created part sits at the start or end of the root (P1, P3). | It is the only reading of D8 under which a framework or an author can own the children without a fight. |
| D41 | A created part is a plain HTML element, never another component (P4). | Importing a class then defines nothing else, so tree-shaking is exact. |
| D42 | A component's prop schema is a generated file, `<id>.props.js`, with four prop types (E1). | D13 makes the manifest the source. The whole manifest is too large to ship to the browser. |
| D43 | The kit does not hide undefined components; instead, defining one must not move or resize its root (U1, U3). | With styles loaded first, an undefined component already looks right. |
| D44 | The form value is updated synchronously in the property setter (F2). | Effects run in a microtask. A form read in the same task would otherwise see the old value. |
| D45 | `press` is a behaviour: Enter activates at key down, Space at key up (F8). | It matches a native button, and every activatable component needs it. |
| D46 | Only `UIFormElement` attaches `ElementInternals` (A4). | D9 keeps ARIA in attributes, so a plain component has no use for internals. |
| D47 | Size budgets: 1 KB for the kernel, 3 KB for the two base classes, minified and gzipped (M5). | "Minimal" needs a number to be checkable. agent-ui's whole button family is 4.4 KB. |
| D48 | The per-component files are `<id>.class.js`, `<id>.js`, `<id>.props.js`, `<id>.css` and `<id>.manifest.json`. | This settles the file split the plan still marks as proposed, and adds the generated schema. |

### The menu button

A menu button is three components: the menu button element, which coordinates; the menu; and the menu items. Its trigger is a button the author puts inside it: the kit's button, or any element with the button role. The decisions behind these rules are [D75 to D79](#decisions-the-menu-button-introduced).

| # | Rule | Basis | Check |
|---|---|---|---|
| G10 | The menu button element shall find its trigger and its menu by role: the menu is the element with the menu role, and the trigger is the first element with the button role that is not inside the menu. It shall write `aria-haspopup="menu"`, `aria-controls` and `aria-expanded` on the trigger, and shall name the menu after the trigger when the author gave the menu no name. | APG menu button; D66, D68 | Test with the kit's button and with a native button as the trigger |
| G11 | A click on the trigger, and so Enter and Space, shall open the menu when it is closed and close it when it is open. ArrowDown on the trigger shall open the menu with focus on its first item, and ArrowUp with focus on its last. | APG menu button | Pointer and keyboard test in three engines |
| G12 | When a menu opens it shall move focus to its first item that is not disabled. Inside it, the up and down arrows, Home and End shall move focus among the items and wrap; a typed letter shall move focus to the next item that starts with it; and the pointer moving over an item shall move focus to that item. | APG menu; ui-interaction-dev `hover.one-highlight` | Keyboard and pointer test |
| G13 | Activating an item, by a click, Enter or Space, shall dispatch one `click` on the item and close the menu. A disabled item shall take no focus, and a click on it shall not close the menu. | APG menu | Test that counts `click` events |
| G14 | Escape, and the activation of an item, shall close the menu and return focus to the element that had focus when it opened. A press outside the menu, and focus that leaves it, shall close it and leave focus where the user put it. | APG; the platform's popover and dialog do the same | Keyboard and pointer test |
| G15 | A menu shall be showing exactly while it has the `open` attribute. It shall show itself in the top layer when the attribute is added, by a script or by the menu button, and hide itself when it is removed. If something else hides it, it shall remove the attribute. | D36, D67 | Test that sets the attribute, and one that calls `hidePopover()` |
| G16 | A closed menu shall take no room and show nothing, before and after it is defined. An open menu shall sit below its trigger with their start edges aligned, and be no narrower than the trigger. Where it does not fit below, it shall sit above. | U1, U2; check 4 | Layout test in three engines |

## Decisions the tabs introduced

The tabs were the first pattern made of several components, and they needed choices that no earlier decision covered. This spec first listed them as Z1 to Z10. All ten were confirmed on 2026-11-13 and are recorded in [decisions.md](../decisions.md).

| # | Decision | Why |
|---|---|---|
| D65 | A pattern made of several ARIA roles is several components: one per role, each with its own five files and its own manifest. Tabs are four: tabs, tab list, tab, tab panel. A manifest names the others under `family`. | D9 makes each root the element that carries its role. A light-DOM tab list cannot be a created part, because a part never wraps author content (D40). |
| D66 | A coordinating component finds the others by ARIA role and watches its subtree with a `MutationObserver`. The others do not register with it (G1, G2). | One mechanism covers every definition order, late children and removals. A class can then name no tag (R3). |
| D67 | A coordinating component sets state through the other component's author attribute: `selected` on a tab, `hidden` on a panel. `value` on the tabs element and `selected` on a tab are kept in step both ways (G3, G6). | The author's markup then paints the state before anything is defined (U2), and a script may use either attribute. |
| D68 | A tab and a panel pair by `value`. One with no `value` attribute has its position as its value, so tabs and panels written in the same order need no values. | The shortest markup works, and ids stay the component's business (G4). |
| D69 | A root that can be disabled but holds no form value, such as a tab, extends `UIElement`. The sentence "every root that can be disabled extends `UIFormElement`" then holds for form controls only. | A tab is not a form control: it should not appear in `form.elements` or be disabled by a fieldset. The tabs element and the behaviours guard a disabled tab themselves. |
| D70 | `rovingFocus` keeps itself up to date with a `MutationObserver` (B10). | A behaviour returns only its cleanup (B1), so the component has no way to call it again. |
| D71 | Tabs select on focus unless the author writes `activation="manual"` (G7). | APG recommends it when the panels are already in the page, which they are here. |
| D72 | `orientation` is an attribute of the tab list, where ARIA puts it. The tabs element does not yet lay out a vertical list beside its panels. | A recipe may size its root from that root's own author attributes only (C17), so the tabs element cannot read the list's orientation. |
| D73 | A hover, active or variant token falls back to the base public token only when the component has one (C7). A tab has no face at rest, so `--tab-face-hover` stands alone. | ui-materials gives a tab no face at rest, and a recipe may not write a literal `transparent` (D59). |
| D74 | The lint asks for a focus ring only on a root that takes focus (C20), and for a forced-colours block only in a recipe that paints (C19). An item inside a tray draws its ring inside itself. | The tabs element takes no focus and paints nothing. ui-geometry gives a hosted item an inset ring, because an outer ring would overlap its neighbours. |

## Decisions the menu button introduced

The menu button is the kit's first overlay. This spec first listed its choices as Q1 to Q5. All five were confirmed on 2026-11-13 and are recorded in [decisions.md](../decisions.md).

| # | Decision | Why |
|---|---|---|
| D75 | A menu button is three components: menu button (it coordinates and has no role), menu and menu item. The trigger is a button the author writes inside the menu button: the kit's button, or any element with the button role. | D65. The button already has the variants, the disabled state and the form behaviour a trigger needs, so there is no second button to keep in step. |
| D76 | Focus moves to the menu's items, with roving focus. The pointer moves focus too, so a menu has one marked row, and the row is painted on the `focus` condition. The state matrix's `highlighted` is kept for an option whose list keeps focus elsewhere, and no longer lists the menu item. | Roving focus exists and is tested, and real focus is the most widely supported way to tell a screen reader where the user is. |
| D77 | A menu is a `popover="manual"` element. The top layer shows it, CSS anchor positioning places it, and the `dismiss` behaviour closes it. The anchor is the menu button element, whose name is scoped to it with `anchor-scope`, so no script and no id takes part in placement. | Check 4: a custom trigger cannot use the declarative popover attributes, and with `popover="auto"` a press on the trigger would close the menu and its click would open it again. |
| D78 | `open` on the menu is its author attribute, and the menu button opens and closes the menu through it. The menu remembers the element that had focus when it opened and returns focus there on Escape and when an item is activated. | D67. The menu then works with any opener, not only inside a menu button. |
| D79 | The menu button writes the pattern's ARIA on the trigger directly (`aria-haspopup`, `aria-controls`, `aria-expanded`), because the button has no `expanded` attribute of its own. | These three belong to the pattern, not to a button. The trigger's paint does not change while its menu is open; ui-materials asks for none. |

## Open

- **Healing.** If an author replaces a root's children, created parts are gone until the next state change (P6). agent-ui repairs this with a `MutationObserver` in 19 controls. The spike should show whether the kit needs that at all.
- **`aria-disabled` on a form-associated root.** Check 6 shows Chromium already exposes such a root as disabled without it. Firefox and WebKit are not tested, so the state matrix keeps the attribute for now.
- **Moves that keep state.** Settled in the spike: `UIElement` defines `connectedMoveCallback`, so `Element.moveBefore()` moves an element without a teardown where the browser has it (Chromium and Firefox; not WebKit 27.2). L5 covers a plain move everywhere.
- **A disabled root that is not a form control.** The platform keeps the pointer, a label and `click()` away from a disabled form-associated root. A tab has none of that (D69): the tabs element ignores a disabled tab and roving focus passes over it, but a listener the author adds to the tab still receives `click`.
- **Observers.** The tabs element and `rovingFocus` each watch a subtree with a `MutationObserver` (D66, D70). Both write an attribute only when it differs, and tests count the writes. A third coordinating component should show whether the two observers belong in one shared behaviour.
- **A menu written open in markup.** It shows before anything is defined, as U2 asks. Focus moves to its first item only if the items are defined by the time the menu is; otherwise the user's first key or pointer move does it.
- **Rows below the pointer floor.** Settled by D96: at compact density ui-geometry makes a menu row and a tab 22px tall, and the token generator holds both at the 24px pointer target until ui-geometry has a taller compact row.
- **Events.** Which events each component dispatches belongs to its manifest. The working assumption is that a control that holds a value dispatches `input` and `change` under their native names.
- **The size budgets** are a first estimate. The spike measures them.
