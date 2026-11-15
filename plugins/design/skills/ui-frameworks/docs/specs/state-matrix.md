# State matrix

Spec 2 of 4. Accepted on 2026-11-12.

Every state a recipe may style, and the one condition that selects it. The matrix is data in [references/states.json](../../references/states.json). The tables below are generated from it by `node scripts/docs.mjs`; edit the data, not the tables. Every condition is tested in three browser engines by `checks/states/run.mjs`.

Terms such as root, part, condition, author attribute and managed attribute are defined in the [vocabulary](vocabulary.md).

## Who reads this

- **A recipe author** takes the condition for a state and writes no other selector for it.
- **A component author**, in any target, reads which author attribute to accept and which managed attribute to write.
- **The Panda preset** takes the conditions table as its `conditions`.
- **A manifest** names the states a component has by their ids.

## Rules

"Built" means a check exists and runs today. "Planned" names the spec or step that will add it.

| # | Rule | Basis | Check |
|---|---|---|---|
| S1 | A recipe shall select a state only through its condition. | D26 | Planned: recipe lint, with the CSS contract |
| S2 | Each state shall have one id and one condition, the same in every target. | D26 | Built: `scripts/docs.mjs` |
| S3 | A state that an author can set in markup shall hold before the component's script has run. Its condition therefore includes the author attribute. | D9 | Built: the fixtures on an element that is never defined |
| S4 | On a custom-element root, the author attribute for a state shall be live: when the state changes, the component reflects the change to the attribute. On form reset the component restores the value it captured when it started. | D26; gen-ui-kit's reset snapshot | Planned: a test per component in the spike (D18) |
| S5 | After it starts, a component shall write the managed attribute for each of its states and keep it in step with the author attribute. | D9 | Planned: the spike |
| S6 | A state with no ARIA name shall be a `data-*` attribute. The kit shall not style with `:state()`. | D17, D26, D32 | Built: `scripts/docs.mjs` refuses `:state(` in a condition |
| S7 | A native pseudo-class shall enter a condition only for the elements on which the three engines agree. | Check 1 | Built: the fixtures |
| S8 | The conditions hover and active shall not hold on a disabled element. The hover condition shall also not hold on an element that holds a state: checked, indeterminate, pressed, selected, current, expanded or open. | D34, D63 | Built: the fixtures, and a real pointer over a disabled root and over a checked root |
| S9 | While Space or Enter is held on a custom-element root that can be activated, the component shall write `data-active`. | Check 1 | Planned: the spike |
| S10 | A component shall write `aria-invalid="true"` only when the user is due to be told: after they have changed or left the field, or after a submit attempt. | D33; agent-ui's `trackUserInvalid` | Planned: the spike |
| S11 | The attributes `data-hover`, `data-focus` and `data-focus-visible` are for specimens and tests. A component shall not write them. | D35 | Planned: a lint of component source |
| S12 | A recipe shall not use `:invalid`, `:valid`, `:required`, `:optional`, `:read-only`, `:read-write`, `:user-valid`, `:checked` or `:indeterminate` outside the conditions. | Check 1 | Planned: recipe lint |
| S13 | A state shall enter the matrix only when a core-set component needs it. | context-system: evidence before structure | Judgement; the reserved list records what is waiting |

Three notes on those rules:

- **S4 differs from native HTML.** On a native checkbox the `checked` attribute is only the default and never changes. On a custom-element root it is the live state, because the recipe has to paint from it before and after the script loads.
- **S6 is why custom states are not used.** Check 1 showed `:state()` works in all three engines, but only a custom element can hold one. The React, Svelte and Solid targets render native elements (D17), which cannot. A `data-*` attribute works on both.
- **S7 has three cases today.** `[checked]` excludes native inputs and options, where the attribute is only the default. `:indeterminate` is limited to checkboxes. `:user-invalid` is limited to native controls.

- **S8 follows the sibling skill `ui-interaction-dev`.** Its rule `hover.face-only` says a hover must not answer on a part that holds state, because a hover paint over a checked or selected part hides that state. The matrix composes the hover condition from the conditions of the states it excludes, and `scripts/docs.mjs` refuses a condition that differs from that composition.

