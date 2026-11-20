# Outside checks

Results of the five checks listed in plan.md, run on 2026-11-12.

## Method

- **Checks 1, 2, 4 and 5** ran as a test page in three engines through Playwright 1.64.1: Chromium 156.0.8078.4, Firefox 157.0 and WebKit 27.2. The WebKit build is Playwright's, not Safari itself. The page is checks/platform/page.html, the runner is run.mjs and the raw output is results.json.
- **Check 3** ran as a minimal Panda 2.4.0 project in checks/panda/: `panda cssgen`, then pages that inline the kit's CSS and Panda's output in different orders, read in the same three engines. The raw output is results.json. The Panda documentation and source were read at 2.5.0.
- **Shipping versions and specification status** come from web research on the same day: the HTML Standard, browser release notes, MDN's compatibility data, web-features and the WebKit and WHATWG trackers. Sources are listed [at the end](#sources). I did not re-verify them beyond the tests here.
- **Check 6** was added with the foundation spec and ran the same way, from checks/forms/run.mjs.
- **Check 7** was added with the CSS contract, from checks/recipes/run.mjs.
- Every result below was the same in all three engines unless a row says otherwise.

One caution on WebKit. Playwright's build reports version 27.2 but runs ahead of Safari's stable release: it accepts `popover="hint"`, which Safari's release notes list only for the 27.3 beta. A pass in that build shows the engine can do it, not that every Safari 26 or 27 release does.

## Answers

| # | Question | Answer |
|---|---|---|
| 1 | Which native pseudo-classes match form-associated custom elements? | Only `:disabled`, `:enabled`, `:valid` and `:invalid` are usable. `:checked`, `:required`, `:indeterminate` and `:default` never match. `:user-invalid` differs by engine. |
| 2 | Does the Safari bug with `:scope` plus a dynamic state inside `@scope` still apply? | No. Every state rule inside `@scope` matched, and the related fixes shipped in Safari 26.2 and 26.4. |
| 3 | Can a Panda project load the kit's `@scope` CSS beside its own output, with a preset? | Yes, on three conditions: the kit's CSS is layered, the layer order is fixed by a statement that comes first, and tokens do not alias a variable of the same name. |
| 4 | Is CSS anchor positioning supported at the browser floor? | Yes in all three engines, including between two custom elements with one as a popover. It sets the floor at Firefox 147 and Safari 26. |
| 5 | What must a custom submit button do? | It cannot be the form's submitter or default button. It can carry a name and value. Enter in a form with several fields does not submit unless the form holds a native submit button. |

## Check 1 · Pseudo-classes on form-associated custom elements

"FACE" is an autonomous custom element with `static formAssociated = true`. "Plain" is a custom element without it.

| Pseudo-class | FACE | Plain custom element |
|---|---|---|
| `:disabled` | Matches with the `disabled` attribute, and inside `fieldset[disabled]` | Never, even with `disabled` |
| `:enabled` | Matches when not disabled | Never |
| `:invalid`, `:valid` | Follow `internals.setValidity()` | Never |
| `:required`, `:optional` | Never, even with `required` | Never |
| `:checked`, `:indeterminate`, `:default` | Never | Never |
| `:placeholder-shown`, `:in-range`, `:out-of-range`, `:read-write` | Never | Never |
| `:read-only` | Always, so it carries no information | Always |
| `:state(x)` | Matches after `internals.states.add('x')` | Same |

Engine differences:

| Behaviour | Chromium | Firefox | WebKit |
|---|---|---|---|
| `:valid` on a disabled FACE or one with `readonly` | Matches | Does not match | Does not match |
| `:user-valid` on an untouched FACE | No | Matches | No |
| `:user-invalid` right after `setValidity()` with an error, no interaction | No | Matches | No |

Other behaviour that bears on the design:

- **ARIA set through `ElementInternals` creates no attribute.** After `internals.ariaChecked = 'true'` the element has no `aria-checked` attribute and `[aria-checked="true"]` does not match. This confirms D9.
- **A disabled FACE behaves like a disabled native control.** A real mouse click dispatches no `click` event, and the element cannot be focused even with `tabindex="0"`.
- **Labels work for a FACE only.** `<label for>` associates with a FACE (`internals.labels`), and clicking the label focuses it and dispatches `click` on it. A plain custom element gets neither, and `internals.labels` throws.
- **`formDisabledCallback` and `formResetCallback` fire** as expected.
- **A custom `role="button"` with `tabindex="0"` gets no keyboard activation.** It is reachable by Tab and matches `:focus-visible`. Space and Enter dispatch no `click`, and `:active` does not match while Space is held. A native button got two clicks, and `:active` on Space in Chromium and WebKit but not in Firefox.
- **Tab order differs in WebKit.** The custom `tabindex="0"` button was reached with Tab; the native button needed Option+Tab, the macOS default.

