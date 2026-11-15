# Decisions

Design decisions for the UI-kit skill. D1 to D84 were put to the author and confirmed: D1 to D48 on 2026-11-12, and D49 to D84 on 2026-11-13. From D85 on, the session decided under the author's standing instruction of 2026-11-13 to complete the work without stopping for confirmation; the author can reopen any of them. D54 was amended on 2026-11-13, and the author confirmed the amendment.

- D1 to D8 as answers to the first planning forks.
- D9 to D18 after the prior-art study. They were first written as proposals P1 to P10.
- D19 to D21 after the outside checks. They were first written as proposals P11 to P13.
- D22 to D28 as answers to the open questions that stood before the specs.
- D29 to D37 with the first two specs. The vocabulary spec first listed them as V1 to V3 and the state matrix as M1 to M6.
- D38 to D48 with the foundation spec, which first listed them as X1 to X11.
- D49 to D62 with the CSS contract, which first listed them as Y1 to Y14.
- D63 and D64 during the spike, on reading the sibling skill `ui-interaction-dev`.
- D65 to D74 with the tabs, the first pattern made of several components. The foundation spec first listed them as Z1 to Z10.
- D75 to D79 with the menu button, the first overlay. The foundation spec first listed them as Q1 to Q5.
- D80 to D84 with the manifest schema and the registry, extracted from the spike. The manifest spec first listed them as W1 to W5.
- D85 to D88 with the icon contract, and D89 with the changes that let several families be built at once. Decided by the session.