## States

<!-- generated:states:start -->
| State | Holds when | Author attribute | Component writes | Native element offers |
|---|---|---|---|---|
| **hover** | The pointer is over the element, and the element is neither disabled nor holding a state: checked, indeterminate, pressed, selected, current, expanded or open. |  |  | :hover |
| **active** | The element is being activated right now: the pointer is down on it, or Space or Enter is held on it. It is not disabled. |  | data-active, while Space or Enter is held | :active |
| **focus** | The element has focus, however it got it. |  |  | :focus |
| **focus-visible** | The element has focus and the browser judges that a focus ring should show. |  |  | :focus-visible |
| **focus-within** | The element or one of its descendants has focus. |  |  | :focus-within |
| **highlighted** | Keyboard or pointer navigation currently points at this item while focus stays on its container. |  | data-highlighted, on the item `aria-activedescendant` names |  |
| **disabled** | The element cannot be operated. | `disabled` | aria-disabled="true" | :disabled |
| **read-only** | The value can be read and focused but not changed. | `readonly` | aria-readonly="true" | the `readonly` attribute |
| **required** | A value must be given before the form can be submitted. | `required` | aria-required="true" | the `required` attribute |
| **checked** | The choice is on. | `checked` | aria-checked="true" or "false" | :checked |
| **indeterminate** | The choice is neither on nor off, because it stands for a group that is partly on. | `indeterminate` | aria-checked="mixed" | :indeterminate, on a checkbox only |
| **pressed** | A toggle button is on. | `pressed` | aria-pressed="true" or "false" |  |
| **selected** | The item is the chosen one, or one of the chosen ones, in its collection. | `selected` | aria-selected="true" or "false" |  |
| **current** | The item stands for the current page, step, location, date or time within its set. | `current` | aria-current, with the author's value or "true" |  |
| **expanded** | The element controls something that is currently shown. It is a state of the controlling element, not of what it shows. | `expanded` | aria-expanded="true" or "false" |  |
| **open** | The element is itself the thing that opens, and it is showing. | `open` |  | the `open` attribute of dialog and details; :popover-open |
| **invalid** | The value fails validation and the user is due to be told: after they have changed or left the field, after a submit attempt, or when the author says so. | `invalid` | aria-invalid="true", once the user has interacted | :user-invalid, on input, select and textarea only |
| **loading** | The element is waiting on work it started, or its content is being updated. | `loading` | aria-busy="true" |  |
| **horizontal** | The component's items run along the inline axis, and that is not its default. | `orientation="horizontal"` | aria-orientation="horizontal" |  |
| **vertical** | The component's items run along the block axis, and that is not its default. | `orientation="vertical"` | aria-orientation="vertical" |  |
| **hidden** | The element is not to be shown at all. | `hidden` |  | the `hidden` attribute |
| **ready** | The component has started and painted once. |  | data-ready, one frame after it starts |  |
<!-- generated:states:end -->

## Conditions

In a recipe a condition follows the root or a part: `:scope` plus the condition. In the Panda preset it follows `&`.

