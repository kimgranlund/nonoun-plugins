<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
fail

## Criteria
- No size/tier/scale/radius variant, no colorPalette/textStyle/park-ui: pass. Evidence: `grep -Ec '^\s*(size|tier|scale|radius): *\{' button.recipe.ts` → 0; `grep -cE 'colorPalette|textStyle|park-ui'` → 0.
- Recipe import shape: pass. Evidence: node import printed `iconOnly,variant primary,ghost true {"variant":"primary"}`.
- Context var counts: pass. Evidence: g-height 2, g-inset 2, g-text 1, r-control 1 in button.recipe.ts; `var(--g-icon)` in icon.recipe.ts → 3.
- px/hex literals and geometry properties: pass. Evidence: `grep -ohE -- '-?[0-9.]+px' recipes/*.recipe.ts | sort -u` → `2px` only; hex count 0 for both files. Read button.recipe.ts:17-21,25,50-52 and icon.recipe.ts:13-15: height/width `var(--g-height)`, paddingInline `var(--g-inset)` / `"0"`, gap `calc(var(--g-inset) / 2)`, fontSize `var(--g-text)`, borderRadius `var(--r-control)`, icon width/height/fontSize `var(--g-icon)`. Colors `control.surface`, `control.text`, `control.hover`, `control.active`, `text.primary`, `surface.hover`, `focusRing` all defined in panda/tokens.ts:48,57,66-69,72; `transparent` otherwise.
- Panda registration and panda tests: pass. Evidence: node import printed `button,icon button,icon`; `pnpm vitest run packages/gen-ui/src/panda packages/gen-ui/src/panda.config.test.ts apps/host/src/panda.config.test.ts` passed (3 files, 6 tests, run as part of the 8-file suite below and builder's run; direct run shown in exclude leg).
- cssgen counts: pass. Evidence: `panda cssgen --outfile /tmp/step2.css` exit 0; counts: variant_primary 3, variant_ghost 2, iconOnly_true 1, `\.icon` 1, g-icon 3, g-height 3, r-control 4, genui-recipe 1, `data-tier="` 9, `data-radius="` 4, size_/solid/outline 0 each.
- styled-system regenerated: pass. Evidence: `ls styled-system/recipes` → icon.d.ts, icon.mjs; `grep -c size button.d.ts` → 0; `grep -c iconOnly button.d.ts` → 1.
- package.json export: pass. Evidence: node exports check exit 0.
- typecheck, lint, format:check exit 0: fail. Evidence: `pnpm typecheck` exit 2: `button.test.tsx(8,20): error TS2322: Type '"solid"' is not assignable to type 'ConditionalValue<"primary" | "ghost"> | undefined'`. `pnpm lint` exit 0; `pnpm format:check` exit 0.
- Render check: pass. Evidence: throwaway worktree at HEAD with the same jsdom test went red on the biting variables (`Received: "button button--variant_solid button--size_lg"`, no `button--iconOnly_true`), then with step-2 files copied in and codegen rerun: `Tests 3 passed (3)` (data-size="lg", no size class, ghost+iconOnly_true, no iconOnly attribute, no data-size when unset). Worktree removed; `git status --porcelain` unchanged.
- `vitest run --exclude '**/button.test.tsx'` passes 8 files; button suite fails exactly `renders solid variant class` with `button--variant_primary` shown: fail (second half). Evidence: exclude run → `Test Files 8 passed, Tests 30 passed`. `pnpm vitest run packages/gen-ui/src/components/button` → `Tests 1 passed (1)`; Panda's runtime `button()` does not validate variant values, so `variant="solid"` still emits `button--variant_solid` and the stale test stays green.
- `pnpm gen:check` exit 1 with only the REG-03 unresolved-reference line: fail. Evidence: exit 1; stderr has two lines: `REG-03.unresolved-reference core.button at config.size: ...` and `REG-03.illegal-realization-value core.button at config.variant.default: default "solid" is not a "variant" member of recipe "recipe.button"`.
- Porcelain lists no test or generated files: pass. Evidence: `git status --porcelain | grep -E '\.test\.tsx?$|packages/gen-ui/generated/'` → no output.

## Out of scope changes
None. `geometry-scope.tsx` (staged, A) and the `./components/geometry-scope` export line in package.json are Step 1's staged work, not Step 2's. `.sdlc/` files are process artifacts.

## For the next attempt
The code matches the Do section; the three reds are contradictions inside the handoff's own criteria, so the fix belongs to the planner, not the builder:
1. `packages/gen-ui/tsconfig.json` includes `src/**/*.tsx`, so `pnpm typecheck` sees `button.test.tsx` line 8 (`variant="solid"`) and exits 2. The only ways to green it (edit the test, keep `solid`, widen the prop type, exclude tests from tsconfig) are forbidden. Amend the criterion to accept a typecheck red confined to `button.test.tsx` until Step 3's hidden tests replace it.
2. `renders solid variant class` cannot fail at runtime: generated `button()` emits `button--variant_solid` for any string. Drop that runtime-failure expectation (Step 3's plan carries the same wrong expectation).
3. `gen:check` emits two REG-03 lines because the manifest's `config.variant.default` is still `"solid"`; that is Step 3 manifest work. Amend the criterion to allow both lines.
