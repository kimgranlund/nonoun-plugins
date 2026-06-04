# Changelog

All notable changes to **product-forge** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.3.1] — 2026-06-04

Fixed two command-name collisions (the same class as brand-forge 0.4.1).

- **`/product-evaluate` → `/product-score`** and **`/product-research` → `/product-discover`.** Each command shared its slug with a same-named skill (`product-evaluate`, `product-research`); since a plugin's commands and skills occupy one `/<plugin>:<slug>` invocation namespace, the skills shadowed the commands and `/product-evaluate` / `/product-research` were unreachable ("Unknown command"). Renamed the commands to distinct verbs; the skills are unchanged and remain what the commands route to. The collision class is now gated by `validate_plugin.py`.

## [0.3.0] — 2026-06-03

The **methodology layer** — adds the runnable _how_ beside the frameworks (the _what_), the rubrics (the _score_), and the critics (the _who_). A machine-readable **method-card** schema + a process-spine frame map the common-sense methodologies a team actually runs, sequenced on the Double Diamond.

### Added

- **The method-card schema** — every methodology carries a frontmatter card (`method · phase · domains · timebox · cadence · participants · inputs · produces · de_risks · rubric`) + a fixed playbook body (when-to / when-NOT · the run · roles · failure modes · good-vs-bad · hand-off · sourcing).
- **`bin/check-methods.py`** — the gate that enforces the schema: every `references/methods/` card must be complete, `phase` ∈ the seven spine phases, `cadence` ∈ {one-off / per-decision / recurring / continuous}, `domains` ⊆ 1–12, `produces` non-empty, optional `de_risks` ⊆ Marty C.'s four risks, and `rubric` must resolve in product-evaluate. Has a `selftest`; **wired into CI** alongside `check-sourcing` and `product-lint`.
- **The process-spine frame** — `skills/product-forge/references/process-spine.md`: the Double Diamond → seven phases + the indexed method library (which method for where you are); the companion to the taxonomy frame.
- **6 new methodology playbooks** — Design Sprint, Story Mapping, Usability Testing, IA validation (card sort + tree test), Service Blueprinting, OOUX/ORCA — each cross-referencing (not restating) its concept reference, to avoid content-tier duplication.
- **5 research methods retrofitted with cards** — interviewing, JTBD discovery, survey design, research ops, behavioral-vs-attitudinal are now first-class indexed methods (**11 carded playbooks** total).

### Changed

- The `methods/` axis is wired into the owning skills' cold-start tables and the orchestrator classifier + References. The orchestrator's sub-council list corrected to the full v0.2 set (architecture / content / service / trust).

## [0.2.0] — 2026-06-03

The **Product Experience Strategy** expansion — adopts the 12-domain taxonomy as the plugin's canonical frame and fills the gaps it exposed (information architecture, service & workflow, governance), hardens content design and trust/safety, and makes the cross-plugin boundaries explicit. Built via the same wave-based research + verification discipline as 0.1.0.

### Added

- **2 skills** — `product-architecture` (experience architecture · interaction model · information architecture) and `product-operations` (service model · governance). Total skills: **8**.
- **6 critics** — `critic-jesse-g` (the five planes), `critic-abby-c` (IA / sensemaking), `critic-torrey-p` (content design), `critic-ann-c` (privacy by design), `critic-marc-s` (service design), `critic-john-c` (operating model & governance). Council: 17 → **23 critics**, with new `architecture` / `content` / `service` / `trust` sub-councils.
- **6 rubrics** — architecture · information-architecture · content-design · trust-safety · service-model · governance (`[gate]`/`[review]` + cited hard tests). Total rubrics: **11**.
- **~42 reference files** — experience-architecture, interaction-model, information-architecture, service-model, governance, content-design depth, and a `trust-safety/` pattern cluster; all dated, coverage-tiered, source-cited.
- **The taxonomy frame** — `skills/product-forge/references/experience-strategy-taxonomy.md`: the 12 domains → owning skill · rubric · critic · cross-plugin boundary; the orchestrator routes by it.

### Changed

- Cross-plugin boundaries are now explicit, both directions: **Brand & Perception → `brand-forge`**; interface-system mechanics (tokens, components, motion, layout) → the **adia-ui / `ui-*`** layer. product-forge owns the experience decision; those plugins own brand and the rendered component system.

### Reviewed

- **Verified all 6 new (living) critics' verbatim quotes against their public sources** before ship; the famous "two coffee shops" line was confirmed **NOT** Marc S.'s (it is 31 Volts, 2008) and excluded, and Covert's IA definition uses the correct "make it _more_ understandable" wording. `bin/check-sourcing.py` enforces the provenance floor across the new references and critics.

### Planned (next)

- The read-only `product-corpus` MCP (carried over) — per-instance retrieval of a team's PRDs / research / personas.

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
