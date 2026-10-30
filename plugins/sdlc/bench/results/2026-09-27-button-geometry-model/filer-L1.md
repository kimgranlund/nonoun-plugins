<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None.

## PR title
Move Button onto the shared geometry model (GeometryScope, size via data-size, icon recipe)

## PR body
### Summary
Moves `Button` off its own size recipe variants onto the shared geometry model. Size now comes from a surrounding `GeometryScope` context, not from a recipe variant. The registry and host app stay consistent with the change.

### Changes
- Added `GeometryScope` (`packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx`), exported as `./components/geometry-scope`. Takes required `tier`/`scale`, optional `size`/`radius`. Renders `data-tier`, `data-scale`, `data-radius` on the outer div; `size` renders as `data-size` on an inner wrapper div so it never outranks the tier+scale selector.
- Rewrote `packages/gen-ui/src/recipes/button.recipe.ts`: base geometry now reads `var(--g-height)`, `var(--g-inset)`, `calc(var(--g-inset) / 2)`, `var(--g-text)`, `var(--r-control)`. Variants are `variant: { primary (default), ghost }` and `iconOnly: { true }` (default `false`); no size/tier/scale/radius variant dimension. Colors use semantic tokens from `src/panda/tokens.ts` only.
- Added `iconRecipe` (`packages/gen-ui/src/recipes/icon.recipe.ts`) sizing width/height/font-size from `var(--g-icon)`; registered in `packages/gen-ui/src/panda/recipes.ts` alongside `buttonRecipe`, both wired into `staticCss`.
- `Button` keeps a `size` prop but only sets `data-size` on the button element; the recipe call never receives `size`.
- Regenerated `packages/gen-ui/generated/` via `pnpm gen:registry`: `button.config.ts` schema now accepts `variant` (`primary`/`ghost`, default `primary`) and `iconOnly` (boolean, default `false`) only, and rejects `size`.
- Updated `button.manifest.ts`, `apps/host/src/genui/render-entry.tsx`, `apps/host/src/routes/index.tsx` to drop `size` and pass `iconOnly`.
- Updated `AGENTS.md` wording: size is now described as the geometry model's `data-size` context attribute, not a recipe variant.
- Updated tests: `button.test.tsx`, new `geometry-scope.test.tsx`, `registry/generate.test.ts` (no tests deleted or weakened; the previously-pinned `solid`/`size` expectations were legitimately replaced with the new behavior).
- Geometry source data (`packages/gen-ui/geometry/`, `packages/gen-ui/src/geometry/`) untouched throughout.

### How each was verified
- Step 1 (recipes/components on the geometry model, builder L3/opus): verifier L2 (sonnet, high) passed all 14 criteria, each with red-at-base/green-at-build evidence (e.g. old recipe import fails at base SHA, passes after the change). Vitest suites for `button.test.tsx` and `geometry-scope.test.tsx` confirmed with named `✓` assertions, not vacuous. Lint and prettier guards green.
- Step 2 (manifest, registry regen, host, builder L2/opus): verifier L1 (sonnet, medium) passed all 12 criteria, including manifest schema, `gen:check`, `registry.json` realization variants, generated `ButtonConfigSchema` behavior, host file greps, and the `AGENTS.md` wording change, each cross-checked red-at-base where applicable. `pnpm typecheck` and the registry vitest suite green.
- Step 3 (full gate sweep, builder L2/opus): verifier L1 (sonnet, medium) ran `pnpm lint`, `format:check`, `check-guidance.mjs`, `typecheck`, `test` (35/35), `gen:geometry:check`, `gen:check`, and `build` directly, all green; confirmed no commit was made and `routeTree.gen.ts` was not regenerated.

## Changelog entry
- Button now derives its size from the geometry model (`GeometryScope`'s `data-size` context) instead of a recipe variant; the button recipe gains `iconOnly` and drops `size`, and a new `icon` recipe sizes icon boxes from `var(--g-icon)`.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

## Follow-ups
None.
