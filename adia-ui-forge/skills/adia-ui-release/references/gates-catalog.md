# `gates-catalog.md` — pre-flight gate roster + failure → recovery map

> Loaded by mode 6 (Just verify) and on any gate failure in modes 1–3. This file maps every gate × what it checks × typical failure modes × recovery path. (Mode 6 absorbs what was once a separate structural-change verification-sweep skill.)

> **Worked example — the @adia-ai monorepo's gate roster.** The gate names, package paths, and failure narratives below are **the worked example** drawn from the @adia-ai lockstep monorepo. They are NOT a universal gate set — a different @adia-ai-style lockstep monorepo has its own roster. The portable discipline is: maintain a catalog of every gate the release cycle runs, grouped by **failure category** (how the operator routes when a gate fails — not by alphabetical namespace), each with command · what it checks · typical failure · recovery. Substitute your monorepo's gates into the same shape.

The @adia-ai monorepo has ~50 `check:*` / `verify:*` / `smoke:*` / `test:*` scripts. This catalogue covers every gate used during a release cycle. They're grouped by **failure category** because that's how the operator routes when a gate fails — not by alphabetical namespace.

For each gate, the row layout is:

```text
### `npm run <gate>`

- **What:** one-line description of what it checks
- **Reads:** the inputs (yaml? package.json? CSS? tests?)
- **Typical failure:** the most common cause of red, with one
  concrete example from a past cycle if there is one
- **Recovery:** the fix path (link to a case study or another section)
```

---

## §Category 1 — Release identity

These are the gates that prevent shipping an inconsistent or mis-versioned release. **Hard-fail any cut on these.**

### `npm run check:lockstep`

- **What:** all 9 `@adia-ai/*` packages declare the same `version`; all internal `@adia-ai/*` dep ranges in their `dependencies` match the policy (`^X.Y.0` during PATCH cycles, bumped at MINOR).
- **Reads:** 9 × `package.json`.
- **Typical failure:** one of the 9 forgot to bump. Or a peer manually edited an internal dep range during a PATCH cut (PATCH-cut asymmetry violation).
- **Recovery:** bump the offender (`scripts/bump.mjs`); re-run.

### `node scripts/release/check-release.mjs --all-pending` (F-N1)

- **What:** for every tag-pending in the working repo (i.e. any tag not yet pushed to origin), verify CHANGELOG coverage of the diff between this tag and the previous version's tag for the same package.
- **Reads:** git tag list, git diff between consecutive package tags, CHANGELOG `[VERSION]` block.
- **Typical failure (cosmetic):** "diff `packages/<pkg>/components/` touched but CHANGELOG `[X.Y.Z]` doesn't mention 'components'." Means the entries describe the component by name (`table-ui`) but not the literal path keyword (`components/`). Cosmetic regex miss.
- **Typical failure (real):** a touched directory has NO matching CHANGELOG entry at all — the cycle missed documenting a change.
- **Recovery for cosmetic:** add path keyword to a relevant entry (e.g. `table.yaml` → `components/table/table.yaml`). Amend release commit. Re-tag at new SHA. See `changelog-discipline.md` § F-N1 enrichment (Phase 2) + v0.6.19 case study.
- **Recovery for real:** add the missing CHANGELOG entry to the relevant package's `[VERSION]` block. Amend + re-tag.

### `npm run check:changelog-coverage`

- **What:** every published package has a `[vX.Y.Z]` CHANGELOG block for the current `package.json` version.
- **Typical failure:** package.json bumped but CHANGELOG missing the new version block.
- **Recovery:** add the block (stub if no source changes).

---

## §Category 2 — Generated-file coherence

These confirm yaml/SoT-to-sidecar generation is in sync. **Hard-fail any cut on these.**

### `node scripts/build/components.mjs --verify`

- **What:** every component yaml has a matching, up-to-date `.a2ui.json` sidecar; `.d.ts` codegen is current.
- **Reads:** `packages/web-components/components/**/*.yaml` + `packages/web-modules/shell/**/*.yaml` + their sidecars.
- **Typical failure:** peer edited a yaml but didn't run `npm run components` to regen the sidecar.
- **Recovery:** `node scripts/build/components.mjs` (without `--verify`) to regenerate; stage the regenerated sidecars.

### `npm run verify:traits`

- **What:** trait catalog (`traits/_catalog.json`) reflects every trait's `defineTrait()` call across the source tree; 100% test coverage.
- **Typical failure:** peer added a trait but didn't run `npm run build:traits`.
- **Recovery:** regenerate; stage.

### `npm run verify:a2ui-schema`

- **What:** the A2UI JSON Schema (`a2ui.schema.json`) is in sync with the TS types in `@adia-ai/a2ui-runtime`.
- **Typical failure:** peer extended the schema but the codegen output is stale.
- **Recovery:** `node scripts/build/a2ui-schema-types.mjs`; stage.

### `npm run verify:tsconfig-strictness`

- **What:** per-package `tsconfig.json` `compilerOptions` don't silently relax flags set strict in `tsconfig.base.json` (the ADR-0029 substrate invariant).
- **Typical failure:** peer added a per-package override without a `// TS-MIG-NNN` tracking comment.
- **Recovery:** either remove the override OR add the tracking comment
  - entry in `.brain/notes/ts-mig-tracking.md`. Per AGENTS.md hard rule #13.

---

## §Category 3 — Component / primitive structural drift

These verify the per-component contract holds (slots, composes-deps, demos, registry parity).

### `npm run check:demo-shells`

- **What:** every component's demo `.html` shell imports all primitives named in its yaml `composes:` field.
- **Reads:** `packages/web-components/components/<name>/<name>.html`
  - the yaml `composes:` list.
