---
id: T-0620
title: "docs: authoritative master files use UPPERCASE names, checked against front matter"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0618]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Authoritative master files in `docs/` carry UPPERCASE names, and `docs_check.py` checks it both ways: an UPPERCASE name needs a master declaration, and a declared master needs an UPPERCASE name, with selftest cases that fail before the fix.

## Context
User decision 2026-10-19: all authoritative files use UPPERCASE (`ROADMAP.md` and the like), chosen over a closed allowlist. To keep it checkable, "authoritative" is declared, not judged: front matter `authority: master`. Ecosystem names (`README.md`, `AGENTS.md`, `CLAUDE.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md`) stay UPPERCASE with no front matter. D-12 (`plugins/sdlc-lite/scripts/docs_check.py:292`) enforces lowercase kebab-case today. The `work/` singletons from T-0618 become `docs/work/ROADMAP.md` and `docs/work/NOTES.md`.

## Constraints
- The failing selftest cases land before or with the fix.
- Rule: a Markdown file whose stem is UPPERCASE kebab (`[A-Z0-9-]+`) and not an ecosystem name must have `authority: master`; a file with `authority: master` must have an UPPERCASE stem. At most one master per folder. Folders keep lowercase kebab names.
- Rename through `git mv` in two steps (case-insensitive macOS) and rewrite links; the T-0618 migrate command does `ROADMAP.md` and `NOTES.md`, and `tickets.py roadmap` writes the new name.
- Ship as a `warning` first, raisable to `error` in `docs/layout.md`, like T-0619.
- Update the onboard managed block and `docs/layout.md` naming rule text, and the doc-standards card for naming.
- Validation: `python3 plugins/sdlc-lite/scripts/docs_check.py selftest`, `python3 plugins/sdlc-lite/scripts/onboard.py selftest`, `python3 plugins/sdlc-lite/scripts/check.py`.
