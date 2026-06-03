---
name: adia-ui-verify
description: >
  Verify an adia-ui app — the browser-QA gate (zero console errors, non-zero bounding boxes, read
  the screenshot), accessibility (region roles, keyboard, AA contrast), and git coordination
  discipline. Use before shipping a surface, in either rendering mode.
---

# adia-ui-verify — the exit gate

The check every surface passes before it ships. **Mode-independent.** Full depth in `${CLAUDE_PLUGIN_ROOT}/references/verification.md`; this is the contract.

## The gate, in order

1. **Browser render** — load the surface in a real browser. Pass requires: **zero** `console.error`/`pageerror` on load, **non-zero** bounding boxes on the key elements, and you have **read** the `deviceScaleFactor: 2` screenshot (DOM-present-but-clipped only shows in pixels). Re-probe after every structural change.
2. **Accessibility** — region role + `aria-label` on the surface; a keyboard path for every interaction; AA contrast; overlays via `.open` (never a hardcoded `open`); real heading roles.
3. **Git hygiene** — re-baseline (status / log / branch / fetch); stage explicit allowlists (never `git add -A` on a shared clone); confirm the branch; surface big cross-cutting changes rather than merging them unilaterally.

## The rule that matters most

**"Tests pass, ship it" is the anti-pattern.** Unit tests are necessary, not sufficient — the browser gate is what catches the 0×0 host, the clipped content, and the console error that no unit test sees. If you haven't rendered it and read the screenshot, it isn't verified.

The advisory `adia-lint` hook catches *structural* smells on write (shadow DOM, raw colors, `::slotted`, SSR traps); it is not a substitute for this gate, and it never blocks.

## Reference

- `${CLAUDE_PLUGIN_ROOT}/references/verification.md` — the probe shape, the a11y checklist, the git discipline.
