<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- packages/agent-ui/components/src/controls/command-modal/command-modal.ts: adds the `#footer` field and builds `<footer data-part="footer">` with 3 `span[data-hint]` hints (navigate ↑↓, select ↵, close Esc). Each label sits in its own `span[data-hint-label]`. The append line is now `modal.append(search, status, list, footer)`, the idempotency guard now includes `#footer`, and the header, LLD-C2 and ORDER comments name the footer.
- packages/agent-ui/components/src/controls/command-modal/command-modal.test.ts: new `describe('ui-command-modal — footer part (keyboard hints)')` with 5 tests covering the single footer after the list inside the dialog, the 3 hints each with a kbd and the right labels, no tabindex or role, still visible when nothing matches, and the same single node after reconnect.

## Checks
- The three `grep -q` criteria (setAttribute footer, data-hint, the append line): all pass.
- `npx vitest run .../command-modal.test.ts -t footer`: exits 0, "Tests 5 passed | 45 skipped (50)", matching the `Tests +[1-9][0-9]* passed` regex.
- (guard) `npx vitest run .../command-modal.test.ts .../command-modal-descriptor.test.ts`: exits 0, 65 passed.
- The `const props` block still declares exactly open, label, placeholder, hotkey and filter.
- `grep -c "key === 'Escape'"` on command-modal.ts: 0.
- `npx tsc --noEmit -p .`: 0 errors. The first run gave TS6133 because `#footer` was never read; including it in the `#ensureParts` idempotency guard fixed that.

## Notes
- The goal says `footer` must be listed in the component's descriptor. That descriptor edit was not in this step's Do and was not made here, so a later step has to do it.
- No existing assertion was changed.
- There is no footer CSS yet. In jsdom the footer is visible because `hidden` is false; its non-zero height in a real browser was not checked.
