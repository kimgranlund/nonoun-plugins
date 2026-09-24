<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `packages/gen-ui/src/components/button/button.manifest.ts`: variant default is now `primary`, `size` is removed, a boolean `iconOnly` runtime field (default false) is added, and `icon-only-requires-name` is added to accessibility.
- `packages/gen-ui/generated/{button.config.ts,registry.json,registry.hash,meta.json}`: regenerated with `pnpm gen:registry`, no hand edits.
- `apps/host/src/genui/render-entry.tsx`: now passes `iconOnly={parsed.iconOnly}` where it used to pass `size`.
- `apps/host/src/routes/index.tsx`: config is now `{ variant: "primary" }`.
- `AGENTS.md`: the Styling sentence now treats size, tier, scale and radius as context attributes read through `var(--g-*)` and `var(--r-*)`, not recipe variants.

## Checks
- Manifest greps: `size:` block 0, `icon-only-requires-name` 1.
- Running `pnpm gen:registry` a second time left `git status` for `generated/` unchanged. The generated diff lists exactly the 4 expected files.
- `button.config.ts` has both required lines, and `size` appears 0 times.
- Registry node probe printed `0 primary,ghost true iconOnly,onClick,variant primary false boolean`.
- Schema probe printed `{"iconOnly":false,"variant":"primary"} false false true false`.
- Host greps: no `size` matches, `iconOnly={parsed.iconOnly}` 1, `variant: "primary"` 1.
- The repo-wide leftover-size grep matches only `generate.test.ts` (3 lines).
- `pnpm lint && pnpm format:check && node scripts/check-guidance.mjs && pnpm gen:geometry:check && pnpm gen:check && pnpm build` exited 0.
- Host tsc exited 0. The gen-ui tsc has no errors outside `button.test.tsx(`, and `button.test.tsx(8,` appears 1 time.
- AGENTS.md: 46 lines, 0 em dashes, `data-size` 1, old sentence 0.
- Built CSS counts:

| Pattern | Count |
|---|---|
| `button--variant_primary` | 3 |
| `button--iconOnly_true` | 1 |
| `.icon` | 1 |
| `--g-md-height` | 19 |
| `data-radius=` | 4 |
| `data-tier=` | 9 |
| `genui-recipe` | 1 |
| `button--size_` | 0 |
| `button--variant_solid` | 0 |

- SSR page: entry attribute 1, `button--variant_primary` 1, `button--size_` 0, `data-size=` 0. After the server was killed, nothing was listening on port 4312.
- `pnpm vitest run --exclude '**/generate.test.ts'`: 8 files and 21 tests passed.
- `pnpm vitest run generate.test.ts`: 9 passed and 1 failed. The failure is `generated ButtonConfigSchema accepts runtime fields only`, which is expected by design.
- `git status --porcelain` lists no test files.

## Notes
The only reds are the expected ones: `generate.test.ts` fails 1 test and the gen-ui tsc reports the error at `button.test.tsx(8,`. Nothing is committed.