- **Typical failure:** a primitive's yaml gained a new `composes:` entry (e.g. `skeleton-ui` after `stat-ui loading` added in v0.6.18), but the demo `.html` shell didn't get the matching `<script>` import.
- **Recovery:** add `<script type="module" src="../<tag>/<tag>.js">` to the demo shell. See v0.6.18 case study (`assets/case-studies/`, Phase 3) — the f167b72bc release commit failed this gate, requiring v0.6.18 to extend to HEAD.
- **Release-blocking severity:** HIGH — a release commit that fails this gate ships broken demo pages in its tarball.

### `npm run check:composes`

- **What:** every yaml `composes:` entry resolves to a real primitive in the registry.
- **Recovery:** fix typos / register missing primitives.

### `npm run check:dts-sibling-presence`

- **What:** every component with a `.js` has a sibling `.d.ts`.
- **Typical failure:** new component added without `.d.ts` (codegen wasn't run, or hand-authored case wasn't added to the `HAND_AUTHORED_DTS` skip-set in `dts-codegen.mjs`).
- **Recovery:** regenerate or hand-author per ADR-0027.

### `npm run check:registry-catalog-coherence`

- **What:** every primitive registered in the runtime has an A2UI catalog entry, and vice versa.
- **Typical failure:** new primitive registered but catalog regen not run. Or `customElements.define` for a co-located element missing (`feedback_orphan_component_registry_catalog_parity` memory).
- **Recovery:** regenerate the catalog (`packages/a2ui/mcp/scripts/ generate.mjs ...`) OR add the missing `customElements.define`.

### `npm run check:required-icons`

- **What:** every `<icon-ui>` referenced by a component yaml or demo is in the icon registry.
- **Typical failure:** new component uses an unregistered Phosphor icon.
- **Recovery:** add to `requiredIcons` list or register.

### `npm run check:standalone-html-phosphor`

- **What:** standalone demo pages that use Phosphor icons include the icon loader.

### `npm run check:substitutable-set-drift`

- **What:** the substitutable-element registry (cross-component shape compatibility) is in sync.

---

## §Category 4 — CSS spec compatibility

These prevent LightningCSS / Vite-7-default minify failures that silently passed in Vite 6.

### `npm run check:scope-bare-descendants`

- **What:** no `@scope { > X {} }` bare-combinator descendants (LightningCSS rejects as "Invalid empty selector").
- **Typical failure:** new CSS authored with the legacy bare-combinator shape.
- **Recovery:** `node scripts/build/codemod-scope-bare-descendants.mjs` rewrites `> X` → `& > X`. See v0.6.9 case study (claims-ui FB-02 closure).

### `npm run check:lightningcss-build`

- **What:** every CSS file under `packages/web-{components,modules}/` minifies cleanly under LightningCSS + Vite 8 default targets (Chromium 125+, Safari 18+, Firefox 129+).
- **Reads:** 120+ CSS files.
- **Typical failure:** new CSS uses a feature LightningCSS doesn't support, or has a bare-combinator descendant inside `@scope` (see above).
- **Recovery:** fix the offending CSS; re-run.

### `npm run check:no-self-import-css`

- **What:** no CSS file `@import`s itself (transitively).
- **Typical failure:** a barrel CSS that includes itself.
- **Recovery:** restructure.

### `npm run check:rolldown-glob`

- **What:** `import.meta.glob` calls work under Rolldown (Vite 8).

---

## §Category 5 — Browser safety / module hygiene

These prevent Node-only imports from leaking into browser bundles.

### `npm run check:browser-safe`

- **What:** no top-level `import 'node:*'` in browser-reachable modules (`packages/a2ui/compose/`, `retrieval/` browser parts, `validator/` browser parts, `web-components/`, `web-modules/`, `apps/*/app/*.contents.js`).
- **Typical failure:** peer added a Node import to a browser-shared module. See AGENTS.md hard rule #11.
- **Recovery:** wrap in the dual-mode pattern (`IS_NODE` check + dynamic `await import(/* @vite-ignore */ 'node:*')` inside the Node-only branch + `import.meta.glob()` in the browser branch). Reference: `retrieval/component-catalog.js`.

### `npm run check:absolute-imports`

- **What:** no leading-`/` imports (the v0.6.8 claims-ui F-001 trap).
- **Typical failure:** peer used `/packages/...` instead of `../../../...`.
- **Recovery:** rewrite to relative.

### `npm run check:no-live-readers`

- **What:** no runtime DOM reads in places they shouldn't be.

### `npm run check:form-bearing-dts`

- **What:** form-element `.d.ts` files correctly declare their form participation.

### `npm run check:form-element-label-opt-out`

- **What:** form elements that opt out of label conventions are declared.

### `npm run check:template-interp`

- **What:** `core/template.js` `${expr}` interpolations match the documented contract (the v0.6.8 FB-55 lesson — `.camelCaseProp=${expr}` routes to the canonical setter; partial-class warns).

### `npm run check:yaml-events`

- **What:** yaml `events:` declarations match the actual runtime `customElement.dispatchEvent` calls.

### `npm run check:yaml-impl-coverage`

- **What:** every yaml-declared prop is implemented in the JS class.

---

## §Category 6 — Visual / structural integrity

### `npm run check:card-structure`

- **What:** every `<card-ui>` body wraps in `<section>` (the `feedback_card_drawer_body_section_wrap` memory). Strict variant of `audit:card-structure` — same probe, fails on any finding.

### `npm run audit:card-structure`

- **What:** soft variant of `check:card-structure` — same probe (`scripts/audit/audit-card-structure.mjs`) but reports findings without failing. Use when sweeping for findings to triage, not when gating a release.

### `npm run check:drawer-structure`

- **What:** same for `<drawer-ui>`. Strict variant of `audit:drawer-structure`.

### `npm run audit:drawer-structure`

- **What:** soft variant of `check:drawer-structure`. Same probe (`scripts/audit/audit-drawer-structure.mjs`), reports without failing.

### `npm run check:with-css-pairing`

- **What:** every shell with paired `.js` + `.css` has a canonical `/with-css` companion + exports-map entry (v0.6.10 closure for claims-ui FB-06).

### `verify:no-legacy-shell-shapes`

