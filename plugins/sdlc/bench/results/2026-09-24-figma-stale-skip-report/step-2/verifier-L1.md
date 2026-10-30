<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Collision produces a `figma.notify` and a `console.warn` naming the skipped variable: pass. Evidence: I checked this by reading the code, not with a mock run.
  - `figma/plugin/code.js` (commit 9e5f72b0) adds `skippedDeprecates` in `applyBundle` (`byName[r.to]` taken → push `{from,to}`), in `applyFloatPlans`, and in `applyFontPrimitivesModes`.
  - The apply handler gathers all three sources and, when the combined count is above 0, runs `console.warn(..., froms.join(", "))` and `figma.notify(...names..., {timeout:6000})`.
  - `fpr` is declared outside the styles `try`, and `r` and `fr` are in scope at the point of use.
  - The notify sits before the final "Applied…" notify and matches the missingFonts style.
- No collision means no extra notify or warn: pass. Evidence: the new block is guarded by `if (skipped.length)`. The non-library branch of `applyBundle` pushes `skippedDeprecates: []`, so it adds no entries.
- `npm test` green with test files untouched: pass. Evidence: `npm test` ended with "✓ all 48 test files passed". `git diff HEAD~1 --stat -- test` shows no changes.
- Regenerated `ui.html`, `figma-plugin-assets.js` and the binder `code.js` are committed as the generators wrote them: pass. Evidence: the commit includes those three files. After `npm test`, `git status` shows a clean tree apart from the untracked `.sdlc/` artifacts, so the generators reproduce the committed output.
- Optional `skippedDeprecates` on the `apply-done` message: pass (optional, not added). The builder skipped it.

## Out of scope changes
- Two review docs were edited: `docs/reference/reviews/2026-08-20-reactivity/03-stores-and-persistence.md` and `04-context-and-messaging.md`. Only their `code.js:N` citations moved. The citation gate in `npm test` requires this after the line shift, so it is justified.
- Commit 9e5f72b0 also carries the Step 1 changes that were uncommitted in the worktree. The applyBundle/applyFloatPlans/applyFontPrimitivesModes report additions in the diff are those changes.

## For the next attempt
None. Optional follow-up: no mock test covers the collision path, since test files had to stay untouched.
