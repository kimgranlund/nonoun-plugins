---
id: T-0780
title: "Give the fanout skill room under its size limit"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/sdlc-lite/skills/fanout/SKILL.md` sits at least 1,500 characters under the 18,000-character packaging limit, with nothing lost: detail moves into the skill's `references/` files it already links.

## Intent
- Do: move the longest detail paragraphs (sub-agent lanes internals, settle and land detail) into the existing `references/` files (lane-lifecycle, land, main) and leave one linked line each in SKILL.md. Then add the lines T-0760, T-0766 and T-0758 could not fit: `advance` stops on a blocked solo report (T-0760); `steps.py next` prints `lane red` when an inherited red's base is off the into branch (T-0766).
- Non-goals: changing behaviour.
- Done when: the criteria pass.

## Context
T-0760, T-0766 and T-0758 (2026-10-24) each had to drop or shorten a SKILL.md line because the file was within 30 characters of the limit `scripts/check-packaging.py` enforces.

## Acceptance criteria
1. `wc -c < plugins/sdlc-lite/skills/fanout/SKILL.md` prints at most 16500.
2. Every fact removed from SKILL.md is present in a linked `references/` file (list the moves in the Outcome), and SKILL.md names the T-0760 and T-0766 behaviours.
3. `python3 scripts/check-packaging.py` passes, `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and `git diff --check <base sha>` exits 0.