<!-- generated:conditions:start -->
| State | Condition |
|---|---|
| hover | `:is(:hover, [data-hover]):where(:not(:is(:disabled, [disabled], [aria-disabled="true"]), :is(:checked, [aria-checked="true"], [checked]:not(input, option)), :is(input[type="checkbox"]:indeterminate, [aria-checked="mixed"], [indeterminate]), :is([aria-pressed="true"], [pressed]), :is([aria-selected="true"], [selected]:not(option)), :is([aria-current]:not([aria-current="false"], [aria-current=""]), [current]), :is([aria-expanded="true"], [expanded]), :is([open], :popover-open)))` |
| active | `:is(:active, [data-active]):where(:not(:is(:disabled, [disabled], [aria-disabled="true"])))` |
| focus | `:is(:focus, [data-focus])` |
| focus-visible | `:is(:focus-visible, [data-focus-visible])` |
| focus-within | `:focus-within` |
| highlighted | `[data-highlighted]` |
| disabled | `:is(:disabled, [disabled], [aria-disabled="true"])` |
| read-only | `:is([readonly], [aria-readonly="true"], :has(> [data-part="input"][readonly]))` |
| required | `:is([required], [aria-required="true"])` |
| checked | `:is(:checked, [aria-checked="true"], [checked]:not(input, option))` |
| indeterminate | `:is(input[type="checkbox"]:indeterminate, [aria-checked="mixed"], [indeterminate])` |
| pressed | `:is([aria-pressed="true"], [pressed])` |
| selected | `:is([aria-selected="true"], [selected]:not(option))` |
| current | `:is([aria-current]:not([aria-current="false"], [aria-current=""]), [current])` |
| expanded | `:is([aria-expanded="true"], [expanded])` |
| open | `:is([open], :popover-open)` |
| invalid | `:is([aria-invalid]:not([aria-invalid="false"]), :is(input, select, textarea):user-invalid, [invalid])` |
| loading | `:is([aria-busy="true"], [loading])` |
| horizontal | `:is([aria-orientation="horizontal"], [orientation="horizontal"])` |
| vertical | `:is([aria-orientation="vertical"], [orientation="vertical"])` |
| hidden | `[hidden]:not([hidden="until-found"])` |
| ready | `[data-ready]` |
<!-- generated:conditions:end -->

## Why each condition is written this way

<!-- generated:basis:start -->
| State | Why the condition is written this way |
|---|---|
| hover | A disabled form-associated root still matches :hover, and a hover paint over a held state hides that state (ui-interaction-dev, hover.face-only). So the condition carries both guards (D34, D63). |
| active | Check 1: on a custom root, Space and Enter never make :active match. |
| focus | Rarely styled. A focus ring belongs to focus-visible. |
| focus-visible | Check 1: a custom root with tabindex matches :focus-visible after keyboard focus in all three engines. |
| focus-within | The root of a text field is not the focused element; its native input part is. |
| highlighted | With `aria-activedescendant` the item is not focused, so no pseudo-class marks it. |
| disabled | Check 1: :disabled matches a form-associated root, also inside a disabled fieldset, and never a plain or not-yet-defined custom element. `[disabled]` covers those two. |
| read-only | Check 1: :read-only matches every element that is not editable, so it carries no information. |
| required | Check 1: :required never matches a custom element, even with the attribute. |
| checked | Check 1: :checked never matches a custom element. On a native input the `checked` attribute is only the default, so `[checked]` excludes native inputs and options. |
| indeterminate | :indeterminate also matches a radio whose group has nothing checked and a progress bar with no value, so the native arm is limited to checkboxes. |
| pressed | ARIA's pressed is the latched state of a toggle. The moment of pressing is the active state. |
| selected | On a native option the `selected` attribute is only the default, so `[selected]` excludes it. The kit renders options as elements with the option role. |
| current | `aria-current` takes page, step, location, date, time or true; false and the empty string both mean not current. |
| expanded | ARIA puts expanded on the control and nothing on the thing it shows. |
| open | Check 4: a custom element with the popover attribute opens with showPopover() and matches :popover-open. |
| invalid | Raw :invalid matches a required field before the user has touched it. Check 1: :user-invalid is defined for native controls only, and Firefox matches it early on a form-associated custom element, so the native arm is limited to native controls. |
| loading | ARIA's name is busy; the author attribute follows the word kits and Panda use. |
| horizontal | A recipe writes its default orientation with no condition, and uses this one only for the other axis. |
| vertical | As for horizontal. |
| hidden | A recipe's `display` rule defeats the browser's own rule for `hidden`, so every recipe restates it. `until-found` stays findable. |
| ready | Transitions run only once this holds, so the first paint does not animate from the un-upgraded look. |
<!-- generated:basis:end -->

## Names in Panda and in ui-materials

Each state id is also the name of a Panda condition, in camel case. Four conditions equal the selector Panda's own `preset-base` gives that name: focus, focus-visible, focus-within and highlighted. The kit's preset sets the other seventeen and adds `ready`. Panda's selectors were read from its v2 source on 2026-11-12.

Two words mean different things in ui-materials, and the table carries the mapping:

