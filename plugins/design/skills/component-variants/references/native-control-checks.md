# Native-control checks

Use for native-dialog dismissal or an ambiguous native-select keyboard failure. Component code owns focus and keyboard behavior; no shared helper rewrite is implied.

## Native modal authoring

Preserve the repaired sequence, using the actual opener in its owner document:

```js
function dismiss() {
  dialog.close();
  trigger.focus();
}
dialog.addEventListener('cancel', event => {
  event.preventDefault();
  dismiss();
});
cancelButton.onclick = dismiss;
// Commit selection, then dismiss() through the same path.
```

An external trigger is inert during `showModal()`. Do not move `trigger.focus()` before `dialog.close()`, or transplant the nonmodal hide/focus sequence into this path. Avoid duplicate dismissal handlers. When the opener is removed, choose a live logical destination explicitly.

## Actual Safari regression

1. Preserve source hashes and a fresh copy. Record Safari version, viewport, theme, requested/measured component width and initial active element. Use actual Safari, not Chromium or a WebKit substitute.
2. From a freshly loaded page, pointer-activate the native modal trigger, then verify the dialog is open and search is focused. Press Escape through browser input. Assert `dialog.open === false` and `dialog.ownerDocument.activeElement === trigger` after dismissal. Reopen independently for Cancel and selection; check the selected outcome and the same closed/focus result.
3. In a separate negative-control copy, change only the dismissal order to `trigger.focus(); dialog.close();`. Use the same fresh-page starting focus and pointer-opening path; do not pre-focus the trigger synthetically. The negative must fail restoration while the repaired sequence passes. If browser automatic focus restoration makes both pass, report a nondiscriminating control rather than a verified regression check. Retain both sources and failures.
4. Save observations outside the conversation. A pass covers the exercised environment and paths, not all browser versions or assistive technology. Test requested width/theme conditions separately when relevant; do not count repeated configurations as independent failure modes.

## Native-select comparison before a keyboard change

Use the unchanged component and a minimal native `<select>` with the same options, order and initial value in the same browser/session. Record browser/version, headful/headless mode, input method, actual focus, observed popup-open state, exact keys, selected value and downstream component effect.

Run separately from reset state:

- Focus with the popup closed, then ArrowDown/Enter. Observe whether the first ArrowDown opens the menu or advances its option; do not assume one platform's behavior.
- Explicitly open both native menus by the same pointer or keyboard action, confirm opening, then ArrowDown/Enter.
- Typeahead as its own scenario. A typeahead pass does not repair or reclassify the arrow result.

Keep control and component focus/opening conditions equivalent. If both exhibit the same behavior, there is no evidence of a component-specific defect. If only the component differs, inspect its event handlers before proposing a rewrite. An interactive-browser result does not explain a historical headless failure without a matched test there; retain the unresolved cause. Label synthetic setters as synchronization probes under the template contract, not native-menu operation.
