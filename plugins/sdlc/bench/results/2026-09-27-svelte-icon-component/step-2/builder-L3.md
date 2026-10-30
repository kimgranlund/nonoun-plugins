<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `src/lib/Icon/Icon.svelte`: new. The module script holds `IconWeight`, `IconProps`, the `PHOSPHOR_SRI` map with all six hashes, and `ensurePhosphorStylesheet`. The instance script calls that helper inside `$effect`. It uses the `icon()` recipe plus the Phosphor classes (a bare `ph` only for regular), spreads `rest` first, and sets the a11y attributes after it.
- `src/lib/Icon/index.ts`: new. Re-exports `Icon`, `IconProps` and `IconWeight`.
- `src/lib/Icon/Icon.svelte.spec.ts`: new client spec with 9 tests. It covers the regular and bold class sets, a caller class, aria-hidden with no role, role img found by name, that `rest` cannot override the a11y attributes, `data-size` pass-through, one link per weight (href, `sha384-` integrity, crossorigin), and font-size, width and height equal to `row.icon` for all 27 `geometryRows` cells.
- `src/lib/Icon/Icon.ssr.spec.ts`: new server spec with 2 tests. It renders through `svelte/server` in node, with no `document`, and checks for `<i`, `ph-house`, `aria-hidden="true"`, and for a labelled bold icon `role="img"` and `aria-label`.

## Checks
- `pnpm exec vitest run src/lib/Icon`: 2 files passed, 11 tests passed.
- `grep -rqF "https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/" src/lib/Icon`: exit 0.
- `grep -rqF` for both the regular and bold `sha384-` hashes, chained with `&&`: exit 0.
- `grep -qF "export { default as Icon }" src/lib/Icon/index.ts`: exit 0.
- `test -f` on both spec files `&& grep -qF "svelte/server" src/lib/Icon/Icon.ssr.spec.ts`: exit 0.
- `grep -n document src/lib/Icon/Icon.svelte`: the only code lines that use `document` are inside `ensurePhosphorStylesheet` (lines 31, 33, 39), and the only caller of that helper is the `$effect`. The other two hits are comments.
- Extra, not in the criteria: `pnpm exec prettier --check src/lib/Icon` passed; `pnpm exec eslint src/lib/Icon` exit 0; `pnpm check` gave 0 errors and 0 warnings.

## Notes
- Step 1's uncommitted work is still in the tree and was not touched: `src/lib/preset/recipes/icon.recipe.ts` and the edit to `src/lib/preset/index.ts`. This step depends on it, because the `icon` recipe comes from `styled-system/recipes`.
- `class` is passed as a Svelte 5 clsx-style array (`[icon(), ph|ph-<weight>, ph-<name>, className]`), not joined into a string, so a caller `className` can be any `ClassValue`. The specs compare sorted `classList`, so class order is not asserted.
- The one-link-per-weight test depends on `document.head` not being cleaned between tests in the same file. The "exactly 1" count is meaningful because at least three regular renders and one bold render run before the check.
- Nothing is exported from `src/lib/index.ts` yet and the showcase page does not use Icon. The task goal assigns both, but they are not in this step's Do.
