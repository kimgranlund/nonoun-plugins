# Native behavior and optional enhancement

Choose implementation by required behavior, not visual resemblance. Prefer native HTML semantics, shared CSS and authored anatomy. Use JavaScript for missing behavior or application state, not merely to add decorative slots. Build-time compilation and authored markup must produce the same geometry and native semantics.

## Current construction paths

- Select: author the canonical wrapper/slots or let the artifact builder compile bare selects. Keep the real select, label, value, options and disabled state. For dynamic creation, use the explicit `createSelectControl` builder in `assets/control-markup.mjs` or supply complete authored anatomy; no runtime scanner decorates arbitrary markup. Decorative SVGs are hidden from accessibility APIs and pointer-transparent. The popup remains native. Do not require the review shell for standalone styling.
- Checkbox/radio/switch: retain native inputs and state selectors. Checkbox indeterminate state and group synchronization require scripting. A switch is binary, not mixed.
- Segmented choices: use a named radio group when choosing a value. A tab interface needs tab focus and panel behavior; radio styling alone does not implement tabs.
- Layout, cards, badges and static table structure: HTML/CSS only. Sorting, filtering, live output and saving belong to the consuming application.

## Native recipes and verification

The [native patterns recipe](../../assets/recipes/native-patterns.html) provides explicit declarative paths for destination popovers, anchored placement, dialog commands and named details. Current artifacts use the native path; the removed menu runtime is not a compatibility fallback. The verified baseline is Chromium 151, Firefox 153 and WebKit 26.5. Browser support and measured behavior must be reported by `check-native-patterns.mjs`; source markup alone is not evidence. See the [research evidence](../../../wireframe-review/references/reports/native-first-2026-10-09.md).

Before migrating a component, verify its exact supported-browser floor and behavior:

- Popover: native auto dismissal is suitable for a nonmodal panel. A popover does not supply command-menu roles or arrow-key behavior. Use links for navigation; modal tasks use dialog.
- Anchors: test half-margin separation, repeated instances, scroll, clipping ancestors, viewport edges, RTL and oversized content. Position fallbacks can all fail; constrain panel dimensions and permit scrolling. Detect individual properties, not just one umbrella feature.
- Dialog: declarative show-modal/close commands can replace trivial click listeners where supported. Application validation, cancellation policy and persistence remain separate.
- Tooltips: preserve dismissibility, hoverability and persistence. A hover-only CSS rule is not a complete implementation. Interest invokers remain a candidate until the target browser and assistive-technology path is verified.
- Customizable select and CSS carousel markers: do not promote from feature detection alone. Confirm fallback semantics and keyboard/accessibility behavior for the actual component.

For a recipe, state required anatomy, CSS dependencies, native behavior, optional/required enhancement, application behavior and tested environments. Test static recipes with page scripts disabled. Feature detection proves syntax/API availability, not correctness or accessibility. Preserve usable native fallback content; do not install native and scripted behavior simultaneously without defining which owns state.

## Verified native recipe baseline

The [native-patterns verification report](../../../wireframe-review/references/reports/native-patterns-2026-10-09.md) records 36 no-page-script cases across Chromium, Firefox and WebKit: narrow/wide viewports, small/medium/large geometry and both text directions. Assertions cover half-margin separation, edge flipping, oversized-panel scrolling, native dismissal/focus return, repeated instances, exclusive disclosures and dialog commands. `scripts/check-native-patterns.mjs` generates the exact engine versions and per-case evidence in its output `verification.json`; run it for the target environment. WebKit's macOS default keyboard preference requires Option+Tab to reach links. This is bounded browser evidence, not an assistive-technology audit or support claim for older browser releases.

Anchored panel customization preserves the shared placement, available-space height cap, overflow and half-gutter gap. A viewport-height cap is not interchangeable with the percentage cap inside the anchor-support rule. Consumers may choose a bounded width and content; long content panels keep Close visible during scrolling. Verify containment after expansion and reopening, independently of document overflow.

Use the [content popover recipe](../../assets/recipes/content-popover.html) for long explanatory panels. Use direct sibling `popover__header` and `popover__body` children: the header keeps title and Close outside the scroll region, while the body scrolls under the shared available-space cap. Do not overlay a sticky header on interactive content; automatic focus/pointer scrolling can put controls beneath it. Destination-link menus remain the smaller navigation recipe.

## Maintained JavaScript ownership

| Source | Responsibility | Why it remains |
| --- | --- | --- |
| `assets/recipes/components.js` | Mixed/group checkbox synchronization, range/number/output synchronization, local validation/reset, tabs, density selection, table filtering/sorting/selection, explicitly labelled local check simulation | Native controls own their individual states; the controller coordinates application relationships and missing tab interaction. |
| `assets/prototype-runtime.js` | Local prototype transitions and application simulation | Reviewable application behavior, not decoration or native opening. |
| `assets/app.mjs` | Review selection, feedback, persistence/export/import, iframe measurement/scaling and annotation/navigation mediation | These are review-application workflows, not component styling. |
| `assets/control-markup.mjs` and `scripts/compile-controls.mjs` | Explicit dynamic construction and build-time decoration | Produce canonical anatomy; no DOM-wide runtime scanner is required. |
| `assets/model.mjs` | Pure review-state validation, choice resolution and feedback interchange | No DOM initializer; shared by build validation and the review application. |
| `assets/recipes/prototype-controller.js` and `collection-workflow.js` | Local application draft/approval/save/restore examples | Explicitly owned state transitions; no native popup/disclosure controller. |
| `assets/demos/*.mjs` | Build-time scenario data and HTML authorship | Not a runtime initializer; output delivery does not execute these modules. |
| Generated sheet runtime | Sheet navigation, scheme/size selection, search and fixed-header space measurement | Page application behavior; native select decoration and popup/disclosure opening remain usable without scripts. |

