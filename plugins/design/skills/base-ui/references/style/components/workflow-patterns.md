# Workflow peers

Retrieve `component-context.mjs combobox|drawer|stepper` and `demonstration-context.mjs` with the same ID. Source markup is in `assets/recipes/components.html`; geometry in `assets/wireframe.css`; scoped enhancement in `assets/recipes/components.js`. Source sheets derive the examples from the specimen registry, including exact implementation, contract and authored guidance.

## Searchable selection

Use for one value from a local bounded set. The native select remains authoritative for values and disabled options. Enhancement shows a labelled input/listbox; active suggestion and committed selection are different. Arrow keys navigate available results, Enter/pointer commits, Escape/blur/Tab discard an uncommitted query. No matches is explicit. Composition events do not prematurely filter IME text. Do not attach interactive actions inside an option. No remote fetching, multi-select, virtualization or arbitrary free text is provided.

## Drawer

A modal navigation panel composes the existing dialog geometry. The browser owns modal focus containment, background inertness and Escape. Explicit Close returns focus to the opener; selecting a destination closes the drawer and focuses that destination. Inline navigation remains available before enhancement. No custom focus trap, drawer animation or nested-modal stack is introduced.

## Staged form

Ordinary sections and fields remain visible without scripts. Enhancement shows one section with ordered progress, Back and Continue. Invalid fields block advancement; Back preserves entered values; final save checks all steps and stores a page-local `workflowSavedDraft` snapshot on the form. Subsequent edits show unsaved status. Nothing is sent and reload persistence is not provided. Branching, server validation and approval/execution workflows need task-specific reducers.

## Lifecycle and reuse

`mountWorkflowPatterns(root)` is defined by the catalog controller and returns cleanup. It binds only descendants of root and guards repeated mounts. Call cleanup before disposing a root; it removes listeners and restores fallback content. The catalog mounts once automatically. Do not copy document-wide handlers into independent proposals.

For review artifacts, load the workflow controller through `generate.mjs --controller`, then bind scoped enhancement inside `registerPrototype.bind` and return its cleanup. The prototype's reducer/render must own any state that must survive switching proposals or rerendering; the standalone catalog enhancement alone does not promise that persistence. Keep a whole staged workflow in one leaf. Declare interactions and test the final artifact. The adapter is [workflow-controller.js](../../../../wireframe-review/assets/recipes/workflow-controller.js): concatenate it after components.js and call `registerWorkflowExample("ACTUAL_LEAF_ID")`. Run `check-workflow-controller.mjs PLAYWRIGHT NEW_OUTPUT` for remount/isolation evidence and `check-workflow-generated.mjs GENERATED_DIR PLAYWRIGHT NEW_REPORT` for the maintained example in the final review shell.

Use the native select when filtering is unnecessary, an inline sidebar when modal interruption is unnecessary, and a single form when staging does not help the task. The shared 3u card/group, 2u content and 1u related hierarchy remains independent of inline control density.

Interaction references: [W3C combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) and [modal dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/). Automated checks are bounded evidence, not assistive-technology certification.

Minimal ordered progress is a fallback only when explicitly requested; it retains native numbering once and inside each item. Generated staged forms default to the adaptive anatomy below.

## Adaptive indicator

Use the explicit indicator/label slots from the stepper contract. The indicator is informational; Back/Continue own navigation. Number/check and connectors are decorative, while the ordered list, title, visible state and aria-current communicate progress. Completed steps replace their number with the bundled Phosphor check. Upcoming remains readable and is not disabled. The form establishes inline-size containment; below 36rem it presents a vertical sequence, above it horizontal tracks with centered labels below indicators. No arbitrary row wrapping. Browsers without container queries retain the vertical layout. Keep DOM order unchanged. CSS owns presentation; the controller owns validity, state, value retention and focus on the new panel heading. Final save uses an explicit button click so cancelled form defaults in the review shell do not swallow activation.

