<!-- role=verifier level=L1 model=sonnet effort=medium -->
All in scope. Let me also verify prettier/format check and header comment style copied, per builder claims (quick spot check already done via file read). Everything checks out.

## Verdict
pass

## Criteria
- `test -f src/lib/preset/recipes/icon.recipe.ts && grep -q "className: .icon." src/lib/preset/recipes/icon.recipe.ts`: pass. Evidence: ran the exact command, output PASS; verified red in throwaway worktree at pre-build SHA `b0a2fac` (`$SDLC_TMP_WORKTREES/base`), output FAIL (file absent).
- `for k in width height fontSize; do grep -qE "$k: .var\(--g-icon\)." ...; done`: pass. Evidence: ran the exact loop, output PASS. Confirmed by reading `src/lib/preset/recipes/icon.recipe.ts:17-19`: `fontSize: 'var(--g-icon)'`, `width: 'var(--g-icon)'`, `height: 'var(--g-icon)'`.
- `test -f ... && ! grep -nE "[0-9]px|#[0-9a-fA-F]{3,8}\b|^\s*size\s*:" ...`: pass. Evidence: ran the exact command, output PASS (no px/hex/size lines in the file, confirmed by reading the full 21-line file).
- `grep -qF "./recipes/icon.recipe.js" src/lib/preset/index.ts && grep -qE "const recipes = \{[^}]*\bicon\b" src/lib/preset/index.ts`: pass. Evidence: ran the exact command, output PASS; `git diff HEAD -- src/lib/preset/index.ts` shows the import added and `const recipes = { button, icon };`. Verified red at pre-build SHA (FAIL, since the import and `icon` entry don't exist there).
- `test -f styled-system/recipes/icon.mjs`: pass. Evidence: ran the exact command, output PASS; read `styled-system/recipes/icon.mjs`, contains a generated `icon` recipe export with empty variant map (consistent with the recipe having no variants). Verified red in the pre-build worktree: `styled-system/recipes/` didn't even exist there (pre-`prepare`).
- (guard) `pnpm exec vitest run src/lib/Button` exits 0: pass. Evidence: ran the command in the built tree, output "Test Files 2 passed (2)", "Tests 11 passed (11)", exit via passing summary (no failures reported).

## Out of scope changes
None. `git status --porcelain` shows only `src/lib/preset/index.ts` (modified, called for by the Do) and the new `src/lib/preset/recipes/icon.recipe.ts`, plus the gitignored `styled-system/` (regenerated build output, `.gitignore` confirms `/styled-system` is ignored) and the task's own `.sdlc/` artifacts dir.

## For the next attempt
None.
