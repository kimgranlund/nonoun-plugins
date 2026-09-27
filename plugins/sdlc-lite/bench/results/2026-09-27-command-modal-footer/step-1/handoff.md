## Task goal
Add an always-visible footer to the command modal (`ui-command-modal`). It shows keyboard hints for navigate, select and close, and adds no new prop.

Interface the tests rely on:
- One `<footer data-part="footer">` element, appended into the modal (`ui-modal`) together with the existing search, list and status parts, rendered below the list and inside the dialog surface.
- Exactly 3 hints, each an element carrying a `data-hint` attribute (tests select them with `[data-hint]`) and containing at least one `<kbd>`, with the labels `Navigate`, `Select` and `Close`.
- The footer and its `<kbd>` elements carry no `tabindex` and no `role`.
- It stays visible (not `hidden`, not `display: none`, non-zero height) even when filtering leaves zero options.
- `footer` is listed as a part in the component's descriptor, next to `search`, `list`, `status` and `empty`.

## Step 1: Create the footer part in command-modal.ts, with unit tests
level: L2
### Do
In `packages/agent-ui/components/src/controls/command-modal/command-modal.ts`, change `#ensureParts()`:
- Create one `footer` element with `document.createElement('footer')` and `setAttribute('data-part', 'footer')`. Keep a `#footer` private field next to `#status`/`#emptyRow`.
- Fill the footer with exactly 3 hint elements, in this order:
  - `span[data-hint="navigate"]` holding `<kbd>↑</kbd><kbd>↓</kbd>` and the label text `Navigate`.
  - `span[data-hint="select"]` holding `<kbd>↵</kbd>` (or `Enter`) and the label `Select`.
  - `span[data-hint="close"]` holding `<kbd>Esc</kbd>` and the label `Close`.
- Put the label text in its own element (for example `<span data-hint-label>`) so each hint's label reads exactly `Navigate`/`Select`/`Close`.
- Set no `tabindex` and no `role` on the footer, the hints or the `<kbd>`s. Never set `hidden` on the footer, and have `#filter` never touch it.
- Change the append line to `modal.append(search, status, list, footer)`. The footer must come after the list, inside the ui-modal, so ui-modal moves it into its `<dialog>`.
- Keep `#ensureParts` idempotent: reconnecting must not create a second footer.
- Add no prop to `static props`.
- Do not write the literal `key === 'Escape'` anywhere (the descriptor test's negative control greps for it). Hint text `Esc` is fine.
- Update the header comment and the `LLD-C2` comment to name the footer part.

In `command-modal.test.ts` (jsdom), add a `describe` whose title contains `footer`. Its tests assert:
- exactly one `[data-part="footer"]`, a `FOOTER` element, whose `previousElementSibling` chain places it after `[data-part="list"]` inside the same `[data-part="dialog"]`/ui-modal;
- `footer.querySelectorAll('[data-hint]')` has length 3, and every hint has at least one `kbd`;
- the hint texts include `Navigate`, `Select` and `Close`;
- the footer and every `kbd` have no `tabindex` and no `role` attribute;
- after typing a query that matches nothing, `footer.hidden` is false and the footer is still attached;
- disconnect plus reconnect keeps exactly one footer, and it is the same node.

Update any existing parts-count or ordering assertion this legitimately changes. Never delete or weaken one.
### Acceptance criteria
- `grep -q "setAttribute('data-part', 'footer')" packages/agent-ui/components/src/controls/command-modal/command-modal.ts`
- `grep -q 'data-hint' packages/agent-ui/components/src/controls/command-modal/command-modal.ts`
- `grep -qE "modal\.append\(search, status, list, footer\)" packages/agent-ui/components/src/controls/command-modal/command-modal.ts`
- `out=$(npx vitest run packages/agent-ui/components/src/controls/command-modal/command-modal.test.ts -t footer 2>&1) && printf '%s\n' "$out" | grep -qE 'Tests +[1-9][0-9]* passed'`
- (guard) `npx vitest run packages/agent-ui/components/src/controls/command-modal/command-modal.test.ts packages/agent-ui/components/src/controls/command-modal/command-modal-descriptor.test.ts` exits 0
- Observable: the `const props = {` block in command-modal.ts declares the same five props as before (`open`, `label`, `placeholder`, `hotkey`, `filter`) and nothing else.