- **What:** scans `site/`, `apps/`, `playgrounds/`, `catalog/` for legacy `<main>` / `<article data-content-root>` / `<div data-content-header>` shapes under `<admin-shell>` ancestors. Added in v0.6.12 (ADR-0032).
- **Recovery:** migrate to 10-tag canonical bespoke composition.

### `npm run audit:native-primitive-leak`

- **What:** static-HTML probe across `apps/`, `playgrounds/`, `catalog/` for native HTML primitives (`<button>`, `<input>`, `<select>`, `<textarea>`, `<table>`, `<a href>`, `<img>`) where an AdiaUI `*-ui` equivalent exists. Catches "agent reached for `<button>` instead of `<button-ui>`" smells. Added in v0.6.27 (commit `9c64e7658`); window- widening fix in commit `<post-§3-commit>` (peer-discovered 80→200- char window pitfall).
- **Severity tiers:** `<button>` / `<input>` / `<select>` / `<textarea>` / `<table>` are **critical** (always wrong, no exceptions); `<a href>` / `<img>` are **info** by default (often legitimate, `--strict-links` promotes `<a>` to warning).
- **Escape hatches:** `<input type="hidden|file|radio|checkbox">` and the `data-native-ok="<reason>"` annotation form (preferred over preceding-comment form per the `adia-ui-dogfood` skill's pitfall note).
- **Recovery for criticals:** either (a) replace the native tag with the `*-ui` equivalent (NOT auto-fixable — slot/attr semantics require human eyeball), (b) annotate the escape hatch with `data-native-ok="<reason>"`, or (c) document why the probe should be retired and update the script's `PROBES` array deliberately.
- **Typical failure mode:** agent generated a composition surface reaching for native primitives. Recovery: pair-with the `adia-ui-dogfood` skill's "Native Primitive Leak Audit" section for the full triage flow.
- **Pre-cut policy:** soft-fail in F-N1 sweep (exit 1 if criticals, exit 0 if only info-level); release proceeds if all criticals are either replaced or annotated. The audit is **opt-in for the release agent** — not blocking, but its findings get folded into the release notes if non-zero.

### `npm run audit:native-primitive-leak:strict`

- **What:** same probe but fails on **any** finding (incl. info-level `<a href>` + `<img>`). Use only for full-sweep audit cycles, not pre-cut gates — info-level findings include legitimate `<a href>` navigation that doesn't need to be `<link-ui>` in most cases.

### `npm run audit:shell-composition`

- **What:** static-HTML probe across `apps/`, `playgrounds/`, `catalog/` for admin-shell compositions missing one or more of the 12 canonical parts (per the consumer/app-author plugin's "Pre-author bundle gate" 8-part enumeration plus 4 sub-part checks). Catches the FEEDBACK-41 / 2026-05-23 claims-ui regression class: shells missing `<admin-statusbar>` (sidebar footer OR content footer), missing `[data-spacer]` + `[data-actions]` in content topbar, sidebar nav not wrapped in `<section>` / `<section-ui>` / `<admin-scroll>`, etc. Added 2026-05-23 in v0.6.29 lockstep (commit `52b5e4738`).
- **Severity tiers:** outer `<admin-shell>`, `<admin-sidebar slot="leading">`, `<admin-content>`, and `<admin-scroll>` > `<admin-page>` are **critical** (shell can't render usefully without these); the `<admin-statusbar>` slots, sidebar topbar header, page-header/body pair, content topbar with toggle+breadcrumb are **warning** (shell renders but loses canonical chrome); `[data-spacer]` + `[data-actions]` are **info** by default.
- **Escape hatch:** `data-shell-opt-out="<reason>"` attribute on the `<admin-shell>` opening tag demotes ALL findings on that shell to info-level. Use sparingly — for minimal shells or custom layouts only.
- **Recovery for findings:** load the consumer/app-author plugin's admin-shell recipe ("Advanced — full markup, start here for any new product surface") and add the canonical markup for the missing part. Do NOT auto-fix — slot/attr semantics require human eyeball.
- **Typical failure mode:** consumer agent (e.g. claude-code in a consumer repo) generates an admin dashboard without loading the Advanced recipe bundle. The FEEDBACK-41 cluster surfaces 5+ canonical-shape defects in one build. Recovery: pair-with the `adia-ui-dogfood` skill's "Admin-Shell Composition Audit" section for the full triage flow.
- **Pre-cut policy:** opt-in soft-fail in F-N1 sweep (exit 1 if criticals/warnings, exit 0 if only info-level). Release proceeds if all findings are either fixed or annotated. The audit is opt-in for the release agent — not blocking, but its findings get folded into the release notes if non-zero.

### `npm run audit:shell-composition:strict`

- **What:** same probe but fails on **any** finding (incl. info-level `[data-spacer]` / `[data-actions]` checks). Use for full-sweep cycles where you want every canonical chrome part enforced.

### `npm run audit:shell-composition:all`

- **What:** same probe with info-level findings rendered in the human-readable output. Doesn't affect exit code. Use when investigating a shell's full composition profile, not just critical defects.

---

## §Category 7 — Corpus / training-pipeline freshness

These are the gates that gate-keep the gen-UI training-data side of a release.

### `npm run verify:corpus`

- **What:** every chunk in `packages/a2ui/corpus/chunks/*.json` is reachable and well-formed.
- **Typical failure (v0.6.19 case):** 22 corpus-drift findings — chunks reference primitives that have changed shape.
- **Recovery:** harvest fix (`packages/a2ui/mcp/scripts/...`). Routes to **`adia-ui-a2ui` skill** for the remediation.

### `npm run check:embeddings-fresh`

- **What:** `chunk-embeddings.json` mtime is at-or-newer-than `chunks/_index.json`.
- **Typical failure (v0.6.15 case):** corpus chunks regenerated but `chunk-embeddings.json` not — found 6.6 days stale.
- **Recovery:** `npm run build:embeddings:chunks`. Requires `OPENAI_API_KEY` env. ~6 seconds for ~230 chunks at `text-embedding-3-small`. Stage `chunk-embeddings.json`; add a note to the a2ui-corpus CHANGELOG `[vX.Y.Z]` entry.

### `npm run check:chunks-fresh`

- **What:** `chunks/_index.json` matches the on-disk chunk files (no orphaned entries, no missing entries).
- **Typical failure:** peer added or removed a chunk without regenerating the index.
- **Recovery:** `node scripts/build/index-chunks.mjs` (or equivalent — check `adia-ui-a2ui` skill).

### `npm run check:css-bundles-fresh`

- **What:** verifies the CSS bundles produced by `scripts/build/bundle-css.mjs` are up-to-date with their source component CSS. Bundles ship as consumer-facing artifacts (e.g. the `@adia-ai/web-components/css/bundled`
  - `@adia-ai/web-modules/<cluster>/<shell>/bundled` exports); stale bundles mean consumers get yesterday's CSS even on a fresh install.
- **Typical failure:** a component CSS file was edited but bundles weren't regenerated.
- **Recovery:** `node scripts/build/bundle-css.mjs` to rebuild bundles; stage and commit the updated `dist/` outputs.

### `npm run check:js-bundles-fresh`

- **What:** verifies the JS bundles produced by `scripts/build/bundle-js.mjs` (`web-components.min.js`, `everything.min.js`, the 4 per-shell `*.min.js`, AND the `icons-manifest.js` artifact) are up-to-date with their source. Bundles ship as CDN-consumer-facing artifacts; stale bundles mean jsdelivr/unpkg serve yesterday's JS.
- **Typical failure:** a primitive or shell `.js` file was edited but bundles weren't regenerated; OR phosphor-icons-core was bumped but `icons-manifest.js` wasn't refreshed.
- **Recovery:** `node scripts/build/bundle-js.mjs` to rebuild all 6 bundles + `icons-manifest.js`. Stage and commit the updated `dist/` outputs.
- **Pre-flight verification** (manual; complements the check script):

  ```bash
  # everything.js entry MUST import @adia-ai/web-components first
  grep "import '@adia-ai/web-components'" packages/web-modules/everything.js
  # → import '@adia-ai/web-components';   (must be present)

  # everything.min.js MUST register primitives (≥100 `*-ui` tag strings)
  grep -oE '"[a-z][a-z-]*-ui"' packages/web-modules/dist/everything.min.js | sort -u | wc -l
  # → ≥100 (was 17 pre-v0.6.32 = shells-only bug)

  # everything.min.js size ≥1 MB raw (was 751KB pre-v0.6.32)
  ls -la packages/web-modules/dist/everything.min.js | awk '{print $5}'
  # → ~1093311 bytes raw / ~330KB Brotli wire

  # icons-manifest.js exists, non-empty, has cdn key
  node -e "const m=require('./packages/web-components/dist/icons-manifest.js'); \
    console.log('regular:', m.default.regular.length, '| cdn:', m.default.cdn)"
  # → regular: 1512 | cdn: https://cdn.jsdelivr.net/npm/@phosphor-icons/core@X.Y.Z/assets/
  ```

- **Why this matters:** the v0.6.29-v0.6.31 release cycles shipped `everything.min.js` as a shells-only bundle (751KB, missing all primitives) AND `web-components.min.js` without a co-distributed `icons-manifest.js`. CDN consumers hit a hard `TypeError: Cannot read properties of undefined (reading 'toLowerCase')` crash on `.value` access for any primitive element. Fix shipped in v0.6.32+ (commits `c531eb82b` / `52b5e4738` and follow-ups); the manual verification commands above catch regressions. Source: FB-51 (chat-ui-framework-gap-analysis-report 2026-05-23).

### `npm run check:llms-fresh` (NOT YET SHIPPED — recommended)

> **Status**: not in `package.json` as of v0.6.31. This is the recommended next-cycle addition; for now, use the manual verification commands below in the pre-flight checklist. See FB-52 §9 for the source.

- **What:** would verify `site/llms.txt` exists, is non-empty (≥900 lines), and was last generated from the current sitemap. The `llms.txt` file is the machine-readable docs route index that AI coding agents consume for discovery. `build:site` runs `build:llms` first; this gate catches the case where `llms.mjs` errored and `build:site` proceeded silently.
- **Typical failure:** a route was added under `site/` but `npm run build:llms` wasn't re-run; OR `scripts/build/llms.mjs` has a runtime error and the generator emitted a stale/partial file.
- **Recovery:**

  ```bash
  npm run build:llms                # regenerate
  ls site/llms.txt && wc -l site/llms.txt
  # → file exists, ≥900 lines
  ```

  Stage and commit the updated `site/llms.txt`.

- **Why this matters:** AI agents (Claude Code, Cursor, Windsurf, Claude Desktop) use `llms.txt` for docs discovery against the live site at `ui-kit.exe.xyz`. A missing or stale file silently breaks that discovery path with no user-visible error.

### `npm run audit:chunk-reconcile`

- **What:** duplicate-reconciliation report for the chunk corpus. Surfaces 3 classes of duplication the harvester does NOT catch: (1) fingerprint collisions (different names, byte-identical normalized HTML), (2) near-duplicates (slot/attr-only differences), (3) structural twins (same component-tree shape, different content).
- **Typical failure:** corpus regrowth introduced accidental name forks (e.g. `auth-card` vs `auth-card-header` for the same shape).
- **Recovery:** rename one source to match the other; re-run harvest; re-run `chunk-reconcile` to confirm convergence.

### `npm run audit:corpus-stats`

- **What:** chunk corpus regrowth dashboard. Tracks `unique_names`, `instances`, `kind` distribution, and primary-tag distribution as the corpus regrows past the 500-tripwire (currently RED in `test:a2ui` 6b).
- **Modes:** default = human-readable summary table; `--json` = machine-readable; `audit:corpus-stats:record` appends a dated row to `docs/reports/corpus-stats-history.md` (cron-friendly).
- **No release gate;** purely for tracking corpus regrowth velocity.

### `npm run audit:corpus-stats:record`

- **What:** record-mode variant of `audit:corpus-stats` — appends a dated row to the corpus-stats-history ledger. Cron-friendly; designed for weekly trend tracking.

---

## §Category 8 — Tests + types

### `npm run test:unit`

- **What:** the vitest unit suite. ~1000+ tests across the monorepo.
- **Typical failure (v0.6.20 case):** a peer changed CSS deliberately (FEEDBACK-38 addendum narrowed `[slot="heading"]`) but did NOT update the regression test (`admin-shell.test.js` still asserted the old blanket shape). **Stale test, not a regression.**
- **Recovery:** if the failure is a stale-test against a deliberate, CHANGELOG-documented change, **update the test assertion**. If the failure is a real regression, fix the regression. The diff between the test's expectation and the actual is the truth: if the actual matches the CHANGELOG `[VERSION]` entry's described behavior, the test is stale.
- **Parallel-contention flake (investigated 2026-06-02, v0.7.5 cut):** a few heavy web-modules composite suites (billing-overview, onboarding-checklist, integrations-page) were observed failing under full parallelism in the 0.7.2–0.7.4 cuts — `signals: drain loop exceeded 100 iterations` (a _non-fatal_ `console.error` + `break` in `core/signals.js`, which abandons pending effects → assertion fail or timeout). **It is load-dependent, NOT a code defect:** the scheduler is untouched since 0.7.2; vitest runs `pool: forks, isolate: true` (files don't share signal state — it's within-file timing under CPU contention); and **4/4 full-parallel runs were green on a quiet machine**. Likely surfaces only under heavy concurrent load (multiple agents/vites — see the multi-vite memory). **Recovery: re-run `npx vitest run --no-file-parallelism` (sequential is the source of truth for gating); do NOT treat a one-off parallel flake as a release blocker.** If it ever reproduces _reliably_, the real fix is to make the heavy suites flush effects deterministically (await settle) or pin them to a single fork via vitest `poolMatchGlobs` — NOT to raise the drain guard blindly (it would mask a genuine effect cycle).

### `npm run typecheck`

- **What:** `tsc --noEmit`.
- **Typical failure:** peer added a TS error in `.d.ts` or `.ts`.
- **Recovery:** fix the type error.

### `npm run smoke:engines`

- **What:** gen-UI engine smoke (monolithic + zettel + free-form) + retrieval-quality probes.
- **Typical failure:** corpus drift produces composition-match failures.
- **Recovery:** corpus remediation (routes to `adia-ui-a2ui`).

### `npm run smoke:register-engine`

- **What:** 11/11 register-engine tests.

### `npm run test:a2ui`

- **What:** A2UI MCP server + integration tests.
- **Note:** expected count is 22/22 (+1 skipped) since v0.6.11; the AGENTS.md figure of "25/25" pre-dates a consolidation.

### `npm run eval:diff -- --engine zettel`

- **What:** end-to-end gen-UI eval. Floors:
  - **Zettel**: cov ≥ 5%, avg ≥ 85, MRR ≥ 0.94 (post-§87a baseline)
  - **Free-form**: cov ≥ 88%, avg ≥ 85, F1 ≥ 52 (v0.5.2 §129 baseline)
  - **Monolithic**: cov = 100%, avg ≥ 95
- **Typical failure:** corpus or schema change broke retrieval.
- **Recovery:** `adia-ui-a2ui` skill — likely a chunk re-annotation pass.

---

## §Category 9 — Misc release safety

### `npm run dogfood:status`

- **What:** aggregator over 7 dogfood audits — runs each via `--json`, classifies findings by defect-class + severity per the dogfooding-plan P0/P1/P2/P3 rubric, writes `.brain/findings/dogfood-tracker.md` as the always-regenerated ledger, prints a console summary. **Gate #17 in the pre-flight roster** (adopted v0.6.38 prep, 2026-05-26).
- **Audits aggregated:**
  - `audit:warning-strong-vs-bg` (token-drift)
  - `audit:contenteditable-placeholder` (layout-jump)
  - `audit:static-properties-vs-yaml` (yaml-drift)
  - `audit:lifecycle-leak` (lifecycle)
  - `audit:token-pair` (contrast)
  - `audit:slot-vocab-vs-css` (yaml-drift)
  - `audit:icon-color-inherit` (icon-inherit)
- **Severity mapping:** each audit's `critical` maps to P1 or P2 by defect class (lifecycle / contenteditable-placeholder / icon-color → P1 visibly wrong; warning-strong / static-properties / token-pair / slot-vocab → P2 conceptually wrong); each `advisory` → P3.
- **Gate signal:** exit-1 when `P0 + P1 > 0`; exit-0 otherwise. P2/P3 findings are advisory and don't block the cut. Read the ledger (`.brain/findings/dogfood-tracker.md`) for the punch list grouped by defect class with canonical fix templates inlined per class.
- **Typical failure:** a new substrate change introduced a P1 — a `MutationObserver` without `.disconnect()`, a `[data-empty]::before` pseudo without `position: absolute`, or an icon-color inheritance regression. Recovery: open the ledger, locate the file:line citation, apply the canonical fix template, re-run `dogfood:status`.
- **Cost:** ~5s on a warm machine (7 audits run in series + temp-file redirect to bypass Node's 8KB pipe-truncation bug).
- **Pre-cut policy:** **MUST PASS BEFORE TAG.** The gate's whole purpose is to catch regressions in defect classes the substrate has already eliminated. Any P0/P1 means "we just re-introduced a class of bug we already paid down" — recovery is canonical (templates inlined), so the floor stays low.

### `npm run check:links`

- **What:** every intra-repo markdown link resolves.
- **Typical failure:** a doc reference broke after a file move.

### `npm run verify:pack`

- **What:** `npm pack --dry-run` succeeds for every package. Catches malformed `files`/`exports` in `package.json`.

### `npm run verify:contrast`

- **What:** color contrast pairs satisfy WCAG thresholds.

### `npm run verify:palette`

- **What:** OKLCH ramp stability.

### `npm run check:extensibility`

- **What:** validates the 5-point §Teach extensibility binding across all senior skills (frontmatter trigger cluster, capability-menu Teach label, teach-protocol content + size, extensibility-rationale cross-reference, manifest binding). Ensures every skill's §Teach mode is harness-discoverable. Source: a substrate-side `check-extensibility` skills gate (lives in the @adia-ai monorepo, not in this plugin).
- **Typical failure:** a new senior skill ships without §Teach wiring; or a skill's teach-protocol falls below the size threshold; or the extensibility-rationale cross-reference rots out.
- **Recovery:** read the per-skill P-failure detail; restore the missing binding point per the skill-ecosystem conventions in `${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md`.

### `npm run check:extensibility:strict`

- **What:** same probe but fails on any P-failure across any senior skill. Used in the skills-ecosystem gate chain.

### `npm run check:pev`

- **What:** validates the 5-point §Plan-Execute-Verify binding across all senior skills (top-band `## §Plan-Execute-Verify` H2 + cold- start band mention, per-mode verify-target table, §Teach → §PEV cross-reference, cold-start mention, skill.json claims verify capability). Source: a substrate-side `check-pev` skills gate (lives in the @adia-ai monorepo, not in this plugin).
- **Typical failure:** a senior skill's §Plan-Execute-Verify section was renamed; or a new mode landed without a verify-target row; or a §Teach landing missed the cross-reference.
- **Recovery:** read the per-skill P-failure detail; restore the binding per the 5-point PEV-binding check in `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md`.

### `npm run check:pev:strict`

- **What:** same probe but fails on any P-failure. Used in the skills-ecosystem gate chain.

### `npm run audit:native-primitive-leak:all`

- **What:** same probe as `audit:native-primitive-leak` but renders info-level findings (`<a href>`, `<img>`) in the human-readable output. Doesn't affect exit code. Use for full-sweep audit cycles where you want to see every native-primitive instance, including legitimate ones.

### `npm run audit:skill-hygiene`

- **What:** measure a skill's token / structure / drift health against soft thresholds. UNLIKE `check:*` gates, this is a health report — emits metrics + flagged findings but exits 0 unless `--strict` is passed. Eight axes (see the skill-hygiene doctrine in `${CLAUDE_PLUGIN_ROOT}/references/shared/skill-conventions.md`).
- **Typical failure:** skill grew past soft thresholds (token count, reference-file count, frontmatter description length).
- **Recovery:** operator triages — sometimes the growth is real and thresholds need raising; sometimes the skill needs pruning. Not release-blocking.

### `npm run audit:skills`

- **What:** ops-repo skill-surface audit. Walks 6 detection signals to surface skill candidates (procedure-shaped sections in journals), stale skills, and redundancy. Read-only. Optionally writes a `kind: skill-audit` entry to `.brain/audit-history/YYYY-MM-DD-*.json`.
- **No release gate;** stewardship companion script that runs out of band when the operator wants to review the skill surface.

---

## §The "minimum 6" — Just-verify (mode 6) default

If the operator says "just verify" without specifying gates, run this subset (it's the fastest cycle-validating set that catches release- blocking issues):

```bash
node scripts/build/components.mjs --verify
npm run check:lockstep
npm run verify:traits
npm run test:unit
npm run typecheck
npm run check:demo-shells
```

Add `verify:corpus` + `check:embeddings-fresh` if corpus chunks were touched. Add `check:lightningcss-build` if CSS was touched. Add F-N1 (`check:release --all-pending`) if release tags exist locally.

---

## §The "full sweep" — pre-cut default for substantive cycles

For modes 1 / 2 (Cut & ship or Author from scratch with substantive package changes), run the full sweep listed in `cycle-happy-path.md` § Step 3. Total wall time on a modern Mac: ~90 seconds.

---

## §The omnibus

```bash
npm run check
```

This invokes everything (per `package.json` `"check"` script). Heavy. Use when re-baselining a stale checkout or after a major architecture change; otherwise the targeted subset is faster.

---

## §Gate-roster currency — self-audit

This file MUST stay in sync with `package.json` `scripts`. The **Phase 4** `scripts/audit-gate-roster.mjs` will enumerate every `check:*` / `verify:*` script in `package.json` and compare to this catalogue. Until then, the discipline is manual: when you encounter a gate that's not in this file, **add it** with the row layout at the top.

The §SelfAudit Axis 9 (`SKILL.md` § SelfAudit Phase 2) makes this a hygiene metric.

---

## §Category 10 — Curation backlog (Phase 4 catalog completion pass)

The 48 gates below exist in `package.json` `scripts` but the Phase 1 catalog (Categories 1-9 above) doesn't yet have proper rows for them. Added in **v1.0.1** of this skill so `audit-gate-roster.mjs` reports a clean roster. **Each entry below is a stub** — the command + 1-sentence hint. Future operators encountering one of these gates in a release cycle should: (a) promote the entry to its proper category above with full **What / Reads / Typical failure / Recovery** columns, and (b) note the cycle the promotion happened in.

### §`npm run check` structural + CSS-layer pre-flight gates

Composed into the `npm run check` pre-flight aggregate (so they gate every substantive cut). Stub rows added **v1.10.5** (2026-06-02) when `audit-gate-roster.mjs` was rescoped to the release-flow universe; promote to a full Category 1-9 row when a cycle interacts with one.

#### `npm run check:admin-page-structure`

Admin-page composite structural integrity (`<admin-statusbar>` / `[data-spacer]` / `[data-actions]` present) — the FB-41 claims-ui regression class. `--strict`.

#### `npm run check:brain-notes-frontmatter`

Required frontmatter on `.brain/notes/` + `.brain/release-notes/` files (the `{date}-`/`{version}-` prefix + `created`/`last_edited` convention).

#### `npm run check:brand-chrome`

Brand-chrome token usage across chrome surfaces (no raw colors; `--a-chrome-*`). `--strict`.

#### `npm run check:cdn-pins`

CDN `@0.X` minor-range pins cited in docs/notes are coherent with the current package minor (catches a stale `@0.6` after a `0.7` cut).

#### `npm run check:components-css-barrel`

The web-components `index.css` barrel `@import`s every primitive's CSS — add-a-component → silently-unstyled drift (the site v1.7.3 regression class).

#### `npm run check:display-default`

Components honor the display-default convention (no missing host `display`).

#### `npm run check:dogfood-audits`

Aggregator — runs the 6 component dogfood audits (`audit:warning-strong-vs-bg`, `:contenteditable-placeholder`, `:static-properties-vs-yaml`, `:lifecycle-leak`, `:token-pair`, `:slot-vocab-vs-css`). These `audit:*` scripts are adia-ui-authoring's §SelfAudit domain; the release flow runs them via this gate.

#### `npm run check:empty-raw-table`

Flags `<table-ui raw>` with an empty element body (renders nothing — `raw` means the consumer owns the body). Comment-aware. Added v0.7.5. `--strict`.

#### `npm run check:foundation-layers`

Foundation CSS cascade-layer placement (tokens/reset/foundation in the right `@layer` order). `--strict`.

#### `npm run check:gap-analysis-freshness`

The gap-analysis docs are regenerated from the current corpus (not stale).

#### `npm run mcp:smoke`

Builds `retrieval` + `mcp-server`, then runs the merged + extended MCP smoke harnesses — the A2UI MCP pipeline composes end-to-end. Tail of `npm run check`.

### §Suffix variant convention

Many gates have `:strict` / `:fix` / `:json` / `:quiet` suffix variants:

- **`:strict`** — non-zero exit on any warning (default: warns don't fail). Most `check:*` audit-script gates have a strict variant.
- **`:fix`** — apply automatic fixes (e.g. `check:lockstep:fix`).
- **`:json`** / **`:quiet`** — output-format variants of the same gate.

A variant is "documented" if it has a row in this catalog OR if its base gate is documented in Categories 1-9 above. The `audit-gate-roster.mjs` script tracks each variant as a separate entry; tighten the catalog by either adding the variant inline in its base's row OR adding a dedicated stub below.

### §Skill / agent hygiene gates

#### `npm run check:agents` / `:json` / `:quiet`

- **Command:** `node scripts/sync-agent-resources.mjs` (+ `--json` / `--quiet`)
- **Hint:** Audits + syncs agent-resource files across the `.agents/` tree.

#### `npm run check:skills` / `:strict`

- **Command:** `node scripts/skills/check-skill-frontmatter.mjs && node scripts/skills/check-skill-patterns-sot.mjs`
- **Hint:** Compound gate — runs skill-frontmatter validation + skill-patterns-vs-SoT drift check. `:strict` fails on any warn.

#### `npm run check:skill-patterns-sot`

- **Command:** `node scripts/skills/check-skill-patterns-sot.mjs`
- **Hint:** Detects drift between skill-declared §Patterns and the upstream yaml SoT. Added in v0.6.21 cycle (§392 journal entry).

### §Component / primitive structural drift gates (extensions)

#### `npm run check:core-barrel-dts`

- **Command:** `node scripts/release/check-core-barrel-dts.mjs`
- **Hint:** Verifies the `@adia-ai/web-components/core` barrel exports have matching `.d.ts` declarations.

#### `npm run check:element-imports`

- **Command:** `node scripts/audit/audit-element-imports.mjs --strict`
- **Hint:** Audits cross-element imports — catches monorepo-absolute paths and other shape drift.

#### `npm run check:extract-props-coverage` / `:strict`

- **Command:** `node scripts/release/check-extract-props-coverage.mjs` (+ `--strict`)
- **Hint:** Verifies extract-props coverage across components.

#### `npm run check:rendered-completeness` / `:strict`

- **Command:** `node scripts/release/check-rendered-completeness.mjs` (+ `--strict`)
- **Hint:** Verifies rendered output completeness across primitive surfaces.

#### `npm run check:dts-sibling-presence:strict`

- **Command:** `node scripts/release/check-dts-sibling-presence.mjs --strict`
- **Hint:** `:strict` variant of `check:dts-sibling-presence` (Category 3).

#### `npm run check:form-element-label-opt-out:strict`

- **Command:** `node scripts/release/check-form-element-label-opt-out.mjs --strict`
- **Hint:** `:strict` variant of `check:form-element-label-opt-out` (Category 5).

#### `npm run check:registry-catalog-coherence:strict`

- **Command:** `node scripts/release/check-registry-catalog-coherence.mjs --strict`
- **Hint:** `:strict` variant of `check:registry-catalog-coherence` (Category 3).

#### `npm run check:template-interp:strict`

- **Command:** `node scripts/release/check-template-interp.mjs --strict`
- **Hint:** `:strict` variant of `check:template-interp` (Category 5).

#### `npm run check:yaml-description-length`

- **Command:** `node scripts/audit/audit-yaml-description-length.mjs --strict`
- **Hint:** Yaml description-length policy enforcement.

#### `npm run check:yaml-impl-coverage:strict`

- **Command:** `node scripts/release/check-yaml-impl-coverage.mjs --strict`
- **Hint:** `:strict` variant of `check:yaml-impl-coverage` (Category 5).

#### `npm run check:yaml-legacy-claims`

- **Command:** `node scripts/audit/audit-yaml-legacy-claims.mjs --strict`
- **Hint:** Audits yaml files for retired-claim phrasings (e.g. `v0.4.0-legacy backcompat`). Added in the §404 SoT-completeness sweep.

#### `npm run check:yaml-rules-coverage`

- **Command:** `node scripts/audit/audit-yaml-rules-coverage.mjs --strict`
- **Hint:** Yaml `a2ui.rules` coverage policy.

### §Visual / structural integrity gates (extensions)

#### `npm run verify:no-legacy-shell-shapes`

- **Command:** `node scripts/verify/no-legacy-shell-shapes.mjs`
- **Hint:** Scans `site/`, `apps/`, `playgrounds/`, `catalog/` for legacy admin-shell DOM. Added in v0.6.12 (ADR-0032). Wired into omnibus `npm run check`.

#### `npm run smoke:consumers`

- **Command:** `node scripts/smoke-consumer-migrations.mjs`
- **Hint:** Smokes 6 consumer-migration paths (admin-shell, site-index, chat, gen-ui, construct-canvas, a2ui-editor). Mentioned in v0.6.12 ledger as "6/6 smoke:consumers."

### §Corpus / training-pipeline gates (extensions)

#### `npm run verify:components` (alias)

- **Command:** `node scripts/build/components.mjs --verify`
- **Hint:** npm-script alias for the canonical pre-flight `node scripts/build/components.mjs --verify` command in Category 2. Both invocations are equivalent.

#### `npm run verify:corpus:strict`

- **Command:** `node scripts/verify/corpus.mjs --strict`
- **Hint:** `:strict` variant of `verify:corpus` (Category 7).

#### `npm run check:corpus-rules-format`

- **Command:** `node scripts/audit/audit-corpus-rules-format.mjs --strict`
- **Hint:** Audits A2UI corpus rules format consistency.

#### `npm run smoke:chunks`

- **Command:** `node packages/a2ui/mcp/scripts/test-chunks.mjs`
- **Hint:** Corpus-chunk smoke (under `adia-ui-a2ui` skill's broader domain).

#### `npm run smoke:state-cache`

- **Command:** `node packages/a2ui/mcp/scripts/smoke-state-cache.mjs`
- **Hint:** A2UI state-cache smoke. Tied to multi-turn refinement state.

### §Release-identity gates (npm-script alias)

#### `npm run check:release`

- **Command:** `node scripts/release/check-release.mjs`
- **Hint:** npm-script form of F-N1 (Category 1). Equivalent to `node scripts/release/check-release.mjs --all-pending` when run during a release cycle.

#### `npm run check:lockstep:fix`

- **Command:** `node scripts/release/check-lockstep.mjs --fix`
- **Hint:** `:fix` variant of `check:lockstep` (Category 1). Auto-aligns internal `^X.Y.0` dep ranges when they drift.

### §Test + types gates (extensions)

#### `npm run verify:exports-conditionals`

- **Command:** `node scripts/verify/exports-conditionals.mjs`
- **Hint:** Verifies `package.json` `exports` map conditionals (TS / import / default) are well-formed.

#### `npm run check:free-form-eval-regression`

- **Command:** `node scripts/release/check-free-form-eval-regression.mjs`
- **Hint:** Free-form eval regression guard (paired with Category 8's `eval:diff`).

#### `npm run check:iteration-prompt-coherence` / `:strict`

- **Command:** `node scripts/release/check-iteration-prompt-coherence.mjs` (+ `--strict`)
- **Hint:** Iteration-prompt-vs-SoT coherence (gen-UI multi-turn refinement).

#### `npm run test:llm`

- **Command:** `vitest run packages/llm/`
- **Hint:** Subset of `test:unit` scoped to the `@adia-ai/llm` package.

#### `npm run test:a2ui:full`

- **Command:** `node packages/a2ui/mcp/scripts/test-a2ui.mjs --thinking --verbose`
- **Hint:** Full A2UI test suite (thinking + verbose). Slower than `test:a2ui`.

#### `npm run test:all`

- **Command:** `node packages/a2ui/mcp/scripts/test-a2ui.mjs && node packages/a2ui/mcp/scripts/test-evals.mjs`
- **Hint:** A2UI test + eval combined.

#### `npm run test:evals` / `:baseline` / `:thinking`

- **Command:** `node packages/a2ui/mcp/scripts/test-evals.mjs` (+ `--save-baseline` or `--mode=thinking`)
- **Hint:** A2UI evals; `:baseline` saves a new baseline; `:thinking` runs in thinking mode.

#### `npm run test:unit:watch`

- **Command:** `vitest`
- **Hint:** Watch-mode variant of `test:unit` (Category 8). Dev convenience.

#### `npm run test:visual` / `:pro`

- **Command:** `node packages/a2ui/mcp/scripts/visual-validate.mjs --open` (+ `--pro`)
- **Hint:** Visual-validation harness (opens a browser).

#### `npm run smoke:genui-composition-retrieval`

- **Command:** `node scripts/smoke-genui-composition-retrieval.mjs`
- **Hint:** Gen-UI composition-retrieval smoke.

#### `npm run smoke:genui-error-ux`

- **Command:** `node scripts/smoke-genui-error-ux.mjs`
- **Hint:** Gen-UI error-UX smoke.

#### `npm run smoke:issues`

- **Command:** `node packages/a2ui/mcp/scripts/smoke-issues.mjs`
- **Hint:** A2UI issue-reporter smoke.

#### `npm run smoke:iteration-synthesis`

- **Command:** `node scripts/smoke-iteration-synthesis.mjs`
- **Hint:** Iteration-synthesis (multi-turn refinement) smoke.

#### `npm run smoke:mcp-extended`

- **Command:** `node packages/a2ui/mcp/scripts/smoke-extended.mjs`
- **Hint:** Extended MCP-server smoke (beyond the standard `mcp:smoke` 3/3).

#### `npm run smoke:refine`

- **Command:** `node packages/a2ui/mcp/scripts/smoke-refine.mjs`
- **Hint:** Multi-turn refinement smoke.

---

That closes the §Category 10 curation backlog at v1.0.1. Subsequent cycles should promote entries from here to Categories 1-9 above as operators encounter them with enough detail to fill the full row shape.
