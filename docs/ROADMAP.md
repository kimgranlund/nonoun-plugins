# Roadmap

The repo-level horizons, by track. This file aggregates what cuts across the catalog and **points at** the per-plugin roadmaps rather than restating them — [`plugins-factory/ROADMAP.md`](../plugins-factory/ROADMAP.md) · [`brand-forge/ROADMAP.md`](../brand-forge/ROADMAP.md) · [`product-forge/ROADMAP.md`](../product-forge/ROADMAP.md) · [`agent-ops/ROADMAP.md`](../agent-ops/ROADMAP.md). The near-term slice with acceptance criteria is [PLAN.md](PLAN.md); defects and decisions are [ISSUES.md](ISSUES.md). Snapshot: **2026-06-10**.

## Track 1 — corpus-reader (the shared product)

The buildless web-component reader vendored into brand-forge + product-forge; single source in `plugins-factory/bin/corpus-reader/`, sync-gated with an XSS guard and a CHANGELOG freshness fingerprint.

- **Now** — the browser visual pass (I-1); the committable demo corpus + CI smoke (I-2).
- **Next** — wordmark separator strip (I-4); `reader.config.json` surfaced in the export commands (I-5).
- **Later**
  - **Per-corpus theme hook.** A `theme.css` slot loaded after `corpus-reader.css` (the OKLCH tokens are the contract), pointed at by `reader.config.json` — the part of the bzzr reader's design worth adopting next; ship a neutral default + example themes.
  - **Baked single-file instance (`file://` support).** An opt-in build that inlines the sitemap + raw markdown + the component modules into one `index.html` (inline module scripts execute on `file://`; only *fetched* modules don't) — double-click distribution without abandoning D-2's architecture. Stdlib string-assembly; no pip renderer (D-5).
  - **Vendored render libs (offline mode).** Swap the pinned CDN marked/DOMPurify/highlight/mermaid for copies in `lib/` — kills the runtime CDN availability dependency for exported sites (SRI already covers integrity); needs a license/update story before default-on.
  - **Search over summaries.** The sidebar filter matches title + path today; baking each page's sitemap `summary` into `data-search` is a cheap recall win. Full-text search only with the baked instance.
  - **`--init` root redirect.** Optionally drop a tiny `index.html` redirect (`→ site/`) at the corpus root — removes the `/site/`-vs-`/` 404 papercut (how I-1's first attempt died).

## Track 2 — verification & gates

The repo's thesis is "structure is mechanized"; this track keeps the mechanization ahead of the structure.

- **Now** — D-6 (clean-checkout-true gates) is encoded and replay-verified (`ffd0c6c`).
- **Next** — JS parse gate (I-3); ci-path liveness (I-6); CI badge via the root README (PLAN #7).
- **Later**
  - **Council calibration to full coverage (I-7)** — product-forge + agent-ops planted-defect fixtures + baselines, per the existing pattern; then catch-*rates* over N runs instead of single baselines (the open half of plugins-factory's eval roadmap).
  - **Context-cost estimator** (`context-cost.py`, from plugins-factory's roadmap) — mechanize the always-on token-cost claim per plugin.
  - **Vendored-rubric drift gate** — the four skills-studio rubrics co-located into plugins-factory have no checksum sync against their originals (named in its ROADMAP since 0.1).

## Track 3 — catalog plugins (pointers, not restatements)

- **plugins-factory** — rubric calibration to N≥3 real plugins; emit `scores/<plugin>.json` adoption-contract records; `carve-quality` rubric; marketplace publish workflow; dimension MECE audit. (Its `ROADMAP.md` is the source of truth.)
- **brand-forge** — deeper council calibration (catch-rates, more fixtures, Muse calibration); stamp-output validation in CI; multi-lens Muse fan-out if aspiration diversity earns it.
- **product-forge** — the **`product-corpus` MCP**, promised since 0.1.0 and still the headline gap (brand-forge's corpus MCP is the model); more carded method playbooks.
- **agent-ops** — its v0.2 MCP slot; a council-calibration eval (shares I-7); first real-repo audit applications to validate the directional rubrics.

## Track 4 — marketplace & distribution

- **Next** — root `README.md` (the repo is public and currently README-less) with install lines + the CI badge.
- **Later** — GitHub Pages for the generated `index.html` catalog page; the marketplace `publish` workflow for carved libraries (plugins-factory roadmap); sibling marketplaces (`adia-plugins`, `maison-plugins`) stay local-only until something needs them published.
- **Standing decision** — the marketplace *name* stays `plugins-forge` (D-1); any future rename is a migration project, not a cleanup.
