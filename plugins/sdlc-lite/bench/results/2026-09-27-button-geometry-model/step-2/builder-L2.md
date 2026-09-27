<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- packages/gen-ui/src/components/button/button.manifest.ts: `variant` now defaults to `primary`. Removed `size`. Added the runtime boolean `iconOnly`, default false.
- packages/gen-ui/generated/button.config.ts, registry.json, meta.json, registry.hash: regenerated with `pnpm gen:registry`, not edited by hand.
- packages/gen-ui/src/registry/generate.test.ts: the expected values are now `{ variant: "primary", iconOnly: false }`. Added a check that `{ size: "md" }` is rejected. The unknown-key rejection is still there.
- apps/host/src/genui/render-entry.tsx: passes `iconOnly={parsed.iconOnly}` and no longer passes `size`.
- apps/host/src/routes/index.tsx: config is now `{ variant: "primary" }`.
- AGENTS.md: the styling rule now says variant values come from the recipe's fixed keys and size is the geometry model's `data-size` context attribute.

## Checks
- Node v24.18.0, taken from `~/.nvm` via PATH.
- `pnpm gen:registry`: ran. `pnpm gen:check`: 4 generated files match their sources.
- Acceptance criteria 1 to 8: all exit 0. For criterion 7 the inner grep found nothing (exit 1), so the negated check passes.
- `pnpm typecheck`: passed.
- `pnpm exec vitest run packages/gen-ui/src/registry`: 15 tests passed.
- (guard) eslint on the named paths: exit 0.
- (guard) prettier --check on the named paths, plus AGENTS.md: all files formatted.
- `node scripts/check-guidance.mjs`: exit 0.

## Notes
The working tree still has Step 1's uncommitted changes (the recipes, button, and geometry-scope), as expected. Nothing was committed.
