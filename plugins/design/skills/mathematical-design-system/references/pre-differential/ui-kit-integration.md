# UI-KIT integration · 2026-10-18

This records the completed slot-model sync and how to maintain it. It is not a second numerical authority or a promise that later edits propagate automatically.

## Ownership and discovery

- This skill owns adopted formulas in `scripts/lib/scale.mjs` and `curvature.mjs`.
- The installed Base UI skill owns its standalone vanilla CSS, portable resolver snapshots, and component contracts. Its generator refreshes those snapshots explicitly.
- The separate UI-KIT repository owns `packages/geometry`, `packages/ui`, and `packages/behavior`. Read its AGENTS.md and run its discovery CLI before editing. Recipe `manifest.json` identifies authored inputs; edit `contractSource` when declared, otherwise `contract`. Panda recipe styles and distributed compiler/behavior files are generated outputs.
- UI-KIT consumers import package exports. Never introduce a skill-directory, personal-home or sibling-repository runtime import. The visualizer is a separate consumer and is not automatically rebuilt or published by a UI-KIT change.

The 2026-10-18 sync adopted current slot geometry into UI-KIT; future syncs still require explicit source changes, projection and verification. UI-KIT had already adopted the current density/button model before this media sync. Its compact recipes need their own current contract; the installed Base UI kit still labels some compact recipes as legacy compatibility. Do not transfer that status between implementations.

## Shared API and slots

`resolveControlSurface` exposes S=3n, m=(q−2)n/4, H=S+2m, W=n×Control percentage/100, L=n/2, wrapperGap=0 and collection spacing E=m/2; fixed icon/glyph square wrappers; icon2n and glyph n+6. Media fields are `mediaSize`, `mediaSlotWidth` (3n), `mediaPadding`, `mediaInset` (0), and `mediaContentSeparation` (L).

`resolveButtonPadding` now returns L=n/2 on both label sides for every arrangement, with zero compensation. Actual occupied siblings affect total edge-to-text distance only. Omit empty slots; a reserved selection column is an explicit listbox alignment choice.

In UI-KIT, `customSelect` from `@ui-kit/ui/select` accepts `leading`/`trailing` descriptors or arrays: icon/glyph `{type,name}`, avatar `{type:'avatar',initials}` or `{type:'avatar',src}`, logo `{type:'logo',src}`. Legacy `icon` and `avatar` fields remain supported. Trigger caret and option selection indicator remain separate glyph slots. Committing selection preserves typed content while updating the label; descriptions remain separate. Native Select remains the default, and the custom Select is opt-in. Do not nest interactive actions inside its trigger/options.

Monochrome icon/glyph artwork inherits the host's paired state foreground. Full media preserves its own colors: avatar cover/circular mask, logo contain/intrinsic shape. Transparent pixels inside an asset are not wrapper spacing.

## Optional media shape

`resolveMediaRadius` is exported by `@ui-kit/geometry/curvature.mjs`; the installed Base UI convenience module also reexports it. Supply `shape`, measured `frame`, `amount`, `retained`, and the immediate row/button's **required** `parentRadius` for Control inheritance. Default shapes remain asset-owned.

Control media candidate=A×height/2, floor=F×parentRadius, R=max(candidate,floor); Sharp A=0 forces0. Validate against min(width,height)/2, report conflicts without clamping, and retain the fixed media size. CSS clipping alone does not validate the geometry. `data-media-shape=control` plus `--media-required-radius` applies a resolved result. UI-KIT has a CSS candidate fallback for ordinary unretained media. Select automatically measures its opted-in trigger and popup-row media, including retained floors and local parent radius overrides. Each uses its immediate owner’s radius and Control settings. Hidden popup frames are skipped; opening/reopening, inserted rows and resized frames trigger recomputation. Other consumers still need their measured result. Clear per-element resolved styles when changing scope or opting out. Select now clears `--media-required-radius` and `data-geometry-conflict` when copying an option’s media into its trigger; it preserves the authored shape. The Select binding now resolves retained media automatically against the new trigger parent after selection, native reset and context changes, while popup media remains scoped to its option row. It restores its measurements on opt-out/destroy/abort and emits a scoped `geometryvalidation` event (`source: select-media`).

## Verification evidence and limits

The completed sync passed numerical/markup tests, projection and CSS checks, browser geometry across180 contexts and rich Select media slots across five densities in LTR/RTL,123 Select/Combobox cases, package boundary/offline installation checks, and88 Vite dev/production smoke cases. These are recorded run results, not permanent release approval or a full visual/accessibility review. The local Proportion visualizer's recent changes have numerical/DOM startup evidence; its responsive browser review remains incomplete.

Two verification repairs accompanied the sync: the global pointer-focus guard uses zero specificity so component inward outline offsets win; keyboard-focus assertions establish keyboard modality. Listbox state fixtures are on `playground/states.html`, not the old reference page. Neither repair changes the slot formulas.

For future changes, run the consuming repository's affected checks. In UI-KIT these include `node --test scripts/test/geometry-model.test.mjs`, `npm run checks -- geometry-current`, `npm run checks -- select-combobox`, `check:projection`, `check:css`, `check:boundary`, and `test:smoke` as appropriate. Build-owned contracts and snapshots must be regenerated. Old passing evidence does not cover new source edits.

## Follow-up audit · 2026-10-18

A rendered audit verified 513 visualizer controls across small/default/large contexts and Sharp/Balanced/Round, including square wrappers, zero-padding media and the then-current exposed-label edge padding (now retired). Narrow/wide checks covered media retention, physical conflicts, opt-out and independent guide toggles. No specimen geometry change was needed. The retained regression is `assets/proportion-lab/tests/rendered-geometry.mjs`; pass an installed Playwright module and optionally a served visualizer URL. This is targeted Chromium evidence, not a full responsive/accessibility review.

