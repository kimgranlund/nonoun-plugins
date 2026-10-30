<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None.

## PR title
Add accessible Phosphor Icon component with geometry-based sizing

## PR body
**Summary**
Adds an `Icon` component (`src/lib/Icon/Icon.svelte`) that renders Phosphor icons via CDN-loaded stylesheets, sized entirely through the geometry design system's `--g-icon` token, and wires it into the package export and the showcase page.

**Changes**
- `src/lib/preset/recipes/icon.recipe.ts`: new Panda recipe (`className: 'icon'`) with `fontSize`/`width`/`height` all reading `var(--g-icon)`, no px/hex literals, no `size` variant. Registered in `src/lib/preset/index.ts`.
- `src/lib/Icon/Icon.svelte` + `index.ts`: renders an `<i>` with `icon` plus Phosphor classes (`ph ph-<name>` for regular, `ph-<weight> ph-<name>` for other weights). Accessible by default (`aria-hidden="true"`, no role) or named (`role="img"`, `aria-label`) when `label` is passed. Injects one SRI-pinned `<link>` per weight from jsdelivr's `@phosphor-icons/web@2.1.2` CDN, only inside `$effect`/`onMount` so SSR never touches `document`.
- `src/lib/Icon/Icon.svelte.spec.ts` (client/browser) and `Icon.ssr.spec.ts` (server/node) cover class sets, a11y states, pass-through attributes, one-link-per-weight injection with integrity/crossorigin, and all 27 `geometryRows` cells for computed size.
- `src/lib/index.ts`: exports `Icon`, `IconProps`, `IconWeight`.
- `src/routes/+page.svelte`: showcase's icon-only Button now renders `<Icon name="x" />` instead of a hand-sized inline `<span>×</span>`.

**Verification**
- Step 1 (recipe): verifier-L1 pass, all criteria proven red on the pre-build worktree and green on the built tree, including the `Button` recipe guard.
- Step 2 (component + specs): verifier-L2 pass, `pnpm exec vitest run src/lib/Icon` green (11/11), each Do behavior confirmed against named test titles, `document` access confirmed confined to `ensurePhosphorStylesheet` called only from `$effect`.
- Step 3 (export + showcase): verifier-L1 pass, all four criteria proven red-at-base/green-at-built, `page.svelte.spec.ts` guard green. (A prior attempt at this step was blocked by a plan-defect acceptance criterion that matched an unrelated pre-existing `×` heading; the corrected criteria in the final step superseded it.)
- Step 4 (gates): verifier-L1 pass — `pnpm check` (0 errors), `pnpm lint` (clean), `pnpm test` (31/31), `pnpm run prepack` (publint "All good!").

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Added an accessible `Icon` component (Phosphor icons, CDN-loaded per weight, sized via the geometry design system) and used it in the showcase's icon-only Button.

## Follow-ups
- decide: The Phosphor CDN stylesheet's own `.ph`/`.ph-*` rules could set `font-size`/`line-height` and override the `icon` recipe's geometry sizing in a real browser; the offline vitest specs can't observe this since they never load the CDN CSS, so visual conformance against the actual stylesheet is unverified (planner-L3.md risk 5).
- note: The six SRI hashes in `Icon.svelte` were self-computed by the researcher via curl+openssl against the live jsdelivr CDN response, not cross-checked against a second published source (researcher-L1.md). Low risk since jsdelivr URLs are immutable, but worth knowing if icon loading ever fails in a real browser.
