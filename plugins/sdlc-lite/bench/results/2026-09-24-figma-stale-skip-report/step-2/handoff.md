## Task goal
When the Figma plugin skips renaming a stale variable because its `_deprecated/` slot is already taken, it currently says nothing. It should report that skip to the user.

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

