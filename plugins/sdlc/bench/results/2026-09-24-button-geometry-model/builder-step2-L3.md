<!-- role=builder level=L3 model=opus effort=high -->
## Status
blocked

## Changes
- packages/gen-ui/src/recipes/button.recipe.ts: rewritten per doc 13 Layer 3. `variant` is primary/ghost, `iconOnly` has only a `true` key, geometry reads `var(--g-*)`/`var(--r-*)`, colors are semantic tokens, and `defaultVariants` is `{ variant: "primary" }`. The header is short, with no Park UI attribution and no em dashes.
- packages/gen-ui/src/recipes/icon.recipe.ts: new `iconRecipe` with `className: "icon"`; width, height and font size come from `var(--g-icon)`.
- packages/gen-ui/src/panda/recipes.ts: imports `iconRecipe`. `recipes` is now `{ button, icon }` and `staticCss.recipes` is `{ button: ["*"], icon: ["*"] }`.
- packages/gen-ui/package.json: added the `"./recipes/icon": "./src/recipes/icon.recipe.ts"` export (not staged; the step-1 lines were already staged).
- packages/gen-ui/src/components/button/button.tsx: now has `size?: Size` and passes it as `data-size={size}`. The recipe is called as `button({ variant, iconOnly })`. The comment is updated to say `size` is a context attribute (Q7), not a variant.
- packages/gen-ui/styled-system/: regenerated with `pnpm --filter @gen-ui/core panda:codegen` (gitignored).
- Nothing committed. No test file or `generated/` file touched.

## Checks
- 🟢 Size/tier/scale/radius variant grep: 0. `colorPalette|textStyle|park-ui` grep: 0.
- 🟢 Recipe import prints `iconOnly,variant primary,ghost true {"variant":"primary"}`.
- 🟢 Var counts in button.recipe.ts: g-height 2, g-inset 2, g-text 1, r-control 1. `var(--g-icon)` in icon.recipe.ts: 3.
- 🟢 px literals across the recipe files: only `2px`. Hex count: 0 in both files.
- 🟢 panda/recipes.ts import prints `button,icon button,icon`. `pnpm vitest run packages/gen-ui/src/panda packages/gen-ui/src/panda.config.test.ts apps/host/src/panda.config.test.ts`: 3 files, 6 tests passed.
- 🟢 `panda cssgen --outfile /tmp/step2.css` exits 0. Counts:

| Pattern | Count |
|---|---|
| `button--variant_primary` | 3 |
| `button--variant_ghost` | 2 |
| `button--iconOnly_true` | 1 |
| `\.icon` | 1 |
| `var(--g-icon)` | 3 |
| `var(--g-height)` | 3 |
| `var(--r-control)` | 4 |
| `genui-recipe` | 1 |
| `data-tier="` | 9 |
| `data-radius="` | 4 |
| `button--size_`, `button--variant_solid`, `button--variant_outline` | 0 each |

- 🟢 `styled-system/recipes` lists `icon.mjs` and `icon.d.ts`. In button.d.ts, `size` count is 0 and `iconOnly` count is 1.
- 🟢 The `./recipes/icon` export check exits 0.
- 🔴 `pnpm typecheck` exits 2: `button.test.tsx(8,20): error TS2322: Type '"solid"' is not assignable to type 'ConditionalValue<"primary" | "ghost"> | undefined'`. The host compiles.
- 🟢 `pnpm lint` exits 0. `pnpm format:check` exits 0.
- 🟢 `pnpm vitest run --exclude '**/button.test.tsx'`: 8 files, 30 tests passed.
- 🔴 `pnpm vitest run packages/gen-ui/src/components/button`: 1 test passed, 0 failed. The handoff expected `renders solid variant class` to fail.
- 🔴 `pnpm gen:check` exits 1 with two stderr lines, where the handoff expected only the first:
  - `REG-03.unresolved-reference core.button at config.size: ...`
  - `REG-03.illegal-realization-value core.button at config.variant.default: default "solid" is not a "variant" member of recipe "recipe.button"`
- 🟢 `git status --porcelain`: no test file and nothing under `generated/`.
- 🟡 The verifier's render check was not run. My throwaway test file was blocked by the sandbox's no-root-deletes hook before it was created, so there is nothing left to clean up.

## Notes
The implementation matches the Do section exactly. It is blocked because three acceptance criteria contradict the handoff's own constraints, and fixing any of them would mean doing something the handoff forbids:

1. **Typecheck.** `packages/gen-ui/tsconfig.json` includes `src/**/*.tsx`, so `pnpm typecheck` type-checks `button.test.tsx`. That test uses `variant="solid"`, which the new recipe types reject. The ways to get exit 0 are all forbidden: edit the test, keep `solid` in the recipe, widen `ButtonProps.variant`, or exclude tests in tsconfig. The planner's note that `pnpm typecheck` exits 0 was wrong.
2. **Button test does not fail.** Panda's generated `button()` does not check variant values, so `button({ variant: "solid" })` still emits the class `button--variant_solid` and the stale test passes at runtime. It is red only at typecheck time. The criterion "fails exactly one test ... shows `button--variant_primary`" cannot hold.
3. **gen:check has a second error.** The manifest's `config.variant.default` is still `"solid"`, so REG-03 also reports `illegal-realization-value`. That is Step 3's manifest work. Step 2's criterion undercounted the intermediate errors.

The planner needs to amend Step 2's criteria:
- Accept that `pnpm typecheck` stays red on `button.test.tsx` only, until the hidden tests replace it.
- Drop the expectation that the button test fails at runtime.
- Allow both REG-03 lines in `gen:check`.

Step 3's criterion (line 78 of planner-L3.md) also expects `renders solid variant class` to fail at runtime, which will not happen for the same reason as item 2.

The working-tree changes are left uncommitted for re-verification.
