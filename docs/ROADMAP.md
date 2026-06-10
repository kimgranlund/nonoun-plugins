# Roadmap

The repo-level horizons, by track. This file aggregates what cuts across the catalog and **points at** the per-plugin roadmaps rather than restating them — [`plugins-factory/ROADMAP.md`](../plugins-factory/ROADMAP.md) · [`brand-forge/ROADMAP.md`](../brand-forge/ROADMAP.md) · [`product-forge/ROADMAP.md`](../product-forge/ROADMAP.md) · [`agent-ops/ROADMAP.md`](../agent-ops/ROADMAP.md). The near-term slice with acceptance criteria is [PLAN.md](PLAN.md); defects and decisions are [ISSUES.md](ISSUES.md). Snapshot: **2026-06-10**.

## Track 1 — corpus-reader (the shared product)

The buildless web-component reader vendored into brand-forge + product-forge; single source in `plugins-factory/bin/corpus-reader/`, sync-gated with an XSS guard and a CHANGELOG freshness fingerprint.

- **Now** — nothing open.
- **Later**
  - **Full-text search in the baked reader** — every page's markdown is inlined now; the sidebar filter can search content (the bake's natural follow-on).
  - **Vendored render libs (offline mode).** Swap the pinned CDN marked/DOMPurify/highlight/mermaid for copies in `lib/` — kills the runtime CDN availability dependency for exported sites (SRI already covers integrity); needs a license/update story before default-on (D-7). A fully-offline *bake* would inline them instead.
- **Shipped 2026-06-10** — demo corpus + CI smoke (I-2, `9cbee6f`); wordmark strip, export-command config, search-over-summaries, honest provenance counts, `--init` root redirect (`bc917fd`); the per-corpus **theme hook** + worked demo theme (`d605590`); **I-1 browser sign-off confirmed** (maintainer: "demo renders well"); the **baked single-file `file://` reader** (`--bake`, plugins-factory 0.2.23).

## Track 2 — verification & gates

The repo's thesis is "structure is mechanized"; this track keeps the mechanization ahead of the structure.

- **Now** — D-6 (clean-checkout-true gates) is encoded and replay-verified (`ffd0c6c`); the JS parse gate (I-3, `9cbee6f`), ci-path liveness (I-6, `d68d1f6`), and the CI badge (`d68d1f6`) all landed 2026-06-10.
- **Later**
  - **Council calibration — coverage complete 2026-06-10 (I-7, 4/4):** product-forge (`6d3b990`: 7/7) and agent-ops (Nightshift: a gate-clean fixture, 8/8, ST5 ×6) joined plugins-factory + brand-forge. Remaining depth: catch-*rates* over N runs instead of single baselines, and additional fixture shapes per council.
  - **Context-cost estimator** (`context-cost.py`, from plugins-factory's roadmap) — mechanize the always-on token-cost claim per plugin.
  - **Vendored-rubric drift gate** — the four skills-studio rubrics co-located into plugins-factory have no checksum sync against their originals (named in its ROADMAP since 0.1).

## Track 3 — catalog plugins (pointers, not restatements)

- **plugins-factory** — rubric calibration to N≥3 real plugins; emit `scores/<plugin>.json` adoption-contract records; `carve-quality` rubric; marketplace publish workflow; dimension MECE audit. (Its `ROADMAP.md` is the source of truth.)
- **brand-forge** — deeper council calibration (catch-rates, more fixtures, Muse calibration); stamp-output validation in CI; multi-lens Muse fan-out if aspiration diversity earns it.
- **product-forge** — the **`product-corpus` MCP**, promised since 0.1.0 and still the headline gap (brand-forge's corpus MCP is the model); more carded method playbooks.
- **agent-ops** — its v0.2 MCP slot; a council-calibration eval (shares I-7); first real-repo audit applications to validate the directional rubrics.

## Track 4 — marketplace & distribution

- **Done 2026-06-10** — root `README.md` with install lines + the CI badge (`d68d1f6`).
- **Later** — GitHub Pages for the generated `index.html` catalog page; the marketplace `publish` workflow for carved libraries (plugins-factory roadmap); sibling marketplaces (`adia-plugins`, `maison-plugins`) stay local-only until something needs them published.
- **Standing decision** — the marketplace *name* stays `plugins-forge` (D-1); any future rename is a migration project, not a cleanup.
