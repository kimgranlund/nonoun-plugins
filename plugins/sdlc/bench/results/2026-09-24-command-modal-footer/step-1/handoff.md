## Task goal
Add an always-visible footer to the command modal (`ui-command-modal`). It shows keyboard hints for navigate, select and close, and adds no new prop.

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
