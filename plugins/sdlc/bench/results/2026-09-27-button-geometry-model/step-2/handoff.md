## Task goal
Move the Button from its own size variants onto the shared geometry model. Size should come from a surrounding geometry scope, not from a recipe variant. The registry and the host app must stay consistent with the change.

Required surface:
- A `GeometryScope` component exported from `packages/gen-ui/src/components/geometry-scope/geometry-scope.tsx` (also exposed as the package export `./components/geometry-scope`). Props: `tier` and `scale` (both required), optional `size` and `radius`, plus normal div props. It renders a div carrying `data-tier`, `data-scale` and `data-radius`. `size` must not go on that element (the tier+scale selector would outrank it); when `size` is given, render it as `data-size` on an inner div that wraps the children.
- `Button` keeps a `size` prop, but it only sets `data-size` on the button element; no `--size_*` recipe class.
- The button recipe has no variant dimension named size, tier, scale or radius. Its `variant` values become `primary` (default) and `ghost`, and it gains a boolean `iconOnly` variant (default false). All geometry properties read `var(--g-*)` / `var(--r-*)` context vars (or calc over them), and colors use semantic tokens from `src/panda/tokens.ts`.
- Add an `iconRecipe` (in `packages/gen-ui/src/recipes/icon.recipe.ts`) for the icon box whose width, height and font size come from `var(--g-icon)`. `buttonRecipe` and `iconRecipe` are the only recipes, and both must be registered with Panda.
- The generated Button config schema accepts runtime fields `variant` and `iconOnly` only (defaults `primary`, `false`), and rejects `size`.

## Step 2: Manifest, registry regeneration and host
level: L2
### Do
Run with node 24 (see Step 1).
- `packages/gen-ui/src/components/button/button.manifest.ts`: `variant` keeps `type: "enum"`, `audience: ["runtime"]`, default becomes `"primary"`; remove the `size` field; add `iconOnly: { type: "boolean", audience: ["runtime"], default: false }`; keep `onClick`. The registry rules need every enum default among the recipe's variant keys, which is why this step follows Step 1.
- Run `pnpm gen:registry` so `packages/gen-ui/generated/` is regenerated, never hand-edited: `button.config.ts` gets `iconOnly: z.boolean().default(false),` and `variant: z.enum(["primary", "ghost"]).default("primary"),` and no `size`; `registry.json` realization variants become `variant: ["primary", "ghost"]` and `iconOnly: ["true"]` with no `size`. Then run `pnpm gen:check`.
- `packages/gen-ui/src/registry/generate.test.ts`, test `generated ButtonConfigSchema accepts runtime fields only`: the pinned `{ variant: "solid", size: "md" }` expectations are legitimately broken; update them to the new defaults `{ variant: "primary", iconOnly: false }`, keep the unknown-key rejection, and add `expect(ButtonConfigSchema.safeParse({ size: "md" }).success).toBe(false)`.
- `apps/host/src/genui/render-entry.tsx`: render `<Button data-genui-entry={entry.id} variant={parsed.variant} iconOnly={parsed.iconOnly}>` with no `size`. `apps/host/src/routes/index.tsx`: `config={{ variant: "primary" }}`.
- `AGENTS.md` line 32 says "Variant and size values come from the recipe's fixed keys"; reword it so variant values come from the recipe's fixed keys and size is the geometry model's `data-size` context attribute. Stay under the 100-line guidance budget (`node scripts/check-guidance.mjs`).
- Run `pnpm typecheck` and `pnpm exec vitest run packages/gen-ui/src/registry` before finishing; both must be green.
### Acceptance criteria
- `node --import ./scripts/ts-resolve.mjs --input-type=module -e "import { buttonManifest as m } from './packages/gen-ui/src/components/button/button.manifest.ts'; const c = m.config; if ('size' in c) process.exit(1); if (c.variant.default !== 'primary') process.exit(2); if (c.iconOnly?.type !== 'boolean') process.exit(3); if (c.iconOnly.default !== false) process.exit(4); if (!c.iconOnly.audience.includes('runtime')) process.exit(5)"`
- `pnpm gen:check && grep -qF 'variant: z.enum(["primary", "ghost"]).default("primary"),' packages/gen-ui/generated/button.config.ts && grep -qF 'iconOnly: z.boolean().default(false),' packages/gen-ui/generated/button.config.ts && ! grep -q size packages/gen-ui/generated/button.config.ts`
- `node -e "const v = require('./packages/gen-ui/generated/registry.json').entries['core.button'].realization.variants; if ('size' in v) process.exit(1); if (JSON.stringify(v.variant) !== JSON.stringify(['primary', 'ghost'])) process.exit(2); if (JSON.stringify(v.iconOnly) !== JSON.stringify(['true'])) process.exit(3)"`
- `node --import ./scripts/ts-resolve.mjs --input-type=module -e "import { ButtonConfigSchema as s } from './packages/gen-ui/generated/button.config.ts'; const d = s.parse({}); if (d.variant !== 'primary') process.exit(1); if (d.iconOnly !== false) process.exit(2); if (s.safeParse({ size: 'md' }).success) process.exit(3); if (!s.safeParse({ variant: 'ghost', iconOnly: true }).success) process.exit(4)"`
- `grep -q "iconOnly" packages/gen-ui/src/registry/generate.test.ts && ! grep -q 'variant: "solid"' packages/gen-ui/src/registry/generate.test.ts`
- `! grep -nE "\bsize\b" apps/host/src/genui/render-entry.tsx apps/host/src/routes/index.tsx && grep -q "iconOnly={parsed.iconOnly}" apps/host/src/genui/render-entry.tsx && grep -q 'variant: "primary"' apps/host/src/routes/index.tsx`
- `! grep -rn 'button--size_\|size: "md"\|sizes=\|variants.size' AGENTS.md CLAUDE.md docs/decisions packages/gen-ui/src apps/host/src scripts --include='*.ts' --include='*.tsx' --include='*.mjs' --include='*.md' --exclude='*.test.ts' --exclude='*.test.tsx'`
- `! grep -q "Variant and size values" AGENTS.md`
- (guard) `pnpm exec vitest run packages/gen-ui/src/registry/generate.test.ts`
- (guard) `pnpm exec eslint apps/host/src packages/gen-ui/src/registry packages/gen-ui/src/components/button/button.manifest.ts`
- (guard) `pnpm exec prettier --check apps/host/src packages/gen-ui/src/registry packages/gen-ui/src/components/button/button.manifest.ts packages/gen-ui/generated`
