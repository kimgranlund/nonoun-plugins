## Goal
Add an accessible `Icon` component at `src/lib/Icon/Icon.svelte` (default export) that renders Phosphor icons as an `<i>` element at several weights (regular, bold, and others).
- Props: `name` (Phosphor icon name), `weight` (default `regular`), optional `label`, plus pass-through attributes such as `data-size`.
- Classes: always `icon`; regular weight uses `ph ph-<name>`, other weights use `ph-<weight> ph-<name>` (no bare `ph`).
- Accessibility: without `label` the element is `aria-hidden="true"` with no role; with `label` it is `role="img"` named by the label.
- Styling: load each weight's stylesheet from the jsdelivr CDN for `@phosphor-icons/web@2.1.2` (`.../src/<weight>/style.css`) as a `<link>` in `document.head` marked `data-phosphor-weight="<weight>"`, with an SRI `sha384-` integrity and `crossorigin="anonymous"`. Inject at most one link per weight, only on client mount; SSR must never touch `document`.
- Size comes only from the geometry icon context (font-size, width and height all equal the geometry `icon` value for the current tier/scale/size), applied through a preset recipe.
- Export `Icon` from the package entry and use it for the showcase page's icon-only Button.

## Context
- Read CLAUDE.md first. Follow the structure of `src/lib/Button/` (component, index.ts, spec).
- Panda recipes live in `src/lib/preset/recipes/` and are registered in `src/lib/preset/index.ts`.
- Geometry data: `src/lib/preset/geometry/` (generated; `geometryRows` in `geometry.generated.ts`), context via `data-tier`, `data-scale`, `data-size` attributes.
- Package entry: `src/lib/index.ts`. Showcase: `src/routes/+page.svelte`.
- Specs are `*.svelte.spec.ts` run in Vitest browser mode (chromium).

## Constraints
- Existing tests your change legitimately breaks may be updated to the new behavior; never delete a test or weaken an assertion to get green. The grader overwrites its own test files after the run, so edits to those do not count.
- Do not hand-edit generated files; regenerate with `npm run prepare` (geometry + panda codegen).
- Do not add an npm dependency for the icons; use the CDN stylesheets.
- Tests must not require network access (they only inspect the injected `<link>` elements).
