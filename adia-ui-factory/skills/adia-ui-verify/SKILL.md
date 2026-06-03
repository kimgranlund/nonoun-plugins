---
name: adia-ui-verify
description: >
  Verify an adia-ui app — the browser-QA gate (zero console errors, non-zero bounding boxes, read the screenshot), accessibility (region roles, keyboard, AA contrast), and git coordination discipline. Use before shipping a surface.
---

# adia-ui-verify

> **Stub — scaffolded in phase (a); content authored in phase (c).**

This skill will own:

- the browser gate: render, zero console errors, non-zero boxes, READ the screenshot
- a11y: region roles + labels, keyboard, AA contrast
- git discipline: re-baseline, explicit allowlists, confirm the branch

Source (to vendor/synthesize): the `app-authoring-best-practices` methodology (SPA) and `adia-ui-kit/rendering-model` (SSR) from the framework, plus the a2ui MCP tool surface.
