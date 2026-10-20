---
id: T-0664
title: "A write-once designs home for grill output in the onboard docs table"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A grill design that a project keeps has its own write-once home in the onboard docs table, so it never lands in `specs/` (edited in place) and a later round points back to the design it replaces.

## Intent
- Do: (1) `plugins/sdlc-lite/scripts/onboard.py` adds a `designs/` kind: a row in `DOCS_AGENTS_TEMPLATE` (holds ratified grill designs, one file per round, write-once, `supersedes:` front matter naming the design it replaces), a row in the layout `## Kinds` table and `## Homes` list, a `DOC_KINDS` entry, and a `Which home` / `## Decide` line placed before `specs/`. (2) `plugins/sdlc-lite/scripts/docs_check.py` adds `designs` to `DEFAULT_HOMES` and warns when a `designs/` file's `supersedes:` names a file that does not exist; update the "twelve default homes" count in its docstring. (3) `plugins/sdlc-lite/skills/grill/SKILL.md` names the target path: a design worth keeping is copied from the records dir to `docs/designs/<slug>.md`, and a re-grill writes a new file with `supersedes: <old file>` instead of editing the old one.
- Non-goals: an `Amended by:` line in the old design (it would break write-once; the `supersedes:` chain is the pointer); moving any existing document; changing where grill writes its working `design.md` (the records dir).
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #24, ui-kit-neue audit 2026-10-20.
In the audited repo 7 of 8 `docs/specs/design-*.md` files say they are write-once, against the docs table's "specs: edited in place"; later amendments sat in closed tickets with no pointer from the spec.
Confirmed here: `plugins/sdlc-lite/skills/grill/SKILL.md:53` says "A ratified design is write-once. When a constraint or the scope shifts, re-grill the affected forks into a new design file; never patch the old one." Grill writes `design.md` in the task's git-ignored records dir (`grill/SKILL.md:33`) and names no committed home for a design worth keeping. The docs table offers `specs/` "What the system is and must do; edited in place" (`onboard.py:444`) and `decisions/` "One numbered decision per file" (`onboard.py:446`); neither fits a multi-fork design. Kind rows: `onboard.py:514` to `:525`; Decide list `onboard.py:528` to `:540`; Which home list `onboard.py:458` to `:470`; `DOC_KINDS` `onboard.py:53`; layout homes list `onboard.py:494` onward. docs_check: `DEFAULT_HOMES` `plugins/sdlc-lite/scripts/docs_check.py:59`, `TOPIC_KINDS` `:62`, docstring count `:21`.
Existing consumer `docs/layout.md` files list their homes explicitly, so they gain `designs/` only when they add the line; say so in the onboard skill's notes if it covers layout upgrades. The docs-schema design under `docs/planning/docs-schema/` names the twelve homes; add one line there.

## Constraints
The managed block changes its stamp; refresh this repo's `docs/AGENTS.md` with `onboard.py setup` in the same change. Existing homes and their rules are unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0, and `grep -n 'designs/' plugins/sdlc-lite/scripts/onboard.py` shows the docs table row, the Kinds row, and the Which home line.
2. `python3 plugins/sdlc-lite/scripts/docs_check.py selftest` exits 0 with a new case: a `docs/designs/b.md` whose `supersedes:` names a missing `docs/designs/a.md` warns, and the same file with `a.md` present does not. The case fails with the change reverted.
3. `grep -n 'docs/designs/' plugins/sdlc-lite/skills/grill/SKILL.md` names the target path and `supersedes:`.
4. `python3 plugins/sdlc-lite/scripts/onboard.py check 2>&1 | grep 'docs/AGENTS.md'` prints `current docs/AGENTS.md`.
5. `python3 scripts/check-packaging.py` exits 0 and `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
6. `git diff --check` exits 0.

## Outcome
- `onboard.py`: `designs` in `DOC_KINDS`; a `designs/` row in the docs table, `## Homes`, `## Kinds`; a Which home line and a `## Decide` line placed before `specs/` (the lists now run to 13); selftest expectations updated.
- `docs_check.py`: `designs` in `DEFAULT_HOMES` (docstring and D-1 message say thirteen); new rule D-15 warns when a `designs/` file's `supersedes:` names a missing file (relative to the design's folder, or a `docs/` path); new `designs` selftest gate with the negative control `drops D-15`.
- `check.py`: the docs check names `D-1` to `D-15`.
- `skills/grill/SKILL.md`: a kept design goes to `docs/designs/<slug>.md`; a re-grill writes a new file with `supersedes: <old file>`.
- `skills/onboard/SKILL.md`: a note that an existing `docs/layout.md` gains `designs/` only when the repository adds it.
- `docs/planning/docs-schema/design.md`: one `designs/` row in the homes table. `docs/AGENTS.md` refreshed by `onboard.py setup`.
- Checks: onboard selftest exit 0, docs_check selftest exit 0, `onboard.py check` prints `current docs/AGENTS.md`, check-packaging exit 0, check.py exit 0, `git diff --check` exit 0.

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: `redck.py deviations` printed no `process deviation:` lines. No `(red)` criterion is declared, and criterion 2's negative control was observed in the selftest and against the base copy. | note: `git grep -i twelve` over plugins, docs and scripts, excluding reports and `.sdlc`, shows no stale home count outside historical ticket records. | note: `docs_check.py --root .` on the repo reports 0 errors and 82 warnings, none of them D-15 or D-1. These are warnings that exist at base.) · verifier: verifier-L2 (sonnet) · base: 37f785dc7925
- Changed: see commits
- Commits: 40e5ff2 T-0664: a write-once designs home for grill output in the onboard docs table
- Check: 1 onboard selftest exits 0 and `grep -n 'designs/' onboard.py` shows the docs table row, the Kinds ...: pass
- Check: 2 `docs_check.py selftest` exits 0 with a new case that warns when `supersedes:` names a missing fi...: pass
- Check: 3 `grep -n 'docs/designs/' grill/SKILL.md` names the target path and `supersedes:`: pass
- Check: 4 `onboard.py check 2>&1 | grep 'docs/AGENTS.md'` prints `current docs/AGENTS.md`: pass
- Check: 5 `check-packaging.py` exits 0 and `check.py` exits 0: pass
- Check: 6 `git diff --check` exits 0: pass
