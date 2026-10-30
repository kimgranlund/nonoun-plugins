## Task goal
When the Figma plugin skips renaming a stale variable because its `_deprecated/` slot is already taken, it currently says nothing. It should report that skip to the user.

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

