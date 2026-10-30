<!-- role=verifier level=L1 model=sonnet effort=medium -->
All changes are within scope of the geometry model migration (button.tsx, recipes.ts, button.recipe.ts belong to steps 1-2 already in the tree, consistent with handoff note). No out-of-scope files. All 14 acceptance criteria verified with actual command execution.

## Verdict
pass

## Criteria
- Manifest size deleted, icon-only-requires-name added: pass. Evidence: `grep -Ec '^\s*size: *\{' button.manifest.ts` → 0; `grep -c 'icon-only-requires-name'` → 1.
- gen:check / gen:geometry:check exit 0, regen idempotent, exactly 4 generated files changed: pass. Evidence: both commands printed success messages; `git status --porcelain packages/gen-ui/generated` identical before/after re-running `pnpm gen:registry`; `git diff --name-only` lists exactly button.config.ts, meta.json, registry.hash, registry.json.
- button.config.ts contains iconOnly/variant lines, no `size`: pass. Evidence: lines 7-8 match exactly; `grep -c size` → 0.
- registry.json entry shape: pass. Evidence: node script printed `0 primary,ghost true iconOnly,onClick,variant primary false boolean`.
- ButtonConfigSchema parse/safeParse behavior: pass. Evidence: node script printed `{"iconOnly":false,"variant":"primary"} false false true false`.
- host render-entry/index.tsx no `size`, correct wiring: pass. Evidence: `grep -n 'size' ...` printed nothing; `iconOnly={parsed.iconOnly}` count 1; `variant: "primary"` count 1.
- repo-wide size-idiom sweep: pass. Evidence: only matches are in `generate.test.ts` (lines 109,111,113), none in `apps/host/src/routes/index.tsx`.
- lint/format/guidance/gen checks/build: pass. Evidence: `pnpm lint && pnpm format:check && node scripts/check-guidance.mjs && pnpm gen:geometry:check && pnpm gen:check && pnpm build` ran to completion, exit 0, build produced dist artifacts.
- tsc host clean, gen-ui tsc only button.test.tsx(8,...) error: pass. Evidence: `pnpm exec tsc -p apps/host/tsconfig.json --noEmit` exit 0; filtered gen-ui tsc grep printed nothing; `grep -c 'button.test.tsx(8,'` → 1.
- AGENTS.md length/content: pass. Evidence: `wc -l` → 46; em-dash count 0; `data-size` count 1; old sentence count 0.
- Built CSS token counts: pass. Evidence: `button--variant_primary` 3, `button--iconOnly_true` 1, `\.icon` 1, `--g-md-height` 19 (≥9), `data-radius=` 4, `data-tier=` 9, `genui-recipe` 1, `button--size_` 0, `button--variant_solid` 0.
- SSR host page content, port cleanup: pass. Evidence: after `pnpm build` and starting server on 4312, `/tmp/step3.html` showed `data-genui-entry="core.button"` (1), `button--variant_primary` (1), `button--size_` (0), `data-size=` (0); `lsof -iTCP:4312 -sTCP:LISTEN` printed nothing after kill.
- vitest run (excluding generate.test.ts) 8 files/21 tests pass, generate.test.ts 9 passed/1 named failure: pass. Evidence: vitest output "8 passed (8)" / "21 passed (21)"; second run "1 failed (1)" / "9 passed | 1 failed", failing test named `generated ButtonConfigSchema accepts runtime fields only`.
- no test files in git status: pass. Evidence: `git status --porcelain` has no `*.test.ts`/`*.test.tsx` entries.

## Out of scope changes
None. button.tsx, recipes.ts, button.recipe.ts, icon.recipe.ts, and geometry-scope.tsx are prior-step (1-2) work already present in the uncommitted tree per the handoff note, and package.json's icon export addition is required wiring for the icon recipe this step introduces.

## For the next attempt
None.
