## Task goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte` (default export) that renders Phosphor icons as an `<i>` element at several weights (regular, bold, and others).
- Props: `name` (Phosphor icon name), `weight` (default `regular`), optional `label`, plus pass-through attributes such as `data-size`.
- Classes: always `icon`; regular weight uses `ph ph-<name>`, other weights use `ph-<weight> ph-<name>` (no bare `ph`).
- Accessibility: without `label` the element is `aria-hidden="true"` with no role; with `label` it is `role="img"` named by the label.
- Styling: load each weight's stylesheet from the jsdelivr CDN for `@phosphor-icons/web@2.1.2` (`.../src/<weight>/style.css`) as a `<link>` in `document.head` marked `data-phosphor-weight="<weight>"`, with an SRI `sha384-` integrity and `crossorigin="anonymous"`. Inject at most one link per weight, only on client mount; SSR must never touch `document`.
- Size comes only from the geometry icon context (font-size, width and height all equal the geometry `icon` value for the current tier/scale/size), applied through a preset recipe.
- Export `Icon` from the package entry and use it for the showcase page's icon-only Button.

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
