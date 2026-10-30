## Task goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte` (default export) that renders Phosphor icons as an `<i>` element at several weights (regular, bold, and others).
- Props: `name` (Phosphor icon name), `weight` (default `regular`), optional `label`, plus pass-through attributes such as `data-size`.
- Classes: always `icon`; regular weight uses `ph ph-<name>`, other weights use `ph-<weight> ph-<name>` (no bare `ph`).
- Accessibility: without `label` the element is `aria-hidden="true"` with no role; with `label` it is `role="img"` named by the label.
- Styling: load each weight's stylesheet from the jsdelivr CDN for `@phosphor-icons/web@2.1.2` (`.../src/<weight>/style.css`) as a `<link>` in `document.head` marked `data-phosphor-weight="<weight>"`, with an SRI `sha384-` integrity and `crossorigin="anonymous"`. Inject at most one link per weight, only on client mount; SSR must never touch `document`.
- Size comes only from the geometry icon context (font-size, width and height all equal the geometry `icon` value for the current tier/scale/size), applied through a preset recipe.
- Export `Icon` from the package entry and use it for the showcase page's icon-only Button.

## Step 1: Icon recipe in the preset
level: L2
### Do
- Create `src/lib/preset/recipes/icon.recipe.ts` exporting `icon = defineRecipe({ className: 'icon', staticCss: ['*'], base: {...} })`. Copy the header comment style from `button.recipe.ts`.
- Base styles:
  - `display: 'inline-flex'`, `alignItems: 'center'`, `justifyContent: 'center'`, `lineHeight: '1'`, `flexShrink: '0'`.
  - `fontSize: 'var(--g-icon)'`, `width: 'var(--g-icon)'`, `height: 'var(--g-icon)'`, written in exactly the `key: 'var(--g-icon)'` shape.
  - No px literal, no hex, and no `size` variant (CLAUDE.md rules 1, 2, 5).
- The recipe has no variants. The Phosphor classes (`ph`, `ph-<weight>`, `ph-<name>`) are added by the component, not the recipe.
- Register it in `src/lib/preset/index.ts`: `import { icon } from './recipes/icon.recipe.js';` and `const recipes = { button, icon };`.
- Run `pnpm run prepare` so that `styled-system/recipes/icon.mjs` is generated. Never hand-edit `styled-system/` or `geometry.generated.ts`.
### Acceptance criteria
- `test -f src/lib/preset/recipes/icon.recipe.ts && grep -q "className: .icon." src/lib/preset/recipes/icon.recipe.ts`
- `for k in width height fontSize; do grep -qE "$k: .var\(--g-icon\)." src/lib/preset/recipes/icon.recipe.ts || exit 1; done`
- `test -f src/lib/preset/recipes/icon.recipe.ts && ! grep -nE "[0-9]px|#[0-9a-fA-F]{3,8}\b|^\s*size\s*:" src/lib/preset/recipes/icon.recipe.ts`
- `grep -qF "./recipes/icon.recipe.js" src/lib/preset/index.ts && grep -qE "const recipes = \{[^}]*\bicon\b" src/lib/preset/index.ts`
- `test -f styled-system/recipes/icon.mjs`
- (guard) `pnpm exec vitest run src/lib/Button` exits 0 (the Button recipe still resolves after the preset change).
