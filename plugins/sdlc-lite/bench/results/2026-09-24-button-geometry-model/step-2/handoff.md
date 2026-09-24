## Task goal
Move the Button from its own size variants onto the shared geometry model. Size should come from a surrounding geometry scope, not from a recipe variant. The registry and the host app must stay consistent with the change.

Required surface:
- A `GeometryScope` component exported from `packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` (also exposed as the package export `./components/geometry-scope`). Props: `tier` and `scale` (both required), optional `size` and `radius`, plus normal div props. It renders a div carrying `data-tier`, `data-scale` and `data-radius`. `size` must not go on that element (the tier+scale selector would outrank it); when `size` is given, render it as `data-size` on an inner div that wraps the children.
- `Button` keeps a `size` prop, but it only sets `data-size` on the button element; no `--size_*` recipe class.
- The button recipe has no variant dimension named size, tier, scale or radius. Its `variant` values become `primary` (default) and `ghost`, and it gains a boolean `iconOnly` variant (default false). All geometry properties read `var(--g-*)` / `var(--r-*)` context vars (or calc over them), and colors use semantic tokens from `src/panda/tokens.ts`.
- Add an `iconRecipe` (in `packages/gen-ui/src/recipes/icon.recipe.ts`) for the icon box whose width, height and font size come from `var(--g-icon)`. `buttonRecipe` and `iconRecipe` are the only recipes, and both must be registered with Panda.
- The generated Button config schema accepts runtime fields `variant` and `iconOnly` only (defaults `primary`, `false`), and rejects `size`.

## Step 2: Button and icon recipes on the geometry model, Panda registration, Button adapter
level: L3
### Do
Level note: the work itself is L1 (confirm files against a fully given spec, run codegen, run checks); two blocked builder files sit in step-2 (`builder-L3.md`, `builder-L2.md`), so the rubric bumps it twice to L3. Both blocks were planner errors in the criteria, not code defects.

State first: the code for this step is already in the working tree, uncommitted, and has passed every code-level criterion twice (step-2/verifier-L2.md, step-2/verifier-L1.md). The only red was the render criterion, which was unsatisfiable as written; it is rewritten below with the exact test body. No code change is expected. Do not rewrite, revert, restage or `git clean` anything except the throwaway test named below: `icon.recipe.ts` is untracked and `geometry-scope.tsx` is only staged, so a bare `git clean`, `git restore` or `git checkout --` destroys finished work. Confirm each file against the spec, run `pnpm --filter @gen-ui/core panda:codegen` and `pnpm format`, then run the checks in order. Edit only where a check below fails. Do not commit.

Spec, `packages/gen-ui/src/recipes/button.recipe.ts` (from `docs/references/geometry-design-system/docs/13-panda-implementation.md` §Layer 3, narrowed to the task handoff):
- Short header, no Park UI attribution, no em dashes: recipe follows doc 13; size, tier, scale and radius are context attributes resolved through `var(--g-*)` and `var(--r-*)`, never recipe variants.
- `className: "button"`. `base` keeps `"--genui-recipe": '"core.button"'` and has `display: "inline-flex"`, `alignItems: "center"`, `justifyContent: "center"`, `height: "var(--g-height)"`, `paddingInline: "var(--g-inset)"`, `gap: "calc(var(--g-inset) / 2)"`, `fontSize: "var(--g-text)"`, `fontWeight: "450"`, `borderRadius: "var(--r-control)"`, `cursor: "pointer"`, `flexShrink: "0"`, `whiteSpace: "nowrap"`, `_focusVisible: { outline: "2px solid", outlineColor: "focusRing", outlineOffset: "2px" }`, `_disabled: { opacity: "0.4", cursor: "not-allowed" }`.
- `variants.variant`: `primary: { bg: "control.surface", color: "control.text", _hover: { bg: "control.hover" }, _active: { bg: "control.active" } }` and `ghost: { bg: "transparent", color: "text.primary", _hover: { bg: "surface.hover" } }`. Nothing else.
- `variants.iconOnly`: `{ true: { width: "var(--g-height)", paddingInline: "0", justifyContent: "center" } }` (only the `true` key; Panda types the prop as `boolean`).
- `defaultVariants: { variant: "primary" }` only (no `iconOnly` default: Panda would emit an empty `button--iconOnly_false` class; the registry default lives in the manifest).
- Forbidden anywhere in the file: a `size`, `tier`, `scale` or `radius` variant dimension; `colorPalette`; `textStyle`; Panda spacing keys for geometry (`h`, `minW`, `px`, `gap: "2"`); hex literals; any px literal other than `1px`, `1.5px`, `2px`, `-2px`. Every geometry property (`height`, `minHeight`, `width`, `minWidth`, `padding*`, `gap`, `fontSize`, `lineHeight`, `borderRadius`) reads `var(--g-*)`, `var(--r-*)`, a `calc(...)` over them, or `0`. Colors are only semantic token names from `packages/gen-ui/src/panda/tokens.ts` or `transparent`.

