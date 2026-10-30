<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- packages/agent-ui/components/src/controls/command-modal/command-modal.css: added the `--ui-command-modal-footer-*` tokens (they alias only existing roles and the space and font ladders), the `[data-part='footer']` rule and the `[data-part='footer'] kbd` rule, a forced-colors CanvasText entry, and `footer` in the header comment's part list.
- packages/agent-ui/components/src/controls/command-modal/command-modal.browser.test.ts: added a new describe "the keyboard-hint footer stays visible below the list" that checks the footer after a query matching nothing.

## Checks
- `grep -q "\[data-part='footer'\]" …command-modal.css`: matched.
- `out=$(npx vitest run --config vitest.browser.config.ts --project packages …command-modal.browser.test.ts -t footer 2>&1) && … grep -qE 'Tests +[1-9][0-9]* passed'`: exit 0, "Tests 2 passed | 30 skipped", the grep matched.
- (guard) full `command-modal.browser.test.ts` browser run: exit 0, 32 passed.
- `git diff "$SDLC_BASE_SHA" -- …command-modal.css`: every added custom-property declaration starts with `--ui-command-modal-`, and no `--md-sys-*:` declarations were added.

## Notes
- `command-modal.ts` and `command-modal.test.ts` were already modified in the tree before this step started (step 1's work). I did not touch them.
- The footer has one extra property the handoff did not list: its background aliases `--ui-command-modal-search-bg`, which the handoff allowed.
- The kbd rule has one extra line the handoff did not list: a `1px solid currentColor` border for the keycap look.
