# product-forge

**Build and evaluate product strategy, management, and UX — grounded in research and named-practitioner authority.** The product counterpart to [`brand-forge`](https://github.com/kimgranlund/plugins-forge/tree/main/brand-forge): where brand-forge builds brands grounded in cultural authority, product-forge builds products grounded in discovery, jobs-to-be-done, positioning, user research, and a comprehensive library of UX patterns and app-genre conventions — judged by an adversarial council of named product, UX, and AI-era practitioners.

> **Status: 0.3.0 — the methodology layer.** Eight skills, a 23-critic council, 11 rubrics, **11 runnable methodology playbooks** on a machine-readable method-card schema, the advisory lint hook, the `/product-*` commands, and a ~135-file reference library, all passing the harness gates (`validate_plugin.py --strict`, `reference-lint.py`, `product-lint selftest`, `check-sourcing.py`, **`check-methods.py`**, markdownlint). v0.3 adds the runnable _how_ — a **process-spine** frame (Double Diamond → seven phases) beside the v0.2 Product Experience Strategy taxonomy frame. Red-teamed with the `plugins-factory` council (records under `reviews/`). A `product-corpus` MCP remains planned. See [ROADMAP.md](ROADMAP.md).

## What it covers

- **Product strategy & management** — discovery, jobs-to-be-done, opportunity framing, the strategy kernel, positioning, prioritization, outcomes/metrics, the four big risks, roadmapping.
- **User & persona definition** — segmentation, user research methods (interviews, JTBD discovery, journey mapping), persona archetypes.
- **A comprehensive UX-pattern library** — registration, onboarding, guidance, support, progressive disclosure, search, navigation, empty/error states, notifications, and many more.
- **The spectrum of app genres** — single-purpose task apps, content consumption, games, tracking, dashboards, finance, health, travel, social, workplace, productivity — each with its conventions, signature patterns, metrics, and pitfalls.
- **AI-era product & UX** — conversational/agentic UX, generative UI, trust/control/steerability, human-in-the-loop.
- **Experience & information architecture** — journeys, flows, navigation/wayfinding, the object model, taxonomy, search/filtering, the interaction model, and state coverage (Garrett's five planes, Covert, the polar-bear systems, OOUX).
- **Service & governance** — service blueprints, human/system handoffs, support and escalation paths, cross-channel continuity; and product governance — enforceable principles, decision rights, ADRs, review rituals.
- **Content design & trust/safety** — UX writing (voice, labels, microcopy, in-product education), and privacy-by-design, consent, explainability, auditability, and risk/harm handling.
- **Authoring** — PRDs / specs and product-vision memos.
- **Runnable methodologies** — the process playbooks a team actually runs (Design Sprint, story mapping, usability testing, IA validation, service blueprinting, OOUX, the research methods, …), sequenced on the Double Diamond, each with a method card (`phase · timebox · produces · rubric`).

## Shape (brand-forge's five-primitive model)

| Primitive | product-forge instance |
| --- | --- |
| **Skills** | the methodology, research, and pattern/genre depth (single source of truth) |
| **Agents** | a named product / UX / AI-product **critic council**, fanned out parallel + isolated |
| **Commands** | thin typed entry points (`/product-*`) |
| **Hook** | advisory PRD/strategy/UX **lint** (goal-as-strategy, output-over-outcome, personas-without-research, vanity metrics, dark-pattern intent) — never blocks |
| **MCP** | _planned_ — a per-instance product-corpus retrieval (research, personas, specs); **not yet shipped** |

## Built on three rolled-in skills

- **plan-spec** — the phase-gated, dual-audience spec discipline + craft rubric (adapted to product PRDs).
- **plan-vision** — the manifesto / reframe / case-for / synthesis archetypes for product-vision memos.
- **meta-expert-author** — the wave-based, source-verified research methodology that builds and maintains the reference library.

## Provenance

Authored and red-teamed with [`plugins-factory`](https://github.com/kimgranlund/plugins-forge/tree/main/plugins-factory) against its 9-dimension architecture standard; the reference library follows `meta-expert-author`'s verification discipline (dated, coverage-tiered, source-cited; observable-public-only). The living-practitioner critics' verbatim quotes were verified against their public sources; `bin/check-sourcing.py` gates that every reference is sourced and every critic carries a sourcing block.