`packages/gen-ui/src/recipes/icon.recipe.ts`: `export const iconRecipe = defineRecipe({ className: "icon", base: { display: "inline-flex", alignItems: "center", justifyContent: "center", flexShrink: "0", width: "var(--g-icon)", height: "var(--g-icon)", fontSize: "var(--g-icon)" } })`. No variants, same forbidden list.

`packages/gen-ui/src/panda/recipes.ts`: import `iconRecipe` from `../recipes/icon.recipe.js`; `recipes = { button: buttonRecipe, icon: iconRecipe }`; `staticCss.recipes = { button: ["*"], icon: ["*"] }`. `shared.ts`, `preset.ts` and `registry/sources.ts` stay untouched (no manifest references `recipe.icon`). `packages/gen-ui/package.json` `exports` has `"./recipes/icon": "./src/recipes/icon.recipe.ts"`.

`packages/gen-ui/src/components/button/button.tsx`: `import type { Size } from "../../geometry/geometry.generated.js"`; `export interface ButtonProps extends ComponentPropsWithoutRef<"button">, ButtonVariantProps { size?: Size }`; `Button({ variant, iconOnly, size, className, ...props })` returns `<ark.button data-size={size} className={cx(button({ variant, iconOnly }), className)} {...props} />`; the comment says `size` is a native prop mapped to `data-size` (context attribute, Q7), not a recipe variant.

`styled-system/` is gitignored; `pnpm --filter @gen-ui/core panda:codegen` must have run after the recipe edits so `styled-system/recipes` exports `icon` and `ButtonVariantProps` has no `size`.

Known reds by design in this step, none of which the builder may "fix": (1) `packages/gen-ui/tsconfig.json` includes `src/**/*.tsx`, so `button.test.tsx` line 8 (`variant="solid"`) is a type error until the hidden tests replace that file; do not edit the test, keep `solid`, widen the prop type, or exclude tests from tsconfig. (2) `apps/host/src/genui/render-entry.tsx` passes `parsed.variant`, still typed `"solid" | "outline" | "ghost"` by the not-yet-regenerated schema, so the host tsc has exactly that one error until Step 3 regenerates; do not touch host files or `generated/`. (3) `pnpm gen:check` reports two REG-03 lines (the manifest still has `config.size` and `default: "solid"`) until Step 3 edits the manifest. (4) `pnpm typecheck` (the script) short-circuits on the first tsc, so the criteria run the two tsc programs separately. The stale `renders solid variant class` test stays green at runtime because Panda's generated `button()` does not validate variant values; that is expected, not a defect.

Render check, exact file. Write `packages/gen-ui/src/components/button/zz-verify.test.tsx` with this body, run only that file, then remove it with `git clean -f packages/gen-ui/src/components/button/zz-verify.test.tsx` before running `pnpm format:check` or `pnpm lint`. The rendered `x` button is `<button class="button button--variant_ghost button--iconOnly_true" aria-label="x"></button>` (attribute names `class` and `aria-label` only), so the attribute-name assertions are what prove `iconOnly` does not leak to the DOM; nothing asserts on `outerHTML`.