Each renumbered entry keeps its old id. Brief ids (B…) refer to [the brief](plan.md#the-brief). The evidence is in [prior-art.md](prior-art.md) and [checks.md](checks.md).

| Id | Decision |
|---|---|
| D1 | Text entry may use a native `<input>` |
| D2 | React, Svelte and Solid get native implementations |
| D3 | Distribution is a copy-in registry |
| D4 | Manifests record material attributes; styles ship Flat |
| D5 | A fresh foundation that ports from the earlier kits |
| D6 | The browser floor is current evergreen |
| D7 | The core set is the APG patterns plus three |
| D8 | Parts, not a template engine |
| D9 | ARIA role and states are real attributes on the root |
| D10 | Component tokens split into public and private |
| D11 | One CSS delivery path, layered inside each file |
| D12 | Shared behaviours are plain DOM functions, used by every target |
| D13 | The manifest is a generation source |
| D14 | Text entry always uses a native `<input>` |
| D15 | Forced-colors rules are required in every recipe |
| D16 | Plain CSS is the style source; Panda gets a preset |
| D17 | Framework targets render native elements to one anatomy contract |
| D18 | The spike proves the root-is-the-control model against forms |
| D19 | A submit button carries a hidden native submit button as a part |
| D20 | Button is form-associated |
| D21 | The browser floor is Chrome 129, Firefox 147 and Safari 26.4 |
| D22 | The skill keeps the name `ui-frameworks` |
| D23 | Tags are `ui-*`, set per kit; public tokens are unprefixed |
| D24 | JavaScript with JSDoc for Web Components; TypeScript for framework adapters |
| D25 | This repository is the source; the installable skill is generated |
| D26 | One named condition per state, written as a selector union |
| D27 | The kit uses Panda's five cascade layer names, and every file starts with the order statement |
| D28 | Cascade layer names contain no dots |
| D29 | Root replaces host |
| D30 | A part is marked with `data-part` |
| D31 | Part keeps its wide meaning |
| D32 | States with no ARIA name are `data-*` attributes; `:state()` is not used for styling |
| D33 | There is one invalid state: invalid, and the user is due to be told |
| D34 | hover and active exclude a disabled element inside the condition |
| D35 | Interaction states can be forced with `data-*` attributes |
| D36 | expanded and open are two states |
| D37 | The author attribute for busy is `loading` |
| D38 | The kernel has no `batch()` |
| D39 | Every author attribute is live, and a default writes no attribute |
| D40 | A part never wraps, moves or removes author content |
| D41 | A created part is a plain HTML element, never another component |
| D42 | A component's prop schema is a generated file |
| D43 | The kit does not hide undefined components |
| D44 | The form value is updated synchronously |
| D45 | `press` is a behaviour |
| D46 | Only `UIFormElement` attaches `ElementInternals` |
| D47 | Size budgets for the foundation |
| D48 | The five files of a component |
| D49 | CSS reaches the page through one index, and no script loads CSS |
| D50 | The kit writes only into the reset, tokens and recipes cascade layers |
| D51 | Recipes paint with material tokens |
| D52 | Geometry variables are generated from ui-geometry's rows |
| D53 | A recipe has one fixed shape |
| D54 | Only a hover, active or variant token falls back to the base public token |
| D55 | Conditions sit inside `:where()`, in a fixed order |
| D56 | Parts are selected with the child combinator |
| D57 | A part with no content and no events is a pseudo-element |
| D58 | A variant block sets private tokens only |
| D59 | Recipes hold no literal colour or length |
| D60 | The words of a public token |
| D61 | Transitions need a ready root and permission to move |
| D62 | Recipes are rewritten for the React, Svelte and Solid targets |
| D63 | Hover does not answer on a part that holds state, and changes paint only |
| D64 | Every hover rule sits inside `@media (hover: hover)` |
| D65 | A pattern with several ARIA roles is several components |
| D66 | A coordinating component finds the others by role and watches its subtree |
| D67 | A coordinating component sets state through the other component's own attribute |
| D68 | A tab and a panel pair by `value`, or by position |
| D69 | A root that is disabled but holds no form value extends `UIElement` |
| D70 | `rovingFocus` keeps itself up to date with an observer |
| D71 | Tabs select on focus unless activation is manual |
| D72 | `orientation` belongs to the tab list |
| D73 | The base fallback of C7 needs a base token |
| D74 | A focus ring only where focus goes, and inside an item in a tray |
| D75 | A menu button is three components, and its trigger is a button the author writes |
| D76 | Focus moves to the items of a menu, and the pointer moves focus too |
| D77 | A menu is a manual popover placed by CSS anchor positioning |
| D78 | `open` is the menu's attribute, and the menu returns focus to where it was |
| D79 | The menu button writes the pattern's ARIA on the trigger |
| D80 | A manifest is JSON held to a closed JSON Schema |
| D81 | `family` is one id, and what follows from it is derived |
| D82 | `focus` is required: own, roving or none |
| D83 | A target is planned or built, and built needs its files |
| D84 | The registry is generated, one entry per component |
| D85 | An icon is painted by CSS, as a mask in the ink |
| D86 | An icon library is a folder of SVG files, mapped by name |
| D87 | Only the icons the config names are generated |
| D88 | An icon is decorative unless the author names it |
| D89 | Shared files are generated or discovered, so families can be built at once |
| D90 | A list that must not take focus highlights an option; a menu, a tree and tabs move real focus |
| D91 | A modal layer is the browser's dialog element, and a link is the browser's anchor |
| D92 | A public token may name a part |
| D93 | A style-only recipe is a manifest of kind recipe, for a native element |
| D94 | The dialog's part is `panel` |
| D95 | The checkbox keeps its own glyphs; their ink is `--checkbox-mark-ink` |
| D96 | A stacked row is never shorter than the pointer's target |
| D97 | Anchoring in a right-to-left subtree is left to the engines |
| D98 | React is proved on the spike's four families |
| D99 | Solid waits for Solid 2.0; Svelte has no sequence |
| D100 | The skill is built by `scripts/package.mjs` and keeps the source layout |
| D101 | A framework target loads `native.css` |
| D102 | A recipe makes its own boxes border boxes |
| D103 | A kit's `tokens.css` can be trimmed to the tokens its sheets reach |
| D104 | The read-only condition also holds for a root whose input is read-only |
| D105 | A grid cell with several controls is entered with Enter or F2 and left with Escape |
| D106 | The carousel's slides are a polite live region |

## D1 · Text entry may use a native `<input>`

Every other component is fully custom: the root, a custom element, is the control, with a role and its own keyboard handling. This amends B10. D14 narrows it. D19 is the second amendment.

Without a native input, text entry means `contenteditable`, which loses autofill, password managers and password masking. Both earlier Web Components kits built `contenteditable` fields, and gen-ui-kit added a native `<input>` for password and autofill anyway.

## D2 · React, Svelte and Solid get native implementations

They share the contract (the manifests) and the styles with the Web Components. They are not wrappers around the web components. This follows B2, where a kit implements one framework. D17 says what they render.

Consequence: styles cannot rely on custom-element tag names alone.

## D3 · Distribution is a copy-in registry

The skill writes component source into the consuming project. There is no published package yet.

The consumer is an agent building a kit in one framework with one styling system. Copying only what is used makes tree-shaking (B14) hold by construction.

Consequence to design for: a copied component should record where it came from, so it can be updated later.

## D4 · Manifests record material attributes; styles ship Flat

Each part's layer, relief and face (the `ui-materials` terms) go in the manifest from the start. The default styles implement the Flat material only.

## D5 · A fresh foundation that ports from the earlier kits

Nothing is forked. The earlier kits are sources of mechanisms and lessons, listed in [prior-art.md](prior-art.md#what-to-port). They may become presets of this system later; they do not constrain it now.

## D6 · The browser floor is current evergreen

D21 names the versions.

`@scope`, `:state()`, the Popover API and CSS anchor positioning are assumed. Check 4 found anchor positioning working in Chromium 156, Firefox 157 and WebKit 27.2 ([checks.md](checks.md#check-4--anchor-positioning)).

## D7 · The core set is the APG patterns plus three

The WAI-ARIA APG patterns, plus text field, form field and icon. Card and badge are style-only recipes: a recipe with no component.

## D8 · Parts, not a template engine

This supersedes "templating systems" in B11.

- A component's manifest names its parts. The same names are what the CSS selects and what the React, Svelte and Solid versions render.
- On connect, the element looks for an authored child for each part and stamps a default only when none exists. An authored part always wins. Author children are never replaced.
- Each signal binding updates one part's text, attribute or ARIA value. There is no render pass.

Both earlier Web Components kits built a template engine that their own components avoid, because rendering into a light-DOM root replaces the author's children.

Cost: collections (options, tabs, rows) are authored child elements, not lists generated from data. Anything data-driven, such as a data grid or a virtual list, needs a separate utility later.

## D9 · ARIA role and states are real attributes on the root

Formerly P1. Never `ElementInternals` only. Each state has one canonical attribute, so it paints before the element upgrades. The component never overwrites a `role`, `tabindex` or `aria-label` the author wrote.

With internals-only ARIA (agent-ui), checked and selected styles cannot paint before upgrade, and shared behaviours cannot reach the internals. B7 asks for styles keyed on ARIA, which needs attributes to match.

When the API attribute and the ARIA attribute differ (`checked` and `aria-checked`), D26 says which the CSS selects.

Check 1 confirmed the premise: ARIA set through `ElementInternals` creates no attribute, and `[aria-checked="true"]` does not match it. It also found that `:checked`, `:required` and `:indeterminate` never match a custom element, so those states can only be styled through attributes.

## D10 · Component tokens split into public and private

Formerly P2. A public token such as `--button-color` is read with a fallback and never declared by the kit, so it can be set on the element or on any ancestor. Variants and states re-point private tokens.

gen-ui-kit and agent-ui declare the token on the root and let variants and hover re-point the same name. A consumer's override then loses once a variant or hover applies. [Check 7](checks.md#check-7--the-recipe-pattern) reproduced that failure in three engines on 2026-11-12, and showed the decided pattern holding.

maison-ui already works the decided way: every component colour is `var(--m-button-surface, …)` read from one mapping table and never declared on the component.

## D11 · One CSS delivery path, layered inside each file

Formerly P3. Each component sheet declares its own cascade layer with `@layer`. There is no runtime asset loader.

gen-ui-kit has three delivery paths, layered on one and unlayered on two, which changes how overrides behave, and a 1,377-line loader. A copy-in registry with static imports needs neither.

## D12 · Shared behaviours are plain DOM functions, used by every target

Formerly P4. Roving focus, typeahead, dismissal and positioning are framework-free functions of the form `(root, options) => cleanup`. Web Components call them on connect; React, Svelte and Solid mount the same functions on their own lifecycle. Components must import them, and the manifest lists them.

gen-ui-kit's 56 attribute-attached traits are imported by two of its components; the rest hand-roll the same logic. agent-ui's function traits are used throughout. maison-ui shares exactly this shape across five targets, where button's shared logic is 83 lines against about 940 of adapters.

Known cost: the functions attach native listeners, so maison-ui wraps React callbacks in `flushSync` in about 50 files.

## D13 · The manifest is a generation source

Formerly P5. Props, the registry and the exports are generated from it. It does not mirror the code.

gen-ui-kit carries 43k lines of YAML against 42k lines of class code, policed by hundreds of check scripts, and still drifts. agent-ui generates its props from the descriptor and gates the rest. maison-ui's manifests total 50k lines, more than any of its adapter sets, while each adapter's prop lists are still written by hand three to four times.

With four targets, generating each adapter's props from the manifest matters more than it did for one.

## D14 · Text entry always uses a native `<input>`

Formerly P6. Not `contenteditable` with a native fallback. This narrows D1.

The two `contenteditable` text fields run to 1,473 and 1,136 lines. maison-ui observed that Chromium's address autofill reached a native input but not a form-associated custom element.

## D15 · Forced-colors rules are required in every recipe

Formerly P7. Custom-painted controls lose their fills when the system substitutes its palette. agent-ui handles this in 84 of 95 sheets and requires a `forcedColors` field in each descriptor; gen-ui-kit handles it in 1 of 127.

## D16 · Plain CSS is the style source; Panda gets a preset

Formerly P8. Each component's CSS file is hand-written and is the source. Panda consumers get a preset of tokens, conditions and layer names, and load the kit's CSS as it is. The kit does not regenerate its styles through Panda. B12 allows either route.

maison-ui authors one rule list per component and emits it twice. That cost two selector contracts per rule, an 843-line selector rewriter, a key-ordering hack to keep cascade order in Panda, and a special case because Panda leaves `&` unresolved in `@scope` parameters.

Check 3 verified this with Panda 2.4 in three engines ([checks.md](checks.md#check-3--panda-beside-the-kits-css)). It holds on three conditions: every kit stylesheet is layered; every kit stylesheet starts with the layer order statement; and the preset's tokens never alias a kit variable of the same name.

Open inside this decision: the root selector and the variant attributes differ per target (`ui-button[variant]` on a custom-element root, a class with `data-variant` on a native element). That needs either union selectors or one mechanical mapping step.

## D17 · Framework targets render native elements to one anatomy contract

Formerly P9. React, Svelte and Solid render native semantic elements, with the part names, state attributes and tokens the manifest declares. One parity script per component server-renders and hydrates each framework beside plain HTML and runs the same assertions. The manifest records readiness per target.

B10 asks for fully custom elements in the Web Components target only. In maison-ui the four non-WC targets render identical DOM, and a test asserts it.

## D18 · The spike proves the root-is-the-control model against forms

Formerly P10. Before the core set is built, button and checkbox must pass form tests: submission by click and by Enter, the submitter's name and value, reset, label click and focus, fieldset disabling and validation. If a test can only pass with a native element, such as a hidden submit proxy, that becomes a recorded exception to B10, like D1.

maison-ui started with custom elements as the controls, left that model, and came back to Web Components only as wrappers around native controls. gen-ui-kit's custom button submits with no submitter, and agent-ui's button does not submit a form at all.

## D19 · A submit button carries a hidden native submit button as a part

Formerly P11. A second amendment to B10, beside D1. A custom button with `type="submit"` stamps a hidden native `<button type="submit">` inside itself and submits through it.

Check 5 found, in all three engines, that a custom element cannot be passed to `requestSubmit()`, never matches `:default`, and cannot make Enter submit a form that has more than one field. A native submit button in the form is the only platform route to that. With the part in place the form also gets a real `submitter`, and the button's name and value travel the native way.

No native alternative is close: `ElementInternals.type` was closed as not planned, and its successor proposal is at Stage 1 behind a flag in one engine.

Without this, D18's form tests cannot pass for Enter.

## D20 · Button is form-associated

Formerly P12. Every interactive root that can be disabled is a form-associated custom element, button included, not only the controls that carry a value.

Check 1 found that a form-associated root gets `:disabled`, suppression of click events, removal from focus, fieldset disabling and label activation from the platform, and that a plain custom element gets none of them, even with a `disabled` attribute.

## D21 · The browser floor is Chrome 129, Firefox 147 and Safari 26.4

Formerly P13. This makes D6 concrete. The kit does not use `popover="hint"` until Safari ships it.

The floor comes from three rows of the version table in [checks.md](checks.md#shipping-versions-and-the-browser-floor): `position-area` in Chrome 129, anchor positioning in Firefox 147, and `@scope` rules reaching a native `<input>` in Safari 26.4. D14 puts a native input inside a scoped root, so the Safari row cannot be waived.

## D22 · The skill keeps the name `ui-frameworks`

It is the name of the project folder. `ui-components` was the alternative considered.

## D23 · Tags are `ui-*`, set per kit; public tokens are unprefixed

The core set ships as `ui-button`, `ui-checkbox` and so on. The prefix is a setting applied when the skill copies source into a project (D3), so a kit can choose its own.

Public tokens carry no prefix: `--button-color`, as B13 writes it. The kit only reads a public token and never declares one (D10), so the kit cannot cause a collision by itself. Private tokens are written `--_name`.

## D24 · JavaScript with JSDoc for Web Components; TypeScript for framework adapters

The Web Components target and the shared behaviour functions (D12) are JavaScript with JSDoc types, checked by the TypeScript compiler. Copied source has to run in a browser with no build step.

The React, Svelte and Solid adapters are TypeScript, which is idiomatic there, with props generated from the manifest (D13).

## D25 · This repository is the source; the installable skill is generated

The skill folder that gets installed (entry file, references, registry, scripts) is a build output of this repository and is checked for drift. Tests, the check harness and authoring docs stay out of it.

This is the author and consumer split from `context-system`: a consumer receives generated artifacts and never needs the authoring material.

## D26 · One named condition per state, written as a selector union

Each state in the state matrix has one name and one selector. The selector is a union that covers the author-facing attribute, the ARIA attribute and the native pseudo-class where each exists:

```css
:is(:checked, [aria-checked="true"], [checked]:not(input, option))
```

Corrected on 2026-11-12 by the [state matrix](specs/state-matrix.md#what-this-corrects). The example first read `:is([checked], [aria-checked="true"], :checked)`, which keeps matching a native checkbox after the user unchecks it, because the `checked` attribute there is only the default.

- The author-facing attribute paints before the element upgrades.
- The ARIA attribute is present after upgrade, and when an author writes it directly.
- The native pseudo-class covers the native elements the framework targets render (D17).

This settles the point D9 left open, and gives every target the same state selectors. The same table becomes the `conditions` of the Panda preset (D16).

## D27 · The kit uses Panda's five cascade layer names, and every file starts with the order statement

The cascade layers are `reset`, `base`, `tokens`, `recipes` and `utilities`. Every kit stylesheet begins with the statement that orders them, then puts its rules in one of them. The names are a setting applied at copy-in (D3), for a project that already uses them for something else.

Check 3 measured this arrangement as correct in every load order, with no configuration needed from a Panda consumer. The alternative, one layer of the kit's own that the consumer places, failed whenever the consumer's order statement was missing.

## D28 · Cascade layer names contain no dots

Lightning CSS, the default minifier in Vite 8, reorders dotted layer statements such as `@layer a.b, a.c;`.

## D29 · Root replaces host

Formerly V1. The outermost element of a component is its root, in every target and every document. ui-geometry already owns host, for a segmented control or a tab list, and the React, Svelte and Solid targets have no host at all. Documents written before this decision were reworded; no decision id changed.

## D30 · A part is marked with `data-part`

Formerly V2. Every part except the root carries `data-part="<part name>"`, in every target. Not a class and not a `slot` attribute.

agent-ui and massimo-ui already do this. A `slot` attribute borrows a word ui-geometry owns and an HTML feature that light DOM does not use. A class cannot be told apart from the author's own classes.

## D31 · Part keeps its wide meaning

Formerly V3. A part is any named element of a component's anatomy, so a label or an icon is a part. ui-materials uses the word more narrowly, for a painted element with a layer, a relief and a face, and calls a label or an icon a mark. D8 was confirmed with the wide meaning, and the manifest needs one word for every named element. `references/terms.json` records the difference.

## D32 · States with no ARIA name are `data-*` attributes; `:state()` is not used for styling

Formerly M1. A state the kit manages and ARIA does not name, such as highlighted or ready, is a `data-*` attribute on the element.

Check 1 showed `:state()` works in all three engines, but only a custom element can hold a custom state. The React, Svelte and Solid targets render native elements (D17), which cannot. A `data-*` attribute works on both, so every target keeps the same condition (D26).

## D33 · There is one invalid state: invalid, and the user is due to be told

Formerly M2. The invalid condition holds after the user has changed or left the field, after a submit attempt, or when the author sets `invalid`. The component writes `aria-invalid="true"` at that same moment. Raw `:invalid` is not a state and no recipe uses it.

A required field matches `:invalid` before anyone has touched it. What the recipe paints and what `aria-invalid` tells assistive technology should be the same thing.

## D34 · hover and active exclude a disabled element inside the condition

Formerly M3. The two conditions carry the "not disabled" guard themselves.

A disabled form-associated root still matches `:hover`. With the guard inside the condition, no recipe can forget it.

D63 widens the hover guard to every element that holds a state.

## D35 · Interaction states can be forced with `data-*` attributes

Formerly M4. `data-hover`, `data-focus`, `data-focus-visible` and `data-active` make the matching condition hold without a pointer or a keyboard. They are for specimens and tests. A component writes only `data-active`, and only while Space or Enter is held, because the platform never makes `:active` match from the keyboard on a custom-element root.

A showcase has to draw every state on a still page. Panda's own conditions have the same hooks.

## D36 · expanded and open are two states

Formerly M5. expanded is a state of the element that controls something, and maps to `aria-expanded`. open is a state of the thing that opens, and maps to the `open` attribute and to `:popover-open`.

ARIA puts `aria-expanded` on the control and nothing on what it shows, while the popover and dialog features mark the thing itself.

## D37 · The author attribute for busy is `loading`

Formerly M6. An author writes `loading`; the component writes `aria-busy="true"`. It is the word the earlier kits and Panda use for a control that is waiting.

## D38 · The kernel has no `batch()`

Formerly X1. An effect runs once, synchronously, when it is created, then at most once per microtask flush however many of its sources changed. That already groups the writes made in one task, so the kernel needs no way to batch them by hand.

## D39 · Every author attribute is live, and a default writes no attribute

Formerly X2. When a prop changes through its property, the element writes the attribute. A prop that holds its default value has no attribute, and returning a prop to its default removes it.

Recipes select variants and states by attribute, so a value set from script has to reach the attribute. A stamped default would change which selectors match; gen-ui-kit recorded that as a bug.

## D40 · A part never wraps, moves or removes author content

Formerly X3. A part the element creates is added at the start or the end of the root, as the manifest states. `<ui-button>Save</ui-button>` keeps its bare text node. Where a wrapper is needed, for example to truncate a label, the author writes it and marks it with `data-part`.

It is the only reading of D8 under which a framework or an author can own the children without a fight.

## D41 · A created part is a plain HTML element, never another component

Formerly X4. A button does not create its own icon; the author places the icon component in the markup.

Importing a component's class then defines no other element, so tree-shaking is exact (B14).

## D42 · A component's prop schema is a generated file

Formerly X5. `<id>.props.js` is generated from the manifest (D13) and imported by the class. A prop has one of four types: boolean, string, number or enum.

The whole manifest is too large to ship to the browser.

## D43 · The kit does not hide undefined components

Formerly X6. Instead, defining a component must not change the size or the position of its root, and a state set in markup must already be painted.

With the stylesheet loaded ahead of the script (D11), an undefined component is already styled and already shows its state. Hiding it, as gen-ui-kit does, would only add a flash.

## D44 · The form value is updated synchronously

Formerly X7. When a prop that feeds the form value changes, the element updates the form value before the property setter returns.

Effects run in a microtask (D38). A form read in the same task would otherwise see the old value. maison-ui records the same rule.

## D45 · `press` is a behaviour

Formerly X8. It activates a root on Enter at key down and on Space at key up, prevents the default action of both, and keeps `data-active` on the root while either key is held.

It matches a native button, and every component that can be activated needs it, because Space and Enter do nothing on a custom-element root (check 1).

## D46 · Only `UIFormElement` attaches `ElementInternals`

Formerly X9. D9 keeps ARIA in attributes, so a component that is not form-associated has no use for internals.

## D47 · Size budgets for the foundation

Formerly X10. At most 1 KB for the signals kernel and 3 KB for `UIElement` with `UIFormElement`, minified and gzipped. The numbers are a first estimate that the spike measures and may revise.

"Minimal" (B9) needs a number to be checkable.

## D48 · The five files of a component

Formerly X11. `<id>.class.js` holds the class and defines nothing. `<id>.js` defines the element. `<id>.props.js` is the generated prop schema. `<id>.css` is the recipe. `<id>.manifest.json` is the contract.

This settles the file split the plan had marked as proposed.

## D49 · CSS reaches the page through one index, and no script loads CSS

Formerly Y1. `kit.css` imports `reset.css`, `tokens.css` and the recipe of each component the project has. A page links it ahead of any kit script. The skill adds a line when it copies a component in.

It is the one delivery path D11 asks for, and it is what lets a component that is not yet defined already be styled (D43). Adding a component adds its recipe and its line, which is how components load with their CSS (B14).

## D50 · The kit writes only into the reset, tokens and recipes cascade layers

Formerly Y2. `base` and `utilities` stay free for the project and for Panda. Check 3 measured that arrangement beside Panda's output.

## D51 · Recipes paint with material tokens

Formerly Y3. A recipe reads ui-materials' material tokens, such as `--raised-face` and `--on-solid`, and not ui-colors roles. `tokens.css` carries ui-materials' base block with the Flat values.

D4 ships Flat only, but a recipe that reads material tokens needs no change when another material arrives.

One exception stands: ui-materials has no token for hover, so recipes read ui-colors' hover roles directly until it does.

## D52 · Geometry variables are generated from ui-geometry's rows

Formerly Y4. Each variable is named after the row's id with dots as hyphens, so `controls.control.h` becomes `--controls-control-h`. Each is a literal length. The rows that change with density are repeated under `[data-density="compact"]` and `[data-density="loose"]`. `tokens.css` holds only the rows some recipe reads.

ui-geometry emits no CSS. Names taken from its ids need no second vocabulary and can be checked against its output.

## D53 · A recipe has one fixed shape

Formerly Y5. One `@scope` block inside the `recipes` cascade layer, holding in order: the token block, the variant blocks, the root rule, the part rules, the condition rules and the environment blocks.

One shape is what makes a lint possible.

## D54 · Only a hover, active or variant token falls back to the base public token

Formerly Y6. Amended on 2026-11-13, after the spike wrote the first two recipes.

- A private token for hover, for active or for a variant reads its own public token, then the base public token, then the kit's value: `var(--button-face-hover, var(--button-face, <kit value>))`.
- A private token for any other state reads its own public token, then the kit's value: `var(--checkbox-face-checked, <kit value>)`. It reads no other public token and no private token.

The first point is what makes an override hold, which is the point of D10. A consumer who sets only `--button-face` gets that colour at rest, in every variant, on hover and when pressed. Check 7 measured this in three engines.

The second point is the amendment. As first confirmed, every state token fell back to the base. That erases a state that carries meaning: a consumer who set only `--checkbox-face` got the same face checked and unchecked, and one who set only `--button-ink` got a disabled button that looked enabled. Hover and active are feedback while the pointer or a key is on the element, so losing their tint loses little. Every other state says something about the element that the user has to be able to see.

Consequence: a consumer who changes both the face and the ink of a component sets the ink of its disabled state as well, because the kit's value for that state no longer follows their ink.

The recipe tests measure both points in three engines, and the mutation runner puts the old fallback back as a negative control.

## D55 · Conditions sit inside `:where()`, in a fixed order

Formerly Y7. A recipe writes each condition inside `:where()`, and writes its condition rules in this order: hover, focus-visible, active, then checked, indeterminate, pressed, selected, current, expanded and open, then invalid, loading, read-only, and disabled last.

The conditions differ in specificity. Check 7 showed that without `:where()` a checked and disabled root keeps its checked look however the rules are ordered.

## D56 · Parts are selected with the child combinator

Formerly Y8. A recipe selects a part as a child of the root or of another part of the same component: `:scope > [data-part="mark"]`.

Check 7 showed a part selected as any descendant leaking into a component nested inside.

## D57 · A part with no content and no events is a pseudo-element

Formerly Y9. Where a part holds no content and takes no events, the recipe draws it as a pseudo-element of the root, and the manifest records that.

A pseudo-element exists before the component is defined, so it cannot cause a layout shift (D43), and it never touches author content (D40).

## D58 · A variant block sets private tokens only

Formerly Y10. Every difference between variants is then something a consumer can override.

## D59 · Recipes hold no literal colour or length

Formerly Y11. A kit value is a material token, a geometry variable or a ui-colors role. The only literal length is `0`. No colour is computed in the browser.

Every value then traces to a sibling skill.

## D60 · The words of a public token

Formerly Y12. `face`, `ink` and `line` for paint; `height`, `inset`, `gap` and `radius` for geometry; the state or the variant as a suffix. So `--button-face`, `--button-ink-disabled`.

They are ui-materials' and ui-geometry's words. The brief's example `--button-color` (B13) becomes `--button-face`.

## D61 · Transitions need a ready root and permission to move

Formerly Y13. A recipe declares a transition or an animation only inside `@media (prefers-reduced-motion: no-preference)`, and only for `:scope:where([data-ready])`.

The first paint then never animates, and reduced motion needs no override.

## D62 · Recipes are rewritten for the React, Svelte and Solid targets

Formerly Y14. A recipe is written once, for the Web Components target. When the skill copies it for another target, it rewrites the tag in `@scope (…)` to the root attribute `[data-<prefix>="<component id>"]`, and each variant attribute selector to its `data-` form. Nothing else is rewritten; conditions already cover every target (D26).

This closes the open point of D16. A kit has one target (B2), so one rewrite at copy time is cheaper than writing every root and variant selector twice.

## D63 · Hover does not answer on a part that holds state, and changes paint only

The kit follows the rule `hover.face-only` of the sibling skill `ui-interaction-dev`, which that skill marks as validated.

- The hover condition does not hold on an element that is disabled or that holds a state: checked, indeterminate, pressed, selected, current, expanded or open. This widens D34. The rule itself names pressed, checked, selected, open and disabled; indeterminate, current and expanded are the same kind of state in this kit's matrix.
- A hover rule changes paint only and sets no property that changes a box.
- The hover paint differs from the paint of the active condition.

A hover paint over a checked or selected part hides that state, and a hover that moves a box shifts the target under the pointer. The state matrix checks the first point in three engines, with the D34 form of the condition as a negative control.

## D64 · Every hover rule sits inside `@media (hover: hover)`

The kit follows the rule `hover.media` of `ui-interaction-dev`, also validated there. A tap leaves a hover behind on a touch screen, where it reads as state.

Check 7 measures it: under touch emulation in Chromium, a hover rule inside the media query paints nothing, and one outside it still paints.

Consequence: an interaction state forced with `data-hover` (D35) also shows only where the device can hover.

## D65 · A pattern with several ARIA roles is several components

Formerly Z1. A pattern made of several ARIA roles is several components, one per role. Each has its own five files (D48) and its own manifest, and names the others under `family`. Tabs are four: tabs, tab list, tab and tab panel.

D9 makes each root the element that carries its role. A tab list in light DOM cannot be a part the component creates, because a part never wraps author content (D40), so the author writes it, and it is a component like the others.

Cost: four directories and four imports for one pattern.

## D66 · A coordinating component finds the others by role and watches its subtree

Formerly Z2. A component that coordinates others finds them by their ARIA role, among its descendants that belong to no component of its own kind nested inside it. It watches its subtree with a `MutationObserver`. The others do not register with it, and its class names no tag (foundation rules G1 and G2).

One mechanism covers every order in which the elements are defined (L7), children that arrive later, and children that leave. The other targets have the same roles and no tags (D17), so the same lookup holds there.

The tabs tests define the four elements in four different orders, and add and remove a tab.

## D67 · A coordinating component sets state through the other component's own attribute

Formerly Z3. A coordinating component sets a state on another component through that component's author attribute: `selected` on a tab, `hidden` on a panel. It writes an attribute only when its value differs. `value` on the tabs element and `selected` on a tab are kept in step both ways (G3, G6).

The author's markup then paints the state before anything is defined (U2), and a script may use either attribute.

Consequence: for a first paint that does not shift, the author writes `selected` on the selected tab and `hidden` on every other panel.

## D68 · A tab and a panel pair by `value`, or by position

Formerly Z4. A tab and a panel pair when they have the same `value`. One with no `value` attribute has its position among its kind as its value, so tabs and panels written in the same order need no values. The tabs element gives a tab or a panel an `id` only when it has none, and builds `aria-controls` and `aria-labelledby` from those ids (G4).

The shortest markup works, and ids stay the component's business.

Cost: where tabs can be added or removed, positions shift, so those tabs need a `value`.

## D69 · A root that is disabled but holds no form value extends `UIElement`

Formerly Z5. A root that can be disabled but holds no form value, such as a tab, extends `UIElement`, not `UIFormElement`. This narrows the foundation's sentence "every root that can be disabled extends `UIFormElement`" to form controls, and D20 with it.

A tab is not a form control: it should not appear in `form.elements`, and a disabled fieldset should not disable it.

Cost: the platform keeps the pointer, a label and `click()` away from a disabled form-associated root, and a tab has none of that. The tabs element ignores a disabled tab and roving focus passes over it, but a listener the author adds to the tab still receives `click`.

## D70 · `rovingFocus` keeps itself up to date with an observer

Formerly Z6. `rovingFocus` watches its root with a `MutationObserver` and brings the tabindex values up to date when an item is added, is removed or changes a watched attribute (B10).

A behaviour returns only its cleanup (B1) and takes changing values as functions (B2), so a component has no way to call it again. The DOM is its source, which is also what lets the React, Svelte and Solid targets mount it unchanged (D12).

## D71 · Tabs select on focus unless activation is manual

Formerly Z7. With `activation="automatic"`, which is the default, the tabs element selects a tab as soon as the tab takes focus. With `activation="manual"` it waits for Enter, Space or a click (G7).

APG allows both and recommends automatic when the panels are already in the page, which they are in light DOM.

## D72 · `orientation` belongs to the tab list

Formerly Z8. `orientation` is an author attribute of the tab list, where ARIA puts `aria-orientation`. The tabs element has no orientation and does not yet lay out a vertical list beside its panels; the author lays out the root.

A recipe may size and place its root from that root's own author attributes only (C17), so the tabs element cannot read the list's orientation, and a tab cannot either. The tab's paint and hit area are therefore written to work in a row and in a column.

## D73 · The base fallback of C7 needs a base token

Formerly Z9. C7 sends a hover, active or variant token to the base public token. That holds only when the component has that base token. Where it has none, the token falls back to the kit's value alone: `var(--tab-face-hover, <kit value>)`.

ui-materials gives a tab no face at rest, and a recipe may not write a literal `transparent` (D59), so a tab has no `--tab-face`.

The recipe lint reports a hover token that skips a base the recipe has, and one that names a base it does not have.

## D74 · A focus ring only where focus goes, and inside an item in a tray

Formerly Z10. Three limits on the CSS contract, all found with the tabs:

- A focus ring (C20) is required only in the recipe of a root that takes focus. The manifest says so with a `tabindex`, or with `focus: "roving"` when a list gives the root its tabindex.
- A forced-colours block (C19) is required only in a recipe that paints, which is what C19 already said and the lint did not.
- An item inside a tray, such as a tab, draws its focus ring inside itself, and takes the pointer over the tray's padding without ever covering a neighbouring item (C20, C21).

The tabs element takes no focus and paints nothing. ui-geometry gives a hosted item an inset ring, because an outer ring would overlap its neighbours.

## D75 · A menu button is three components, and its trigger is a button the author writes

Formerly Q1. A menu button is three components: the menu button, which coordinates and has no role, the menu and the menu item (D65). The trigger is a button the author writes inside the menu button: the kit's button, or any element with the button role.

The button already has the variants, the disabled state and the form behaviour a trigger needs, so the kit has no second button to keep in step with the first.

Cost: the author writes the button, and a chevron in it, by hand until the kit has an icon contract.

## D76 · Focus moves to the items of a menu, and the pointer moves focus too

Formerly Q2. When a menu opens, focus moves to its first item that is not disabled, and roving focus moves it among the items. The pointer moving over an item moves focus to that item as well, so a menu has one marked row, painted on the `focus` condition. A menu item has no hover rule.

Roving focus exists and is tested, and real focus is the most widely supported way to tell a screen reader where the user is. The state matrix keeps `highlighted` for an option whose list leaves focus elsewhere, as in a combobox, and no longer lists the menu item under it.

A press inside the menu moves no focus: on a disabled item or between the items it would take focus from the menu and leave it open with no key to close it.

## D77 · A menu is a manual popover placed by CSS anchor positioning

Formerly Q3. A menu is a `popover="manual"` element. The top layer shows it, CSS anchor positioning places it, and the `dismiss` behaviour closes it on Escape, on a press outside and when focus leaves.

The anchor is the menu button element. Its recipe sets `anchor-name` and `anchor-scope` to one fixed name, and the menu's recipe names it in `position-anchor`; the scope keeps each menu to its own menu button. No script and no id takes part in placement. The menu sits below the trigger with start edges aligned, no narrower than the trigger, and flips above where it does not fit.

Check 4 found that a custom trigger cannot use the declarative popover attributes. With `popover="auto"`, a press on the trigger would close the menu and its click would open it again, so the kit dismisses the menu itself.

Measured in Chromium 156, Firefox 157 and WebKit 27.2, before and after the elements are defined, including the flip, which check 4 had left untested.

## D78 · `open` is the menu's attribute, and the menu returns focus to where it was

Formerly Q4. `open` is the menu's author attribute. The menu shows itself while it has the attribute, in the same task as the write, whoever writes it; the menu button opens and closes the menu through it (D67). If something else hides the popover, the menu removes the attribute.

The menu remembers the element that had focus when it opened, and returns focus there on Escape and when an item is activated. A press outside, and focus that leaves, close the menu and leave focus where the user put it.

The menu then works with any opener, not only inside a menu button, and behaves as the platform's own popover and dialog do.

## D79 · The menu button writes the pattern's ARIA on the trigger

Formerly Q5. The menu button writes `aria-haspopup="menu"`, `aria-controls` and `aria-expanded` on the trigger directly, and names the menu after the trigger when the author gave the menu no name.

These three belong to the pattern, not to a button, and the button has no `expanded` attribute of its own to set them through. The trigger's paint does not change while its menu is open; ui-materials asks for none.

## D80 · A manifest is JSON held to a closed JSON Schema

Formerly W1. A manifest is a JSON file held to `references/manifest.schema.json`, and names the version of that schema it is written to. The schema describes every field, declares every closed set once, and allows no field it does not describe.

JSON with a schema is read by every tool and agent with no build, and the schema doubles as the field reference. A closed schema is what turns a mistyped field into an error.

`node scripts/manifests.mjs` checks it, with a reader for the subset of JSON Schema the schema uses, because the project installs nothing.

## D81 · `family` is one id, and what follows from it is derived

Formerly W2. `family` is the id of the component that leads a pattern, not a list of members repeated in every member. A component alone is its own family. The only other relations are `uses`, for a component outside the family that the markup needs, and `writes`, for the attributes a component writes on another component's root.

The members of a family, what a component comes with, and who writes its attributes are derived in the registry. A manifest no longer says in prose who writes its tabindex.

One home per fact: the list of the four tabs components had been written in four manifests.

## D82 · `focus` is required: own, roving or none

Formerly W3. `focus` is required in every manifest. `own`: the root is a Tab stop of its own, and has a `tabindex`. `roving`: a list gives the root its tabindex. `none`: the root never takes focus.

The recipe lint asks for a focus ring from it (D74) and the registry routes by it. It could not be read from `tabindex` alone, because a tab and a menu item have none of their own.

## D83 · A target is planned or built, and built needs its files

Formerly W4. A target's status is `planned` or `built`. `built` means the target's files exist and its tests pass; for the Web Components target the files are the five of D48, and the checker requires them. `in progress` is gone.

A status that states no evidence cannot be checked.

## D84 · The registry is generated, one entry per component

Formerly W5. `kit/registry.json` is generated from the manifests by `node scripts/manifests.mjs` and is never edited. It has one entry per component: the fields a consumer routes by (`kind`, `family`, `tier`, `role`, `focus`), the summary, the tag, the path of the manifest, the stylesheet, and every module the component loads, however indirectly.

D3 makes distribution a copy-in registry: the skill has to know what to copy for a component without reading source. `--check` fails when the registry differs from what the manifests generate.

## D85 · An icon is painted by CSS, as a mask in the ink

An icon is one element with a `name`. Its recipe paints a square box in the ink through the icon as a mask, and no script draws it.

It is therefore painted before the component is defined (U2), takes the ink of whatever it sits in, and never flashes in. The alternatives were an inline SVG stamped by script from a registered pack, as agent-ui does, and an SVG the author pastes in. The first paints nothing until its script runs and ships a pack; the second leaves every author to do the kit's work.

Cost: one ink per icon.

## D86 · An icon library is a folder of SVG files, mapped by name

`kit.config.json` names a folder of SVG files under `icons.source` and maps each name the kit uses to a file in it. `scripts/icons.mjs` generates `kit/styles/icons.css` from them. Phosphor's regular weight is the default (B8), vendored as the subset the map names.

A kit that uses another library changes the folder and the file names. The names the kit and its pages use stay the same: `chevron-down` is `caret-down` in Phosphor and `chevron-down` in most others.

## D87 · Only the icons the config names are generated

`icons.css` holds one rule per name in the config and nothing else. There is no pack, no closed list of names every library must cover, and no weight axis.

agent-ui's whole pack loads at once, and its names are Phosphor's.

## D88 · An icon is decorative unless the author names it

The icon component writes `aria-hidden="true"` on an icon with no accessible name, and `role="img"` on one the author gave `aria-label` or `aria-labelledby`. Its size is one of ui-geometry's four icon sizes, `md` by default.

An icon beside a label says nothing the label does not. One that stands alone is named on itself or on the control around it.

## D89 · Shared files are generated or discovered, so families can be built at once

No builder of a component family edits a file another family uses. `kit/styles/kit.css` and `kit/registry.json` are generated from the manifests; the definition test reads the registry; mutation sets live in `tests/mutations/<family>.mjs` and the preview in `preview/sections/<family>.html`, both discovered. A manifest starts with its target `planned`, and the tests that read code apply once it says `built`. The Node tests touch no file a browser run serves.

Several agents can then build different families at the same time, each to the rules of [authoring.md](authoring.md).

## D90 · A list that must not take focus highlights an option; a menu, a tree and tabs move real focus

The kit has two ways to move among items, and each pattern uses one. Tabs, a menu, a toolbar, a radio group and a tree move real focus, with `rovingFocus` (D76). A listbox keeps focus on itself and marks one option with `data-highlighted` and `aria-activedescendant`, with a second behaviour, `activeDescendant`.

A combobox's list must not take focus from its text field, so the listbox, which a combobox reuses, cannot move focus. Building the listbox that way from the start means one list for both.

ui-interaction-dev's rule `focus.cursor` then applies to it: a pressed option becomes the highlighted one, and the highlight differs from the selected and from the pressed paint.

## D91 · A modal layer is the browser's dialog element, and a link is the browser's anchor

Two more amendments to B10, beside D1 (text entry) and D19 (the submit part). The kit's dialog wraps a native `dialog` element the author writes, and the kit's link is a native `a` with a style-only recipe.

In both cases the platform gives something a custom element cannot. A modal dialog makes the rest of the page inert, keeps focus inside, closes on Escape and returns focus, without a line of script. An anchor opens in a new tab, has a context menu, shows its address, and works before any script runs.

The component still adds what the element lacks: the dialog gets an `open` attribute, a name from its title and the kit's paint.

## D92 · A public token may name a part

A public component token is `--<component>-<word>`, or `--<component>-<part>-<word>` for a part other than the root, each with an optional state or variant after it: `--meter-face` is the meter's track, `--meter-fill-face` its fill. The part is one of the manifest's parts. This extends D60.

A component with two painted parts had no way to name the second. The meter's fill was first `--meter-face-value`; the lint read `value` as a variant and made it fall back to `--meter-face` (D54), so an author who coloured the track coloured the fill the same and the meter read as empty. A part's token has its own base, so it falls back to the kit's value.

The recipe lint takes the part names from the manifest.

## D93 · A style-only recipe is a manifest of kind recipe, for a native element

Link, card, badge and table have no behaviour to add to the browser's own elements. Each is a recipe and a manifest, with no class, no script and no custom element. Its root is a native element that carries `data-ui="<id>"`, and a variant is `data-<name>`: the form D62 gives a root in the React, Svelte and Solid targets, here used in every target, the Web Components one included.

The manifest says `kind: "recipe"` and names the element. The recipe lint scopes it to the attribute and otherwise holds it to the same contract; the registry lists it with a selector in place of a tag.

A static table is among them. APG's table pattern is the semantics the `table` element already has; an interactive grid is a component.

## D94 · The dialog's part is `panel`

Decided by the session. The native dialog element the author writes inside a dialog is marked `data-part="panel"`, and its tokens are `--dialog-panel-face`, `-ink`, `-inset` and `-radius`. It was `dialog`, which gave `--dialog-dialog-face`. `panel` is ui-geometry's word for a framed surface and names no role.

## D95 · The checkbox keeps its own glyphs; their ink is `--checkbox-mark-ink`

Decided by the session. `icons.css` gives a glyph to `ui-icon[name]` only, so another recipe cannot read one without loading the icon sheet and widening the icon contract. A recipe loads alone (B14), so the checkbox, and the checkable menu item after it, keep the two Phosphor glyphs they embed. The glyph's ink is now the public token `--checkbox-mark-ink` (D92), falling back to the kit's value.

## D96 · A stacked row is never shorter than the pointer's target

Decided by the session. At compact density ui-geometry makes a menu row and a tab 22px tall. Rows stack with no gap, so a hit area cannot grow without covering a neighbour. `scripts/tokens.mjs` therefore writes `collections.rows.menu-row` and `collections.rows.segment-tab` no smaller than `controls.target.t_hit-pointer` (24px). This covers the menu items, the option, the tree item and the tab. The lasting fix is a taller compact row in ui-geometry; when it has one, the floor changes nothing and can go.

## D97 · Anchoring in a right-to-left subtree is left to the engines

Decided by the session, from a measurement in plain HTML (`checks/anchor-rtl/run.mjs`, Chromium 156, Firefox 157, WebKit 27.2). In a right-to-left page, with `dir` on the root element, all three engines place an anchored popup correctly. In a right-to-left subtree of a left-to-right page, `position-area` resolves its logical keywords against the containing block, which is the viewport: Chromium and WebKit align the popup to the anchor's left edge, as the specification says, and Firefox 157 puts it about 390px away. That is the engine, not the recipe; removing `anchor-scope`, the popover, the fallbacks or the minimum width changes nothing. The recipes stay as they are, and the one test that mixes directions (J25) lets Firefox off.

## D98 · React is proved on the spike's four families

Decided by the session. The second target (plan step 6) is React 19, built for button, checkbox, tabs and menu button: a form control, a coordinating composite and an overlay. If the manifests, the recipes, the conditions and the behaviours carry those unchanged, the contract is neutral; the other components stay `planned` for React and are built on demand by the same rules ([targets](specs/targets.md)). A React component is plain JavaScript that calls `createElement`, so the target needs no build step, as the kit itself needs none (D24).

## D99 · Solid waits for Solid 2.0; Svelte has no sequence

Decided by the session. The brief names SolidJS 2.0 (B1). The only Solid at hand is 1.9, and nothing is installed here without being asked, so the Solid target is not started. Svelte stays `planned` with no place in the sequence until the author gives it one.

## D100 · The skill is built by `scripts/package.mjs` and keeps the source layout

Decided by the session. This settles D25. `node scripts/package.mjs` writes the installable skill to `dist/ui-frameworks`: the entry file from `skill/SKILL.md`, all of `kit/` without its tests, the scripts a consumer runs, the specs with `decisions.md` and `checks.md`, and the data files in `references/`. Tests, the harness, the preview, the plan, the prior-art review and the authoring guide stay out. The folders keep their names, so no script and no link is rewritten; `--check` fails when the built skill differs from the source. A kit is created in a project by `scripts/create-kit.mjs`, which copies the chosen families of one target with every module they import. Route tests for a fresh agent are in `skill/evals/evals.json` and are not shipped.

Installing is a copy of `dist/ui-frameworks` to `~/.claude/skills/ui-frameworks`, done by the author.

## D101 · A framework target loads `native.css`

Decided by the session, from the React proof ([report](reports/react.md)). The recipes, conditions, behaviours and manifests carried the nine React components unchanged. Two things were missing, and both come from a native root, not from a recipe: a native `button` keeps the browser's border, padding and font (59.92px wide against 51.22px), and the checkbox's native input shows inside its label. `kit/styles/native.css` resets the first and hides the second, in the `reset` layer, and each framework target's `kit.css` loads it (X11). The Web Components target does not.

Left open by the proof, and recorded in the targets spec: a menu rendered open on the server paints closed until hydration, because nothing in HTML opens a popover; a `label` root cannot carry ARIA states, so it mirrors them as plain attributes; a disabled fieldset does not reach a checkbox's label; a trigger's ARIA is written after hydration.

## D102 · A recipe makes its own boxes border boxes

Decided by the author on 2026-11-14, after a review ([report](reports/review-tree-shaking-and-css.md)). Without `reset.css`, 12 of 32 families changed size, because the recipes relied on the reset's `box-sizing: border-box`. Every recipe now carries one rule, `:where(:scope, [data-part]) { box-sizing: border-box; }`, and the table and grid recipes add `caption, th, td` to it (C31). The rule leaves `::before` and `::after` alone. The reset named them inside `:where()`, where a pseudo-element is not valid and is dropped, so they were content boxes all along and the recipes were written for that: with them made border boxes, two tests of the slider's fill failed in three engines. The reset now says what it does, `:where(*)`. The lint requires the rule. With it, no family differs with or without the reset. `reset.css` stays in the kit and in `kit.css`: it still serves the project's own content.

A project's unlayered reset still beats a recipe. That is how cascade layers work, and the skill says to put such a reset in a layer.

## D103 · A kit's `tokens.css` can be trimmed to the tokens its sheets reach

Decided by the author on 2026-11-14, after the same review. `tokens.css` holds every ramp of the colour preset, and the recipes reach 157 of its 446 custom properties. `scripts/trim-tokens.mjs` removes every declaration of a property that no kit stylesheet reads, directly or through another token, in every mode, density and media query, and keeps the names a project lists. `create-kit --tokens used` applies it to the copied file, for the components chosen, and writes `"tokens": "used"` into the copied `kit.config.json`; `tokens.mjs` reads that key and writes the same trimmed file when the project restyles. `--keep` and the `keep` key name properties, or prefixes ending in `*`, that the project's own CSS reads.

The source kit keeps the full file, which is the default: a project that writes its own CSS with the kit's colours needs the ramps. Measured: 107 KB to 27 KB (12 KB to 3.5 KB gzipped) for all components, 9 KB for a button alone; 192 pages (32 families, two modes, three densities) paint the same against the trimmed file (`checks/review/trimmed-tokens.mjs`).

Fallback values for global tokens inside the recipes were considered and refused: they would double the recipes and fix one mode's colours in them. `tokens.css` stays required.

## D104 · The read-only condition also holds for a root whose input is read-only

Decided by the session on 2026-11-14. The author writes `readonly` on the input inside a text field, and the component mirrors it onto the root only once it is defined, so a paint keyed to the root alone would appear late and break U2. The read-only condition in `references/states.json` is now `:is([readonly], [aria-readonly="true"], :has(> [data-part="input"][readonly]))`. `:has()` works in the three engines the kit tests. No recipe used the condition before, so nothing else changes. The text field paints the state as ui-materials' etched fill (J77). The combobox and the spinbutton hold an input too and paint it the same way (J80, J81), by the author's request of 2026-11-14; a read-only combobox does not open its list and a read-only spinbutton hides its buttons.

## D105 · A grid cell with several controls is entered with Enter or F2 and left with Escape

Decided by the session on 2026-11-14, from the APG grid pattern. A cell with one plain control hands focus to it (J69). A cell with several controls, or with one that takes text or uses the arrow keys, is itself the stop: Enter or F2 moves focus inside, Tab moves among its controls and wraps, and Escape or F2 returns to the cell (J79). While focus is inside, the grid leaves the arrow keys to the control. Wrapping Tab inside the cell keeps the grid one stop in the Tab order: the user leaves the cell with Escape and the grid with Tab.

## D106 · The carousel's slides are a polite live region

Decided by the session on 2026-11-14, from the APG carousel pattern. The kit's carousel never rotates by itself, so its slides part carries `aria-live="polite"` and a slide the user brings into view is announced (J78). The author's own `aria-live` is kept.