The audit found stale option-scoped media measurements being cloned into the UI-KIT Select trigger. Its binding now discards these measurements on transfer; the Select browser check covers that regression. The shipped geometry check also covered the then-current leading and trailing media compensation (now retired) across all 180 contexts (six arrangements each).

The automatic Select trigger-media follow-up passed 30 density/amount/retention browser cases covering initial enhancement, selection, native reset, density changes, required-parent overrides, Sharp, opt-out and destroy/abort, plus the 123-case Select/Combobox suite. The initial site smoke run stopped on a missing generated `foundations/color-mapping.html` destination. A follow-up verified the generated page, updated stale navigation-count and Manifest-tab expectations, rebuilt production output, and passed all 92 development/production page-width cases. Color mapping is now included through the declared foundation page inventory.

Popup media follow-up: the maintained geometry check covers five densities, independent row overrides, hidden/open/reopened popup states, inserted/removed rows and cleanup. Select validation includes per-media owner and scope metadata.

### Wrapper paint ownership (2026-10-19)

Across the retained visualizer, installed Base UI and UI-KIT, slot wrappers own resolved curvature and clipping. Parent rules must not impose radius, overflow or clip-path on icon/glyph artwork or media img/SVG children. Authored artwork paint survives default shape, Control inheritance and opt-out; sizing and fit rules remain separate. Avatar circles are wrapper defaults. Physical conflicts retain fixed dimensions and separate dashed diagnostics. Targeted browser checks cover artwork-style preservation; this update does not claim a full-site smoke review.

The 2026-10-19 follow-up also synchronized icon/glyph/indicator wrapper candidate/floor inheritance into installed Base UI, including Sharp and fractional amounts. All mathematical round wrappers explicitly set `corner-shape: round` to resist global superellipse styling; authored artwork corner shapes remain untouched. UI-KIT bindings restore owned slot state on opt-out/removal/destroy and recompute against each new parent. Installed Base UI has no equivalent automatic binding and documents the consumer’s cleanup responsibility.

The user’s still-squircle screenshot was traced to stale preview assets in the actual open browser (wrapper overflow visible, SVG radius50% plus superellipse1.5). Updating the CSS/module graph revision and reloading changed the live wrapper to hidden overflow and round12px, with SVG radius0. The preview now has a deterministic `scripts/refresh-assets.mjs` command and `--check`; fresh isolated test pages alone do not verify a long-lived tab.

Menu command rows use resolveControlSurface directly: fixed inner slots S = 3n; row clearance m = (q − 2)n/4 on all edges; outer row height H = S + 2m. At n=8, Tight/Compact/Regular/Spacious/Loose rows are 24/28/32/36/40px while slots remain24px. Label padding L=n/2 and icon/glyph budget W are internal anatomy; internal slot gaps are zero. Collection row spacing remains E=m/2. No extra compensation applies to any Control label. Menu-frame outer padding is separate; a three-item frame is 2m + 3H + 2E. Menu row radius uses H/2; ordinary selection-listbox rows retain S height and S/2 radius reference. Do not apply this menu change to selection rows.

Tables and data-lists use resolveDataRowGeometry(n,density,controlPercent): inner slot minimum S=3n, block clearance m=(q−2)n/4, row minimum H=S+2m, cell inline padding P=m+W (W=n×Control percentage), and column gap E=m/2. At md/md Regular: S24px, H32px, m4px, P6px, E2px. Vertically center slots; allow both slots and rows to grow with multiline content. Native collapsed tables reserve E/2 on each facing cell edge, excluding the two outer edges; data-lists use grid gap E. Content separation across cells is 2P+E. Paint one row divider through an explicit color token, without adding layout thickness or duplicate cell borders/shadows. This replaces the previous 1.25d cell padding / d/4 clearance / 2n+2.5d row convention for current data rows; legacy formulas remain historical only.

For UI-KIT example parity, follow the [five-density comparison requirements](consumer-integration.md#five-density-data-row-comparisons): matching Table and Data-list specimens, measured multiline growth, explicit padding/gap guides, and accessible scrolling. Keep the example implementation and fixtures in the consuming repository; do not reference installed skill paths at runtime.

UI-KIT shape comparison exhibits follow the [Sharp/Pill and specimen-card contract](consumer-integration.md#sharppill-comparisons-and-specimen-cards): measured equal-width pairs and per-arrangement leading/trailing label padding across densities, local shape overrides and independent Container card geometry. Consuming projects own their implementation and generated bundles.

Not yet propagated (2026-10-21): product coefficients [8, 1, 2, 0]; label padding/zero-gap sync is a separate change. Do not infer coefficient adoption from a label-padding sync: verify UI-KIT and `@ui-kit-neue/geometry` independently; consumers that pin them (for example `ultimate-tokens-color-science` geometry pins) must capture a new pin after that update.


### UI-KIT-neue audit boundary (2026-10-21)

The visualizer, standalone Base UI and UI-KIT-neue now share the label rule: n/2 on both inline sides, zero decorative slot gaps (including adjacent non-label wrappers), and no extra compensation. UI-KIT-neue's independently interactive action clearance and collection spacing retain their own contracts. The five-density LTR/RTL audit covered Button/Select/Input, menu/listbox rows, optional listbox icons and equal-width Sharp/Pill pairs. Do not restore the retired half/full exposed-edge policy in any consumer.