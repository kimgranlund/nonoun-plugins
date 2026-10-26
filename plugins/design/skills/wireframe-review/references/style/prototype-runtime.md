# Local prototype controllers

Build trusted author code with `node scripts/generate.mjs manifest.json NEW_OUTPUT_DIRECTORY PLAYWRIGHT --controller controller.js`. Use `--review review.json` for initial feedback. Generation runs mandatory artifact and lint gates before publishing output. Builder syntax-checks the assembled executable and escapes script closing sequences. Never splice into the resulting HTML. Controller code runs in the parent with its privileges; this is not a sandbox for imported feedback or untrusted code. External operations remain outside the local simulation contract.

## Controller interface

Use assets/recipes/prototype-controller.js as a minimal implementation. Customize its unit ID, domain state and callbacks; preserve registerPrototype lifecycle and shared revision helpers. Do not fork the runtime or duplicate review note/snapshot/export bookkeeping inside the controller. See [reuse boundaries](../workflows/reuse-and-measure.md#stable-inputs-and-customization-seams). Call registerPrototype once per leaf unit with:
- unitId: the exact manifest leaf ID.
- initialState: structured-cloneable local state.
- reduce(state, action): return the next cloneable state, no DOM work.
- render(root, state): paint this leaf from state; do not replace the focused input on every keystroke.
- bind({root,on,dispatch,signal}): attach events through on(type,selector,handler). Handler receives event,node,dispatch. Optionally return cleanup for timers/resources.

State keys are unitId + variantId. They persist across page/viewport/scheme rerenders for the tab session and reset on reload. Different proposals are isolated; simultaneous instances of the same leaf/proposal repaint together. Workspace identity within a leaf belongs in its state/reducer. Coherent multi-step flows should live in one leaf when they require shared state; cross-leaf synchronization is not implemented. Do not claim reload persistence or arbitrary mixed-flow compatibility.

## Bounded approval

The runtime unmounts old views and aborts bound listeners. Overview and annotation views render state without event bindings. Review votes remain separate from simulated approval. Helpers revisePrototypePlan, approvePrototypePlan and prototypePlanApproved compare an approved revision with the current plan revision; route every consequential scope/budget/permission edit through revision invalidation. Before coding, list edits that change the approved plan (for example budget, collection permissions, investigation direction or lead path). Each such action must revoke approval. Keep approval and execution distinct when the brief requires separate start/resume actions. Domain validation still belongs in the reducer before approval.

Declare implemented interactions in the manifest and verify them with browser tests on the final artifact. A declaration is not evidence. Static boundaries must be visible and count as missing scope when the brief required working behavior.

## Local save and restore

For local save/apply flows, distinguish the editable draft from the last saved snapshot. Derive current status from that relationship: edits replace prior success messaging with an unsaved/stale status; a failed save does not overwrite the snapshot; restore returns to it. Keep one authoritative current-status message beside the action group, while a retained summary may identify its saved revision. State whether persistence is page-local. See the catalog Save/Restore example. Primary commit, reset and help actions should have distinct emphasis using existing action appearances; do not give every action the primary fill.

Save notifications are derived from the saved revision, not from the notification preference. The preference may stay enabled after edits; every visible message claiming the current draft is saved must clear or become stale when that draft changes, including secondary confirmation banners. If retaining a receipt, label it explicitly as the last saved revision rather than current success. Render all save-related outputs from the same current-versus-saved comparison. A stale main status beside an unchanged “Saved successfully” confirmation is contradictory even if the stored snapshot remains intact.

The catalog now demonstrates this with the Local save confirmations switch and a secondary notice derived from the same saved comparison. Editing hides the notice without disabling the preference; restoring or returning to the saved value may show a notice explicitly stating that the values match. `check-save-status.mjs` exercises preference toggles, edits, invalid saves, restores and an injected stale secondary notice across three engines. This authored example is not proof that fresh generation reliably follows the rule.

Controller previews use allow-same-origin plus allow-scripts so WebKit can invoke trusted parent-installed callbacks. Their explicit script-src 'none' CSP still blocks authored script elements, inline handlers and external code; controller code executes in the parent. Controller-free previews and no-script fallback frames remain script-sandboxed. Never remove the preview CSP or enable unsafe-inline scripts as a workaround. This does not sandbox trusted controller code from the parent.

## User activation and form defaults

The review shell cancels default button/form submission. A controller listening only for `submit` can appear implemented while a user's Save or Start does nothing. Use an explicit `type="button"` and a delegated click handler; validate its form with `reportValidity()` before dispatch. Native button Enter/Space activation produces click. Do not add both click and submit dispatch paths that execute twice. Enter-to-submit from a text field, if required, needs an explicit, tested controller path; it is not supplied by this recipe.

```js
on('click', '[data-review-id="save"]', (event, node, dispatch) => {
  if (node.form && !node.form.reportValidity()) return;
  dispatch({type:'save'});
});
```

Verify observable state change by clicking the actual visible button and by keyboard activation; synthetic `submit` is not user-path evidence. Test invalid inputs, later edits and restore separately.

Minimal optional manifest interaction (replace IDs with existing leaf/element IDs):
```json
{"id":"save-draft","unitId":"booking","variantId":"A","elementId":"save","status":"implemented","action":"Activate Save draft","expectedResult":"Visible saved status reflects the current valid draft","persistence":"session","limitations":["Page-local simulation; reload clears state"]}
```
A declaration remains a promise until observed on the final artifact.

## Revision DOM and runtime fidelity

For a controller revision, keep every render/bind target present in every supported proposal. Required targets must fail clearly when absent; optional targets may be guarded only when that state legitimately omits them. Preserve original fixtures and selected-detail behavior. Generation executes initial controller mounts across declared routes and rejects runtime exceptions; it does not prove later interactions. On the final revision, exercise the new control, empty result and recovery, then the existing selection and consequential action. Record actual visible state changes and runtime errors; static interaction declarations are insufficient. Use verify-rendered.mjs with an affected task module for these paths, retaining previous evidence.

## Committed staged focus

Generated controllers have focusWorkflowStep(form,index,{panelSelector}) from the shared runtime. See [focus and task grouping](components/workflow-patterns.md#focus-and-task-grouping) for ordered panel anatomy and the handler seam. Call only after committed Next/Back visibility changes. Initial mounts, viewport remounts and typing do not request focus. Check actual activation and missing-helper errors separately from startup.

## Supplied API discovery

`component-context.mjs --runtime` returns the authoritative `runtimeAPI` contract from [prototype-api.json](prototype-api.json) with source identity: registration, approval helpers and committed staged focus. It states signatures, lexical controller scope, prerequisites, call timing, return/failure behavior and limits. Recipe-local functions require their declared dependencies; do not infer availability from a catalog example. Validate adoption through actual activation and [independent task acceptance](../evaluation-checks.md#isolated-acceptance-and-delivery-version-2).
