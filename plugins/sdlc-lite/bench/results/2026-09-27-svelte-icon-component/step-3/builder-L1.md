<!-- role=builder level=L1 model=sonnet effort=low -->
All criteria pass.

## Status
done

## Changes
None (edits were already present in the tree from the prior blocked attempt; verified they match the Do and left them unchanged).

## Checks
- `grep -qE "export \{ Icon\b" src/lib/index.ts` — pass
- `grep -qE "^\s*import \{[^}]*\bIcon\b" src/routes/+page.svelte` — pass
- `grep -qE '<Icon name="x"' src/routes/+page.svelte` — pass
- `! grep -qF 'style:width="var(--g-icon)"' src/routes/+page.svelte` — pass
- `pnpm exec vitest run src/routes/page.svelte.spec.ts` — pass (1 test file, 1 test passed)

## Notes
Working tree also has unrelated pre-existing untracked/modified files from earlier steps (`src/lib/Icon/`, `src/lib/preset/index.ts`, `src/lib/preset/recipes/icon.recipe.ts`, `.sdlc/bench-svelte-icon-component/`) — not touched by this step, left as-is.
