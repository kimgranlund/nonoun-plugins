---
id: T-0894
title: "ui-colors: pageTint with an ink anchor collapses dim onto dark"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-27
claimed_by: nonoun-author 2026-11-27
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
With `settings.pageTint` above 0 and an `ink` anchor, the `dim` mode keeps its own tone instead of taking the anchored dark page's tone, so `dim` stays distinct from `dark`, and its accents still re-base on dim's own page. User decision 2026-11-27: "Keep dim's own tone".

## Repro
1. In `plugins/design/skills/ui-colors`, write a request: `{ "anchors": [{ "role": "ground", "value": "#fff3e4" }, { "role": "ink", "value": "#2a1608" }], "settings": { "pageTint": 100 } }` (extra modes on, the default).
2. `node scripts/system.mjs --request <file> --out <dir>` and compare `system.json > modes.dim` with `modes.dark`.

## Expected
`dim` places its ramps at its own dark tone (`darkTone` 14 by default, or `modes.dim.settings.darkTone`), its page (neutral step 1) differs from `dark`'s, and every accent's step 1 equals dim's page.

## Actual
From the T-0893 solo report: "With pageTint and an ink anchor, `dim` takes the anchored dark page's tone, so it comes out the same as `dark`." `references/system.md` documents that pageTint overrides `darkTone`, "including dim's 14".

## Context
- T-0893 (landed, `design` 0.10.0) added `settings.pageTint`: `rebaseOnPage` in `scripts/system/anchors.js` and the tone override in `scripts/system.mjs`. Its report is in `.sdlc/runtime/tasks/0893-ui-colors-accents-on-ground/0893-solo-L3.md` in the main checkout.
- Find how the ink anchor sets the dark page (`deriveNeutral`) and whether `dim`'s neutral page also follows the ink today without `pageTint`. If dim's neutral already equals dark's page without the key, the fix is only to not override dim's tone; say which it is.

## Constraints
- Output without `pageTint` is unchanged, and default output for `{}` stays byte-identical.
- `light`, `dark` and the contrast modes under `pageTint` are unchanged by this fix.
- Update the `references/system.md` sentence that says the override includes dim's 14.
- Do not edit any CHANGELOG, `generate.cjs` or `runtime.json`.

## Acceptance criteria
- On the repro request, `modes.dim` neutral step 1 differs from `modes.dark` neutral step 1, and every accent's step 1 in `dim` equals dim's neutral step 1.
- `node scripts/check.mjs` exits 0 with a new check for the above and a negative control: a `dim` page equal to `dark`'s under `pageTint` fails it.
- `light` and `dark` outputs on the repro request are byte-identical before and after the fix.
- `python3 scripts/check-packaging.py` and `git diff --check` pass.

## Outcome

2026-11-27 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: def462e95e05
- Changed: see commits
- Commits: f547e65 T-0894: ui-colors: dim keeps its own tone under pageTint with an ink anchor; 7983fc9 T-0894: record lane T-0894-t0894
- Check: 1 On the repro request, dim neutral step 1 differs from dark's, and every accent's step 1 in dim eq...: pass
- Check: 2 `node scripts/check.mjs` exits 0 with a new check and a negative control: pass
- Check: 3 light and dark outputs on the repro request are byte-identical before and after: pass
- Check: 4 `python3 scripts/check-packaging.py` and `git diff --check` pass: pass
- Follow-up: note: references/system.md line 366 now says dim's page is the ink's dark... -> notes.md
