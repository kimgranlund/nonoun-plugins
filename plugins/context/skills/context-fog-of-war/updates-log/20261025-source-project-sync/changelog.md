---
date: 2026-10-25
slug: source-project-sync
requested_by: user
harness: Claude Code
authors:
  - role: solo
    agent: Claude Code
    model: claude-opus-5-5
    did: Brought the source project's skill folder up to the reconciled installed version
project: context-fog-of-war-map (source project)
verification: Byte parity of the source skill folder with both installed copies (excluding __pycache__); project suite 143 tests pass before and after; skill suite 51 tests pass in all three copies
backup: /private/tmp/claude-501/-Users-kimba-Projects-differential-ui/c9549422-5cce-4b8c-9cd2-158262cc2047/scratchpad/fog-sync/project-backup
---

## Added

- `references/learnings/cli-routing.md` and the change set records `20261020-cli-routing-lessons`, `20261020-claude-sync`, `20261025-claude-truncation` and `20261025-claude-codex-reconcile`, which existed only in the installed copies.

## Changed

- `SKILL.md`, `references/engineering.md` and `references/learnings/README.md` now carry the CLI routing route and wording already shipped in the installed copies.
- `scripts/truncation.py` and `tests/test_diagnostics.py` now include the `[N characters truncated]` marker and its regression tests.
- `updates-log/CHANGELOG.md` lists every change set in all three copies.

## Fixed

- The source project was behind both installed copies. Every difference was content added later to the installed copies; the source held no edits of its own, so nothing was overwritten.

## Open

- The source project and the two installed copies are three separate directories. Make future changes in the source project, then copy the skill folder to both installed paths and confirm byte parity.
- Browser checks (`node tests/browser.cjs`) were not run; this change touches no shell asset.
