## Task goal
Add an always-visible footer to the command modal (`ui-command-modal`). It shows keyboard hints for navigate, select and close, and adds no new prop.

Interface the tests rely on:
- One `<footer data-part="footer">` element, appended into the modal (`ui-modal`) together with the existing search, list and status parts, rendered below the list and inside the dialog surface.
- Exactly 3 hints, each an element carrying a `data-hint` attribute (tests select them with `[data-hint]`) and containing at least one `<kbd>`, with the labels `Navigate`, `Select` and `Close`.
- The footer and its `<kbd>` elements carry no `tabindex` and no `role`.
- It stays visible (not `hidden`, not `display: none`, non-zero height) even when filtering leaves zero options.
- `footer` is listed as a part in the component's descriptor, next to `search`, `list`, `status` and `empty`.

## Step 3: Document the footer part in the descriptor, the descriptor test and the LLD
level: L1
### Do
In `packages/agent-ui/components/src/controls/command-modal/command-modal.md`:
- Add a `- name: footer` entry to `parts:` after `empty`. It has no `role:` line. Its description says: the control-created always-visible `<footer>` below the list, inside the dialog, holding 3 `[data-hint]` keyboard hints (Navigate ↑↓, Select ↵, Close Esc) as `<kbd>`s; no tabindex or role; never hidden, even at zero results; not a prop.
- Mention the footer in the prose "Composition" bullet that lists the parts moved into the modal. Optionally add a short `## The keyboard-hint footer` section.
- Leave `attributes[]` unchanged.

In `command-modal-descriptor.test.ts`, extend the parts `arrayContaining` list to `['search', 'list', 'status', 'empty', 'footer']`.

In `.claude/docs/lld/command-modal.lld.md`, add the footer to the LLD-C2 row, the `modal.append(...)` interface snippet, the `parts:` list near line 393, and a CSS note. Record it as an amendment. Do not renumber existing IDs.
### Acceptance criteria
- `awk '/^parts:/,/^customStates:/' packages/agent-ui/components/src/controls/command-modal/command-modal.md | grep -q -- '- name: footer'`
- `grep -q "'footer'" packages/agent-ui/components/src/controls/command-modal/command-modal-descriptor.test.ts`
- `grep -q footer .claude/docs/lld/command-modal.lld.md`
- (guard) `npx vitest run packages/agent-ui/components/src/controls/command-modal/command-modal-descriptor.test.ts packages/agent-ui/components/src/controls/naming-gates.test.ts` exits 0
