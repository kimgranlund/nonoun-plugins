# Verification — the exit gate

Mode-independent. A surface is done when it passes the **browser gate** + the a11y check + git hygiene — not when it compiles and not when unit tests pass. "Tests pass, ship it" is the anti-pattern: unit tests are necessary, not sufficient.

## The browser gate (the real gate)

Render the surface in a real (headless) browser and assert four things:

1. **Zero `console.error` / `pageerror` on load** — collect them during navigation; any is a failure.
2. **Non-zero bounding boxes** on the key elements — catches the "upgraded but never sized" 0×0 host, where the element exists but renders nothing.
3. **Read the screenshot** — capture at `deviceScaleFactor: 2` and actually look at it. Content can be present in the DOM yet visually clipped, overlapped, or off-canvas; only the pixels catch that. A probe that screenshots but doesn't read it hasn't verified anything.
4. **Re-probe after every structural change** — a stale screenshot lies.

Minimal probe shape (Playwright; works against a Vite static host or an SSR dev URL):

```js
const errors = [];
page.on('console', m => m.type() === 'error' && errors.push(m.text()));
page.on('pageerror', e => errors.push(String(e)));
await page.goto(url, { waitUntil: 'networkidle' });
const box = await page.locator('my-surface').boundingBox();   // expect non-zero w/h
await page.screenshot({ path: 'probe.png', scale: 'device' }); // then READ probe.png
// gate: errors.length === 0 && box.width > 0 && box.height > 0 && (you read the image)
```

## Accessibility

- **Landmarks** — the surface carries `role="region"` with an `aria-label`; control clusters are labelled.
- **Keyboard** — every interaction has a keyboard path; no mouse-only affordances.
- **Contrast** — AA minimum; don't let host styles override the computed contrast of tokens.
- **Overlays** — drive `<modal-ui>` / `<drawer-ui>` via the `.open` property; a hardcoded `open` attribute bricks the page.
- **Roles** — don't use deprecated `aria-grabbed`; a presentational `text-ui variant="heading"` needs a real heading role or `<h*>` wrapper.

## Git coordination

- **Re-baseline at the start of every turn** — `git status --short`, `git log --oneline -5`, `git branch --show-current`, and a `fetch` to see remote drift. Memory records the tree "as of last write"; after a peer commit it's stale.
- **Never `git add -A` on a shared clone** — stage explicit allowlists; the commit message names what was deliberately left out.
- **Confirm the branch before committing or releasing.** Trust the working tree + `git log` over memory.
- **Surface big cross-cutting changes** — don't unilaterally merge a library-wide refactor into shared main; scope it and hand it to the release flow.
