---
id: T-0889
title: "ui-colors: P3 that uses P3 (anchor p3 option, usage report, families --from-p3)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
claimed_by: nonoun-author 2026-11-25
branch: lane/T-0889-t0889
worktree: ../sdlc-lite.worktrees/T-0889-t0889
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A `ui-colors` system with target `display-p3` can use the P3 gamut on purpose, and says how much of it it actually uses.

## Intent
- Do: the six changes under Do, from the user's brief (pasted from a claude.ai session, 2026-11-25).
- Non-goals: changing default output; the open items (step-10 hover, T-0884; bundled Radix scales, T-0885; warm text, T-0886); publishing (the conductor pushes the branch and opens the PR after landing).
- Done when: the criteria below hold.

## Context
- Skill: `plugins/design/skills/ui-colors/` (`scripts/system.mjs`, `scripts/families.mjs`, `scripts/check.mjs`, `references/system.md`, `SKILL.md`). T-0883 added `familyAnchors`, role-name checks, the single bright-hue verdict and `families.mjs`; read `references/system.md` "Family anchors" and "Family files" first. `clampChroma(L, C, h, gamut)` is in `scripts/system/anchors.js` (imported by `system.mjs`).
- Measured by the user (Node 22): with the Radix hue set, 25 `familyAnchors` pinned to Radix's sRGB step-9 hex and target `display-p3`, P3 and sRGB outputs differed visibly (OKLab ΔE×100 > 2) in only 3 of 372 light and 10 of 372 dark swatches; largest 3.4. Pinning each anchor's P3 version instead (same OKLCH L and H; muted anchors, C / Cmax_srgb(L,H) < 0.7: C_p3 = C × Cmax_p3 / Cmax_srgb; saturated anchors: C_p3 = max(C, 0.95 × Cmax_p3)) with `keyIntensity` 300 and `keyRamp` 2 gave 108 light and 77 dark swatches outside sRGB, 93 per mode with ΔE > 2, 27 with ΔE > 5, largest 10.8 light (grass 9) and 11.8 dark (grass 10). Every text and solid pair still passed; weakest solid label grass Lc 46.3 (floor 45); hover pairs under threshold: 5 light, 4 dark. Example: red 9 went from C 0.193 to 0.271, past the sRGB maximum 0.2526 at that L and H.
- `plugins/design/AGENTS.md` `ui-colors` row lists differences from the MacBook source; extend it.
- `SKILL.md` must stay under 18,000 characters (`python3 scripts/check-packaging.py`).

## Do
1. Anchor option `p3` on `anchors` and `familyAnchors` entries, plus a top-level default: `"exact"` (default, today's behaviour), `"relative"` (scale chroma by Cmax_p3 / Cmax_srgb), `"edge"` (the hybrid above, the 0.7 threshold and 0.95 share as named constants). Applied only when target is `display-p3`; a bad value exits 2. `anchorReport` records the requested and the lifted value. Gamut maxima from `clampChroma`.
2. A P3 usage report in `system.json` and the CLI summary line, per mode: ramp swatches outside sRGB, and the largest and median OKLab ΔE between each P3 value and its sRGB mapping. With target `display-p3`, a `WARNING` when fewer than 5% of swatches leave sRGB, saying the system is effectively sRGB and pointing to the anchors' `p3` option and `keyIntensity`.
3. `families.mjs --from-p3 <system output dir>`: `colors-p3/` from a P3-tuned run, `colors/` from the sRGB run. Without it, behaviour as today, but `README.md` and `manifest.json` state how far `colors-p3/` differs from `colors/` (the item 2 counts).
4. Docs in `references/system.md`: the `p3` option under Anchors and Family anchors; the P3 usage report under Outputs; a Plain-word requests row "the P3 and sRGB colours look identical": check the usage report, anchor with `p3: "edge"`, raise `keyIntensity`, and note it needs a wide-gamut screen to see. At most one short line in `SKILL.md`, pointing to `system.md`.
5. `check.mjs`: a run with `familyAnchors`, `p3: "edge"` and target `display-p3` whose step-9 anchors lie outside sRGB, keep L and H within tolerance, and whose usage report counts match the ramps; negative controls: a report count that does not match the ramps, an `"edge"` anchor that stayed inside sRGB, a bad `p3` value (exit 2).
6. Append the measurements in Context to `docs/reports/2026-11-24-ui-colors-radix-match.md` as a section "P3 that uses P3", and extend the `ui-colors` row in `plugins/design/AGENTS.md`.

## Acceptance criteria
- `cd plugins/design/skills/ui-colors && node scripts/check.mjs` reports every check passing and every negative control biting, including the new ones; the recorded default-output digest is unchanged (`git diff <base> -- scripts/check.mjs` changes no digest line).
- A `{}` request's output (`system.css`, `system.json`, `tokens.dtcg.json`, `preview.html`) is byte-identical to the base (`cmp`).
- A request with 25 Radix `familyAnchors`, `p3: "edge"`, `target: "display-p3"` reports more than 5% of swatches outside sRGB per mode and no `WARNING`; the same request with `p3: "exact"` prints the `WARNING`.
- `{"anchors":[...], "p3":"bogus"}` (or an entry with `p3: "bogus"`) exits 2.
- `families.mjs --from-p3 <dir>` writes `colors-p3/` from that dir; without it, `manifest.json` carries the usage counts.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check <base>` is clean.

## Constraints
- Default output (`{}`) unchanged; the recorded digest unchanged.
- Do not edit any CHANGELOG (the conductor records it at landing).

## Outcome

2026-11-25 · lane: solo L3 · verdict: closed by reason (delivered by the solo agent (level L3); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: d0cb82574a67
- Changed: see commits
- Commits: 2d74816 T-0889: solo lane skips; 713c041 T-0889: record lane T-0889-t0889
- Check: 1 check.mjs reports every check passing and every control biting, digest unchanged: pass
- Check: 2 `{}` output byte-identical to base: pass
- Check: 3 25 Radix familyAnchors, p3 edge vs exact, target display-p3: pass
- Check: 4 bad p3 exits 2: pass
- Check: 5 families.mjs --from-p3 writes colors-p3/ from that dir; without it manifest carries usage counts: pass
- Check: 6 check-packaging exits 0 and `git diff --check <base>` is clean: pass
- Follow-up: note: docs/reports/2026-11-24-ui-colors-radix-match.md records an open... -> notes.md
