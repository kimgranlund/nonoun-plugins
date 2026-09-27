<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
Add an accessible Phosphor `Icon` component (`src/lib/Icon/Icon.svelte`) that is sized by a preset `icon` recipe reading only `var(--g-icon)`, injects one SRI-pinned CDN stylesheet per weight on client mount, is exported from the package entry, and replaces the showcase's icon-only Button glyph.

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

## Step 2: Icon component, stylesheet injection, and specs
level: L3
### Do
Follow the `src/lib/Button/` layout.

**`src/lib/Icon/Icon.svelte`**
- Put in `<script module lang="ts">`:
  - `export type IconWeight = 'regular' | 'thin' | 'light' | 'bold' | 'fill' | 'duotone'`.
  - `export type IconProps = Omit<HTMLAttributes<HTMLElement>, 'children'> & { name: string; weight?: IconWeight; label?: string }`.
  - A `PHOSPHOR_SRI` map from weight to integrity, with these values from `researcher-L1.md`:
    - regular `sha384-6p9AefaqUhEVheRlj1mpAkbngHXy9mbYMrIdcIt4Jlc9lOLIablJq3bBsLOjGwZ7`
    - bold `sha384-nblAP2mo2pVPyMQZDw9Xy9Cwgs9lowushAYep4w5+Q9kF4Ibf3n0B/gCMVdR+Vqy`
    - fill `sha384-pPVoXE8ft+zxKtxIDDI7SfTK6y95NHm4qa+hKEg/hs8VkjW5IP+9/dGOPCbDpUPl`
    - light `sha384-GzhNOdwUkh38xzoNEY1vRdLr+w8q+bXEJsd/km6Ef61w1Kfk+lself6cn14ilrpO`
    - thin `sha384-ZrguSahlNzFt9jT0cuIhTCpssPYg2cCEoWz7Bpd96tKHthb+kBAIugSMdw0DUcEy`
    - duotone `sha384-UVFvhZP7fWAENUPOoq61rJg5ef6QZW0k5vpAn71041/QS4STvUcJQCGNhStZLGx9`
  - An `ensurePhosphorStylesheet(weight)` helper:
    - If `document.head` has no `link[data-phosphor-weight="<weight>"]`, append a `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/<weight>/style.css" integrity=<sri> crossorigin="anonymous" data-phosphor-weight="<weight>">`.
    - Result: at most one link per weight, shared across all instances.
- Instance script:
  - `let { name, weight = 'regular', label, class: className, ...rest }: IconProps = $props()`.
  - Call `ensurePhosphorStylesheet(weight)` only inside `$effect` or `onMount`, so SSR never touches `document`. `$effect` also covers a weight change after mount.
  - Classes: `icon()` from `styled-system/recipes/index.mjs` (which yields `icon`), then `ph ph-<name>` for regular or `ph-<weight> ph-<name>` for any other weight (no bare `ph`), then `className` if given.
- Render `<i class={...} {...rest}>`, with this accessibility:
  - With `label`: `role="img"` and `aria-label={label}`.
  - Without `label`: `aria-hidden="true"` and no role attribute.
  - Spread `rest` first and set the a11y attributes after it, so pass-through attributes like `data-size` reach the element and cannot override the a11y contract.

**`src/lib/Icon/index.ts`**
- `export { default as Icon } from './Icon.svelte'; export type { IconProps, IconWeight } from './Icon.svelte';`

**`src/lib/Icon/Icon.svelte.spec.ts`** (client project; import `../../app.css`; `await render(...)`), covering:
- Classes for regular (`icon ph ph-house`) and bold (`icon ph-bold ph-house`, no `ph` class).
- `aria-hidden="true"` and no `role` without a label; `role="img"` found via `page.getByRole('img', { name })` with a label.
- `data-size` passes through.
- After two regular icons and one bold icon render, `document.head` has exactly one `link[data-phosphor-weight="regular"]` and one `link[data-phosphor-weight="bold"]`. Each has the jsdelivr 2.1.2 href, a `sha384-` integrity, and `crossorigin="anonymous"`. No network is needed: only the link elements are inspected.
- For every `geometryRows` cell, rendered inside a `data-tier`/`data-scale` wrapper with `data-size` on the icon (the same pattern as `Button.cells.svelte.spec.ts`), the computed `font-size`, `width` and `height` all equal `${row.icon}px`.

