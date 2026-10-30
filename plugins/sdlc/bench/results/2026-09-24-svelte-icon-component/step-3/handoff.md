## Task goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte` (default export) that renders Phosphor icons as an `<i>` element at several weights (regular, bold, and others).
- Props: `name` (Phosphor icon name), `weight` (default `regular`), optional `label`, plus pass-through attributes such as `data-size`.
- Classes: always `icon`; regular weight uses `ph ph-<name>`, other weights use `ph-<weight> ph-<name>` (no bare `ph`).
- Accessibility: without `label` the element is `aria-hidden="true"` with no role; with `label` it is `role="img"` named by the label.
- Styling: load each weight's stylesheet from the jsdelivr CDN for `@phosphor-icons/web@2.1.2` (`.../src/<weight>/style.css`) as a `<link>` in `document.head` marked `data-phosphor-weight="<weight>"`, with an SRI `sha384-` integrity and `crossorigin="anonymous"`. Inject at most one link per weight, only on client mount; SSR must never touch `document`.
- Size comes only from the geometry icon context (font-size, width and height all equal the geometry `icon` value for the current tier/scale/size), applied through a preset recipe.
- Export `Icon` from the package entry and use it for the showcase page's icon-only Button.

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

