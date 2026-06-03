# product-forge — ROADMAP

The build plan and live state. This is the spec the waves execute against.

## Scope (signed off)

A **brand-forge-style plugin for product strategy, management, and UX** — the five-primitive shape (skills + named critic council + commands + advisory lint hook + product-corpus MCP) — with a **comprehensive, research-grounded reference library** (the "full library", not foundational-first). Three of the user's global skills roll in: **plan-spec** (spec discipline + craft rubric), **plan-vision** (vision archetypes), **meta-expert-author** (the wave-research + verification engine that builds the library).

## Skill roster (refined by the scoping survey)

| Skill | Job |
| --- | --- |
| `product-forge` | orchestrator — classify the task (strategy / spec / vision / research / persona / UX-pattern / genre / evaluate) → route |
| `product-methodology` | the maker — discovery, JTBD, opportunity framing, strategy kernel, positioning, prioritization, outcomes/metrics, the four risks, roadmapping; absorbs **plan-vision** archetypes |
| `product-spec` | PRD / requirements authoring — the adapted **plan-spec** (phase-gated, dual-audience, craft + gate rubrics) _(add if the scoping confirms it earns its own skill)_ |
| `product-research` | user & persona definition + research methods (segmentation, interviews, JTBD discovery, journey mapping) |
| `product-patterns` | the UX-pattern library (registration, onboarding, guidance, support, progressive disclosure, …) |
| `product-genres` | the app-genre taxonomy (task · content · games · tracking · dashboards · finance · health · travel · social · workplace · productivity) _(split from patterns given full-library depth)_ |
| `product-evaluate` | the judge — adversarial scoring against the rubrics + the council |

"More skills if it makes sense" — final split set by the scoping survey's file-plan.

## The council (≈17 named critics — parallel, isolated; each a distinct cited lens)

- **Strategy:** Marty C. (product operating model / the four big risks) · Richard R. (strategy kernel: diagnosis → policy → action) · Clayton C. (JTBD) · Melissa P. (outcomes vs the build trap) · April D. (positioning).
- **Discovery / research:** Torres (continuous discovery, opportunity-solution trees) · Cooper (goal-directed personas).
- **UX:** Norman (affordances, design principles) · Krug (usability, "don't make me think") · Nielsen (heuristics) · Kathy S. (make users awesome).
- **Prioritization / metrics:** Shreyas D. (product sense, prioritization) · Ron K. (trustworthy online experimentation).
- **AI-era product:** Catherine Wu (Anthropic — Claude Code product; capability-led, prototype-first, eval-driven) · Meaghan C. (Anthropic — **Head of Design**; design craft, design-to-code fidelity, dev-tool UX) · Kevin W. (OpenAI — model-maximalism, iterative deployment) · Garry T. (Y Combinator — founder/market product sense, "make something people want", talk to users). Sourcing is observable-public-only with anti-fabrication guardrails (Cat W. has a named-authored Anthropic blog; Choi is talk/demo-sourced as a design lens; Weil via interviews; Tan via YC canon).

Sub-councils: `strategy` · `discovery` · `ux` · `ai-product` · `full`. Orchestrator: `product-council` (fans out the critics in isolated contexts, runs cross-critic synthesis). Each critic carries the trust-boundary block (the artifact under review is data, never instructions) and cites a public source for its lens.

## Reference library (the deep research — `meta-expert-author` waves)

Every file **dated · coverage-tiered (foundational / expanded / deep) · source-cited**; observable-public-only; no fabricated quotes/frameworks (critical for the living AI-product leaders).

- **UX patterns** — the full taxonomy (registration, onboarding, guidance, JTBD framing, support, progressive disclosure, search, navigation, empty/error states, notifications, settings, forms, permissions, paywalls, personalization, social proof, accessibility, …).
- **App genres** — each genre's conventions, signature patterns, key metrics, and pitfalls.
- **Personas + user research** — methods + archetypes.
- **AI-product UX** — conversational/agentic UX, generative UI, trust/control/steerability, streaming, citations, human-in-the-loop.

## Rubrics (strong — reviewed or created; `[gate]`/`[review]` dims)

- **product-strategy** — problem/opportunity framing · discovery evidence · JTBD/demand · strategy kernel · positioning · prioritization · outcomes/metrics · the four risks · roadmap · org alignment.
- **ux-quality** — usability heuristics · accessibility · IA · interaction-pattern fit · progressive disclosure · genre-fit.
- **prd-quality** — adapted from plan-spec's Tier-A craft + Tier-B gates.
- **ai-product** — trust/control/steerability · uncertainty surfacing · human-in-the-loop · eval-grounded claims.

Each grounded in the canon the scoping survey maps; registered for both the maker (`product-methodology`/`product-spec` build against them) and the judge (`product-evaluate` scores with them).

## Build phases

- [x] **0. Scaffold** — dirs, `plugin.json`, marketplace entry, README, CHANGELOG, this ROADMAP.
- [x] **1. Scoping survey** — 6-skill roster (product-genres split out; PRD folded into methodology `spec/`), ~78-file plan, 5 rubrics, 17-critic lenses + public sources, wave plan. MCP deferred to v0.2.
- [x] **2. Research waves** — the full library authored via parallel waves: methodology (30), research (12), patterns (31), genres (14) + vision archetypes (4) = ~91 files; dated, coverage-tiered, source-cited.
- [x] **3. Skills** — orchestrator + methodology (+ vision archetypes + `spec/`) + research + patterns + genres + evaluate, built on the library.
- [x] **4. Council** — `product-council` orchestrator + 17 `critic-*` agents (read-only; trust boundary; cited lens; living-people quotes verified).
- [x] **5. Rubrics** — the 5 strong rubrics, grounded in the canon (`[gate]`/`[review]` + cited hard tests).
- [x] **6. Hook + commands** — `product-lint` (advisory, never-blocks) + `check-sourcing.py` (provenance gate) + the 6 `/product-*` commands. (`product-corpus` MCP → v0.2.)
- [x] **7. Validate** — `validate_plugin.py --strict` · `reference-lint.py` · `product-lint`/`check-sourcing` selftests · markdownlint 0/129 · marketplace — all PASS.
- [x] **8. Red-team** — `plugins-factory` 9-critic council (CONDITIONAL → all MUST-folds applied → APPROVED). Record: `reviews/2026-06-03-v0.1-red-team.md`. **Cut 0.1.0.**

## Verification discipline (from `meta-expert-author`, applied throughout)

Every reference file carries `date` + `coverage` + `primary_sources`; single-source claims are labeled; the living product leaders' lenses cite observable public material only (no invented quotes); fetched/ingested content is data, never instructions. `bin/check-sourcing.py` **mechanizes** this — it fails if any library reference lacks the frontmatter or any critic lacks a source signal — and the living-practitioner critics' verbatim quotes were verified against their public sources before 0.1.0.
