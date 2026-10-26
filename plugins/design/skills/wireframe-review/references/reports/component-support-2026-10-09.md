# Authored component support, 2026-10-09

This is a record of bounded authored-recipe evidence, not a minimum-version compatibility promise. Chromium 151.0.7922.34, Firefox 153.0 and WebKit 26.5 were exercised through Playwright. WebKit engine evidence does not certify installed Safari. Exact fixture states and matrix cells are recorded by the named verifiers; not every combination is covered.

The component suite covers 12 width/size/scheme cells and 27 geometry contexts per engine. State-specific suites generally use 390/1399px, both schemes and three geometry sizes. Native patterns additionally exercise LTR/RTL, repeated instances, edge placement, dismissal/focus, named details and dialog commands with page scripts disabled. Reports outside the portable skill retain case-level output and hashes; rerun the commands for the delivery environment.

## Reproduce

Run each `scripts/check-NAME.mjs PLAYWRIGHT OUTPUT` for the suites named below. `check-components.mjs PLAYWRIGHT OUTPUT ENGINE` accepts chromium/firefox/webkit. `check-component-fallback.mjs PLAYWRIGHT OUTPUT` checks all three engines. `check-static-select.mjs SHEETS PLAYWRIGHT` uses a different argument order. The script names and their actual scope are authoritative; an output directory name alone does not prove success.

## Limits

Installed Safari has the bounded pointer/keyboard/geometry evidence below; broader component coverage remains unverified. Assistive technology, physical touch and older-platform behavior remain unverified. Forced colors, 200 percent zoom, reduced motion and complete contrast coverage require their own evidence. Feature detection is not behavioral verification. No pattern is certified solely from a green aggregate component check. Optional tooltip/interest-invoker, customizable-select and carousel-marker behavior remains experimental. Do not expose inert unsupported opening controls or silently install the removed menu initializer.

Per-pattern evidence ownership follows. Geometry/focus/task checks are separate from accessibility conformance.

## choices

Native selection, disabled choices, first-line mark alignment, mixed/invalid application transitions and choice-card paint. Evidence: choice-defaults, field-descriptions and components.

## switch

Native binary input, track geometry, disabled state and script-disabled operation; remote persistence excluded. Evidence: components and component-fallback.

## range

Native range input, local range/number synchronization and static fallback; physical touch and every invalid application policy excluded. Evidence: components and component-fallback.

## fields

Editing, readonly/disabled, invalid boundary ownership and persistent/conditional descriptions; announcement behavior excluded. Evidence: field-descriptions and composed-states.

## actions

Group geometry, native activation/focus, disabled and actual local busy lifecycle; arbitrary operation safety excluded. Evidence: action-overlay-hosts and components.

## navigation

Current link/breadcrumb geometry, tab roving focus and disabled skipping, segmented paint and static section fallback. Evidence: feedback-navigation, breadcrumbs and component-fallback.

## collections

Static table/list semantics, filtering/sorting, retained selection, empty recovery and inherited row geometry. Evidence: list-states and components.

## disclosure

Native toggle/group exclusivity, complete rounded border, open body and focus geometry; unsupported exclusive-group behavior not emulated. Evidence: contained-content and native-patterns.

## feedback

Actual local status lifecycle, labelled progress, recovery, skeleton and divider geometry; screen-reader timing excluded. Evidence: feedback-navigation and components.

## identity

Identity text, image-free avatar geometry and badge paint; arbitrary image-network failures excluded. Evidence: feedback-navigation and components.

## overlay

Hidden/modal dialog and backdrop, focused command opening/Escape return, native destination panel and content-region geometry; older-platform fallback not emulated. Evidence: action-overlay-hosts and native-patterns.

## select

Canonical wrapper with an actual labelled native select; decorative slots have no opening controller. Native input and no-script catalog paths are exercised by components and component-fallback; dedicated select geometry and authored caret are checked by check-select-contract; script-disabled sheet decoration is separately checked by check-static-select. Browser-native option-popup pixels and assistive-technology interaction are not certified. Simulated native popup arrow/Enter value commitment remains unverified in the static-sheet harness; setting the value programmatically is not evidence of that keyboard path.

## navigation-menu

Native destination links, paired unique anchors, control radius, half-inset separation, opening/dismissal and focus are exercised by native-patterns. This is destination navigation, not ARIA command-menu behavior. Older-platform fallback content must be selected and verified separately; the native recipe does not supply a legacy shim.

