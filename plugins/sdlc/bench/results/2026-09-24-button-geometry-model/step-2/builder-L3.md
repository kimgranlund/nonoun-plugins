<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- None. Every step file already matched the spec, so no code changed.
  - `button.recipe.ts`, `icon.recipe.ts`, `panda/recipes.ts` and `button.tsx` are unchanged. The `./recipes/icon` export in `package.json` is unchanged.
  - Codegen regenerated `packages/gen-ui/styled-system/`, which is gitignored.
  - `pnpm format` changed no files.
  - The throwaway `zz-verify.test.tsx` was written, run, and removed with `git clean -f`.

## Checks
- Recipe variant dimensions: `grep -Ec '^\s*(size|tier|scale|radius): *\{'` on `button.recipe.ts` printed 0. The `colorPalette|textStyle|park-ui` grep printed 0.
- Recipe shape: the node import printed `iconOnly,variant primary,ghost true {"variant":"primary"}`.
- Geometry vars: `button.recipe.ts` counts were g-height 2, g-inset 2, g-text 1, r-control 1. `icon.recipe.ts` had 3 `var(--g-icon)`.
- Literals: the px grep printed only `2px`. The hex grep printed 0 for both files.
- Colors: all 7 color tokens exist in `tokens.ts` (read at lines 42-79): `control.surface`, `control.text`, `control.hover`, `control.active`, `text.primary`, `surface.hover` and `focusRing`.
- Geometry properties: I read both files. Every geometry property is `var(--g-*)`, `var(--r-*)`, `calc` over them, or `0`.
- Registration: the `panda/recipes.ts` import printed `button,icon button,icon`. The panda vitest subset passed, 3 files and 6 tests.
- `panda cssgen --outfile /tmp/step2.css` exited 0. Counts:

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

- Generated files: `styled-system/recipes` has `icon.mjs` and `icon.d.ts`. `button.d.ts` has 0 `size` and 1 `iconOnly: boolean`.
- `./recipes/icon` export check: exit 0.
- gen-ui tsc: the filtered error grep printed nothing. The `button.test.tsx(8,` count was 1, which is red by design.
- host tsc: the filtered error grep printed nothing. The `render-entry.tsx(` count was 1, which is red by design.
- Render check: the handoff's exact body passed, 1 file and 1 test. After `git clean -f`, the zz-verify count in `git status` was 0.
- `pnpm lint` exited 0, `pnpm format:check` exited 0, `pnpm build` exited 0.
- `pnpm vitest run`: 9 files and 31 tests passed.
- `pnpm gen:check` exited 1 with exactly two `REG-03.` lines, both expected: `unresolved-reference core.button at config.size` and `illegal-realization-value core.button at config.variant.default`.
- `git status --porcelain`: no test files and no `generated/` files are listed. `A  packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` and `?? packages/gen-ui/src/recipes/icon.recipe.ts` are both still there.

## Notes
- Nothing is committed, as the handoff says.
- `package.json` shows `MM`: the `./components/geometry-scope` export is staged and the `./recipes/icon` export is unstaged. Both are in the working tree. I left the index as it was.
- The three reds by design (the stale test type error, the host `render-entry` type error, and the two REG-03 lines) are still there and should clear in Step 3.
