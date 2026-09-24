<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte`. It renders Phosphor icons as an `<i>` sized only by the geometry `--g-icon` context through a preset recipe, and loads each weight's CDN stylesheet once, only on the client. Export it from the package and use it in the showcase's icon-only Button.

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

## Step 2: Build the Icon component, its barrel, package export and a behavior spec
level: L3
### Do
- Create `src/lib/Icon/Icon.svelte` (Svelte 5 runes). Mirror `src/lib/Button/Button.svelte`.
- `<script module lang="ts">` block:
  - Export `type IconWeight = 'regular' | 'bold' | 'thin' | 'light' | 'fill' | 'duotone'`.
  - Export `type IconProps = Omit<HTMLAttributes<HTMLElement>, 'children'> & { name: string; weight?: IconWeight; label?: string }`, with `HTMLAttributes` from `svelte/elements`.
  - Add a constant map from weight to `{ href, integrity }`. The href is `https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/<weight>/style.css`. The integrity values come verbatim from `.sdlc/bench-svelte-icon-component/researcher-L1.md`:
    - regular: `sha384-6p9AefaqUhEVheRlj1mpAkbngHXy9mbYMrIdcIt4Jlc9lOLIablJq3bBsLOjGwZ7`
    - bold: `sha384-nblAP2mo2pVPyMQZDw9Xy9Cwgs9lowushAYep4w5+Q9kF4Ibf3n0B/gCMVdR+Vqy`
    - thin: `sha384-ZrguSahlNzFt9jT0cuIhTCpssPYg2cCEoWz7Bpd96tKHthb+kBAIugSMdw0DUcEy`
    - light: `sha384-GzhNOdwUkh38xzoNEY1vRdLr+w8q+bXEJsd/km6Ef61w1Kfk+lself6cn14ilrpO`
    - fill: `sha384-pPVoXE8ft+zxKtxIDDI7SfTK6y95NHm4qa+hKEg/hs8VkjW5IP+9/dGOPCbDpUPl`
    - duotone: `sha384-UVFvhZP7fWAENUPOoq61rJg5ef6QZW0k5vpAn71041/QS4STvUcJQCGNhStZLGx9`
  - Add a function `ensurePhosphorStylesheet(weight)`:
    - Return early if `document.head.querySelector('link[data-phosphor-weight="<weight>"]')` already exists.
    - Otherwise create a `<link>` with `rel="stylesheet"`, `href`, `integrity`, `crossorigin="anonymous"` and `data-phosphor-weight=<weight>`, and append it to `document.head`.
- Instance script:
  - `let { name, weight = 'regular', label, class: className, ...rest }: IconProps = $props();`
  - Call `ensurePhosphorStylesheet(weight)` inside `$effect`. It must re-run when `weight` changes, never at module top level and never during SSR.
  - Build the class string as `icon()` from `styled-system/recipes/index.mjs`, then the weight classes: `ph ph-<name>` for regular, `ph-<weight> ph-<name>` for any other weight (no bare `ph`). Append `className` if one is given.
  - The recipe class must produce the literal class `icon`.
- Markup: `<i class={...} {...rest} role={label ? 'img' : undefined} aria-label={label} aria-hidden={label ? undefined : 'true'}></i>`. Put the a11y attributes after `{...rest}` so they win. `data-size` and other attributes pass through via `rest`.
- Create `src/lib/Icon/index.ts`: `export { default as Icon } from './Icon.svelte'; export type { IconProps, IconWeight } from './Icon.svelte';`.
- Add `export { Icon, type IconProps, type IconWeight } from './Icon/index.js';` to `src/lib/index.ts`.
- Add the builder's own spec at `src/lib/Icon/Icon.behavior.svelte.spec.ts`. Do not use or edit `Icon.svelte.spec.ts`, which may be supplied as a hidden test. Import `'../../app.css'` and use `await render(...)`. Cover:
  - The classes for regular and bold.
  - `aria-hidden="true"` with no role when there is no label.
  - With a label, `page.getByRole('img', { name })` finds the element.
  - After rendering two regular icons and one bold icon, there is exactly one `link[data-phosphor-weight="regular"]` and exactly one `link[data-phosphor-weight="bold"]`, each with the right `href`, an `integrity` starting with `sha384-`, and `crossorigin="anonymous"`.
  - Resolved CSS: for every `geometryRows` row, render Icon with `data-size=row.size` inside a wrapper carrying `data-tier` and `data-scale`. `fontSize`, `width` and `height` must all equal `${row.icon}px`, and the spec asserts that 27 cases ran.
- Load the `svelte-code-writer`, `panda-in-svelte` and `svelte-vitest-browser` skills before writing.
### Acceptance criteria
- `pnpm vitest run src/lib/Icon` passes. If the hidden `src/lib/Icon/Icon.svelte.spec.ts` is present, it passes too.
- `pnpm vitest run src/lib/Button` still passes.
- `pnpm check` exits 0.
- `pnpm lint` exits 0.
- `grep -n "Icon" src/lib/index.ts` shows the export.
- `grep -nE "^\s*(document|ensurePhosphor)" src/lib/Icon/Icon.svelte` shows no `document` access at module top level. The only call site of the injection is inside `$effect`.
- `pnpm build` exits 0 (SSR prerender of the showcase does not touch `document`), and publint reports "All good!".

## Step 3: Use Icon in the showcase's icon-only Button
level: L1
### Do
- In `src/routes/+page.svelte`, import `Icon` alongside `Button` from `$lib/index.js`.
- In the "Icon only" section, replace the `<span style:...>×</span>` child with `<Icon name="x" />`. Keep `aria-label="Close"` on the Button. The icon stays unlabeled, so it renders `aria-hidden`.
### Acceptance criteria
- `grep -n '<Icon name="x"' src/routes/+page.svelte` matches, and `grep -n "×" src/routes/+page.svelte` finds nothing.
- `pnpm vitest run src/routes` passes. The existing page spec still passes.
- `pnpm check`, `pnpm lint` and `pnpm build` exit 0.
- Full suite: `pnpm test` exits 0.

## Risks
- The hidden spec may expect a different class order, or `aria-hidden` absent rather than undefined when labeled. The plan's order is `icon` first, then the weight classes, and it relies on Svelte omitting attributes whose value is `undefined`.
- The hidden spec may check sizing with `data-size` set on the Icon element itself. That works because `--g-icon` is re-resolved per element. If it instead expects inheritance from a wrapper `data-size`, that also works.
- In real browsers, the CDN stylesheet is unlayered and would beat the `@layer recipes` rules if it set `font-size`, width or height on `.ph*`. I believe it only sets font-family, font-weight and line-height, but nobody has verified that. Tests run without the stylesheet loading, so they would not catch it.
- The browser still tries to fetch the injected `<link>` during tests. With no network this fails quietly and should not fail any assertion.
- The researcher did not cross-check the SRI hashes against a second source. A wrong hash only breaks loading in a real browser, not the tests.
- The `dist/` `styled-system/*` import issue (a CLAUDE.md open item) now applies to Icon too. It is out of scope here.
