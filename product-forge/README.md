# product-forge

**Build and evaluate product strategy, management, and UX — grounded in research and named-practitioner authority.** The product counterpart to [`brand-forge`](https://github.com/kimgranlund/plugins-forge/tree/main/brand-forge): where brand-forge builds brands grounded in cultural authority, product-forge builds products grounded in discovery, jobs-to-be-done, positioning, user research, and a comprehensive library of UX patterns and app-genre conventions — judged by an adversarial council of named product, UX, and AI-era practitioners.

> **Status: 0.1.0 — built and red-teamed.** All six skills, the 17-critic council, five rubrics, the advisory lint hook, the `/product-*` commands, and the ~91-file reference library are in place and pass the harness gates (`validate_plugin.py --strict`, `reference-lint.py`, `product-lint selftest`, `check-sourcing.py`, markdownlint). Red-teamed with the `plugins-factory` council (record under `reviews/`). A `product-corpus` MCP is planned for v0.2. See [ROADMAP.md](ROADMAP.md).

## What it covers

- **Product strategy & management** — discovery, jobs-to-be-done, opportunity framing, the strategy kernel, positioning, prioritization, outcomes/metrics, the four big risks, roadmapping.
- **User & persona definition** — segmentation, user research methods (interviews, JTBD discovery, journey mapping), persona archetypes.
- **A comprehensive UX-pattern library** — registration, onboarding, guidance, support, progressive disclosure, search, navigation, empty/error states, notifications, and many more.
- **The spectrum of app genres** — single-purpose task apps, content consumption, games, tracking, dashboards, finance, health, travel, social, workplace, productivity — each with its conventions, signature patterns, metrics, and pitfalls.
- **AI-era product & UX** — conversational/agentic UX, generative UI, trust/control/steerability, human-in-the-loop.
- **Authoring** — PRDs / specs and product-vision memos.

## Shape (brand-forge's five-primitive model)

| Primitive | product-forge instance |
| --- | --- |
| **Skills** | the methodology, research, and pattern/genre depth (single source of truth) |
| **Agents** | a named product / UX / AI-product **critic council**, fanned out parallel + isolated |
| **Commands** | thin typed entry points (`/product-*`) |
| **Hook** | advisory PRD/strategy/UX **lint** (goal-as-strategy, output-over-outcome, personas-without-research, vanity metrics, dark-pattern intent) — never blocks |
| **MCP** | _planned for v0.2_ — a per-instance product-corpus retrieval (research, personas, specs); **not shipped in 0.1.0** |

## Built on three rolled-in skills

- **plan-spec** — the phase-gated, dual-audience spec discipline + craft rubric (adapted to product PRDs).
- **plan-vision** — the manifesto / reframe / case-for / synthesis archetypes for product-vision memos.
- **meta-expert-author** — the wave-based, source-verified research methodology that builds and maintains the reference library.

## Provenance

Authored and red-teamed with [`plugins-factory`](https://github.com/kimgranlund/plugins-forge/tree/main/plugins-factory) against its 9-dimension architecture standard; the reference library follows `meta-expert-author`'s verification discipline (dated, coverage-tiered, source-cited; observable-public-only). The living-practitioner critics' verbatim quotes were verified against their public sources; `bin/check-sourcing.py` gates that every reference is sourced and every critic carries a sourcing block.
