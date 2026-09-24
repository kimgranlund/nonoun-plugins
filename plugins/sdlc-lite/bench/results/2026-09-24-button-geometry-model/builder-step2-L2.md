<!-- role=builder level=L2 model=opus effort=low -->
## Status
blocked

## Changes
None. Codegen regenerated the gitignored `styled-system/`. `pnpm format` changed no tracked files, and `git status --porcelain` is the same as before.

## Checks
- `pnpm --filter @gen-ui/core panda:codegen && pnpm format`: exit 0 🟢
- Recipe variant-dimension grep: 0. `colorPalette|textStyle|park-ui` grep: 0 🟢
- buttonRecipe shape: `iconOnly,variant primary,ghost true {"variant":"primary"}` 🟢
- Var counts: g-height 2, g-inset 2, g-text 1, r-control 1. `var(--g-icon)` in icon.recipe.ts: 3 🟢
- px literals: only `2px`. Hex count: 0 and 0. All colors are tokens in tokens.ts or `transparent` 🟢
- panda/recipes.ts keys: `button,icon button,icon`. Vitest panda subset: 3 files, 6 tests passed 🟢
- `panda cssgen`: exit 0. Counts: variant_primary 3, variant_ghost 2, iconOnly_true 1, `.icon` 1, g-icon 3, g-height 3, r-control 4, genui-recipe 1, data-tier 9, data-radius 4. size_, variant_solid and variant_outline all 0 🟢
- styled-system/recipes has icon.mjs and icon.d.ts. button.d.ts: `size` 0, `iconOnly` 1 🟢
- package.json exports check: exit 0 🟢
- gen-ui tsc: no other errors, `button.test.tsx(8,` count 1 🟢
- host tsc: no other errors, `render-entry.tsx(` count 1 🟢
- `pnpm lint`, `pnpm format:check`, `pnpm build`: all exit 0 🟢
- Render check (zz-verify.test.tsx): FAILED 🔴 on `expected '<button class="button button--variant…' not to contain 'icononly'`. The file was removed with `git clean -f`.
- `pnpm vitest run`: 9 files, 31 tests passed 🟢
- `pnpm gen:check`: exit 1, with exactly the two expected REG-03 lines 🟢
- `git status --porcelain`: no test files or `generated/` listed. `A  geometry-scope.tsx` and `?? icon.recipe.ts` are still present 🟢

## Notes
The render criterion contradicts itself. It requires the `x` button's `className` to contain `button--iconOnly_true`. It also requires `outerHTML.toLowerCase()` not to contain `icononly`. But `outerHTML` includes the class attribute, so that class string lowercases to `icononly` every time.

The code already does what the criterion is after. A dump of the rendered element shows `<button class="button button--variant_ghost button--iconOnly_true" aria-label="x"></button>`, with attributes `class,aria-label` only, so no `iconOnly` prop leaks to the DOM.

Suggested amendment: assert `x.getAttributeNames()` has no name containing `icononly`, or run the `outerHTML` check with the class attribute removed. The other criteria all pass with the work already in the tree, and no code change is needed.
