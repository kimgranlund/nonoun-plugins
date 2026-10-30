## Task goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte` (default export) that renders Phosphor icons as an `<i>` element at several weights (regular, bold, and others).
- Props: `name` (Phosphor icon name), `weight` (default `regular`), optional `label`, plus pass-through attributes such as `data-size`.
- Classes: always `icon`; regular weight uses `ph ph-<name>`, other weights use `ph-<weight> ph-<name>` (no bare `ph`).
- Accessibility: without `label` the element is `aria-hidden="true"` with no role; with `label` it is `role="img"` named by the label.
- Styling: load each weight's stylesheet from the jsdelivr CDN for `@phosphor-icons/web@2.1.2` (`.../src/<weight>/style.css`) as a `<link>` in `document.head` marked `data-phosphor-weight="<weight>"`, with an SRI `sha384-` integrity and `crossorigin="anonymous"`. Inject at most one link per weight, only on client mount; SSR must never touch `document`.
- Size comes only from the geometry icon context (font-size, width and height all equal the geometry `icon` value for the current tier/scale/size), applied through a preset recipe.
- Export `Icon` from the package entry and use it for the showcase page's icon-only Button.

## Step 1: Add the `icon` config recipe to the preset and regenerate
level: L2
### Do
- Create `src/lib/preset/recipes/icon.recipe.ts`. Follow the pattern in `button.recipe.ts` (`defineRecipe`, header comment citing the geometry rules):
  - `className: 'icon'`
  - `staticCss: ['*']`
  - `base`: `display: 'inline-flex'`, `alignItems: 'center'`, `justifyContent: 'center'`, `flexShrink: '0'`, `lineHeight: '1'`, `fontSize: 'var(--g-icon)'`, `width: 'var(--g-icon)'`, `height: 'var(--g-icon)'`.
  - `display` must not be `inline`. On an inline `<i>`, width and height are ignored and `getComputedStyle` reports `auto`.
  - No `size` variant, no px literals, no hex colors.
- Register the recipe in `src/lib/preset/index.ts`: `import { icon } from './recipes/icon.recipe.js';` and `const recipes = { button, icon };`.
- Run `pnpm run prepare` to regenerate `styled-system/`. Do not hand-edit generated files.
### Acceptance criteria
- `pnpm run prepare` exits 0.
- `ls styled-system/recipes/icon.mjs styled-system/recipes/icon.d.mts` finds both files.
- `grep -n "icon" styled-system/recipes/index.mjs` shows the icon export.
- `grep -nE "[0-9]+px|#[0-9a-fA-F]{3,6}|size:" src/lib/preset/recipes/icon.recipe.ts` finds nothing.
- `pnpm check` exits 0.

