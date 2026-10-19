---
id: T-0642
title: "docs/AGENTS.md 'Adding a document' misleads hand edits and ignores numbered forms"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The onboard-generated "Adding a document" steps in `docs/AGENTS.md` let a person or agent without the plugin add a document correctly: the right name form (kebab-case or the numbered form `docs/layout.md` declares), a collision-free number, and a link that does not break a managed block.

## Repro
1. Read the "## Adding a document" section `plugins/sdlc-lite/scripts/onboard.py` writes (lines 472-478 at filing).

## Expected
- Step 2 names the numbered form: a home whose `docs/layout.md` `## Kinds` form is numbered (e.g. `NNNN-slug.md`) takes the next number from `docs_check.py next <folder>`, or by hand with a create-only `git update-ref refs/sdlc/doc-ids/<home>/<NNNN> <blob> ""` after reading the highest existing number and ref.
- Step 3 says to add the link outside the `<!-- sdlc-lite:managed:start` block (D-13 accepts any link in the nearest AGENTS.md, `docs_check.py` lines 34-37), and that the onboard setup also lists it.

## Actual
- Step 2: "Name it lowercase kebab-case; reports lead with `YYYY-MM-DD-`." No numbered form.
- Step 3: "Add a link to it in its folder's `AGENTS.md`; the onboard setup refreshes the generated Contents lists." The list it points at is a sha-stamped managed block; a hand edit inside it fails the stamp.

## Context
- Template: `plugins/sdlc-lite/scripts/onboard.py` "## Adding a document".
- Reservation code: `docs_check.py` `DOC_ID_REFS` (line 87) and `next`; copy its exact ref layout and blob, do not invent one.
- Split from T-0641 (2026-10-19, user decision): T-0641's `.sdlc/by-hand.md` links to this section instead of repeating docs rules.

## Constraints
- One source: the docs rules live only in this template; no copy in `.sdlc/by-hand.md`.
- Regenerate this repo's managed blocks with `onboard.py setup --yes` (or the repo's equivalent) so `onboard.py check` stays current.

## Acceptance criteria
- `grep -q 'refs/sdlc/doc-ids/' plugins/sdlc-lite/scripts/onboard.py`
- `grep -q 'docs_check.py next' plugins/sdlc-lite/scripts/onboard.py`
- `grep -q 'managed:start' docs/AGENTS.md && grep -A12 '^## Adding a document' docs/AGENTS.md | grep -qi 'outside'`
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0
- `python3 plugins/sdlc-lite/scripts/onboard.py check 2>&1 | grep -qx 'current docs/AGENTS.md'` (amended 2026-10-19, the ticket's one replan: plain `onboard.py check` already exits 1 on main from unadopted `docs/goals/` and `docs/kpi/`)
- `python3 plugins/sdlc-lite/scripts/docs_check.py selftest` exits 0

## Outcome

2026-10-19 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full; verifier notes: note: redck.py deviations printed no process deviation lines; no criterion is marked (red). | note: the scratch probe repo /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0642-verifier-L2/repo could not be removed (rm denied by the permission system); the throwaway worktree was removed.) · verifier: verifier-L2 (opus) · base: 7c191b1d1a85
- Changed: see commits
- Commits: 9916c72 T-0642: docs/AGENTS.md 'Adding a document' misleads hand edits and ignores numbered forms; 4164cbd T-0642: amend criterion 5 (pre-existing onboard check red)
- Check: 1 `grep -q 'refs/sdlc/doc-ids/' plugins/sdlc-lite/scripts/onboard.py`: pass
- Check: 2 `grep -q 'docs_check.py next' plugins/sdlc-lite/scripts/onboard.py`: pass
- Check: 3 `grep -q 'managed:start' docs/AGENTS.md && grep -A12 '^## Adding a document' docs/AGENTS.md | gre...: pass
- Check: 4 `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0: pass
- Check: 5 `python3 plugins/sdlc-lite/scripts/onboard.py check 2>&1 | grep -qx 'current docs/AGENTS.md'`: pass
- Check: 6 `python3 plugins/sdlc-lite/scripts/docs_check.py selftest` exits 0: pass
