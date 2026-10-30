## Goal
Add an always-visible footer to the command modal (`ui-command-modal`). It shows keyboard hints for navigate, select and close, and adds no new prop.

Interface the tests rely on:
- One `<footer data-part="footer">` element, appended into the modal (`ui-modal`) together with the existing search, list and status parts, rendered below the list and inside the dialog surface.
- Exactly 3 hints, each an element carrying a `data-hint` attribute (tests select them with `[data-hint]`) and containing at least one `<kbd>`, with the labels `Navigate`, `Select` and `Close`.
- The footer and its `<kbd>` elements carry no `tabindex` and no `role`.
- It stays visible (not `hidden`, not `display: none`, non-zero height) even when filtering leaves zero options.
- `footer` is listed as a part in the component's descriptor, next to `search`, `list`, `status` and `empty`.

## Context
- Component lives in `packages/agent-ui/components/src/controls/command-modal/` (`command-modal.ts`, `command-modal.css`, the `command-modal.md` descriptor, and the unit, descriptor and browser tests).
- Design spec: `.claude/docs/lld/command-modal.lld.md` (base version). Read it and the existing control-created parts (search, list, status, empty) to follow the same part conventions.
- Styling uses only existing `--md-sys-color-*` tokens; do not add new tokens.
- Browser tests need Playwright browsers installed (`npx playwright install chromium` if missing).

## Constraints
- Existing tests your change legitimately breaks may be updated to the new behavior; never delete a test or weaken an assertion to get green. The grader overwrites its own test files after the run, so edits to those do not count.
- Do not add a new public prop or attribute to the component.
- Keep the `command-modal.md` descriptor in sync with the component's parts.
