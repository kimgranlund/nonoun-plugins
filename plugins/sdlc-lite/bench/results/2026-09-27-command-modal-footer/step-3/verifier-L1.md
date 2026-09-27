<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `awk '/^parts:/,/^customStates:/' .../command-modal.md | grep -q -- '- name: footer'`: pass. Evidence: exits 0 on the built tree and 1 in a throwaway worktree at `$SDLC_BASE_SHA` (220ae0ac), so the check can fail. The diff adds `- name: footer` after `empty` in `parts:`, with no `role:` line. Its description covers the `<footer>`, the 3 `[data-hint]` hints with `<kbd>`, no tabindex or role, never hidden, and not a prop. `attributes[]` is not changed in the diff.
- `grep -q "'footer'" .../command-modal-descriptor.test.ts`: pass. Evidence: exits 0 on the built tree and 1 at base. The diff extends `arrayContaining` to `['search', 'list', 'status', 'empty', 'footer']`.
- `grep -q footer .claude/docs/lld/command-modal.lld.md`: pass. Evidence: exits 0 on the built tree and 1 at base. The diff updates the LLD-C2 row, the LLD-C11 CSS note, the `modal.append(search, status, list, footer)` snippet and the `parts:` list (line 395). It also adds a new `## 9 · Amendments` section. No IDs were renumbered.
- (guard) `npx vitest run .../command-modal-descriptor.test.ts .../naming-gates.test.ts` exits 0: pass. Evidence: on the built tree, "Test Files 2 passed (2), Tests 99 passed (99)", EXIT=0. Negative control: I copied the new descriptor test into the base worktree, where the `.md` has no footer part. There it gives "× declares the search/list/status/empty parts + the empty slot ... - "footer"", "1 failed | 14 passed", EXIT=1. So the extended assertion catches a missing footer part. I removed the worktree afterwards.

## Out of scope changes
None for this step. `git status` also shows changes to `command-modal.ts`, `command-modal.css`, `command-modal.test.ts` and `command-modal.browser.test.ts`. Those belong to step 1 ("Create the footer part in command-modal.ts, with unit tests") and step 2 ("Style the footer and add a browser visibility test"), according to the step-1 and step-2 `handoff.md` headings. Step 3 touched only its three named files.

## For the next attempt
None
