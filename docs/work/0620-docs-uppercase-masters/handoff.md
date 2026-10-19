---
id: T-0620
title: "docs: generated folder index, opt-in numbering with atomic allocation, declared UPPERCASE singletons"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0618]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`docs/` naming stays checkable without renaming history: each folder's index is the onboard-generated Contents list in its `AGENTS.md`, numbering applies to new files in kinds that `docs/layout.md` marks numbered, numbers come from an atomic allocator, and UPPERCASE names are allowed only for singletons `layout.md` declares; each rule has a selftest case that fails before the fix.

## Context
User decision 2026-10-19 after an adversarial review of the earlier "one UPPERCASE master per folder, every child numbered" model, which was rejected because: renaming breaks 153 frozen closed-ticket citations and 44 live links in this repo; "next free number in the folder" collides across parallel lanes (the gen-ui-kit cf2/cf3 id swap in the 2026-10-18 retro, the same race T-0588 fixed for ticket ids with refs); an index (derived) and a source of truth (content) are different roles; a master beside `AGENTS.md` makes two indexes that drift; and the fleet's large folders are already numbered or dated kinds (gen-ui-kit `ops/adr` 116, `tickets` 86, `releases` 60). D-7 already requires a folder `AGENTS.md`; D-12 (`plugins/sdlc-lite/scripts/docs_check.py:292`) enforces lowercase kebab and decision numbers.

## Constraints
- The failing selftest cases land before or with the fix.
- Index: onboard writes and refreshes a Contents list in each folder `AGENTS.md`; T-0619's D-13 checks against it. No separate master file.
- Numbering: a `layout.md` Kinds row may declare `form: NNN-slug` (decisions, goals, kpi, work already do); D-12 checks new files in such a folder only; existing files keep their names (grandfathered by first-seen commit or an allowlist written by the migrate step). No renames of existing docs.
- Allocation: `docs_check.py next <folder>` reserves a number through an atomic git ref (as `refs/sdlc/ids/<id>` does for tickets, T-0588), so two lanes never get the same number.
- UPPERCASE: allowed for the ecosystem names (`README.md`, `AGENTS.md`, `CLAUDE.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md`) and for singletons a `layout.md` row declares (`work/ROADMAP.md`, `work/NOTES.md` from T-0618); any other UPPERCASE stem is a D-12 finding.
- Ship new findings as `warning` first, raisable to `error` in `layout.md`.
- Validation: `python3 plugins/sdlc-lite/scripts/docs_check.py selftest`, `python3 plugins/sdlc-lite/scripts/onboard.py selftest`, `python3 plugins/sdlc-lite/scripts/check.py`.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/docs_check.py selftest` exits 0; its gates `numbered`, `uppercase`, `grandfather` and `next` each reject their negative variants (a numbered-form rule dropped, Grandfathered or Levels ignored, ecosystem names or declared singletons dropped, a migrate step that writes nothing, an allocator that reserves no ref).
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0; its gates `create` and `layout-sections` pass (the entry block heading change and the two new layout sections with their form errors).
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- `python3 plugins/sdlc-lite/scripts/docs_check.py --root .` reports 0 errors.
- No existing file under `docs/` is renamed: `git diff --name-status --diff-filter=R $(git merge-base HEAD main)` prints nothing.
