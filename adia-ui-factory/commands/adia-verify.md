---
description: Verify an adia-ui surface in the browser (QA + a11y gate).
argument-hint: [path]
---

Verify an adia-ui surface before shipping. **$ARGUMENTS**

Hand off to **`adia-ui-verify`** for the exit gate: render in a real browser (zero console errors on load, non-zero bounding boxes, and *read* the screenshot), check accessibility (region roles + labels, keyboard paths, AA contrast), and confirm git hygiene (re-baseline, explicit allowlists, right branch).

> The `adia-ui-verify` skill's full depth lands in a later phase (see ROADMAP.md); the gate above is the contract it will mechanize.
