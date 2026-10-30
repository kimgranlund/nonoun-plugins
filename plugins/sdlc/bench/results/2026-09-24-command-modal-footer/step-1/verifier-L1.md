<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Command-modal test file exits 0: pass. Evidence: `npx vitest run .../command-modal.test.ts` gave 45 passed (45). The `EXIT` line printed empty because `PIPESTATUS` is zsh-unsafe, so the exit code was not captured directly.
- jsdom behaviour: pass. Evidence: I ran a throwaway test in a temporary worktree with the changed `command-modal.ts` copied in, then removed the worktree. It passed 1/1 and asserted these:
  - exactly one `[data-part="footer"]`, before and after a disconnect and reconnect;
  - the footer's parent is `[data-part="dialog"]` and it is the dialog's `lastElementChild`;
  - `hidden` is false, including after typing `zzzz` and dispatching `input`;
  - `aria-hidden="true"` is set and there is no `tabindex`;
  - the text contains Navigate, Select and Close.
- No change to the `props` object: pass. Evidence: the `command-modal.ts` diff hunks touch only the header comment, the `#footer` field, `#ensureParts` and the modal append. `static props` is not touched.
- Every `--md-sys-*` token in the CSS is already defined in shared tokens: pass. Evidence:
  - I grepped for `<token>:` under `shared/src/tokens`. Each named token has at least 1 hit: `neutral-outline-variant` 11, `space-sm` 1, `shape-corner-base` 2, and so on.
  - The only two zero-hit entries, `--md-sys-color-` and `--md-sys-space`, are prefix fragments from comments, not tokens.
  - The CSS defines no new `--md-sys-*` token.
- `npm run check` exits 0: pass. Evidence: `CHECK EXIT 0`, last line `selftest: all green`.
- No `*.test.ts` file changed: pass. Evidence: `git diff --stat` lists only `command-modal.css` and `command-modal.ts`.
- Implementation matches the Do list: pass. Evidence:
  - `command-modal.ts` builds the footer once, with items in the order `↑↓` Navigate, `↵` Select, `Esc` Close.
  - It is stored in `#footer`, and the `#ensureParts` guard includes `#footer`.
  - `modal.append(search, status, list, footer)` puts the footer last, with search first and list after it.
  - Both comments (header and ORDER) are updated.
  - The CSS adds the footer tokens, the `:scope [data-part='footer']` rule (flex, gap, caption font, muted ink, 1px `border-block-start`, `flex-shrink: 0`), the `kbd` rule, the forced-colors lines and the header part list.

## Out of scope changes
None. `.sdlc/` is untracked harness state.

## For the next attempt
None
