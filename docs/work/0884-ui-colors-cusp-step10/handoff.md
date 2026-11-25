---
id: T-0884
title: "ui-colors: step 10 of a cusp-bright solid barely changes in dark"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
In dark mode, step 10 (hover) of a solid at the gamut cusp differs visibly from step 9.

## Intent
- Do: for a solid at the cusp (`solidLabels[f].cusp`), place dark step 10 by moving away from the cusp (darker or less chroma) until the hover ΔE threshold (4) is met; add a check and a negative control.
- Non-goals: light mode; non-cusp families; the default targets of other steps.
- Done when: the criteria below hold.

## Context
- Measured with `hueSet: "radix"`, `target: "display-p3"` and dark `keyDepth: 4` (request in `docs/reports/2026-11-24-ui-colors-radix-match.md`): dark hover ΔE 9 to 10 is yellow 0.66, lime 0.93, mint 1.50, sky 2.17, cyan 2.70, grass 2.79; threshold 4. These solids sit at the cusp, so "lighter" has no room.
- Source write-up: `/Volumes/kimba/Downloads/ui-colors-updates/ui-colors-pr.md` (read-only; never write under `/Volumes/kimba`), section 4.
- Skill: `plugins/design/skills/ui-colors/` (`scripts/system.mjs`, `scripts/check.mjs`, `references/system.md`). Its `plugins/design/AGENTS.md` row records differences from the MacBook source; add this one.

## Acceptance criteria
- With the request above, every family's dark step 9 to 10 ΔE is at least 4, shown by a new `check.mjs` check.
- A negative control that restores the old placement fails that check.
- `node scripts/check.mjs` reports every check passing and every control biting; a `{}` request's output is byte-identical to `main`.
- `python3 scripts/check-packaging.py` exits 0.

## Constraints
- Default output (`{}`) unchanged.
