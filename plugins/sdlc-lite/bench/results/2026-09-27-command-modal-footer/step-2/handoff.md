## Task goal
Add an always-visible footer to the command modal (`ui-command-modal`). It shows keyboard hints for navigate, select and close, and adds no new prop.

Interface the tests rely on:
- One `<footer data-part="footer">` element, appended into the modal (`ui-modal`) together with the existing search, list and status parts, rendered below the list and inside the dialog surface.
- Exactly 3 hints, each an element carrying a `data-hint` attribute (tests select them with `[data-hint]`) and containing at least one `<kbd>`, with the labels `Navigate`, `Select` and `Close`.
- The footer and its `<kbd>` elements carry no `tabindex` and no `role`.
- It stays visible (not `hidden`, not `display: none`, non-zero height) even when filtering leaves zero options.
- `footer` is listed as a part in the component's descriptor, next to `search`, `list`, `status` and `empty`.

## Step 2: Style the footer and add a browser visibility test
level: L2
### Do
In `packages/agent-ui/components/src/controls/command-modal/command-modal.css`:
- In the `:where(ui-command-modal)` token block, add `--ui-command-modal-footer-*` chain tokens. They alias only existing roles: `--md-sys-color-neutral-on-surface-variant` for ink, `--md-sys-color-neutral-container-low` (or the existing search-bg alias) for the background, `--md-sys-space-*` for padding and gap, and `--md-sys-font-sm` for the font. Add no new `--md-sys-*` token.
- In the `@scope (ui-command-modal)` block, add a `:scope [data-part='footer']` rule: `display: flex`, gap, padding, caption font, muted ink, and `flex-shrink: 0`, so it keeps a non-zero height when the list is empty.
- Add a `:scope [data-part='footer'] kbd` rule for the keycap look (radius from `--ui-command-modal-radius`, a padding-inline off the space ladder, `font: inherit`).
- Add a `[data-part='footer']` entry to the forced-colors block if it needs one (CanvasText).
- Update the sheet header comment's part list.

In `command-modal.browser.test.ts`, add a `describe` whose title contains `footer`. It opens the palette, types a query that matches nothing, then asserts:
- the footer is inside the open `dialog` and below the list (`footer.getBoundingClientRect().top >= list.getBoundingClientRect().bottom`);
- `getComputedStyle(footer).display !== 'none'`;
- `footer.hidden === false`;
- `footer.getBoundingClientRect().height > 0`;
- 3 `[data-hint]`, each with a visible `kbd`.
### Acceptance criteria
- `grep -q "\[data-part='footer'\]" packages/agent-ui/components/src/controls/command-modal/command-modal.css`
- `out=$(npx vitest run --config vitest.browser.config.ts --project packages packages/agent-ui/components/src/controls/command-modal/command-modal.browser.test.ts -t footer 2>&1) && printf '%s\n' "$out" | grep -qE 'Tests +[1-9][0-9]* passed'`
- (guard) `npx vitest run --config vitest.browser.config.ts --project packages packages/agent-ui/components/src/controls/command-modal/command-modal.browser.test.ts` exits 0
- Observable: `git diff "$SDLC_BASE_SHA" -- packages/agent-ui/components/src/controls/command-modal/command-modal.css` adds no `--md-sys-*:` declaration. Every new custom property it declares starts with `--ui-command-modal-`.
