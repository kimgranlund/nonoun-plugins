<!-- role=builder level=L1 model=sonnet effort=low -->
Guard passes. The two other criteria: first passes, second is defective per unrelated pre-existing "×" text. Status is blocked, leaving work in tree.

## Status
blocked

## Changes
- src/lib/index.ts: added `export { Icon, type IconProps, type IconWeight } from './Icon/index.js';`
- src/routes/+page.svelte: imported `Icon`, replaced the icon-only Button's `<span>×</span>` child with `<Icon name="x" />`, removed the inline span

## Checks
- `grep -qE "export \{ Icon\b" src/lib/index.ts` — PASS
- `grep -qE "<Icon\b" src/routes/+page.svelte && ! grep -qF "×" src/routes/+page.svelte` — FAIL (see Notes: plan defect)
- (guard) `pnpm exec vitest run src/routes/page.svelte.spec.ts` — PASS (1 passed)

## Notes
plan defect: `! grep -qF "×" src/routes/+page.svelte` is file-wide and always fails because of the pre-existing, unrelated `<h2>Tier × scale × size</h2>` heading (confirmed present in `HEAD` before this step's edits, via `git show HEAD:src/routes/+page.svelte`). The step's actual target, the icon-only Button's inline `<span>×</span>`, was correctly removed and replaced with `<Icon name="x" />`. Fixing the criterion as written would require editing unrelated heading text outside this step's Do, which is out of scope. Work is left in the tree: `src/lib/index.ts` and `src/routes/+page.svelte` edits are complete and correct per the Do section.
