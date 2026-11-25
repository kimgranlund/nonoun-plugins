---
id: T-0885
title: "ui-colors: bundle the full Radix scales and add compare radix"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`ui-colors` carries the full Radix scales, so a system can pin grays and dark values and report its distance from Radix at every step.

## Intent
- Do: bundle all 31 `@radix-ui/colors` scales, steps 1 to 12, light and dark (and alpha), with the version in provenance; add an opt-in `compare: "radix"` that writes per family and step the ΔE (OKLab ×100) and lightness, chroma and hue deltas to `system.json`, and a column in the preview.
- Non-goals: changing defaults; pinning anything by default.
- Done when: the criteria below hold.

## Context
- `runtime.json` today carries Radix 3.0.0 step 9, light, accents only. That pins step 9 but cannot pin the six grays, measure other steps or dark mode, or pin dark values that differ from light.
- The runtime data is built from a source project (see the skill's provenance file); the PR author says it "needs the runtime rebuilt from its source project". Find that source first; if it is only on the MacBook, stop and report.
- Measured step-9 gap before pinning (light, ΔE OKLab ×100): mint 33, sky 32, orange 12, cyan/grass/teal/jade/green 11 to 12, blue 9.5; hue within 3°.
- Source write-up: `/Volumes/kimba/Downloads/ui-colors-updates/ui-colors-pr.md` (read-only; never write under `/Volumes/kimba`), section 5.

## Acceptance criteria
- The bundled data has 31 scales × 12 steps × light and dark, and its provenance names the `@radix-ui/colors` version.
- `compare: "radix"` adds the per-step deltas to `system.json`; a check confirms a `familyAnchors` step-9 pin reports ΔE 0 at that step, with a negative control.
- A `{}` request's output is byte-identical to `main`; `node scripts/check.mjs` passes; packaging passes.

## Constraints
- Default output (`{}`) unchanged.