- **pressed.** In ARIA and here, a toggle button that is on. In ui-materials, the moment of being pressed down, which is **active** here.
- **active.** Here, being activated right now. In ui-materials, "live / active" is an indicator that is lit.

<!-- generated:mapping:start -->
| State | Panda condition | Against Panda's own selector | ui-materials state | Used by |
|---|---|---|---|---|
| hover | `hover` | differs; the preset sets it | hover | every interactive component |
| active | `active` | differs; the preset sets it | pressed | button, link, checkbox, radio, switch, tab, menu item, option |
| focus | `focus` | same |  | text field, menu item |
| focus-visible | `focusVisible` | same | focus | every focusable component |
| focus-within | `focusWithin` | same |  | text field, form field, toolbar, menu |
| highlighted | `highlighted` | same |  | option, tree item |
| disabled | `disabled` | differs; the preset sets it | disabled | every interactive component and item |
| read-only | `readOnly` | differs; the preset sets it |  | text field, combobox, spinbutton, slider, checkbox, switch |
| required | `required` | differs; the preset sets it |  | text field, checkbox, radio group, combobox, listbox, spinbutton, switch |
| checked | `checked` | differs; the preset sets it | selected / latched | checkbox, radio, switch, menu item checkbox, menu item radio |
| indeterminate | `indeterminate` | differs; the preset sets it |  | checkbox, menu item checkbox |
| pressed | `pressed` | differs; the preset sets it | selected / latched | button |
| selected | `selected` | differs; the preset sets it | selected / latched | tab, option, row, grid cell, tree item |
| current | `current` | differs; the preset sets it | selected / latched | link, breadcrumb |
| expanded | `expanded` | differs; the preset sets it | open | disclosure, accordion, menu button, combobox, tree item |
| open | `open` | differs; the preset sets it | open | dialog, alert dialog, menu, listbox popup, tooltip, disclosure panel |
| invalid | `invalid` | differs; the preset sets it | invalid | text field, checkbox, radio group, combobox, listbox, slider, spinbutton, switch, form field |
| loading | `loading` | differs; the preset sets it |  | button, feed |
| horizontal | `horizontal` | differs; the preset sets it |  | menu, listbox, tree, radio group |
| vertical | `vertical` | differs; the preset sets it |  | tabs, toolbar, slider, window splitter, menubar |
| hidden | `hidden` | differs; the preset sets it |  | every component |
| ready | none | the preset adds `ready` |  | every component that has a transition |
<!-- generated:mapping:end -->

## Environment conditions

Queries about the device or the user's settings, not about an element. A recipe uses them alongside the states.

<!-- generated:environment:start -->
| Condition | Query | Meaning | Panda condition |
|---|---|---|---|
| forced-colors | `@media (forced-colors: active)` | The system has replaced the page's colours with its own palette. | `highContrast` |
| reduced-motion | `@media (prefers-reduced-motion: reduce)` | The user asked for less motion. | `motionReduce` |
| more-contrast | `@media (prefers-contrast: more)` | The user asked for more contrast. | `moreContrast` |
| coarse-pointer | `@media (pointer: coarse)` | The main pointer is a finger. | `pointerCoarse` |
| can-hover | `@media (hover: hover)` | The main pointer can hover. | none |
| rtl | `:dir(rtl)` | The element's text runs right to left. | `rtl` |
<!-- generated:environment:end -->

Colour modes are not listed. ui-colors owns them and its stylesheet carries their selectors.

## Reserved

States that are known to be coming and are not specified until a component needs them (S13).

<!-- generated:reserved:start -->
| State | Needed by | Note |
|---|---|---|
| placeholder-shown | text field, wave 4 | A state of the native input part, or of an empty select value. |
| autofill | text field, wave 4 | A state of the native input part. |
| dragging | slider and window splitter, wave 4 | `aria-grabbed` is deprecated, so it will be a `data-*` state. |
| ascending, descending | table, wave 5 | From `aria-sort` on a column header. |
| valid | none yet | Check 1: engines disagree on :valid for a disabled or read-only form-associated root. |
<!-- generated:reserved:end -->

## Verification

