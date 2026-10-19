---
id: T-0619
title: "docs_check: every doc listed in its home index, per-home file cap"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0618, T-0620]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`docs/` cannot become a dumping ground: every document is listed in its home's (or topic's) entry file, and a home or topic past a file cap must split into topic subfolders, both enforced by `docs_check.py` with selftest cases that fail before the fix.

## Context
User decision 2026-10-19: numbers by kind plus an index, not numbers everywhere. Naming stays as today: `NNNN-slug` for decisions and work tickets, `NNN-slug` for goals and kpi, `YYYY-MM-DD-slug` for reports (D-12 already enforces kebab-case and decision numbers), kebab-case for specs, planning, guides and references. Existing rules: D-7 requires an `AGENTS.md` once a folder reaches `onboard.ENTRY_THRESHOLD` documents (`plugins/sdlc-lite/scripts/docs_check.py:326`), D-5 and D-6 guard `other/` (`owner:`, `review-by:`). Missing: a document not linked from its folder's entry file passes, and nothing caps a folder's size. Depends on T-0618 so the `work/` home exists first.

## Constraints
- The failing selftest cases land before or with the fix.
- New rules: D-13, a document not linked from its folder's UPPERCASE master (T-0620), falling back to the folder's `AGENTS.md` while no master exists; D-14, a home or topic with more than a cap of documents (default 12, set in `docs/layout.md`) that has no topic subfolders. Report and evidence folders, `assets/`, `archive/`, `work/` ticket folders and frozen paths are exempt.
- Ship both as `warning` first, so adopting repos are not broken on upgrade; a `layout.md` line can raise them to `error`. This repo raises them to `error` once its own docs pass.
- Update the onboard managed block's "Adding a document" steps so step 3 says to add the link to the folder's entry file (onboard setup refreshes the generated Contents list).
- Validation: `python3 plugins/sdlc-lite/scripts/docs_check.py selftest`, `python3 plugins/sdlc-lite/scripts/onboard.py selftest`, and `python3 plugins/sdlc-lite/scripts/check.py`.
