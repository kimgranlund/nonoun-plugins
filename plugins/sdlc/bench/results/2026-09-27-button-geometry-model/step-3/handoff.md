## Task goal
Move the Button from its own size variants onto the shared geometry model. Size should come from a surrounding geometry scope, not from a recipe variant. The registry and the host app must stay consistent with the change.

Required surface:
- A `GeometryScope` component exported from `packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` (also exposed as the package export `./components/geometry-scope`). Props: `tier` and `scale` (both required), optional `size` and `radius`, plus normal div props. It renders a div carrying `data-tier`, `data-scale` and `data-radius`. `size` must not go on that element (the tier+scale selector would outrank it); when `size` is given, render it as `data-size` on an inner div that wraps the children.
- `Button` keeps a `size` prop, but it only sets `data-size` on the button element; no `--size_*` recipe class.
- The button recipe has no variant dimension named size, tier, scale or radius. Its `variant` values become `primary` (default) and `ghost`, and it gains a boolean `iconOnly` variant (default false). All geometry properties read `var(--g-*)` / `var(--r-*)` context vars (or calc over them), and colors use semantic tokens from `src/panda/tokens.ts`.
- Add an `iconRecipe` (in `packages/gen-ui/src/recipes/icon.recipe.ts`) for the icon box whose width, height and font size come from `var(--g-icon)`. `buttonRecipe` and `iconRecipe` are the only recipes, and both must be registered with Panda.
- The generated Button config schema accepts runtime fields `variant` and `iconOnly` only (defaults `primary`, `false`), and rejects `size`.

## Step 3: Gates green
level: L2
### Do
Under node 24 (`. "$HOME/.nvm/nvm.sh" && nvm use`) run every gate of `pnpm check` one by one: `pnpm lint`, `pnpm format:check`, `node scripts/check-guidance.mjs`, `pnpm typecheck`, `pnpm test`, `pnpm gen:geometry:check`, `pnpm gen:check`, `pnpm build`. Fix any red that Steps 1 and 2 introduced (unformatted new files, host types, a stale test expectation) without deleting or weakening a test, without hand-editing `packages/gen-ui/generated/` (run `pnpm gen:registry`), and without changing geometry source data (`packages/gen-ui/geometry/component-geometry.csv`, `packages/gen-ui/src/geometry/`). `pnpm build` only writes the gitignored `apps/host/dist`; if it reports `routeTree.gen.ts` regenerated, a route file changed and that is a defect to undo, not to commit. Never commit.
### Acceptance criteria
- (guard) `pnpm lint`
- (guard) `pnpm format:check`
- (guard) `node scripts/check-guidance.mjs`
- (guard) `pnpm typecheck`
- (guard) `pnpm test`
- (guard) `. "$HOME/.nvm/nvm.sh" && nvm use >/dev/null && pnpm gen:geometry:check`
- (guard) `. "$HOME/.nvm/nvm.sh" && nvm use >/dev/null && pnpm gen:check`
- (guard) `pnpm build`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- packages/gen-ui/src/geometry packages/gen-ui/geometry)" && test -z "$(git ls-files --others --exclude-standard -- packages/gen-ui/src/geometry packages/gen-ui/geometry)"`
