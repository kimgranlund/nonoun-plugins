## Task goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte` (default export) that renders Phosphor icons as an `<i>` element at several weights (regular, bold, and others).
- Props: `name` (Phosphor icon name), `weight` (default `regular`), optional `label`, plus pass-through attributes such as `data-size`.
- Classes: always `icon`; regular weight uses `ph ph-<name>`, other weights use `ph-<weight> ph-<name>` (no bare `ph`).
- Accessibility: without `label` the element is `aria-hidden="true"` with no role; with `label` it is `role="img"` named by the label.
- Styling: load each weight's stylesheet from the jsdelivr CDN for `@phosphor-icons/web@2.1.2` (`.../src/<weight>/style.css`) as a `<link>` in `document.head` marked `data-phosphor-weight="<weight>"`, with an SRI `sha384-` integrity and `crossorigin="anonymous"`. Inject at most one link per weight, only on client mount; SSR must never touch `document`.
- Size comes only from the geometry icon context (font-size, width and height all equal the geometry `icon` value for the current tier/scale/size), applied through a preset recipe.
- Export `Icon` from the package entry and use it for the showcase page's icon-only Button.

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

