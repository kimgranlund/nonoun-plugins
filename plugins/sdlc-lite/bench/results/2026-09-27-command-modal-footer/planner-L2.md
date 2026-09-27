<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add an always-visible `<footer data-part="footer">` to `ui-command-modal`. It shows three keyboard hints (Navigate, Select, Close), each with at least one `<kbd>`. The footer adds no new prop and is listed as a part in the descriptor.

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

## Step 4: Gates green
level: L2
### Do
Run every project gate and fix any red that steps 1 to 3 introduced. Likely spots:
- naming-gates Gate 4 (rendered parts vs descriptor);
- family-coherence;
- `site/lib/command-palette*.test.ts`, whose layout or part assertions the new footer may affect;
- the site-coverage descriptor test.

Fix the code, or update a test to the new behavior. Never delete a test or weaken an assertion. Judge by exit codes. A gate already red at `$SDLC_BASE_SHA` is reported as `inherited red`: prove it by running the same command in a `git worktree add --detach <tmp> "$SDLC_BASE_SHA"` copy.
### Acceptance criteria
- (guard) `npm run check` exits 0
- (guard) `npm test` exits 0
- (guard) `npm run test:browser:packages:components` exits 0
- (guard) `npm run test:browser:site` exits 0
- (guard) `npm run test:browser` shows no new failures versus the base: run the same command in a `git worktree add --detach <tmp> "$SDLC_BASE_SHA"` copy and compare.

## Risks
- Unicode arrow and `↵` glyphs may render differently across engines. Tests should match hint labels by text, never by glyph.
- The footer adds height to the dialog, which may shift site or command-palette browser assertions that measure the dialog frame. Step 4 owns those fixes.
- The grader's hidden tests may pick exact hint markup (for example the label's element), which this plan leaves to the builder. The plan pins only the handoff interface: `[data-hint]`, `<kbd>`, labels, no tabindex or role, and visibility.
- `npm test` takes about 5 minutes, and the full `npm run test:browser` is heavy on a loaded host. A red under load may be contention, not a regression; see `flaky-gates`.
