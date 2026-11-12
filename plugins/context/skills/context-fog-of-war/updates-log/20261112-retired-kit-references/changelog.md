---
date: 2026-11-12
slug: retired-kit-references
requested_by: T-0847 (drop references to the retired UI kit skill)
harness: Claude Code
model: claude-opus-5-5
authors:
  - role: solo
    agent: T-0847 solo L2
    model: claude-opus-5-5
    did: Reworded live guidance and comments that named the retired UI kit skill as current.
verification: 72 unittest methods pass.
---

## Changed

- `assets/tokens.css` and its mirrored comment in `assets/shell.html`: geometry now credits the UI kit bundle embedded in the shell.
- `scripts/build_shell.py`: `--kit` help and docstring describe the needed fragment build and say no shipped skill offers one.
- `references/viewer.md`, `references/workflows.md`, `scripts/workflow.py`: no longer name the retired kit as the current source.

## Open

- The shipped shell cannot be rebuilt until a UI kit offers `scripts/build.mjs FRAGMENT OUT`; its embedded source stamp and the frozen cohort name in `references/diagnostics.md` stay as history.
