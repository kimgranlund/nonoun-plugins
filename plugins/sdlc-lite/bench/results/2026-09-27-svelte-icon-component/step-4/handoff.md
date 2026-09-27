## Task goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte` (default export) that renders Phosphor icons as an `<i>` element at several weights (regular, bold, and others).
- Props: `name` (Phosphor icon name), `weight` (default `regular`), optional `label`, plus pass-through attributes such as `data-size`.
- Classes: always `icon`; regular weight uses `ph ph-<name>`, other weights use `ph-<weight> ph-<name>` (no bare `ph`).
- Accessibility: without `label` the element is `aria-hidden="true"` with no role; with `label` it is `role="img"` named by the label.
- Styling: load each weight's stylesheet from the jsdelivr CDN for `@phosphor-icons/web@2.1.2` (`.../src/<weight>/style.css`) as a `<link>` in `document.head` marked `data-phosphor-weight="<weight>"`, with an SRI `sha384-` integrity and `crossorigin="anonymous"`. Inject at most one link per weight, only on client mount; SSR must never touch `document`.
- Size comes only from the geometry icon context (font-size, width and height all equal the geometry `icon` value for the current tier/scale/size), applied through a preset recipe.
- Export `Icon` from the package entry and use it for the showcase page's icon-only Button.

## Step 4: Gates green
level: L2
### Do
Run every project gate and fix any red that steps 1 to 3 introduced, such as prettier formatting on new files, eslint, or svelte-check types. All gates were green at the build-start HEAD. Do not weaken or delete tests.
### Acceptance criteria
- (guard) `pnpm check`
- (guard) `pnpm lint`
- (guard) `pnpm test`
- (guard) `pnpm run prepack`
