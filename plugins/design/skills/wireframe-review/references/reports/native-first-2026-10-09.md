# Native-first research, 2026-10-09

## Evidence and decisions

The installed Chromium passed ten assertions with page JavaScript disabled: declarative popover open, 4px anchor separation, Tab reaches panel link, Escape dismissal, Escape restores trigger focus, outside-click dismissal, named-details exclusivity, command opens modal, command closes modal, and viewport-edge anchor flip above. Test automation reads browser state; the artifact contains no scripts. Saved result: [native-first-2026-10-09.json](native-first-2026-10-09.json). Raw probe and result: /tmp/wf-native-research/check.cjs, artifact.html, results.json. This is a focused native-platform experiment, not the shared component acceptance suite.

Only Chromium was installed in the Playwright runtime. Firefox and WebKit were not exercised. No screen-reader, touch-device, forced-colors or full zoom audit was performed. Feature detection also returned true for base-select and interest invokers; those were not behavior-tested. Existing menu/dialog implementations remain unchanged pending a broader migration test.

## Primary documentation

- [MDN invoker commands](https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API): declarative button commands for dialogs/popovers; documented Baseline 2025. Simple open/close listeners are not inherently necessary.
- [Apple Safari 26.2 release notes](https://developer.apple.com/documentation/safari-release-notes/safari-26_2-release-notes): command and commandfor support. Does not establish the user's installed Safari version.
- [MDN position fallbacks](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position-try-fallbacks): documented Baseline 2026; if every fallback overflows, placement returns to the default. Size constraints/scrolling remain necessary.
- [MDN popover](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/popover): native auto-popover behavior. Nonmodal popover is not a modal dialog or an ARIA command-menu implementation.
- [WAI navigation disclosure example](https://www.w3.org/TR/2021/NOTE-wai-aria-practices-1.2-20211129/examples/disclosure/disclosure-navigation-hybrid.html): ordinary navigation links need not acquire menu roles.
- [MDN customizable select](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Customizable_select): limited availability; richer native picker styling is a distinct feature from static decoration of a traditional select.
- [WebKit customizable select](https://webkit.org/blog/18117/the-golden-rule-of-customizable-select/): preserve option text so behavior and fallback retain meaning.
- [MDN interest invokers](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using_interest_invokers): browser-owned interest interactions, including Escape. Treat as a feature-specific candidate, not a universally supported tooltip contract.
- [WAI hover/focus content](https://www.w3.org/WAI/WCAG21/Understanding/content-on-hover-or-focus): dismissible, hoverable and persistent supplemental content.
- [WAI tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/): expected tab state/focus behavior. Radio tricks do not establish tab conformance.
- [MDN CSS carousels](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Overflow/Carousels): emerging native scroll controls are relevant to carousels, not evidence that all application tabs should use scroll markers.

## Next migration gates

Test popover and dialog recipes in target Safari/Firefox/Chromium; include nested/clipped containers, oversized panels, repeat instances, keyboard and touch paths, and accessible names/states. Keep static select anatomy independent of those newer features. Promote only tested construction paths, retaining explicit limits in context. Package guidance must distinguish researched candidates from shipped behavior.
