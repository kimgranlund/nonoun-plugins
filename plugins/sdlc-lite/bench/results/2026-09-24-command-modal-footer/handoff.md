## Goal
Add an always-visible footer to the command modal (`ui-command-modal`). It shows keyboard hints for navigate, select and close, and adds no new prop.

## Context
- Component lives in `packages/agent-ui/components/src/controls/command-modal/` (`command-modal.ts`, `command-modal.css`, the `command-modal.md` descriptor, and the unit, descriptor and browser tests).
- Design spec: `.claude/docs/lld/command-modal.lld.md` (base version). Read it and the existing control-created parts (search, list, status, empty) to follow the same part conventions.
- Styling uses only existing `--md-sys-color-*` tokens; do not add new tokens.
- Browser tests need Playwright browsers installed (`npx playwright install chromium` if missing).

## Constraints
- Do not edit test files.
- Do not add a new public prop or attribute to the component.
- Keep the `command-modal.md` descriptor in sync with the component's parts.