Against the HTML Standard: `:user-valid` and `:user-invalid` are defined for `input`, `textarea` and `select` only, so Firefox is the engine that departs; extending them to custom elements is an open request (whatwg/html#9639). A disabled or `readonly` form-associated element is barred from constraint validation, so Chromium is the one that departs on `:valid`.

What this decides:

- The state matrix can use `:disabled` and `:invalid` on form-associated roots. Checked, required, indeterminate, read-only and pressed need an attribute.
- `:user-invalid` cannot be used. The kit needs its own attribute for "invalid after the user has interacted".
- A root that is form-associated gets `:disabled`, click suppression, removal from focus, fieldset disabling and labels from the platform. That is an argument for making button form-associated, not only the value-carrying controls.

## Check 2 · `@scope` with `:scope` and a dynamic state

All of these rules, written inside `@scope (x-scope)` which is itself inside `@layer`, applied to the scope root:

`:scope`, `:where(:scope)`, `:scope:hover`, `:scope:active`, `:scope:focus-visible`, `:scope[data-on]`, `:scope[data-on]:hover`, `:scope[aria-checked="true"]`, `:scope:state(on)`, `:scope > [data-part]`.

Hover and active were driven by a real pointer and focus by the keyboard. Adding and removing the attribute, the ARIA attribute and the custom state after first render each updated the style, and hover cleared when the pointer left.

Two more cases were added after the research turned up WebKit bugs that match them. Both passed in all three engines:

- `:scope:not(:state(on))` updated when the state was added and removed. WebKit bug 280807, still open, reports this form not updating.
- Rules inside `@scope` reached a native `<input>` and `<textarea>` inside the scope root. Safari 26.0 to 26.3 did not apply them (WebKit bug 305369, fixed in 26.4). D14 puts a native input inside a scoped root, so this one matters.

The bug gen-ui-kit worked around has no single report. The nearest are style-invalidation bugs for `:scope` rules, WebKit 279225 and its duplicate 276454, fixed in Safari 26.2.

What this decides: state rules can live inside `@scope`, provided the browser floor is Safari 26.4 or later. The split that gen-ui-kit made in 22 sheets is not needed there.

## Check 3 · Panda beside the kit's CSS

### What Panda 2.4 emitted

With a preset that adds conditions and tokens, and `layers` renamed to `kit.*`:

```css
@layer kit.reset, kit.base, kit.tokens, kit.recipes, kit.utilities;
@layer kit.recipes { @layer base, slots, variants, compound_variants; }
@layer kit.tokens {
  :where(:root, :host) {
    --colors-kit-primary: var(--colors-primary-solid);
    --colors-primary-solid: var(--colors-primary-solid);
  }
}
@layer kit.utilities {
  .checked\:opacity_0\.25:is([aria-checked="true"], :checked) { opacity: 0.25; }
}
```

- **Layer names follow the `layers` config**, and the order statement comes first.
- **Conditions from a preset work.** The `checked` condition above is the kit's own selector.
- **A token may point at a kit variable**: `--colors-kit-primary: var(--colors-primary-solid)`.
- **A token with the same name as the kit variable refers to itself**: `--colors-primary-solid: var(--colors-primary-solid)`. Panda always emits a variable for every token.
- **Panda 2 adds no presets by default.** Without `@pandacss/preset-base` there are no utilities, so `backgroundColor: 'kitPrimary'` was emitted as the literal text `kitPrimary`. preset-base was not installed locally, so token utilities resolving to the kit's variable are documented but not tested here.

### Cascade, measured in the browser

Each page holds one custom button styled by the kit's `@scope` CSS, plus Panda classes that set a background, the public token `--button-color`, and a `checked:` condition.

| Setup | Result |
|---|---|
| A · Kit CSS uses Panda's five layer roles under `kit.*`; every kit file starts with the order statement; Panda's `layers` is set to the same names | Correct with kit first and with Panda first |
| B · Kit CSS sits in one top-level `kit` layer; the consumer's entry CSS has `@layer reset, base, tokens, kit, recipes, utilities;` | Correct with kit first and with Panda first |
| B without the entry statement, kit first | The button loses its colour: Panda's `tokens` layer lands after `kit`, and the self-referring token wins |
| B without the entry statement, Panda first | The kit beats Panda's utilities |
| Kit CSS unlayered | The kit beats Panda's utilities |

In setup A the self-referring token did no harm only because the kit's `:root` rule outranks Panda's `:where(:root, :host)` inside the same layer.

From the Panda 2.5 documentation and source:

- Panda does not parse CSS it did not generate, so `@scope`, `:where()` and nested `@layer` in the kit's files pass through untouched.
- A consumer's order statement may contain extra layer names. The FAQ shows this for third-party CSS.
- `layers` is not part of the `Preset` type. It has to be set in the consumer's config.
- `polyfill: true` replaces layers with specificity and loses the positioning.
- Lightning CSS, the default minifier in Vite 8, reorders dotted statements such as `@layer a.b, a.c;`. The nested form `@layer a { @layer b, c; }` survives.

What this decides: D16 holds. The CSS contract has to state three rules.

1. Every kit stylesheet, including `reset.css`, is layered.
2. Every kit stylesheet starts with the layer order statement, so load order cannot change the outcome.
3. The Panda preset names its tokens differently from the kit's variables, for example `colors.kit.primary.solid`, or carries literal values. It never aliases a variable of the same name.

Still open: whether the kit takes Panda's five roles under its own namespace (setup A) or one layer of its own (setup B), and whether layer names avoid dots because of the minifier.

## Check 4 · Anchor positioning

`CSS.supports()` returned true in all three engines for `anchor-name`, `position-anchor`, `anchor()`, `position-area`, `position-try-fallbacks`, `anchor-size()`, `position-visibility` and `anchor-scope`.

A custom element with `popover="manual"` opened with `showPopover()` and sat exactly under a custom-element trigger through `anchor-name` and `position-anchor`: trigger bottom 448, popup top 448; both left edges 124.

`popover="hint"` was accepted by all three builds, but Safari's stable 27.2 does not ship it; its release notes add it in the 27.3 beta.

Not tested: how `position-try-fallbacks` behaves when a popup does not fit. gen-ui-kit records that it did not fire for tall popovers.

From the research:

- The initial value of `position-anchor` has changed across versions in every engine, so the kit should always set it.
- WebKit has dozens of open anchor-positioning bugs, among them a popover anchored to a fixed element drifting on scroll (326820).

Related findings from the same page:

| Feature | Chromium | Firefox | WebKit |
|---|---|---|---|
| `popovertarget` and `commandfor` on anything but a native button | No | No | No |
| `interestfor` | Yes | No | No |
| `Element.moveBefore()` | Yes | Yes | No |
| `ElementInternals.type` | No | No | No |

What this decides: overlays do not need a JavaScript positioning path for basic placement. A custom trigger must open its popover from script, because the declarative attributes exist only on native buttons; extending them to custom elements is an open request with no resolution (whatwg/html#9110). `popover="hint"` should wait until Safari ships it.

## Check 5 · A custom submit button

The form holds two text inputs and a form-associated custom element meant as its submit button.

| Attempt | Result |
|---|---|
| `form.requestSubmit(customElement)` | Throws `TypeError`: the element is not a submit button |
| `form.requestSubmit()` | Submits; `event.submitter` is `null` |
| `internals.setFormValue('yes')` just before `requestSubmit()` | The form data includes the custom element's `name=yes` |
| `new FormData(form, customElement)` | Throws `TypeError` |
| `:default` on the custom element | Never matches |
| Enter in a text input, two inputs, custom submit only | No submission |
| Enter in a text input, one input, custom submit only | Submits; `submitter` is `null` |
| Enter in a text input, two inputs, plus a hidden native `<button type="submit">` | Submits; `submitter` is the native button |
| `ElementInternals.type = 'submit'` | Not available in any of the three engines |

What this decides: a fully custom submit button can submit on click and can carry its name and value, but it cannot make Enter submit a form with more than one field. The only platform route to that is a native submit button in the form. So a submit button needs a hidden native `<button type="submit">` as a part, which is a second exception to B10 beside D1. With that part in place, `requestSubmit(part)` also gives the form a real submitter.

The standard agrees with every row: `requestSubmit()` throws for anything that is not a submit button, the default button is the first submit button in the form, and with no submit button a form submits on Enter only if it has at most one text-like field.

No relief is close. `ElementInternals.type` was closed as not planned in March 2026 (whatwg/html#11061). Its successor, platform-provided behaviours (whatwg/html#12150), is at Stage 1 and behind a flag in Chrome, with no position from Mozilla or WebKit.

## Check 6 · Forms and the accessibility tree

Added on 2026-11-12 with the [foundation spec](specs/foundation.md), which depends on three more facts. The runner is checks/forms/run.mjs and the raw output is results.json. Parts A and B gave the same result in all three engines.

### A · A hidden native submit button inside a custom button

The form holds two text inputs and a form-associated custom button. Inside the custom button is `<button type="submit" hidden tabindex="-1">`, whose name and value copy the custom button's.

| Case | Result |
|---|---|
| The native button matches `:default` | Yes |
| Enter in a text input | Submits. The submitter is the native button, and the data holds the custom button's name and value. |
| Click on the custom button, which calls `requestSubmit` with the native button | The same |
| The custom button's name in the data when it sets no form value | Absent, so the name is not submitted twice |
| Enter, and click, with both buttons disabled | No submission |

### B · An invalid form-associated root at submit

A form-associated root was given a validity error through `setValidity`, with itself as the anchor.

| Case | Result |
|---|---|
| Click on the form's submit button | No `submit` event. The root receives one `invalid` event, and focus moves to it. |
| `form.requestSubmit()` | The same |
| The same click once the root is valid | Submits |

### C · The accessibility tree, in Chromium only

Read through the DevTools protocol, so it is the browser's own tree. Firefox and WebKit were not tested.

| Element | Role | Name | Disabled in the tree |
|---|---|---|---|
| Form-associated root with `role="checkbox"` and a `<label for>` | checkbox | "Accept terms", from the label | No |
| Form-associated root with `disabled` | button | "Go" | Yes |
| Form-associated root inside `fieldset[disabled]` | button | "Go" | Yes |
| Plain custom element with `disabled` | button | "Go" | No |
| Plain custom element with `aria-disabled="true"` | button | "Go" | Yes |

### What this decides

- D19's design works as specified: the hidden native button gives the form a default button and a real submitter, and carries the name and value.
- The `invalid` event is the signal that the user is due to be told (D33), and the form already moves focus to the invalid root.
- A `<label for>` names a form-associated root, so the kit needs no labelling code of its own for that case.
- In Chromium a form-associated root needs no `aria-disabled`; a plain custom element does. This is one more reason for D20.

## Check 7 · The recipe pattern

Added on 2026-11-12 with the [CSS contract](specs/css-contract.md), and extended on 2026-11-13 for D63 and D64. It builds the recipe shape the contract prescribes, and the patterns the contract rules out, and reads computed styles. The runner is checks/recipes/run.mjs and the raw output is results.json. All engines agree: chromium 156.0.8078.4: 25 cases, 0 failed, firefox 157.0: 22 cases, 0 failed, webkit 27.2: 22 cases, 0 failed. Chromium has three more cases because only it can emulate a touch screen.

### The prescribed pattern

| Case | Result |
|---|---|
| A root with no override takes the material token | Holds |
| A variant re-points the private token | Holds |
| The variant re-points the ink as well | Holds |
| Hover takes the private hover token | Holds |
| Hover on a variant takes that variant's hover token | Holds |
| A public token set on an ancestor reaches the root | Holds |
| The same override survives a variant | Holds |
| The same override survives hover | Holds |
| A public token set on the root beats one set on an ancestor | Holds |
| A hover-only override leaves rest alone | Holds |
| A hover-only override applies on hover | Holds |
| A second public token works the same way | Holds |
| With conditions inside :where(), the later rule wins: disabled over checked | Holds |
| Hover does not apply to a disabled root | Holds |
| Hover does not apply to a root that holds a state | Holds |
| An unlayered consumer rule beats the recipe | Holds |
| A part is styled as a child of its root | Holds |
| The same part name inside a nested component is left alone | Holds |
| Touch emulation reports that the device cannot hover | Holds |
| On a touch screen a hover rule inside the media query paints nothing | Holds |

### The patterns ruled out

Each of these is a negative control: it shows the failure a rule of the contract exists to prevent.

| Failure | Result |
|---|---|
| Without :where(), checked outranks a later disabled rule | Confirmed |
| A public token declared on the root ignores the ancestor override | Confirmed |
| And a variant that re-points the same name ignores it too | Confirmed |
| A part selected as any descendant leaks into a nested component | Confirmed |
| On a touch screen a hover rule outside the media query still paints | Confirmed |

### What this decides

- D10's premise is now observed, not only read from the earlier kits' CSS: a public token that the kit declares on the root ignores a value set on an ancestor, and so does a variant that re-points the same name.
- With the public token only read, an override set on an ancestor holds at rest, in a variant and on hover.
- Rule order decides which state shows only when every condition is inside `:where()`.
- A part must be selected with the child combinator.
- A hover rule must sit inside `@media (hover: hover)` to stay off a touch screen.

## Check 8 · The platform in November 2026

Run on 2026-11-15 from checks/modern/run.mjs, in Chromium 156, Firefox 157 and WebKit 27.2; the full table is checks/modern/results.json. It says what these builds can do, not which stable version first shipped it, and the caution on Playwright's WebKit above holds.

| Feature | Chromium | Firefox | WebKit |
|---|---|---|---|
| `closedby="any"` closes a modal dialog on a press outside | Yes | Yes | Yes |
| `beforetoggle` and `toggle` on a dialog | Yes | Yes | Yes |
| `commandfor` with `show-modal` and `close`, native button | Yes | Yes | Yes |
| `requestClose()`, `CloseWatcher`, `showPopover({ source })` | Yes | Yes | Yes |
| `@starting-style`, `transition-behavior: allow-discrete`: a popover fades in | Yes | Yes | Yes |
| The same pair keeps a popover displayed while it fades out | Yes | No | No |
| `overlay`, `interpolate-size`, `calc-size()`, `interestfor`, `focusgroup`, scroll-state queries, `reading-flow` | Yes | No | No |
| `appearance: base-select` | Yes | No | Yes |
| `moveBefore`, `ariaNotify` | Yes | Yes | No |
| `field-sizing`, `sibling-index()`, `Temporal`, ARIA element reflection, `text-wrap: balance` | Yes | Yes | Yes |

What this decides is D118: the dialog follows a panel the browser opened, and nothing else changes.

## Check 9 · `popover="auto"` from a custom trigger

Run on 2026-11-15 from checks/popover-auto/run.mjs, with the browser's own pointer and keyboard; results in checks/popover-auto/results.json. A custom element with `role="button"` toggles an auto popover from its click, passing itself as `showPopover({ source })`. Every row was the same in Chromium 156, Firefox 157 and WebKit 27.2.

| Question | Result |
|---|---|
| A press on the trigger while its popover is open | Light dismiss closes it as the pointer comes up; the click then finds it closed and opens it again. The same with no source. |
| A press outside | Closes, and the control outside still gets its click. |
| Escape with focus inside | Closes, and focus returns to the trigger. |
| Focus leaves the popover | It stays open. |
| A second popover that is not a descendant, opened from inside the first with a source | Both stay open; Escape closes the inner one only; a press in the parent closes the inner one only. |
| Opening an unrelated auto popover | Closes the first. |
| Inside a modal dialog | Opens; Escape closes the popover and leaves the dialog. |

What this decides: D77 stands. A source gives nesting, not an exemption from light dismiss, so a custom trigger would still need script to keep one press from closing and reopening, and the kit closes on focus leaving, which the platform does not.

## Shipping versions and the browser floor

First stable version of each feature the plan relies on, from the research.

| Feature | Chrome | Firefox | Safari |
|---|---|---|---|
| Form-associated custom elements | 77 | 98 | 16.4 |
| Popover API | 114 | 125 | 17 |
| `@scope` | 118 | 146 | 17.4 |
| `@scope` rules reaching `<input>` and `<textarea>` | 118 | 146 | 26.4 |
| `:scope` rules updating on state change | 118 | 146 | 26.2 |
| `:state()` | 125 | 126 | 17.4 |
| Anchor positioning: `anchor-name`, `anchor()`, `anchor-size()` | 125 | 147 | 26 |
| `position-try-fallbacks` | 128 | 147 | 26 |
| `position-area` | 129 | 147 | 26 |
| `position-visibility` | 125 | 147 | 26.2 |
| `commandfor`, native buttons only | 135 | 144 | 26.2 |
| `popover="hint"` | 151 | 153 | 27.3 beta |

The binding rows give a floor of **Chrome 129, Firefox 147 and Safari 26.4**. Firefox 147 shipped on 2026-01-13 and Safari 26.4 in March 2026.

Baseline status is less settled than the versions. `@scope` is listed as newly available from either December 2025 or March 2026, depending on whether the Safari input bug counts. Anchor positioning was announced as newly available in January 2026, but its roll-up currently reads as limited because of a keyword rename.

## Sources

Specification:

- HTML Standard: [pseudo-classes](https://html.spec.whatwg.org/multipage/semantics-other.html), [custom elements](https://html.spec.whatwg.org/multipage/custom-elements.html), [form submission](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html), [forms](https://html.spec.whatwg.org/multipage/forms.html), [interaction](https://html.spec.whatwg.org/multipage/interaction.html)
- Open requests: [`:user-invalid` on custom elements](https://github.com/whatwg/html/issues/9639), [invokers from custom elements](https://github.com/whatwg/html/issues/9110), [`ElementInternals.type`](https://github.com/whatwg/html/issues/11061), [platform-provided behaviours](https://github.com/whatwg/html/issues/12150)

WebKit bugs: [279225](https://bugs.webkit.org/show_bug.cgi?id=279225), [280807](https://bugs.webkit.org/show_bug.cgi?id=280807), [305369](https://bugs.webkit.org/show_bug.cgi?id=305369), [326820](https://bugs.webkit.org/show_bug.cgi?id=326820)

Versions:

- [Safari 26.2](https://developer.apple.com/documentation/safari-release-notes/safari-26_2-release-notes), [26.4](https://developer.apple.com/documentation/safari-release-notes/safari-26_4-release-notes) and [27.3](https://developer.apple.com/documentation/safari-release-notes/safari-27_3-release-notes) release notes
- [Firefox 146](https://developer.mozilla.org/en-US/Firefox/Releases/146) and [147](https://developer.mozilla.org/en-US/Firefox/Releases/147) release notes
- web-features: [`@scope`](https://web-platform-dx.github.io/web-features-explorer/features/scope), [anchor positioning](https://web-platform-dx.github.io/web-features-explorer/features/anchor-positioning), [`:state()`](https://web-platform-dx.github.io/web-features-explorer/features/state), [popover](https://web-platform-dx.github.io/web-features-explorer/features/popover)

Panda:

- [Cascade layers](https://panda-css.com/docs/styling/cascade-layers), [presets](https://panda-css.com/docs/theming/presets), [conditions](https://panda-css.com/docs/theming/conditions), [tokens](https://panda-css.com/docs/theming/tokens), [upgrading to v2](https://panda-css.com/docs/get-started/upgrading-to-v2), [FAQ](https://panda-css.com/docs/get-started/faq)
- [Lightning CSS reordering dotted layer statements](https://github.com/chakra-ui/panda/issues/3933)

## Running the checks again

Both runners take the path of any project whose `node_modules` holds Playwright with its browsers installed.

```bash
node checks/platform/run.mjs checks/platform/page.html <project-with-playwright>
```

For check 6:

```bash
node checks/forms/run.mjs <project-with-playwright>
```

For check 7:

```bash
node checks/recipes/run.mjs <project-with-playwright>
```

For check 3, generate Panda's output twice, build the pages, then read them in one engine:

```bash
panda cssgen --cwd checks/panda --config checks/panda/panda.config.mjs -o checks/panda/panda-a.css
```

```bash
panda cssgen --cwd checks/panda --config checks/panda/panda.config.b.mjs -o checks/panda/panda-b.css
```

```bash
node checks/panda/build-pages.mjs
```

```bash
node checks/panda/cascade.mjs <project-with-playwright> chromium
```

For the C20 stacking rule:

```bash
node checks/focus-on-top/run.mjs <project-with-playwright>
```

Then the same with `--negative`, which must see the neighbour on top in every case, and with `--strip=<case>` for each case (`button`, `text-field`, `combobox`, `spinbutton`, `date-field`, `file-field`), where only that case may. Before any browser starts the runner lists every rule of the reset and the recipes that sets `z-index` on a focus condition, and fails when one has no case.
