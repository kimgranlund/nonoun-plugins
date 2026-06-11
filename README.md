# claude-plugins — the `plugins-forge` marketplace

[![ci](https://github.com/kimgranlund/claude-plugins/actions/workflows/ci.yml/badge.svg)](https://github.com/kimgranlund/claude-plugins/actions/workflows/ci.yml)

A public **Claude Code plugin marketplace**: self-contained, reference-quality plugins, each authored and adversarially red-teamed with the catalog's own lifecycle tool. The marketplace *name* is `plugins-forge` (install ids end in `@plugins-forge`) while the repo is `claude-plugins` — deliberate; see [docs/ISSUES.md](docs/ISSUES.md) D-1.

## Install

```text
/plugin marketplace add kimgranlund/claude-plugins
/plugin install brand-forge@plugins-forge
/plugin install plugins-factory@plugins-forge
/plugin install product-forge@plugins-forge
/plugin install agent-ops@plugins-forge
```

## Catalog

| Plugin | What it is |
| --- | --- |
| [`brand-forge/`](brand-forge/) | build and evaluate brands grounded in cultural authority — the catalog's worked example of the five plugin primitives |
| [`plugins-factory/`](plugins-factory/) | the plugin-lifecycle tool: author, carve, score, and red-team plugins against one 9-dimension standard (this repo dogfoods it on itself) |
| [`product-forge/`](product-forge/) | product strategy, management, and UX across the 12-domain Product Experience Strategy frame |
| [`agent-ops/`](agent-ops/) | author, operate, and review agentic systems and the repos they live in |

Each plugin's own `README.md` is its authoritative description; a generated catalog page (`gen-index.py`, gated fresh in CI) is browsable online at **[kimgranlund.github.io/claude-plugins](https://kimgranlund.github.io/claude-plugins/)** and lives in-repo at [`index.html`](index.html). The shared **corpus-reader** — a buildless static site for any folder-of-Markdown corpus — lives in [`plugins-factory/bin/corpus-reader/`](plugins-factory/bin/corpus-reader/) and is vendored into the plugins that use it.

## How this repo is verified

Stdlib-only gates run in CI on every push: manifest/layout validation, reference resolution, declared-state sync (version ↔ CHANGELOG ↔ counts), vendored corpus-reader drift + XSS wiring + CHANGELOG freshness, sourcing/provenance, method-card schemas, behavioral gate evals, council-calibration baselines, a JS parse gate, a demo-corpus pipeline smoke, and the workflow's own path liveness. The standing rule: **gates must be clean-checkout-true** — green on a maintainer tree must imply green on a fresh clone ([docs/ISSUES.md](docs/ISSUES.md) D-6).

## Repo docs

[docs/PLAN.md](docs/PLAN.md) (current execution plan) · [docs/ROADMAP.md](docs/ROADMAP.md) (cross-catalog horizons) · [docs/ISSUES.md](docs/ISSUES.md) (issues, decisions, postmortems) · [CLAUDE.md](CLAUDE.md) (working-in-this-repo guidance). Per-plugin roadmaps and reviews stay with each plugin.