Do not remove these responsibilities merely to reduce script count. No-script specimens should expose honest static content and usable native controls; omit or explicitly disable application actions whose controller is absent. A tab controller is required for tab roles: a static alternative uses headings and links, not inert tab buttons hiding content. Never add a second controller to native disclosure/popover/dialog commands.

The component verifier accepts an engine as its fourth argument. Pointer-opened dialog focus return is platform-dependent when clicking does not focus the trigger. Test keyboard opening from a focused trigger separately; Escape must restore the actual previously focused element. Record installed-browser, assistive-technology and physical-device gaps separately from Playwright engine evidence.

The maintained component catalog includes a no-script presentation: all tab content becomes visible and controller-dependent actions, aggregate choices, synchronized output and table tools are hidden. Native input behavior remains available. Verify with `scripts/check-component-fallback.mjs PLAYWRIGHT OUTPUT`; this is a catalog fallback, not proof that every generated application has a usable no-script path.

Generated reference sheets expose ordinary page links when JavaScript is disabled, hide unavailable search/display controls, and retain source content and native disclosures. `check-sheet-fallback.mjs SHEETS PLAYWRIGHT REPORT` verifies all five pages in three engines. This fallback does not certify arbitrary specimen application actions. The review builder includes a separate static proposal browser when scripts are disabled: native disclosure, isolated scrollable frames and declared page compositions. It hides inactive review chrome and explicitly excludes choices, annotations, export and application simulation. Run `check-shell-fallback.mjs PLAYWRIGHT OUTPUT`; see [shell foundations](../../../wireframe-review/references/shell-foundations.md#scripts-disabled-preview) for the delivery cost and ownership.

Two-region content popovers reserve a scrolling row of at least two local control heights, rather than forcing a fixed minimum on the entire panel. Shared placement first tries side flips, then full-inline-width positions above/below when horizontal room prevents every simple flip from fitting. These fallbacks preserve the half-gutter anchor gap and local viewport margins. Keep the named fallback rules: a height failure can originate from unavailable inline space. Verify the header, usable body, Close and pointer/focus access together at shorter viewports; a contained panel with an inaccessible body is a failure. See the [CSS anchor overflow model](https://www.w3.org/TR/css-anchor-position-1/#overflow).

## Outside the verified native overlay baseline

### Experimental-pattern boundary

The maintained assets do not implement the following candidates. Their status is corpus policy, not a claim about universal browser support. Read this boundary when proposing one of these patterns.

| Candidate | Current status and usable baseline | Evidence required before promotion |
| --- | --- | --- |
| Custom tooltip / interest invoker | Unverified. Keep essential help inline or in an explicit native disclosure; use the content-popover recipe for click-open nonmodal help within its verified baseline. Do not make essential text available only on hover or in `title`. | Keyboard and pointer opening, dismissal without moving focus/pointer, movement into the help without disappearance, persistence, accessible association, touch route and target browser/assistive-technology checks. One owner controls any missing behavior. |
| Customizable select | Experimental in this corpus. Retain the canonical real select, label and native options; its wrapper supplies decoration only. | Value/form submission, required/disabled states, keyboard selection, popup dismissal/focus, accessible name/options, unsupported parsing and native fallback. Rich child markup must not carry the only option text/value. |
| CSS carousel markers/buttons | Experimental in this corpus. Prefer an ordinary list of reachable items and links; do not hide content behind unsupported generated controls. | Complete item access, named navigation, keyboard/focus behavior, selected-item communication, touch and assistive-technology checks. If rotation is requested, verify pause controls and focus/hover suspension separately. |

Feature detection may choose an enhancement, but does not establish these outcomes. No tooltip, customizable-select or carousel runtime is supplied. The [hover-content criterion](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html), [select standard](https://html.spec.whatwg.org/multipage/form-elements.html#the-select-element), [carousel guidance](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) and [CSS overflow draft](https://www.w3.org/TR/css-overflow-5/) inform the checks; they do not certify a local implementation.

`scripts/check-experimental-boundary.mjs` checks that maintained assets have not silently adopted these experimental primitives. It checks source adoption only; passing it does not verify custom tooltip behavior or old-platform compatibility.

Choose a usable baseline before authoring when required overlay features are unavailable or unverified. The [native fallback recipe](../../assets/recipes/native-fallbacks.html) uses ordinary destination links, an inline editable task and native disclosure. It supplies no popup/anchor/dialog commands, feature scanner or opening initializer. Keep meaningful destinations and fields in normal reading order; do not claim modal focus/inertness for the inline task. It intentionally has no save operation: a consuming application supplies a real form/page route or one application controller and verifies it separately.

This is an explicit authoring alternative, not automatic compatibility for every existing native-overlay artifact. Consumers targeting unknown older platforms must select this baseline or provide one owned, verified enhancement/fallback; an inert command button is not acceptable. Run `check-native-fallbacks.mjs PLAYWRIGHT OUTPUT` with page scripts both enabled and disabled. Testing this alternative in current engines does not emulate every old platform. The [per-pattern support record](../../../wireframe-review/references/reports/component-support-2026-10-09.md) preserves those boundaries.

Content popover headers wrap as a group when the title and Close action cannot share the available inline space. The title retains a geometry-derived flex basis, and Close is bounded to the header width with a wrapping label. Never preserve a single header row by shrinking the title to zero or allowing action text beyond the panel. Use `check-popup-swatch-composition.mjs PLAYWRIGHT NEW_OUTPUT` for enlarged long labels in both directions, schemes and densities; its old-header fault must fail.