```tsx
// @vitest-environment jsdom
import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { Button } from "./button";

it("button reads geometry from context, not from a size variant", () => {
  render(
    <>
      <Button size="lg">Go</Button>
      <Button variant="ghost" iconOnly aria-label="x" />
      <Button>Plain</Button>
    </>,
  );
  const go = screen.getByRole("button", { name: "Go" });
  expect(go.className).toContain("button--variant_primary");
  expect(go.className).not.toContain("button--size_");
  expect(go.getAttribute("data-size")).toBe("lg");
  expect(go.getAttributeNames().sort()).toEqual(["class", "data-size"]);

  const x = screen.getByRole("button", { name: "x" });
  expect(x.className).toContain("button--variant_ghost");
  expect(x.className).toContain("button--iconOnly_true");
  expect(x.getAttributeNames().sort()).toEqual(["aria-label", "class"]);

  const plain = screen.getByRole("button", { name: "Plain" });
  expect(plain.className).toContain("button--variant_primary");
  expect(plain.className).not.toContain("iconOnly");
  expect(plain.hasAttribute("data-size")).toBe(false);
  expect(plain.getAttributeNames()).toEqual(["class"]);
});
```
### Acceptance criteria
- `grep -Ec '^\s*(size|tier|scale|radius): *\{' packages/gen-ui/src/recipes/button.recipe.ts` prints 0; `grep -cE 'colorPalette|textStyle|park-ui' packages/gen-ui/src/recipes/button.recipe.ts` prints 0.
- `node --import ./scripts/ts-resolve.mjs --input-type=module -e "import('./packages/gen-ui/src/recipes/button.recipe.ts').then(m=>{const v=m.buttonRecipe.variants;console.log(Object.keys(v).sort().join(','),Object.keys(v.variant).join(','),Object.keys(v.iconOnly).join(','),JSON.stringify(m.buttonRecipe.defaultVariants))})"` prints `iconOnly,variant primary,ghost true {"variant":"primary"}`.
- `for v in g-height g-inset g-text r-control; do grep -c "var(--$v)" packages/gen-ui/src/recipes/button.recipe.ts; done` prints four numbers all at least 1; `grep -c 'var(--g-icon)' packages/gen-ui/src/recipes/icon.recipe.ts` prints at least 3.
- `grep -ohE -- '-?[0-9.]+px' packages/gen-ui/src/recipes/*.recipe.ts | sort -u` prints nothing outside `1px`, `1.5px`, `2px`, `-2px`; `grep -cE '#[0-9a-fA-F]{3,8}' packages/gen-ui/src/recipes/button.recipe.ts packages/gen-ui/src/recipes/icon.recipe.ts` prints 0 for both; reading both files, every geometry property listed in Do is a `var(--g-*)`, `var(--r-*)`, `calc(...)` over them, or `0`, and every color is a token name present in `packages/gen-ui/src/panda/tokens.ts` or `transparent`.
- `node --import ./scripts/ts-resolve.mjs --input-type=module -e "import('./packages/gen-ui/src/panda/recipes.ts').then(m=>console.log(Object.keys(m.recipes).sort().join(','),Object.keys(m.staticCss.recipes).sort().join(',')))"` prints `button,icon button,icon`; `pnpm vitest run packages/gen-ui/src/panda packages/gen-ui/src/panda.config.test.ts apps/host/src/panda.config.test.ts` passes (3 files, 6 tests).
- `(cd packages/gen-ui && pnpm exec panda cssgen --outfile /tmp/step2.css)` exits 0 and in `/tmp/step2.css` (`grep -c`): `button--variant_primary` at least 1, `button--variant_ghost` at least 1, `button--iconOnly_true` at least 1, `\.icon` at least 1, `var(--g-icon)` at least 3, `var(--g-height)` at least 1, `var(--r-control)` at least 1, `genui-recipe` at least 1, `data-tier="` at least 9, `data-radius="` exactly 4, and `button--size_`, `button--variant_solid`, `button--variant_outline` each 0.
- `ls packages/gen-ui/styled-system/recipes` lists `icon.mjs` and `icon.d.ts`; `grep -c 'size' packages/gen-ui/styled-system/recipes/button.d.ts` prints 0 and `grep -c 'iconOnly: boolean' packages/gen-ui/styled-system/recipes/button.d.ts` prints 1.
- `node -e "const e=require('./packages/gen-ui/package.json').exports;process.exit(e['./recipes/icon']==='./src/recipes/icon.recipe.ts'?0:1)"` exits 0.
- `pnpm exec tsc -p packages/gen-ui/tsconfig.json --noEmit --pretty false 2>&1 | grep 'error TS' | grep -v 'src/components/button/button.test.tsx('` prints nothing, and `pnpm exec tsc -p packages/gen-ui/tsconfig.json --noEmit --pretty false 2>&1 | grep -c 'button.test.tsx(8,'` prints 1 (the stale `variant="solid"`, red by design).
- `pnpm exec tsc -p apps/host/tsconfig.json --noEmit --pretty false 2>&1 | grep 'error TS' | grep -v 'src/genui/render-entry.tsx('` prints nothing, and `pnpm exec tsc -p apps/host/tsconfig.json --noEmit --pretty false 2>&1 | grep -c 'render-entry.tsx('` prints 1 (stale schema type, cleared by Step 3).
- Render check: with `packages/gen-ui/src/components/button/zz-verify.test.tsx` containing exactly the body in Do, `pnpm vitest run packages/gen-ui/src/components/button/zz-verify.test.tsx` reports 1 file, 1 test passed; then `git clean -f packages/gen-ui/src/components/button/zz-verify.test.tsx` and `git status --porcelain | grep -c zz-verify` prints 0.
- After the throwaway file is gone: `pnpm lint` and `pnpm format:check` exit 0; `pnpm build` exits 0.
- `pnpm vitest run` reports 9 test files and 31 tests passed (the stale `renders solid variant class` stays green at runtime; it is red only at typecheck).
- `pnpm gen:check` exits 1 and `pnpm gen:check 2>&1 | grep '^REG-03\.'` prints exactly two lines: one containing `unresolved-reference core.button at config.size` and one containing `illegal-realization-value core.button at config.variant.default` (known intermediate state until Step 3).
- `git status --porcelain` lists no `*.test.ts`, `*.test.tsx` or `packages/gen-ui/generated/` file, and still lists `A  packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` and `?? packages/gen-ui/src/recipes/icon.recipe.ts`.
