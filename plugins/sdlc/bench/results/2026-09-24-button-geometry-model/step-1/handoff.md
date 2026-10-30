## Task goal
Move the Button from its own size variants onto the shared geometry model. Size should come from a surrounding geometry scope, not from a recipe variant. The registry and the host app must stay consistent with the change.

Required surface:
- A `GeometryScope` component exported from `packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` (also exposed as the package export `./components/geometry-scope`). Props: `tier` and `scale` (both required), optional `size` and `radius`, plus normal div props. It renders a div carrying `data-tier`, `data-scale` and `data-radius`. `size` must not go on that element (the tier+scale selector would outrank it); when `size` is given, render it as `data-size` on an inner div that wraps the children.
- `Button` keeps a `size` prop, but it only sets `data-size` on the button element; no `--size_*` recipe class.
- The button recipe has no variant dimension named size, tier, scale or radius. Its `variant` values become `primary` (default) and `ghost`, and it gains a boolean `iconOnly` variant (default false). All geometry properties read `var(--g-*)` / `var(--r-*)` context vars (or calc over them), and colors use semantic tokens from `src/panda/tokens.ts`.
- Add an `iconRecipe` (in `packages/gen-ui/src/recipes/icon.recipe.ts`) for the icon box whose width, height and font size come from `var(--g-icon)`. `buttonRecipe` and `iconRecipe` are the only recipes, and both must be registered with Panda.
- The generated Button config schema accepts runtime fields `variant` and `iconOnly` only (defaults `primary`, `false`), and rejects `size`.

## Step 1: GeometryScope component
level: L1
### Do
Create `packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx`:
- Import types with a relative path, matching sibling code: `import type { RadiusStyle, Scale, Size, Tier } from "../../geometry/geometry.generated.js";` (do not self-reference `@gen-ui/core/geometry`; the package is not resolvable from inside itself).
- `export interface GeometryScopeProps extends ComponentPropsWithoutRef<"div"> { tier: Tier; scale: Scale; size?: Size; radius?: RadiusStyle }`.
- `export function GeometryScope({ tier, scale, size, radius, children, ...props })` renders `<div data-tier={tier} data-scale={scale} data-radius={radius} {...props}>` and, inside it, `size === undefined ? children : <div data-size={size}>{children}</div>`.
- A short comment saying why `size` goes on an inner div: the generated `[data-tier][data-scale]` block (specificity 0,2,0) sets `--g-height: var(--g-md-height)` and would beat the `[data-size]` alias (0,1,0) on the same element, so the alias must sit one level down where it inherits the `--g-lg-*` vars.
- Add `"./components/geometry-scope": "./src/components/geometry-scope/geometry-scope.tsx"` to `exports` in `packages/gen-ui/package.json`.
- Run `pnpm format`. No em dashes. Do not add or edit any test file.
### Acceptance criteria
- `node -e "const e=require('./packages/gen-ui/package.json').exports;process.exit(e['./components/geometry-scope']==='./src/components/geometry-scope/geometry-scope.tsx'?0:1)"` exits 0.
- `grep -c 'export function GeometryScope' packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` prints 1 and `grep -c '@gen-ui/core' packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` prints 0.
- `pnpm typecheck`, `pnpm lint` and `pnpm format:check` each exit 0.
- Verifier render check (a throwaway `*.test.tsx` under `packages/gen-ui/src` with `// @vitest-environment jsdom`, run with `pnpm vitest run <file>`, deleted afterwards): `<GeometryScope tier="product" scale="md" size="lg" radius="pill" id="s">x</GeometryScope>` renders an outer `div` with `data-tier="product"`, `data-scale="md"`, `data-radius="pill"`, `id="s"` and no `data-size` attribute, whose only child is a `div` with `data-size="lg"` containing the text `x`. `<GeometryScope tier="content" scale="lg">y</GeometryScope>` renders one `div` with no `data-radius` and no `data-size` attribute, whose only child is the text `y` (no wrapper div).
- A throwaway `.tsx` containing `<GeometryScope tier="product" />` fails `tsc` (scale is required); one containing `<GeometryScope tier="product" scale="md" />` passes.
- `pnpm vitest run` still reports 9 test files and 31 tests passed.