Design references: [MUI anatomy](https://mui.com/material-ui/react-stepper/), [USWDS progress semantics](https://designsystem.digital.gov/components/step-indicator/), [Carbon alignment](https://www.carbondesignsystem.com/building-blocks/core/components/progress-indicator/guidelines). These inform our pattern; our geometry and native semantics remain authoritative.

## Focus and task grouping

On an actual Next/Back stage transition, retain entered state, render/show the destination panel, then focus its [data-step-heading] (or first h1-h6), with tabindex=-1. Repeat focus after a controller replaces that DOM; focusing a removed node before render loses focus to BODY. Initial mount and ordinary input rerenders must not steal focus. Invalid advancement keeps focus on the invalid input and the reducer retains the current step, including whitespace-only required titles. Reporting validity must not be followed by an unconditional transition. When a page heading and a panel heading coexist, focus the destination panel heading. Test Next and Back independently, so failed Next does not hide Back evidence. The generated runtime supplies focusWorkflowStep(form,index) before author controllers; no catalog script concatenation is needed for this helper. Ordered panels use [data-step] or [data-stage]; custom anatomy passes {panelSelector: "YOUR_SELECTOR"}. Call it after dispatch commits visibility, from the actual Next/Back handler, never unconditionally in render. It returns false when the destination is missing, disconnected or hidden. Verify actual heading focus and runtime errors after activation; startup alone cannot exercise the handler.

Collection workflows distinguish catalogue, derived summary and draft actions through semantic groups. Within the active stage use section__flow for task boundaries, flow__root for fields and heading-group__root for related text. A desktop split may put catalogue beside summary when useful; otherwise bound reading width with content__root instead of leaving a narrow content strip in an unbounded card. Keep the summary next to its controlling choices and draft actions with the delivery fields; retain this order when stacking. Use page__root only at the outer page for 4u margin; do not substitute card padding or a larger universal gap for grouping.

## Rendering options

On the adaptive ol, data-step-orientation selects horizontal or vertical; omit it (or use adaptive) for container-based switching. data-step-label-position selects inline or center; omit it for orientation defaults: horizontal center, vertical inline. Horizontal inline draws the connector after the label; horizontal center distributes equal tracks with space-around and joins marker edges. Vertical inline shares one marker rail. Vertical center centers each marker and its label in the container, with connectors only between item groups so text stays clear. Choose explicit orientation for a known container; retain adaptive for variable-width layouts. These are CSS presentation options, not navigation modes.

Custom reducer handler seam (replace IDs and form selector; validate advancement first):
```js
on('click', '[data-review-id="next"]', () => {
  dispatch({type:'step', step:1}); // synchronous committed render
  if (!focusWorkflowStep(root.querySelector('form'), 1)) throw Error('Missing visible destination heading');
});
```
Use the corresponding committed index for Back. Keep initial mount and input changes free of focus requests. If a controller schedules its render asynchronously, invoke the helper after that render completes, not before it.

Run `check-staged-focus.mjs GENERATED_DIR PLAYWRIGHT NEW_REPORT` for a custom two-stage generated booking flow: committed Next/Back heading focus, typing, retained choice, viewport remount and runtime errors across three engines. It assumes visible Continue/Next, Back and a named contact field; adapt an affected task module for other workflows rather than claiming unmatched paths pass.

## Summary beside a form

Use the responsive grid in `assets/recipes/collection-workflow.html` for a choice catalogue plus derived summary. At narrow widths the summary follows choices in normal flow; do not overlay it with absolute positioning, grid-row overlap or fixed heights. Preserve wrapped labels and populated summary. Verify native pointer activation at 390px and 320px, then keyboard reachability; focus alone cannot prove unobstructed activation.

The bounded `assets/recipes/booking-composition.html` shows a page gutter plus responsive sibling-card gap. The exact stepper demonstration remains authoritative for step indicator, number/check, title/state and aria-current anatomy. Do not substitute a plain numbered list bearing only stepper__root.

For a minimal stateful required-title workflow, use [title-request.html](../../../assets/recipes/title-request.html) with [title-request.js](../../../assets/recipes/title-request.js), replacing the actual leaf ID. The reducer owns required-title transition eligibility; committed handlers use the runtime focus helper. This is a maintained recipe, not an evaluated-output repair.
