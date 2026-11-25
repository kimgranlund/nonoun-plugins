---
id: T-0886
title: "ui-colors: warm text steps 11 and 12 read brown at the default targets"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Decide and apply how `ui-colors` handles warm text steps 11 and 12 reading brown at the default targets.

## Intent
- Do: either lower the default step 11/12 targets to about Lc 75 / 90 (still APCA body text), or keep the defaults and make the existing Plain-word request ("text looks brown") give exact values. The choice changes default output, so ask the user before choosing the first.
- Non-goals: other steps.
- Done when: the criteria below hold.

## Context
- Default targets put steps 11 and 12 at about Lc 83 / 95 against the page; warm hues read brown (light orange 11 `#842c00`, 12 `#270600`; Radix `#cc4e00`, `#582d1d`).
- T-0883 documented it as a Plain-word request in `plugins/design/skills/ui-colors/references/system.md`; defaults unchanged.
- Source write-up: `/Volumes/kimba/Downloads/ui-colors-updates/ui-colors-pr.md` (read-only; never write under `/Volumes/kimba`), "Note on text steps".

## Acceptance criteria
- The user's choice is recorded in this ticket's Outcome.
- If defaults change: the default-output digest in `check.mjs` is updated with the reason, and a check shows light orange 11 and 12 at the new targets. If not: `references/system.md` names the request values that give the lighter text.
- `node scripts/check.mjs` passes; packaging passes.

## Constraints
- No default change without the user's word.
