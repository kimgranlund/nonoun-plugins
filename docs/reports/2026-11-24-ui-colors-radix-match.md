# ui-colors: matching Radix, and what it exposed (2026-11-24)

Evidence for the `ui-colors` changes in this branch. A session generated HCT versions of the 31 default Radix 12-step scales (Display P3, light and dark), then pinned every accent's step 9 to Radix and laid the result out one file per family. Each finding below was measured with `scripts/system.mjs` from this skill (Node 22.23.5); the workaround the session needed is what this branch replaces.

Request used for the measurements (plus `familyAnchors` where stated):

```json
{ "extraModes": false,
  "settings": { "hueSet": "radix", "target": "display-p3", "base": 100, "falloff": 5, "rc": 1, "toneMax": 95, "darkTone": 8, "tint": 100 },
  "modes": { "dark": { "settings": { "keyDepth": 4 } } } }
```

## Fixed in this branch

### Custom roles and anchors were dropped without a word

`roles: { "pin-orange": "orange" }` with an anchor on `pin-orange` ran with exit 0, no warning and an empty `anchorReport`: `resolveRoles` keeps only `ROLE_NAMES`, and `applyAnchors` skips a role it cannot resolve. Pinning 25 families therefore took five runs of one request, each remapping the six solid roles to six families, and a merge taking each family from the run that pinned it (the unpinned families were byte-identical across the five runs, so the merge was sound).

Now: an unknown `roles` key or anchor `role` exits 2 and names `familyAnchors`. `familyAnchors: { "<family>": { value, dark?, step?, darkStep?, reach?, name? } }` pins a family by name with a role anchor's semantics and no role. One run with all 25 Radix step-9 values gives the same 744 ramp swatches as the five-run merge (0 differences) and the same solid labels, with the roles unmoved (`primary` indigo … `info` cyan).

### The bright-hue window was judged per mode, on a hue that can drift

With dark `keyDepth` 4, lime's dark step 9 solved to `#527d00` (an olive, white label) while light lime stayed `#a7e200` (dark label): darkening moved its OKLCH hue just past 125°. Widening `brightHues` to `[70, 130]` was the workaround.

Now: the window is judged once, on the light mode's generated light step 9, and holds in every mode and scheme. The same request without the widened window gives lime `#a7e200` light and `#99e300` dark, both dark-label and `brightHue: true`. The default output (`{}`) and `{ "settings": { "hueSet": "radix" } }` are byte-identical before and after.

### No per-family output

`split: true` splits by mode. The session wrote one file per family, per gamut, with `--x-light`, `--x-dark` and `--x: light-dark(var(--x-light), var(--x-dark))`, plus globals, semantic files, a manifest and docs, by script. That script is now `scripts/families.mjs` (`references/system.md › Family files`); on the pinned run, every one of 6,026 variables per folder resolves to a colour in both schemes with no missing reference.

## Documented, not changed

### `keyDepth` acts at the label choice

Dark-mode step 9 with the request above:

| keyDepth (dark) | blue 9 | red 9 | label |
|---|---|---|---|
| 0–3 | `#55a5ff` | `#ff6a6f` | dark |
| 4, 10, 20, 30 | `#0270d7` | `#d2002c` | light |

The darker target lets the light label pass, the family switches to white first and its solid is solved there, so neighbouring values give identical output. `references/system.md › Settings` now says so.

### Equal-contrast solids differ from Radix in lightness, not hue

Step 9, light, before pinning (OKLab ΔE × 100 against `@radix-ui/colors` 3.0.0, as bundled in `runtime.json`): mint 33, sky 32, orange 12 (`#c84700` against `#f76b15`), cyan, grass, teal, jade and green 11–12, blue 9.5, lime, brown, bronze, yellow and gold 7–9, tomato, red, ruby and crimson 5.6–6, amber and pink 4–4.5, violet, iris, indigo, purple and plum 0.6–2.5. Every hue stayed within 3°. Every solid sits at one APCA contrast, so naturally light Radix hues are darkened ("orange looks rusty"). `references/system.md › Plain-word requests` maps that complaint to `familyAnchors`.

## Open

- **Hover on cusp-bright solids.** Dark step 9 → 10 with Radix pinned: yellow ΔE 0.66, lime 0.93, mint 1.50, sky 2.17, cyan 2.70, grass 2.79 (threshold 4). A solid at the gamut cusp has no room to lighten; step 10 needs its own rule (move off the cusp, or darken). Not changed here: it moves every bright family's step 10.
- **Full Radix reference.** `runtime.json` carries Radix step 9, light, accents only. All 31 scales, steps 1–12, light and dark, would let the grays be pinned, the gap be reported per step (a `compare: "radix"` option) and dark step 9 be pinned where Radix's differs. Needs the bundled runtime rebuilt from its source project.
- **Warm text steps.** With default targets, light orange 11 is `#842c00` and 12 `#270600` (Radix `#cc4e00`, `#582d1d`): steps 11–12 at Lc ≈ 83 / 95 read brown on warm hues. Documented as a plain-word request; the defaults are unchanged.

## Checks

`node scripts/check.mjs` in `skills/ui-colors`: 73/74 checks pass, 134/134 negative controls bite (six new: a family anchor off its step 9, one that moved a role, an internal `family:` name in the CSS, a valid family anchor in the bad list, a family file with a missing reference, one with a moved step 9). The one failing check, `neutrals: default run byte-identical to the recorded digest`, fails the same way on the unmodified skill in this environment (`system.json` sha256 `5d65e37a3e41`, recorded `00427f06e157`); this branch's default output is byte-identical to the unmodified skill's. `python3 scripts/check-packaging.py` from the repository root: PASS.