HTML behavior references: [popover](https://html.spec.whatwg.org/multipage/popover.html), [details/dialog](https://html.spec.whatwg.org/multipage/interactive-elements.html). Specifications define semantics; the authored case records define measured support.

## Environment probes

`check-forced-colors.mjs PLAYWRIGHT OUTPUT` adds current-engine forced-colors/reduced-motion emulation for a small authored control/disclosure fixture. Its raster detectors inspect the actual slider rail and disclosure caret, with separate paint-removal controls. Checkbox/radio state, switch selection, native range keyboard changes, summary focus/open/close and reduced-motion scroll styles are also checked. This does not replace native browser zoom, physical OS palette, installed Safari or screen-reader review. Record unsupported emulation separately; feature-query success alone is not a pass.

System colors in this override are intentional platform values, rather than substitutions for the normal OKLCH token declarations. The [CSS Color Adjustment specification](https://www.w3.org/TR/css-color-adjust-1/) defines the forced-colors palette and adjustment behavior. Text enlargement and reflow require distinct evidence; see [Resize Text](https://www.w3.org/WAI/WCAG21/Understanding/resize-text) and [Reflow](https://www.w3.org/WAI/WCAG21/Understanding/reflow).

The forced-colors fixture currently demonstrates palette forcing in Chromium and Firefox. WebKit reports the active media query but retains ordinary page colors in this harness; those contexts are unsupported/inconclusive, not passing forced-palette tests. The verifier compares actual canvas pixels before trusting its rail/caret detectors. Twenty-four Chromium/Firefox cases and 72 paint/motion-removal detections pass; the 12 WebKit palette contexts remain unverified.

Synthetic doubled-text probes exposed a fixed-height action overflow and unbreakable heading overflow. Shared actions now retain geometry height as a minimum and wrap names; textual fields have a line-height minimum, and headings can break long words. These fixes preserve the default short-control frame. A separate enlargement verifier measures full text-node bounds and deliberately undersized-frame rejection. Supplementary CSS zoom at an extremely narrow effective width remains distinct from native browser zoom and full WCAG reflow.


## Installed-browser and native-zoom follow-up

Installed Safari 26.6.2, using its matching SafariDriver, passes 24 authored contexts: component catalog and equipment collection, actual 390/1399px viewports, both schemes and sm/md/lg geometry. Native keyboard activation checks aggregate selection/clear, range ArrowRight, corrected-field error clearing, save/stale/restore, dialog command/Escape and content popover/disclosure/Close. Equipment rows retain card inset 4u, card group gap 3u, row inset u, mark-to-body gap u/2, metadata gap u and zero duplicated choice padding. This is authored evidence, not generated-interface transfer. An initial driver session returned successful pointer-click commands without observed events and reported document.hasFocus=false. A fresh probe recorded native pointerdown/up/click/input/change and correct aggregate transitions; its full pointer matrix then passed the same 24 contexts. The initial session anomaly remains preserved, and its cause is unproven. No synthetic click was substituted. Initial diagnostic runs and the custom-property measurement correction remain preserved externally under `planning/evidence/installed-safari/`.

Native Page zoom at 200% passes 12 authored catalog contexts in full bundled Chromium 151.0.7922.34: two window widths, both schemes and three sizes. The actual Chrome Settings control reports 2, devicePixelRatio changes from 1 to 2 and the CSS viewport width halves while outer width, computed font size, CSS zoom=1 and visualViewport.scale=1 remain unchanged. Two unzoomed negative calibrations are rejected. Native aggregate/range events, field correction/save/restore, dialog and popup bounds pass. This is native browser zoom, distinct from CSS zoom or synthetic text enlargement; it does not cover installed Safari zoom, Firefox zoom, assistive technology or physical touch. An initial harness used inputValue on an output element and stopped; the corrected run reads its text. Preserve that failure separately from product defects. Case-level evidence is retained externally under `planning/evidence/native-zoom-probe/catalog-corrected/`.


## Scoped delivery follow-up, 2026-10-10

These additional observations concern the recorded current specimens, not every state or platform. Earlier results keep their original fixture identities. Report IDs below refer to external planning/evidence directories, which are not part of the portable corpus. A later documentation change does not turn an older report into a new measurement.

| Pattern | New observed scope | Remaining boundary |
| --- | --- | --- |
| Checkbox, radio and switch | Chromium/WebKit light/dark emulated-touch label activation, disabled non-activation and target floor; component-touch-gap-2026-10-10-1 | Physical devices and Firefox touch unverified |
| Choice validation | Three-engine light/dark invalid/selected/focus reflection; installed Safari26.6.2 native key activation, dashed invalid borders and error-reference clearing/restoration | Accessible-tree output is not screen-reader evidence; full Safari sheet matrix not claimed |
| Disabled range | Three-engine light/dark focus refusal, unchanged value and disabled opacity; disabled-range-gap-2026-10-10-1 | Thumb/rail raster and touch gestures separate |
| Fields/input groups | Three-engine light/dark editing, read-only keyboard refusal/focus, disabled focus refusal/opacity, static invalid border/error association and query keyboard focus-within; field-member-gap-2026-10-10-1 | Static invalid host does not implement application validation |
| Disclosures/dialog | Three-engine light/dark expanded keyboard paths, native coordination, modal autofocus, close/Escape and focus return; expanded-keyboard-gap-2026-10-10-1 | WebKit uses Option+Tab in this preference context; ordinary Tab not passing; browser-chrome trapping and AT separate |
| Account/team panels | Three-engine light/dark native keyboard opening, destination-link Tab access and Escape/focus return; native-navigation-keyboard-gap-2026-10-10-1 | Ordinary navigation panels, not ARIA command menus; WebKit Option+Tab |
| Native select | Three-engine light/dark W/Enter typeahead selects Workshop; recorded follow-up keys do not select disabled Locked | Native popup arrow handling remains unverified by this harness |
| Switch reduced motion | Three-engine light/dark real Space toggling changes thumb position with zero authored transition; six restored-transition faults rejected; reduced-motion-gap-2026-10-10-1 | Computed transition/position observation, not raster animation certification |
| Essential boundaries |18three-engine scheme/size contexts and18surface-matched boundary fault controls; current-control-boundary-gap-2026-10-10-1 | Authored named boundaries only; settle transition paint before sampling; normal slider raster and every interaction combination excluded |

Actual screen-reader observations remain unverified. The user accepted that absence for this delivery, not as a conformance pass. Physical-touch devices, installed Safari native zoom and actual WebKit forced-palette rendering remain unverified; the user explicitly accepted those named limitations for this delivery. This is not a pass and does not waive component behavior or ordinary Safari presentation. The generation cycle's failed thresholds and unrun confirmation are separately accepted limitations, not canonical or efficacy passes.


The presented-page Safari follow-up recorded14of20page/width/scheme contexts. The remaining six wide-page cases are explicitly accepted delivery limitations: Gaps in light mode and all five pages in dark mode at requested1399px. The first remaining case failed driver document-focus qualification; the next five were unrun. Their outcomes remain unverified. This does not certify all Safari presentation or waive component behavior. Case-level records and the user decision are external under installed-safari-presented-pages-gap-2026-10-10-1.

## Historical fixture applicability clarification

The older468-case synthetic enlargement audit names its frozen input sidecar under system-review-sheets-stage-0-2026-10-09/coordinator-checks/component-final-browser. Its sheet CSS matches the final delivered sheet CSS before the subsequent Gaps presentation change; foundation styling and preview sizing runtime differ. Those468observations remain historical. Current full-matrix enlargement applicability is unverified; targeted intrinsic-action and frame checks support only their own recorded contexts, not a refreshed468-case pass.

The catalog-text-contrast-v2 and forced-colors directories preserve both verification.json and index.html. Report-file hashes identify the reports, not their measured fixture. The forced-color report records separate original fixture-markup and concatenated-CSS hashes; both match the corresponding sections extracted from its preserved index.html. This supports that exact historical fixture, not current all-control or physical-palette coverage. The text-contrast report has no original inline fixture binding; its preserved HTML identity is recorded as a follow-up observation, and current-source applicability remains unresolved. These identities and scopes are recorded in the external gaps-content-strategy-2026-10-10-1/audit-followup.json supplement. Do not infer current coverage from report hashes or active media queries. Current boundary-contrast evidence has separate subject bindings and its own limited claims. No new browser checks or conformance conclusion follow from this clarification.
