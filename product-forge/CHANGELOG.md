# Changelog

All notable changes to **product-forge** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.1.0] — 2026-06-03

Initial release — the product counterpart to `brand-forge`: a brand-forge-style plugin for product strategy, management, and UX, with a research-grounded reference library and a named-practitioner critic council. Built via wave-based research (the `meta-expert-author` methodology).

### Added

- **6 skills** — `product-forge` (orchestrator) + `product-methodology` (strategy/PM canon + PRD `spec/` + vision archetypes), `product-research` (user research + personas), `product-patterns` (UX pattern library), `product-genres` (app-genre taxonomy), `product-evaluate` (the judge: 5 rubrics + the council).
- **18 agents** — the `product-council` orchestrator + 17 named critics across `strategy` / `discovery` / `ux` / `ai-product` sub-councils, all read-only (`Read, Grep, Glob`) and trust-bounded.
- **6 commands** — `/product-orient·strategy·research·ux·evaluate·council`.
- **5 rubrics** — product-strategy · discovery · prd-quality · ux-quality · ai-product (`[gate]`/`[review]` dimensions with cited hard tests).
- **Advisory lint hook** — `bin/product-lint` (6 PM-doc smells; `PostToolUse` on `Write|Edit`, never blocks) + `bin/check-sourcing.py` (the provenance gate).
- **~91 reference files** — dated, coverage-tiered (foundational/expanded/deep), source-cited. The plan-spec / plan-vision / meta-expert-author roll-ins are **absorbed** (self-contained, zero cross-plugin paths).

### Reviewed

- Red-teamed with the `plugins-factory` 9-critic council (CONDITIONAL → folded): reconciled the build-state docs, removed the phantom-MCP claim (deferred to v0.2), **verified the living-practitioner critics' verbatim quotes against their public sources** (corrected one Cat W. misquote + Choi's title), added the `check-sourcing.py` provenance gate, and made the README sibling links copy-alone-safe. Record under `reviews/`.

### Planned (v0.2)

- A read-only `product-corpus` MCP for per-instance retrieval of a team's PRDs / research / personas.
