---
id: T-0884
title: "ui-colors: step 10 of a cusp-bright solid barely changes in dark"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
claimed_by: nonoun-author 2026-11-25
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

## Replan
2026-11-25, after the solo's block (`.sdlc/runtime/tasks/0884-ui-colors-cusp-step10/0884-solo-L2.md`): the six figures in Context came from a `familyAnchors` run and do not reproduce at base, and a default rule would change `{}` output (dark and dim yellow and lime hover ΔE 2.96 to 3.84). User decision 2026-11-25: an opt-in request key.

- Do: add a request key (name it, e.g. `hoverMin`, a ΔE in OKLab ×100) that, when set, places step 10 of any solid, anchored or cusp, so that step 9 to 10 ΔE is at least that value in every mode, by moving away from the solid (darker or less chroma, keeping its hue). Unset, output is unchanged. Document it in `references/system.md` next to the hover rule, and the opt-in in the Plain-word requests ("hover barely changes").
- Acceptance criteria, replacing the ones above:
  - With `{"settings":{"hueSet":"radix"},"hoverMin":4}` every family's step 9 to 10 ΔE is at least 4 in every mode, shown by a new `check.mjs` check; the same with the report's 25 `familyAnchors` too.
  - A negative control that drops the key's effect fails that check; an invalid value (negative, or not a number) exits 2.
  - A `{}` request's output is byte-identical to the base and the recorded digest is unchanged; `node scripts/check.mjs` passes every check with every control biting; `python3 scripts/check-packaging.py` exits 0.
- Constraints: do not edit `plugins/design/AGENTS.md` or any CHANGELOG (T-0889 runs on the same files; the conductor records both at landing).

## Outcome

2026-11-25 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: a771d36f4f78
- Changed: see commits
- Commits: 9f52714 T-0884: ui-colors hoverMin, an opt-in least step 9 to 10 dE for every solid; ff99575 T-0884: record lane T-0884-t0884
- Check: 1 With `{"settings":{"hueSet":"radix"},"hoverMin":4}` every family's step 9 to 10 ΔE is at least 4 ...: pass
- Check: 2 A negative control that drops the key's effect fails that check; an invalid value (negative, or n...: pass
- Check: 3 A `{}` request's output is byte-identical to the base and the recorded digest is unchanged; `node...: pass
- Follow-up: note: references/system.md still says "Then 74 negative controls" in the... -> notes.md
