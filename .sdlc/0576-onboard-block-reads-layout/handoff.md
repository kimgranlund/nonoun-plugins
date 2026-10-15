---
id: T-0576
title: "Root AGENTS.md managed block names flat-layout paths after layout: topics"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The root `AGENTS.md` managed block that `onboard.py setup` writes names the paths of the repo's actual `.sdlc` layout: with `layout: topics`, notes at `.sdlc/notes/notes.md` and the tidy archive at `.sdlc/work/archive/`.

## Repro
1. A repo with `layout: topics` in `.sdlc/config` (agent-ui, 2026-10-15, after `migrate-layout`).
2. Run `python3 <plugin>/scripts/onboard.py setup`.

## Expected
The block's notes and tidy lines name `.sdlc/notes/notes.md` and `.sdlc/work/archive/`.

## Actual
The root block (onboard template 1, `ROOT_AGENTS_TEMPLATE`) still says "notes go to `.sdlc/notes.md`" and "`tickets.py tidy` moves it into `.sdlc/archive/`". The block can't be hand-edited, so the repo is stuck with wrong text.

## Context
`tickets.py` already resolves layout-dependent paths for its own router (notes `<R>/notes/notes.md` with topics). Reuse that resolution in `onboard.py` instead of fixed strings. Reported by the agent-ui conductor.

## Constraints
Flat-layout output stays byte-identical.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0. Its new case shows a fixture with `layout: topics`: the root block names `.sdlc/notes/notes.md` and `.sdlc/work/archive/` and not `.sdlc/notes.md`. The case failed before the change.
2. The existing flat-layout block cases pass unchanged.
3. `git diff --check` exits 0.
