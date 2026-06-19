# Roadmap

The repo-level horizons for the **product** marketplace (brand-forge, product-forge) + the shared tooling. This file points at the per-plugin roadmaps rather than restating them — [`brand-forge/ROADMAP.md`](../brand-forge/ROADMAP.md) · [`product-forge/ROADMAP.md`](../product-forge/ROADMAP.md). The near-term slice with acceptance criteria is [PLAN.md](PLAN.md); defects + decisions are [ISSUES.md](ISSUES.md).

> **The builder/operator toolchain split to the sibling [nonoun-factory](https://github.com/kimgranlund/nonoun-factory) marketplace (D-18, 2026-06-17).** Its horizons — plugins-factory, harness-forge, agent-ops, dev-factory, plus the verification-gate and integration-contract tracks — now live in that repo's ROADMAP. plugins-factory's gate suite is vendored here as `tools/gates/` (drift-gated, Track 2). Snapshot: **2026-06-19**.

## Track 1 — corpus-reader (the shared product)

The buildless web-component reader vendored into brand-forge + product-forge; single source in `tools/corpus-reader/` (repo-root build tooling, D-14), sync-gated (`tools/sync-corpus-reader.py`) with an XSS guard + a CHANGELOG freshness fingerprint; `tools/gates/check-bake-safety.py` (vendored from nonoun-factory) retains the bake-safety security gate.

- **Now** — nothing open.
- **Later** — **Vendored render libs (offline mode).** Swap the pinned CDN marked/DOMPurify/highlight/mermaid for copies in `lib/` — kills the runtime CDN availability dependency for exported sites (SRI already covers integrity); needs a license/update story before default-on (D-7). A fully-offline *bake* would inline them.
- **Shipped 2026-06-10** — demo corpus + CI smoke; wordmark strip, export-command config, search-over-summaries, honest provenance counts, `--init` root redirect; the per-corpus theme hook + worked demo theme; I-1 browser sign-off; the baked single-file `file://` reader + full-text search in it.
- **Shipped 2026-06-17** — the Mermaid font-ready render gate + enriched/field-scoped search (frontmatter folded into the index, `field:value` tokens, a frontmatter preview line) + nested folder nav (build-sitemap emits a per-section `tree`; `cr-ui-nav` renders folder groups recursively with 00-README-promoted labels). Render + filter verified headlessly against the real module.

## Track 2 — verification (the vendored gate suite)

The products are validated by **plugins-factory's gate suite, vendored into `tools/gates/`** (D-18) and kept byte-identical to nonoun-factory by `tools/sync-gates.py --check` (the cross-repo drift gate in CI). The gates' own roadmap — new dimensions, calibration depth — lives in nonoun-factory; here the open work is keeping the vendor honest and the products green.

- **Now** — nothing open; D-6 (clean-checkout-true gates) encoded + replay-verified; the cross-repo drift gate runs in CI on every push.
- **Council calibration** — brand-forge + product-forge fixtures at **N=3, 100% per-defect catch-rate** (brand: strategy/Northwind 6/6 · design/Lumina 5/5 · voice/Verve 5/5 · Muse/Halcyon 6/6; product: all eight sub-councils). The recall corpora re-homed to `tools/gates/recall-corpus/`, CI-gated by `check-recall.py`; the judge records to `tools/gates/scores/`, validated by `score-record.py`.

## Track 3 — product plugins (pointers, not restatements)

- **brand-forge** — calibration complete across all three sub-councils at N=3 (strategy/Northwind 6/6 · design/Lumina 5/5 · voice/Verve 5/5) plus the `Muse` seat (Halcyon 6/6). Remaining: stamp-output validation in CI; a multi-lens Muse fan-out if aspiration diversity earns it. (Its `ROADMAP.md` is the source of truth.)
- **product-forge** — the `product-corpus` MCP shipped 2026-06-11 (0.3.16); all eight sub-councils calibrated. Remaining: more carded method playbooks. (Its `ROADMAP.md` is the source of truth.)

## Track 4 — marketplace & distribution

- **Done 2026-06-10/11** — root `README.md` + CI badge; the **GitHub Pages catalog** (`.github/workflows/pages.yml`) publishing the generated `index.html` to [kimgranlund.github.io/nonoun-plugins](https://kimgranlund.github.io/nonoun-plugins/) on every push to main (a single self-contained file, no relative deps).
- **Done 2026-06-13/16** — marketplace *name* `plugins-forge` → **`nonoun-plugins`** (D-12), then repo + folder aligned to the name (D-17); install ids are `<plugin>@nonoun-plugins`; `gen-index.py` reads the `name` field dynamically.
- **Done 2026-06-14** — install **project-local by default** (D-16); the plugin + its wiring travel with the repo.
- **Done 2026-06-17 (D-18)** — split the builder toolchain to the sibling **nonoun-factory** marketplace; nonoun-plugins is now the product marketplace, with plugins-factory's gates vendored into `tools/gates/` and cross-repo drift-gated.
