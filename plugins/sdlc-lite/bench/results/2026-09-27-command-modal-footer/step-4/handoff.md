## Task goal
Add an always-visible footer to the command modal (`ui-command-modal`). It shows keyboard hints for navigate, select and close, and adds no new prop.

Interface the tests rely on:
- One `<footer data-part="footer">` element, appended into the modal (`ui-modal`) together with the existing search, list and status parts, rendered below the list and inside the dialog surface.
- Exactly 3 hints, each an element carrying a `data-hint` attribute (tests select them with `[data-hint]`) and containing at least one `<kbd>`, with the labels `Navigate`, `Select` and `Close`.
- The footer and its `<kbd>` elements carry no `tabindex` and no `role`.
- It stays visible (not `hidden`, not `display: none`, non-zero height) even when filtering leaves zero options.
- `footer` is listed as a part in the component's descriptor, next to `search`, `list`, `status` and `empty`.

## Step 4: Gates green
level: L2
### Do
Run every project gate and fix any red that steps 1 to 3 introduced. Likely spots:
- naming-gates Gate 4 (rendered parts vs descriptor);
- family-coherence;
- `site/lib/command-palette*.test.ts`, whose layout or part assertions the new footer may affect;
- the site-coverage descriptor test.

Fix the code, or update a test to the new behavior. Never delete a test or weaken an assertion. Judge by exit codes. A gate already red at `$SDLC_BASE_SHA` is reported as `inherited red`: prove it by running the same command in a `git worktree add --detach <tmp> "$SDLC_BASE_SHA"` copy.
### Acceptance criteria
- (guard) `npm run check` exits 0
- (guard) `npm test` exits 0
- (guard) `npm run test:browser:packages:components` exits 0
- (guard) `npm run test:browser:site` exits 0
- (guard) `npm run test:browser` shows no new failures versus the base: run the same command in a `git worktree add --detach <tmp> "$SDLC_BASE_SHA"` copy and compare.
