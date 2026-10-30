<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add an always-visible, control-created `[data-part=footer]` to `ui-command-modal` that shows keyboard hints for navigate, select and close. It adds no new prop or attribute, uses only existing `--md-sys-*` tokens, and the descriptor stays in sync.

## Step 1: Create and style the footer part
level: L2
### Do
- `packages/agent-ui/components/src/controls/command-modal/command-modal.ts`, in `#ensureParts()`:
  - Build the footer once, like the status and empty parts: `const footer = document.createElement('div')` with `data-part="footer"`.
  - Give it three hint items, in this order: navigate, select, close. Each item is a `<span data-role="hint">` holding a `<kbd>` key glyph plus a text label: `↑↓` "Navigate", `↵` "Select", `Esc` "Close".
  - Mark the footer `aria-hidden="true"`. It is a visual affordance only; the keyboard map already lives in the descriptor and ARIA wiring, and the hints must not add to the dialog's accessible content.
  - Do not make it focusable (no tabindex) and never set `hidden`. It stays visible whether the filter has results or not.
  - Store it in a new private field `#footer`, next to `#status` and `#emptyRow`.
  - Append it last: change `modal.append(search, status, list)` to `modal.append(search, status, list, footer)`. It must go into the modal before the modal goes into the host (the LLD §3 ORDER note). Search stays first and list stays after search, so the `[data-part='search']:focus ~ [data-part='list']` sibling selector keeps working.
  - Keep `#ensureParts` idempotent: the early-return guard must not create a second footer on reconnect.
  - Update the header comment and the `#ensureParts` ORDER comment to mention the footer.
  - Add no entry to `static props`.
- `packages/agent-ui/components/src/controls/command-modal/command-modal.css`:
  - In the `:where(ui-command-modal)` token block, add `--ui-command-modal-footer-*` tokens that alias existing roles only: `--ui-command-modal-footer-ink: var(--md-sys-color-neutral-on-surface-variant)`, `--ui-command-modal-footer-border: var(--md-sys-color-neutral-outline-variant)` (use that role only if `grep -r "neutral-outline-variant" packages/agent-ui/shared/src/tokens` finds it, else reuse `--ui-command-modal-muted-ink`), and gap/padding from `--md-sys-space-*`. Define no new `--md-sys-*` token.
  - In the `@scope` block, add a `:scope [data-part='footer']` rule: `display:flex`, a gap, the caption font (`--ui-command-modal-caption-font`), muted ink, a 1px `border-block-start`, padding on the item pad tokens, and `flex-shrink:0`.
  - Add a small `:scope [data-part='footer'] kbd` rule: inherit the font family or use a monospace font, and give it the existing radius token.
  - Add a forced-colors line (`color: CanvasText`, `border-block-start-color: CanvasText`) inside the existing `@media (forced-colors: active)` block.
  - Update the file-header comment's part list (search / list / status / empty / footer).
### Acceptance criteria
- `npx vitest run packages/agent-ui/components/src/controls/command-modal/command-modal.test.ts` exits 0.
- In jsdom, after connecting a `<ui-command-modal>` (quick throwaway check, or observed via the existing test harness pattern):
  - `el.querySelectorAll('[data-part="footer"]').length === 1`, both before and after a disconnect and reconnect.
  - The footer sits inside the nested `[data-part="dialog"]` and is the dialog's last element child.
  - It is not `hidden`, and it stays not hidden after the filter matches nothing (type `zzzz` into search and dispatch `input`).
  - Its text contains "Navigate", "Select" and "Close".
- `git diff packages/agent-ui/components/src/controls/command-modal/command-modal.ts` shows no change to the `props` object.
- `grep -o -- '--md-sys-[a-z0-9-]*' packages/agent-ui/components/src/controls/command-modal/command-modal.css | sort -u` lists only tokens already defined under `packages/agent-ui/shared/src/tokens/` (each greppable there).
- `npm run check` exits 0.
- `git diff --stat` shows no `*.test.ts` file changed.

## Step 2: Sync the descriptor and LLD with the footer part
level: L1
### Do
- `packages/agent-ui/components/src/controls/command-modal/command-modal.md`:
  - Frontmatter `parts:` gets a fifth entry after `empty`: `- name: footer` with a `description`. The description says the footer is the control-created, always-visible, `aria-hidden` keyboard-hint row (↑↓ Navigate · ↵ Select · Esc Close), appended last inside the nested modal's dialog, never focusable, and adds no prop. It gets no `role` key.
  - Prose body: add a short `## The keyboard-hint footer` section, and add "footer" to the "moves the search/list/status parts" sentence in the Composition section.
  - Leave `attributes:` untouched.
- `.claude/docs/lld/command-modal.lld.md`:
  - LLD-C2 row: "search/list/status parts" becomes "search/list/status/footer parts".
  - The §3 ORDER note (append order): add the footer.
  - The descriptor `parts:` sketch around line 390: add the footer line.
  - CSS sketch: add a `[data-part='footer']` stub. Keep the edits minimal.
### Acceptance criteria
- `npx vitest run packages/agent-ui/components/src/controls/command-modal/command-modal-descriptor.test.ts` exits 0.
- `grep -n "name: footer" packages/agent-ui/components/src/controls/command-modal/command-modal.md` returns exactly one hit, inside the frontmatter fence.
- `grep -n "footer" .claude/docs/lld/command-modal.lld.md` returns hits in the LLD-C2 row and the parts sketch.
- `npm test` exits 0.
- `npm run check` exits 0.

## Step 3: Real-engine verification
level: L2
### Do
- Make sure Chromium is available: run `npx playwright install chromium` if it is missing.
- Run the command-modal browser test file in the real engine.
- Fix any regression in `command-modal.ts` or `command-modal.css` only. The likely one is the TKT-0017 fixed-frame assertion that the search rect stays identical across a filter that empties the list; a footer placed after the list must not move the search field. Do not edit tests.
### Acceptance criteria
- `npx vitest run --config <the components browser vitest config used by the packages:components shard in package.json> packages/agent-ui/components/src/controls/command-modal/command-modal.browser.test.ts` exits 0 in Chromium and in every other engine the shard runs.
- In a real browser, with the palette open and a filter that matches nothing, the `[data-part="footer"]` bounding rect has height > 0 and sits below the list's rect (`footer.top >= list.bottom`).
- `npm run test:browser` shard `packages:components` exits 0.

## Risks
- **Hidden grader tests may expect different details** than this plan picks: a different part name (for example `data-part="hints"`), `role` or `aria-hidden` semantics, `<kbd>` markup, or hint wording. `data-part="footer"`, "Navigate/Select/Close" and `aria-hidden="true"` are the best guesses from the handoff wording and the part conventions.
- **Region styling:** the nested dialog is `[data-box]`, and `container-box.css` styles `footer` and `[data-region=footer]` children as regions. Using a `div[data-part=footer]` avoids that on purpose, but it still gets the generic `[data-box] > *` inset margin, which could look slightly off next to the flush search field.
- **Token role:** if `--md-sys-color-neutral-outline-variant` does not exist, the border has to reuse an existing role. Step 1 says to grep first.
