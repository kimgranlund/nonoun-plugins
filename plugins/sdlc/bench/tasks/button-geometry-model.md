repo: /Users/kimba/Projects/nonoun/gen-ui-system
base: 20708d08d1235d9eb5bbfc2c3a85a82fa79ed799
solution: 8b1cca3
level: L4
tests_from: 8b1cca3
test_paths:
  - packages/gen-ui/src/components/button/button.test.tsx
  - packages/gen-ui/src/components/geometry-scope/geometry-scope.test.tsx
  - packages/gen-ui/src/recipes/recipes.test.ts
  - packages/gen-ui/src/registry/generate.test.ts
setup: pnpm install --frozen-lockfile
check: pnpm typecheck && pnpm test && pnpm gen:check && pnpm gen:geometry:check

## Goal
Move the Button from its own size variants onto the shared geometry model. Size should come from a surrounding geometry scope, not from a recipe variant. The registry and the host app must stay consistent with the change.

Required surface:
- A `GeometryScope` component exported from `packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` (also exposed as the package export `./components/geometry-scope`). Props: `tier` and `scale` (both required), optional `size` and `radius`, plus normal div props. It renders a div carrying `data-tier`, `data-scale` and `data-radius`. `size` must not go on that element (the tier+scale selector would outrank it); when `size` is given, render it as `data-size` on an inner div that wraps the children.
- `Button` keeps a `size` prop, but it only sets `data-size` on the button element; no `--size_*` recipe class.
- The button recipe has no variant dimension named size, tier, scale or radius. Its `variant` values become `primary` (default) and `ghost`, and it gains a boolean `iconOnly` variant (default false). All geometry properties read `var(--g-*)` / `var(--r-*)` context vars (or calc over them), and colors use semantic tokens from `src/panda/tokens.ts`.
- Add an `iconRecipe` (in `packages/gen-ui/src/recipes/icon.recipe.ts`) for the icon box whose width, height and font size come from `var(--g-icon)`. `buttonRecipe` and `iconRecipe` are the only recipes, and both must be registered with Panda.
- The generated Button config schema accepts runtime fields `variant` and `iconOnly` only (defaults `primary`, `false`), and rejects `size`.
## Context
- Read CLAUDE.md and AGENTS.md first.
- Code lives in packages/gen-ui/src/{recipes,components,registry,panda} and apps/host/src. Geometry types (Tier, Scale, Size, RadiusStyle) are in packages/gen-ui/src/geometry/.
- The button manifest (button.manifest.ts) feeds the registry generator; the host app uses Button and must still typecheck.
## Constraints
- Existing tests your change legitimately breaks may be updated to the new behavior; never delete a test or weaken an assertion to get green. The grader overwrites its own test files after the run, so edits to those do not count.
- Files under packages/gen-ui/generated/ are regenerated with `pnpm gen:registry`, never hand-edited; `pnpm gen:check` must pass.
- Do not change the geometry source data; `pnpm gen:geometry:check` must pass.
