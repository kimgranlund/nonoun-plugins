<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `packages/agent-ui/components/src/controls/command-modal/command-modal.ts`: new `#footer` field. `#ensureParts()` now builds an `aria-hidden` `[data-part=footer]` with three `span[data-role=hint]` items (`<kbd>↑↓</kbd>` Navigate, `<kbd>↵</kbd>` Select, `<kbd>Esc</kbd>` Close). The call is now `modal.append(search, status, list, footer)`. The header and ORDER comments are updated, and `props` is unchanged.
- `packages/agent-ui/components/src/controls/command-modal/command-modal.css`: new `--ui-command-modal-footer-*` tokens (ink, border, gap, pad-inline, pad-block), which only alias existing roles. `neutral-outline-variant` exists in shared tokens, so the border uses it. Added the `:scope [data-part='footer']` and `footer kbd` rules, a forced-colors footer rule, and the footer in the header part list.

## Checks
- `npx vitest run .../command-modal/command-modal.test.ts`: exit 0.
- A throwaway jsdom test, run before the final guard edit and then deleted, passed all of these:
  - footer count is 1, and still 1 after disconnect and reconnect
  - footer is inside `[data-part=dialog]` and is its `lastElementChild`
  - footer is not `hidden`, and stays not hidden after typing `zzzz` and dispatching `input`
  - footer has `aria-hidden="true"`
  - its text contains Navigate, Select and Close
- The whole command-modal directory ran with that test in place: 3 files, 61 tests, exit 0.
- `npm run check`: the first run exited 2 (TS error: `#footer` declared but never read). After the fix it exits 0.
- Token check: I looped over every `--md-sys-*` token in the CSS and grepped for its definition (`token:`) under `shared/src/tokens`. Every real token is defined there. The only two "missing" hits are the pre-existing prose fragments `--md-sys-color-` and `--md-sys-space` in comments.
- `git diff` of the `.ts` changes no line in `props`.
- `git diff --stat` shows only the two files above and no `*.test.ts`.

## Notes
- The handoff has no footer reader, so `#footer` alone failed `noUnusedLocals`. I added `this.#footer` to the `#ensureParts` early-return guard, which now reads `this.#modal && this.#search && this.#list && this.#footer`. All four fields are set in the same pass, so the guard behaves the same and stays idempotent.
- The reconnect check ran before that guard edit, and I did not re-run the throwaway test afterwards. After the edit, `command-modal.test.ts` and `npm run check` both exited 0.
