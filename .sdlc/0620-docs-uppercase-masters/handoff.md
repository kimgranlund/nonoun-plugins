---
id: T-0620
title: "docs: one UPPERCASE master per folder, numbered children"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0618]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every `docs/` home or topic folder holds one UPPERCASE master file (its index, barrel or single source of truth) and numbered children `NNN-slug.md`; `docs_check.py` enforces both, with selftest cases that fail before the fix.

## Context
User decisions 2026-10-19: authoritative files are the barrel, index or single source of truth of a folder and use UPPERCASE names (`ROADMAP.md`, `SPECS.md`, `GUIDES.md`); the other files in that folder are numbered. This replaces "number only decisions, goals and kpi": numbering now applies to every child document. Existing forms keep working: `decisions/NNNN-slug.md`, `goals/` and `kpi/` `NNN-slug.md`, `reports/YYYY-MM-DD-slug.md` (dated reports count as numbered), `work/NNNN-slug/` ticket folders. `AGENTS.md` stays the agent router for the folder and links the master; the master holds the content index. D-12 (`plugins/sdlc-lite/scripts/docs_check.py:292`) enforces lowercase kebab today. The `work/` masters from T-0618 are `docs/work/ROADMAP.md` and `docs/work/NOTES.md`.

## Constraints
- The failing selftest cases land before or with the fix.
- Rule M (master): a folder with documents has exactly one UPPERCASE `[A-Z0-9-]+.md` master besides ecosystem names (`README.md`, `AGENTS.md`, `CLAUDE.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md`); `work/` may have its two named masters. A master lists every child in the folder (this is the T-0619 index rule's target).
- Rule N (numbered): every other Markdown file is `NNN-slug.md` (or `NNNN-` where that form exists, or a dated report); numbers are identity, assigned next-free per folder and never reused; a gap is fine.
- Provide `docs_check.py next <folder>` to print the next free number, and a migrate helper that numbers existing children and writes the master from the folder's current entry-file links, rewriting inbound links.
- Ship both rules as `warning` first, raisable to `error` in `docs/layout.md`.
- Update the onboard managed block ("Adding a document"), `docs/layout.md` forms column, and the naming card in `specs/doc-standards/`.
- Validation: `python3 plugins/sdlc-lite/scripts/docs_check.py selftest`, `python3 plugins/sdlc-lite/scripts/onboard.py selftest`, `python3 plugins/sdlc-lite/scripts/check.py`.
