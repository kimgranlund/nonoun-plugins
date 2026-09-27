## Task goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte` (default export) that renders Phosphor icons as an `<i>` element at several weights (regular, bold, and others).
- Props: `name` (Phosphor icon name), `weight` (default `regular`), optional `label`, plus pass-through attributes such as `data-size`.
- Classes: always `icon`; regular weight uses `ph ph-<name>`, other weights use `ph-<weight> ph-<name>` (no bare `ph`).
- Accessibility: without `label` the element is `aria-hidden="true"` with no role; with `label` it is `role="img"` named by the label.
- Styling: load each weight's stylesheet from the jsdelivr CDN for `@phosphor-icons/web@2.1.2` (`.../src/<weight>/style.css`) as a `<link>` in `document.head` marked `data-phosphor-weight="<weight>"`, with an SRI `sha384-` integrity and `crossorigin="anonymous"`. Inject at most one link per weight, only on client mount; SSR must never touch `document`.
- Size comes only from the geometry icon context (font-size, width and height all equal the geometry `icon` value for the current tier/scale/size), applied through a preset recipe.
- Export `Icon` from the package entry and use it for the showcase page's icon-only Button.

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