**`src/lib/Icon/Icon.ssr.spec.ts`** (server project, node):
- Render with `render` from `svelte/server` and assert that the body contains `<i` and `ph-house` and does not throw (proves no `document` access during SSR).
- If vitest's node project cannot compile the component for SSR, report it as blocked `plan defect:`. Do not drop the file.
### Acceptance criteria
- `pnpm exec vitest run src/lib/Icon`
- `grep -rqF "https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/" src/lib/Icon`
- `grep -rqF "sha384-6p9AefaqUhEVheRlj1mpAkbngHXy9mbYMrIdcIt4Jlc9lOLIablJq3bBsLOjGwZ7" src/lib/Icon && grep -rqF "sha384-nblAP2mo2pVPyMQZDw9Xy9Cwgs9lowushAYep4w5+Q9kF4Ibf3n0B/gCMVdR+Vqy" src/lib/Icon`
- `grep -qF "export { default as Icon }" src/lib/Icon/index.ts`
- `test -f src/lib/Icon/Icon.svelte.spec.ts && test -f src/lib/Icon/Icon.ssr.spec.ts && grep -qF "svelte/server" src/lib/Icon/Icon.ssr.spec.ts`
- Observable: `Icon.svelte.spec.ts` asserts each behavior in the Do list (class sets for regular and bold, aria-hidden versus role img, one link per weight with integrity and crossorigin, and geometry icon size for every `geometryRows` cell), and `Icon.svelte` touches `document` only inside `$effect`/`onMount`.

## Step 3: Package export and showcase
level: L1
### Do
- In `src/lib/index.ts`, add `export { Icon, type IconProps, type IconWeight } from './Icon/index.js';`.
- In `src/routes/+page.svelte`:
  - Import `Icon` from `$lib/index.js` (extend the existing `import { Button } from '$lib/index.js'` line).
  - Replace the icon-only Button's child, the hand-sized `<span style:display="inline-flex" style:width="var(--g-icon)" style:height="var(--g-icon)">×</span>`, with `<Icon name="x" />`. The Button keeps `aria-label="Close"`, and the Icon stays unlabeled, so it is `aria-hidden`.
  - Remove that inline span. Touch nothing else on the page: the `<h2>Tier × scale × size</h2>` heading keeps its `×` characters, which is why the criteria below target the span's `style:width` attribute rather than the `×` glyph.
- The blocked attempt left both edits in the tree already. Keep them, confirm they match the Do, and run the criteria; if the tree was reset, redo the two edits.
### Acceptance criteria
- `grep -qE "export \{ Icon\b" src/lib/index.ts`
- `grep -qE "^\s*import \{[^}]*\bIcon\b" src/routes/+page.svelte`
- `grep -qE '<Icon name="x"' src/routes/+page.svelte`
- `! grep -qF 'style:width="var(--g-icon)"' src/routes/+page.svelte`
- (guard) `pnpm exec vitest run src/routes/page.svelte.spec.ts`

## Step 4: Gates green
level: L2
### Do
Run every project gate and fix any red that steps 1 to 3 introduced, such as prettier formatting on new files, eslint, or svelte-check types. All gates were green at the build-start HEAD. Do not weaken or delete tests.
### Acceptance criteria
- (guard) `pnpm check`
- (guard) `pnpm lint`
- (guard) `pnpm test`
- (guard) `pnpm run prepack`

## Risks
- Step 3's edits are already in the uncommitted tree from the blocked attempt, so its four new-behavior criteria are green on the current tree; each was proven red against the `HEAD` file content (`git show HEAD:<file>`), where the behavior is absent, and the page-spec guard was proven red in a fixture worktree at `HEAD` whose showcase imports the not-yet-exported `Icon` (`does not provide an export named 'Icon'`).
- `! grep -qF 'style:width="var(--g-icon)"'` goes red if a main sync adds that exact inline attribute elsewhere on the showcase page; unlikely, and the Do explains the choice over the `×` glyph.
- The six SRI hashes were computed by the researcher from the live CDN response and were not cross-checked against a published source. A wrong hash only blocks real browser loading, which the offline tests never exercise.
- `svelte-package` output in `dist/` still imports `styled-system/*` (the open item in CLAUDE.md); the `icon` recipe import inherits that consumability gap and `publint` does not catch it.
- The Phosphor stylesheet may set its own `font-size` or `line-height` on `.ph`/`.ph-*` and override the recipe in a real browser; the offline tests cannot observe this.
