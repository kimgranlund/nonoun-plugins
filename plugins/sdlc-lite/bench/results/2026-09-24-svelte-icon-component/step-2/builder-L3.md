<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `src/lib/Icon/Icon.svelte`: new. Module script exports `IconWeight` and `IconProps`, holds the per-weight `{ href, integrity }` map with the SRI values from the handoff, and defines `ensurePhosphorStylesheet`. The instance script calls it only inside `$effect`. Classes are `icon()` plus `ph ph-<name>` for regular or `ph-<weight> ph-<name>` for other weights, then `className` if given. The a11y attributes come after `{...rest}`.
- `src/lib/Icon/index.ts`: new barrel exporting `Icon`, `IconProps` and `IconWeight`.
- `src/lib/index.ts`: added `export { Icon, type IconProps, type IconWeight } from './Icon/index.js';`.
- `src/lib/Icon/Icon.behavior.svelte.spec.ts`: new, 8 tests:
  - regular and bold classes
  - caller class and attribute pass-through
  - `aria-hidden` with no role when there is no label
  - `getByRole('img', { name })` when there is a label
  - exactly one link each for regular and bold, checking href, `sha384-` integrity and `crossorigin`
  - the 27-cell resolved-CSS matrix for fontSize, width and height, asserting that 27 cases ran
  - a negative control: a bare `<i>` does not get the icon width

## Checks
- `pnpm vitest run src/lib/Icon`: 1 file, 8 tests passed. The hidden `Icon.svelte.spec.ts` is not in the tree, so it was not run.
- `pnpm vitest run src/lib/Button`: 2 files, 11 tests passed.
- `pnpm check`: exit 0, "799 FILES 0 ERRORS 0 WARNINGS".
- `pnpm lint`: exit 0. Prettier reports clean, and eslint printed nothing.
- `grep -n "Icon" src/lib/index.ts`: line 3 shows the export.
- `grep -nE "^\s*(document|ensurePhosphor)" src/lib/Icon/Icon.svelte`: the only hit is line 68, `ensurePhosphorStylesheet(weight);`, inside the `$effect` block (lines 66-68). No `document` access at module top level.
- `pnpm build`: exit 0, and publint printed "All good!".
- `pnpm dlx @sveltejs/mcp svelte-autofixer ./src/lib/Icon/Icon.svelte`: no issues. It made one generic suggestion about calling a function inside `$effect`. I ignored it because `ensurePhosphorStylesheet` changes only `document.head` and never assigns reactive state.

## Notes
- Links are added to `document.head` and never removed on unmount, so they stay there across tests in the same browser session. The one-link-per-weight test depends on that: the regular link from earlier tests must still be the only one.
- The showcase page's icon-only Button was not changed. That work belongs to a later step, not this handoff.
- The step-1 recipe files (`icon.recipe.ts` and the `preset/index.ts` diff) are still uncommitted in the worktree. This step did not commit anything.
