---
id: T-0896
title: "ui-colors: families.mjs manifest gains pairings and per-step data"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-28
claimed_by: nonoun-author 2026-11-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`families.mjs` writes the pairing rules and each step's use into `manifest.json` as data, and `USAGE.md` renders them from that same data, so the docs cannot drift from the manifest.

## Intent
- Do: add `manifest.json › steps` (one entry per step 1 to 12: step, group id, use) and `manifest.json › pairings` (the rules the USAGE "Pairing:" line states: text 11 to 12 on steps 1 to 5; a component on 3 to 5 takes border 7, then 8 on hover; hover one step up within its group, 3 to 4, 7 to 8, 9 to 10; text on a solid is the role's `-on-solid`). Render the USAGE "Pairing:" line and the hover sentence from `pairings`, and the step table from `steps` (`STEPS` stays the one source).
- Non-goals: accent-to-neutral pairs (one neutral per run today), any change to `system.mjs` output, new request keys.
- Done when: the manifest carries both arrays, USAGE.md text for the default run is unchanged or changes only where it now reads from the data, and `check.mjs` asserts both.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
- Source: the ui-colors PR brief, item 7 (`/Volumes/kimba/Downloads/ui-colors-updates/ui-colors-pr.md`, read-only; summarised here, do not open it). The brief asks for "`steps` / `stepGroups` / `pairings` in the manifest". `stepGroups` and `USAGE.md` already exist from T-0889; this ticket adds the other two.
- Code: `plugins/design/skills/ui-colors/scripts/families.mjs`, `STEPS` (line ~138), the USAGE.md template (`put('USAGE.md', ...)`, line ~141) and the `manifest` object (line ~212).
- Contract: `plugins/design/skills/ui-colors/references/system.md › Family files` (the files table row for `manifest.json` lists what it holds; add `steps` and `pairings`).
- Checks: `plugins/design/skills/ui-colors/scripts/check.mjs` already runs `families.mjs` and checks the manifest hashes and the resolver; extend that block.

## Constraints
- `system.mjs` default output stays byte-identical (`scripts/system/fixtures/default-digest.json`).
- Do not edit any CHANGELOG.
- Keep the T-0889 to T-0894 checks intact.

## Acceptance criteria
- `cd plugins/design/skills/ui-colors && node scripts/check.mjs` exits 0, with new checks that `manifest.json › steps` has 12 entries whose group ids match `stepGroups`, and that `pairings` holds the four rules above.
- Negative controls bite: dropping a `steps` entry and removing a `pairings` rule each make `check.mjs` fail.
- `USAGE.md`'s "Pairing:" line and hover sentence are generated from `pairings` (a grep of `families.mjs` shows no hard-coded copy of the rule text outside the data).
- `references/system.md` lists `steps` and `pairings` in the `manifest.json` row.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.
