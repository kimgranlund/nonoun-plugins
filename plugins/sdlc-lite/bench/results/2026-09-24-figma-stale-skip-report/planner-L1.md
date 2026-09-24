<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
When the Figma plugin skips deprecating a stale variable because its `_deprecated/` name is already taken, report the skip to the user in the apply result instead of skipping silently.

## Step 1: Record skipped deprecations at all three sites
level: L2
### Do
In `figma/plugin/code.js` (source only), collect each skipped deprecation as `{ from, to }` at the three places that skip a deprecate when `byName[r.to]` already exists:
- the color path, `reconcileColorCollection` in `applyBundle` (about line 1629). Here the skip is `if (!vr || byName[r.to]) continue;`. Split it so a missing `vr` is still ignored silently, and a taken `byName[r.to]` pushes `{ from: r.from, to: r.to }` onto a local `skippedDeprecates` array.
- the float path, `applyFloatPlans` (about line 1775). The `if (vr && !byName[r.to])` guard gets an else branch that records the skip when `vr` exists and `r.to` is taken.
- the font path, `applyFontPrimitivesModes` (about line 1115), with the same guard change.

Expose the list as `skippedDeprecates` on the returned reports:
- on each `colorReports` entry (`libraryMode: true` and the classic branch, where it is `[]`)
- on the `libraryReport` returned by `applyFontPrimitivesModes` (line 1124)
- on each `libraryReports` entry pushed at line 1783
Use `[]` when nothing was skipped, so the shape stays uniform.

### Acceptance criteria
- `grep -n skippedDeprecates figma/plugin/code.js` shows the field populated at all three skip sites and carried into all three report constructions.
- A skip is recorded only when the source variable exists and the `_deprecated/` target name is taken. A missing source variable stays silent.
- Behaviour is unchanged when no skip occurs: the rename, `preserved`, `deprecates`, and `removed` fields are identical to before.
- `git diff --stat` shows only `figma/plugin/code.js` changed by hand. No test files are edited.

## Step 2: Surface the skips to the user in the apply handler
level: L2
### Do
In the `apply` message handler in `figma/plugin/code.js` (around lines 176-208):
- Gather `skippedDeprecates` from three sources: `r.colorReports` (applyBundle), `fr.libraryReports` (applyFloatPlans), and the `fpr.libraryReport` returned by `applyFontPrimitivesModes` inside the styles `try`.
- Keep the font-primitives report reachable outside that `try` so it can be counted with the others.
- If the combined count is above 0, `console.warn("[Ultimate Tokens] published-library mode: skipped deprecating", n, "stale variable(s), _deprecated/ name already taken:", from names)`. This matches the existing staleModes warnings.
- Also emit a `figma.notify` in the same style and timeout as the missingFonts notice, for example "N stale variable(s) not deprecated — _deprecated/ name already taken: a, b, c…". Emit it once, before the final "Applied…" notify.
- Optionally add `skippedDeprecates: <count>` to the `apply-done` postMessage. Add it only if `test/figma/plugin.mjs` does not deep-equal that message.

### Acceptance criteria
- With a mock file where `_deprecated/X` already exists and `X` is stale in library mode, the apply produces a `figma.notify` and a `console.warn` that name the skipped variable.
- With no collision, no extra notify or warn is emitted.
- `npm test` is green, including `test/figma/plugin.mjs`, with test files untouched.
- After `npm test`, the regenerated `figma/plugin/ui.html`, `src/ui/figma-plugin-assets.js`, and the binder `code.js` are committed as the generators wrote them, never hand-edited.

## Risks
- Existing tests in `test/figma/plugin.mjs` may deep-equal a report or a posted message. Adding `skippedDeprecates` would then fail them, and since test files cannot be edited, the builder would have to attach the field only when non-empty. Check this before finalising.
- The binder `code.js` mirrors parts of the plugin logic under a parity gate. If the same skip logic exists there, its behaviour would diverge. The handoff says it is generated, so treat it as regenerated only.
- Whether the apply-handler notify fires for the float and font paths depends on how the test mock handles `figma.notify`. Verify against the mock.