Every state lists elements its condition must match and must not match. `checks/states/run.mjs` builds each one in a real page and asks the browser. Five states also have cases driven by a real pointer or keyboard: hover, active, focus-visible, focus-within and invalid.

Last recorded run:

<!-- generated:verification:start -->
| Engine | Cases | Failed |
|---|---|---|
| chromium 156.0.8078.4 | 135 | 0 |
| firefox 157.0 | 135 | 0 |
| webkit 27.2 | 135 | 0 |
<!-- generated:verification:end -->

The check has a negative control. Run with `--negative`, it swaps in each known-bad condition below and fails if any of them passes. All five are caught in all three engines.

<!-- generated:mutations:start -->
| State | Known-bad condition | Why it is wrong |
|---|---|---|
| checked | `:is([checked], [aria-checked="true"], :checked)` | the union written in D26; it keeps matching a native checkbox the user unchecked |
| indeterminate | `:is(:indeterminate, [aria-checked="mixed"], [indeterminate])` | unqualified :indeterminate matches an unchecked radio group and an empty progress bar |
| invalid | `:is(:invalid, [data-invalid], [aria-invalid=true])` | Panda's own `invalid`; raw :invalid matches a required field nobody has touched |
| hover | `:is(:hover, [data-hover])` | Panda's own `hover`; it has no guard for a disabled element |
| disabled | `:disabled` | the pseudo-class alone misses a custom element that is not yet defined |
| hover | `:is(:hover, [data-hover]):where(:not(:disabled, [disabled], [aria-disabled="true"]))` | the condition as first confirmed in D34; it still answers on a checked, pressed, selected or open part |
<!-- generated:mutations:end -->

To run both, give the path of any project whose `node_modules` holds Playwright with its browsers:

```bash
node checks/states/run.mjs <project-with-playwright>
```

```bash
node checks/states/run.mjs <project-with-playwright> chromium,firefox,webkit --negative
```

## What this corrects

**The example in D26 is wrong for native checkboxes.** It gives the checked condition as `:is([checked], [aria-checked="true"], :checked)`. A native checkbox that starts checked keeps its `checked` attribute after the user unchecks it, so that selector goes on matching. The matrix uses `[checked]:not(input, option)` for the attribute arm. D26 itself, one condition per state written as a union, stands.

## Decisions this spec introduced

All six were confirmed on 2026-11-12 and are recorded in [decisions.md](../decisions.md).

| # | Decision | Why |
|---|---|---|
| D32 | Kit-managed states with no ARIA name are `data-*` attributes, and `:state()` is not used for styling (S6). | Native elements in three of the four targets cannot hold a custom state. |
| D33 | There is one invalid state, and it means "invalid and the user is due to be told". Raw `:invalid` is not a state. | A required field is `:invalid` before anyone touches it. `aria-invalid` should say the same thing the recipe paints. |
| D34 | hover and active carry the "not disabled" guard inside the condition (S8). | A disabled form-associated root still matches `:hover`. With the guard in the condition, no recipe can forget it. |
| D35 | Interaction states can be forced with `data-hover`, `data-focus`, `data-focus-visible` and `data-active` (S11). | A showcase has to draw every state without a pointer. Panda's own conditions have the same hooks. |
| D36 | expanded and open are two states. expanded belongs to the element that controls; open belongs to the thing that opens. | ARIA puts `aria-expanded` on the control and nothing on what it shows, while the popover and dialog features mark the thing itself. |
| D37 | The author attribute for busy is `loading`, and the component writes `aria-busy`. | It is the word earlier kits and Panda use for a button that is waiting. |

## Open

- **`aria-disabled` on a form-associated root.** The matrix has the component write it on every disabled root. [Check 6](../checks.md#check-6--forms-and-the-accessibility-tree) shows Chromium already exposes a disabled form-associated root as disabled without it. Firefox and WebKit are not tested, so the attribute stays for now.
- **Which condition wins.** When hover, active, checked and disabled all hold, their order in the recipe decides. That order belongs to the CSS contract.
- **Default orientation.** Each manifest says which axis is a component's default; the matrix only names the two conditions.
- **The "used by" column** is a first reading of the APG patterns. Each manifest becomes the authority when it is written.
