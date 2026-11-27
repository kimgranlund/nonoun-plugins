---
id: T-0893
title: "ui-colors: opt-in re-base of accent ramps on an anchored page colour"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-27
claimed_by: nonoun-author 2026-11-27
branch: lane/T-0893-t0893
worktree: ../sdlc-lite.worktrees/T-0893-t0893
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
An opt-in request key in `ui-colors` re-bases every accent ramp on an anchored page colour (a `ground` or `ink` anchor). Step 1 becomes the page, steps 2 to 8 carry the page's tint fading to none at step 9, each moved step keeps its luminance, and accents are placed against the anchored page's tone. Default output stays byte-identical.

## Context
The user's brief, pasted 2026-11-27, quoted in full below. Treat it as the spec. Where it says "PR description", report in this ticket's solo report: this repo lands lanes locally and the conductor writes the changelog.

> In `scripts/system.mjs`, a `ground` / `ink` anchor re-bases only the neutral family (`deriveNeutral` in `scripts/system/anchors.js`). Every accent ramp keeps steps 1-8 as generated against the engine's own near-neutral page. On a tinted page, accent backgrounds and `-subtle` fills then look cold and detached from the page. `references/system.md` says "Steps 1-2 backgrounds (1 is the page)", which with a ground anchor is true for `gray` only.
>
> Reproduce: `{ "anchors": [{ "role": "ground", "value": "#fff3e4" }, { "role": "ink", "value": "#2a1608" }], "extraModes": false }`, run `node scripts/system.mjs --request min.json --out out` and read `system.json > modes.<id>.ramps`. Two gaps:
> 1. Tint. Light page is `#fff3e4`, but `cyan` 1-4 are `#f8f8f9 #e6f0f5 #d3e7f0 #c0dce8` (step 1 is OKLab dE x 100 of 2.7 from the page; dark is 6.9).
> 2. Tone. Accents are placed against `settings.toneMax` / `settings.darkTone` (97.5 and 5), not the anchored page's tone (96.39 and 9.67). In dark, accent steps 1-2 end up darker than the page. The only workaround is hand-matching those two settings in 0.5 steps.
>
> `settings.rc: 1`, `settings.tint: 100`, `settings.neutralFrom` and their combination do not change this, and `familyAnchors` cannot pin a second step.
>
> What to build: an opt-in request key (name it to fit the contract and `references/terms.json`; `accentsOnGround: true` is a placeholder). When set and a `ground` or `ink` anchor is present: step 1 of every accent family becomes the mode's page (neutral step 1); steps 2-8 shift in OKLab a/b by the page's tint (page minus the family's own step 1), weighted from 1 at step 1 to 0 at step 9, so the solid and steps 10-12 are untouched; each moved step keeps its luminance, so its APCA placement against the page holds; it runs per mode at that mode's settings, contrast modes included.
>
> Also close the tone gap: with a `ground` or `ink` anchor, either place accents against the anchored page's tone, or have the CLI warn when it differs from `toneMax` / `darkTone`. Decide which and say why. Fix this before judging the tint pass on unpinned families.
>
> Prototype (a starting point, not the final design), added to `scripts/system/anchors.js` and called at the end of `prepare()` after `deriveNeutral` as `rebaseOnPage(data, r.roles.neutral, targets);`:
>
> ```js
> export function rebaseOnPage(data, neutral, targets) {
>     const gamut = data.settings?.target ?? 'display-p3', rad = Math.PI / 180, neutrals = neutralFamiliesOf(data);
>     for (const mode of ['light', 'dark']) {
>         const scheme = data.schemes[mode], page = scheme?.[neutral]?.[0]; if (!page) continue;
>         const [Lp, Cp, Hp] = page.oklch, ap = Cp * Math.cos(Hp * rad), bp = Cp * Math.sin(Hp * rad);
>         const lc = [0, ...targets[mode]];
>         for (const [name, ramp] of Object.entries(scheme)) {
>             if (name === neutral || neutrals.has(name)) continue;
>             const [, C1, H1] = ramp[0].oklch, da = ap - C1 * Math.cos(H1 * rad), db = bp - C1 * Math.sin(H1 * rad);
>             for (let s = 7; s >= 1; s--) {
>                 const w = 1 - lc[s] / lc[8], [, C, H] = ramp[s].oklch, Y = linearY(ramp[s].oklch);
>                 const a = C * Math.cos(H * rad) + w * da, b = C * Math.sin(H * rad) + w * db, C2 = Math.hypot(a, b), H2 = C2 < 1e-4 ? H : ((Math.atan2(b, a) / rad) + 360) % 360;
>                 moveSwatch(ramp[s], [solveLightness(Y, C2, H2, gamut), C2, H2], gamut);
>             }
>             moveSwatch(ramp[0], [Lp, Cp, Hp], gamut);
>         }
>     }
>     return data;
> }
> ```
>
> Measured with it, twelve accents pinned at step 9 (`familyAnchors` + `brandExact`), the two anchors above, `toneMax: 96.5`, `darkTone: 9.5`, both contrast modes: light cyan-slot 1-4 went from `#f2f5f8 #e2eef2 #d0e4ec #bdd9e4` to `#fff3e4 #eeece1 #dbe3dc #c6d8d7`; no step's Lc on the page changed by more than 0.20, steps 9-12 unchanged, no contrast pair under its APCA threshold in any mode. On the minimal request (no pins, tones not matched) it was worse: five step 9-12 values moved in light and one step's Lc shifted by 1.8, because step 1 took the anchored page's tone and later solves read the low steps. That is why the tone gap comes first.
>
> Decisions to make and report: (1) the weight curve: the prototype fades by APCA target; a lightness-scaled weight, closer to chromatic adaptation with the page as white point, keeps more tint in steps 6-8; compare both on a cream page and pick one. (2) A strength dial (0-1): on a strongly tinted dark page (`#2a1608`) steps 2-4 of cool hues turn brown-grey before the hue shows; boolean or number, and does dark need its own value. (3) With `neutrals`: re-base on the ground, the surface, or by role. (4) Whether alpha steps, series and the tonal map need anything beyond re-solving from the moved ramps.
>
> Constraints: without the key, default output byte-identical (`scripts/system/fixtures/default-digest.json`); keep SKILL.md invariants (every variable is a generated colour or an alias, contrast reported never fixed, light and dark generated separately, vocabulary in step with `references/terms.json`); do not hand-edit the bundled engine (`generate.cjs`, `scripts/system/runtime.json`); unknown or invalid values for the new key exit 2.
>
> If any of this conflicts with how the generator is structured, stop and say so before working around it.

Conductor's starting position on the tone gap (the solo may overrule it with a stated reason): with the key set, place accents against the anchored page's tone, so the opt-in path is right without hand-matching; without the key, print a `WARNING` when an anchored page's tone differs from `toneMax` / `darkTone` by more than a small tolerance, so existing anchored output does not change silently.

## Constraints
- Default output for `{}` stays byte-identical, and output for a request without the new key changes only by the added warning line, if that path is chosen.
- `T-0892` adds `scripts/named.mjs` and edits `check.mjs` and `AGENTS.md` in the same skill; keep both sides on any merge.
- Do not edit any CHANGELOG.
- If the generator's structure conflicts with the brief, stop with status `blocked` and say where.

## Acceptance criteria
- `node scripts/check.mjs` exits 0 with a new run that sets the key and checks: accent step 1 equals the page in every mode; pinned steps 9 to 12 are unchanged; steps 2 to 7 stay within the existing placement tolerance; the contrast matrix is recomputed.
- Negative controls fail as they must: a step 1 left off the page, a moved pinned solid, and an invalid key value (exit 2).
- `references/system.md` documents the key (request keys table, Anchors and Brand colours sections, plain-word rows such as "normalize the ramps to the page" and "the tints look cold on our paper") and the "1 is the page" sentence is accurate.
- SKILL.md's natural-language mapping lists the key, and `references/terms.json` has any new term.
- The solo report gives the four decisions with before and after hex for one warm and one cool family in light and dark.
- `python3 scripts/check-packaging.py` and `git diff --check` pass.
