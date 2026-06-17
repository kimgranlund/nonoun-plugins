# nonoun-plugins — the `nonoun-plugins` marketplace

[![ci](https://github.com/kimgranlund/nonoun-plugins/actions/workflows/ci.yml/badge.svg)](https://github.com/kimgranlund/nonoun-plugins/actions/workflows/ci.yml)

A public **Claude Code plugin marketplace** for **brand & product work**: self-contained, reference-quality plugins, each authored and adversarially red-teamed with `plugins-factory`. Its sibling, **[nonoun-factory](https://github.com/kimgranlund/nonoun-factory)**, holds the builder/operator toolchain (plugins-factory, harness-forge, agent-ops) — split out on 2026-06-17 (D-18) so the products and the tooling each have their own marketplace + audience. Install ids end in `@nonoun-plugins` (products) or `@nonoun-factory` (toolchain).

## Install

```text
/plugin marketplace add kimgranlund/nonoun-plugins
/plugin install brand-forge@nonoun-plugins
/plugin install product-forge@nonoun-plugins

# the builder/operator toolchain is the sibling marketplace (D-18):
/plugin marketplace add kimgranlund/nonoun-factory
/plugin install plugins-factory@nonoun-factory   # + harness-forge@nonoun-factory, agent-ops@nonoun-factory
```

## Catalog

| Plugin | What it is |
| --- | --- |
| [`brand-forge/`](brand-forge/) | build and evaluate brands grounded in cultural authority — the catalog's worked example of the five plugin primitives |
| [`product-forge/`](product-forge/) | product strategy, management, and UX across the 12-domain Product Experience Strategy frame |

> **Sibling marketplace — [nonoun-factory](https://github.com/kimgranlund/nonoun-factory):** `plugins-factory` (the lifecycle tool, whose gate suite is vendored here as `tools/gates/` to validate these products), `harness-forge` (the latticed-agentic-workflow kernel), `agent-ops` (operate/review agentic systems), and the nested `dev-factory`.

Each plugin's own `README.md` is its authoritative description; a generated catalog page (`gen-index.py`, gated fresh in CI) is browsable online at **[kimgranlund.github.io/nonoun-plugins](https://kimgranlund.github.io/nonoun-plugins/)** and lives in-repo at [`index.html`](index.html). The shared **corpus-reader** — a buildless static site for any folder-of-Markdown corpus — is repo-root build tooling at [`tools/corpus-reader/`](tools/corpus-reader/) (alongside `gen-index.py`) and is vendored into the maker plugins that use it.

## How this repo is verified

Stdlib-only gates run in CI on every push: manifest/layout validation, reference resolution, declared-state sync (version ↔ CHANGELOG ↔ counts), vendored corpus-reader drift + XSS wiring + CHANGELOG freshness, sourcing/provenance, method-card schemas, behavioral gate evals, council-calibration baselines, a JS parse gate, a demo-corpus pipeline smoke, and the workflow's own path liveness. The standing rule: **gates must be clean-checkout-true** — green on a maintainer tree must imply green on a fresh clone ([docs/ISSUES.md](docs/ISSUES.md) D-6).

## Repo docs

[docs/PLAN.md](docs/PLAN.md) (current execution plan) · [docs/ROADMAP.md](docs/ROADMAP.md) (cross-catalog horizons) · [docs/ISSUES.md](docs/ISSUES.md) (issues, decisions, postmortems) · [CLAUDE.md](CLAUDE.md) (working-in-this-repo guidance). Per-plugin roadmaps and reviews stay with each plugin.
