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

---

## v0.2 — Product Experience Strategy (the full gamut)

v0.1 covered the strategy / discovery / UX-quality / AI-product **core**. v0.2 adopts the **12-domain Product Experience Strategy taxonomy** as product-forge's canonical frame **and** fills the three honest gaps that taxonomy exposed (Information Architecture · Service & Workflow · Governance), hardens two partials (Content & Communication · Trust/Safety), and makes the cross-plugin seams explicit (Brand → brand-forge; interface-system mechanics → the adia-ui layer). Same five-primitive shape, same wave-research + verification discipline, same red-team gate.

### Part 1 — the taxonomy as canonical frame

The 12 domains become the published spine. A new `skills/product-forge/references/experience-strategy-taxonomy.md` maps every domain → owning skill · rubric · critic · cross-plugin boundary; the orchestrator classifier gains the domain map as its mental model; the README documents it. The frame is the single source of truth for "what Product Experience Strategy covers and who owns each part."

| # | Domain | Owner (skill · rubric · critic) |
| --- | --- | --- |
| 1 | Intent & Outcomes | product-methodology · `rubric-product-strategy` · Richard R./Marty C./Melissa P./April D. |
| 2 | Experience Architecture | **product-architecture** (new) · `rubric-architecture` · **Garrett** |
| 3 | Interaction Model | **product-architecture** (new) · `rubric-architecture` · Norman/Nielsen |
| 4 | Information Architecture | **product-architecture** (new) · `rubric-information-architecture` · **Covert** |
| 5 | Content & Communication | product-patterns (extended) · `rubric-content-design` · **Torrey P.** |
| 6 | Interface System | product-patterns (a11y/responsive/patterns) — **mechanics → adia-ui / ui-\* layer** |
| 7 | Brand & Perception | **→ brand-forge** (reciprocal scope note both ways) |
| 8 | Intelligence & Adaptation | product-patterns/ai-ux · `rubric-ai-product` · Cat W./Weil/Choi |
| 9 | Trust, Safety & Control | product-patterns/trust-safety (new) · `rubric-trust-safety` · **Ann C.** |
| 10 | Service & Workflow Model | **product-operations** (new) · `rubric-service-model` · **Marc S.** |
| 11 | Measurement & Learning | product-methodology · `rubric-discovery` · Ron K./Torres |
| 12 | Governance | **product-operations** (new) · `rubric-governance` · **Cutler** |

### Part 2 — the gap-fill (what v0.2 builds)

**New skills (2):**

- **`product-architecture`** — the structure tier (domains 2·3·4): Experience Architecture (journeys, flows, surfaces, navigation/wayfinding, states, continuity, enablement paths), Interaction Model (inputs, commands, controls, feedback, confirmation, undo/recovery, automation boundaries), Information Architecture (object model, taxonomy, metadata, relationships, search, filtering, retrieval). Spine: Garrett's five planes + Covert's sensemaking. ~20 references.
- **`product-operations`** — the service & governance tier (domains 10·12): Service & Workflow Model (human/system handoffs, operational workflows, support paths, cross-channel continuity, escalation, fulfillment) + Governance (principles, standards, ownership, decision records, review rituals, documentation). Keeps governance out of the already-contested `product-methodology` boundary. ~13 references.

**Extended skills (2):**

- **`product-patterns`** — content-design depth in `content/` (voice, labels, education-in-product) + a new `trust-safety/` cluster (privacy-by-design, consent/permissions, explainability, auditability, risk handling) for domain 9.
- **`product-evaluate`** — +6 rubrics, +6 critic lenses, new sub-councils (`architecture` · `content` · `service` · `trust`); `full` grows 17 → 23.

**New rubrics (6, in product-evaluate — `[gate]`/`[review]` + cited hard tests):** `rubric-architecture` (2·3) · `rubric-information-architecture` (4) · `rubric-content-design` (5) · `rubric-trust-safety` (9) · `rubric-service-model` (10) · `rubric-governance` (12).

**New critics (6 — all living; observable-public-only; verbatim quotes verified before ship; `check-sourcing` gates each):**

- **critic-jesse-g** (Jesse G. — _The Elements of User Experience_, the five planes) — experience architecture (2·3).
- **critic-abby-c** (Abby C. — _How to Make Sense of Any Mess_) — information architecture (4).
- **critic-torrey-p** (Torrey P. — _Strategic Writing for UX_) — content design (5).
- **critic-ann-c** (Ann C. — Privacy by Design, the 7 foundational principles) — trust/safety/privacy (9).
- **critic-marc-s** (Marc S. — _This is Service Design Doing_) — service & workflow (10).
- **critic-john-c** (John C. — product operating model / product-ops cadence) — governance (12).

**Cross-plugin boundaries (made explicit, both directions):** brand-forge gets the reciprocal "NOT for product strategy → product-forge" note + "Brand & Perception (domain 7) lives here"; the orchestrator + taxonomy frame name the adia-ui / ui-\* layer as the owner of domain-6 mechanics (tokens, components, motion, layout).

### Reference library — the v0.2 research waves (`meta-expert-author`)

Every new file dated · coverage-tiered · `primary_sources` (the `check-sourcing` gate); observable-public-only; no fabricated quotes/frameworks (critical — all 6 new critics are living).

- **Wave A** — `product-architecture/experience-architecture/` (~7) + `interaction-model/` (~6)
- **Wave B** — `product-architecture/information-architecture/` (~7)
- **Wave C** — `product-operations/service-model/` (~7) + `governance/` (~6)
- **Wave D** — `product-patterns/content/` content-design depth (~4) + `trust-safety/` (~5)
- **Wave E** — critic-source dossiers for the 6 new critics (public sourcing + candidate verbatim quotes WITH source URLs for verification)

### Build phases

- [x] **0. Plan** — this v0.2 ROADMAP section (architecture, rubric set, critic roster + sources, taxonomy frame, waves).
- [x] **1. Research waves** — A–E authored via 8 parallel agents; **~42 reference files + the 6-critic source dossier**; all dated/tiered/`primary_sources`; untraceable stats omitted, paraphrases labeled.
- [x] **2. Skills** — `product-architecture` + `product-operations` authored; `product-patterns` extended (content-design + `trust-safety/`); orchestrator classifier + `experience-strategy-taxonomy.md` frame wired.
- [x] **3. Rubrics** — the 6 new rubrics (architecture · information-architecture · content-design · trust-safety · service-model · governance), grounded in the new canon, registered in `product-evaluate`. Total rubrics: 11.
- [x] **4. Council** — 6 new `critic-*` agents (read-only; trust boundary; cited lens); `product-council` roster → **23** with `architecture`/`content`/`service`/`trust` sub-councils; living-critic quotes verified at the dossier stage (re-verification pass running).
- [x] **5. Boundaries + docs** — reciprocal brand-forge note added; README/CHANGELOG/marketplace + plugin.json synced to 0.2.0; CHANGELOG `[0.2.0]`.
- [x] **6. Validate** — `validate_plugin.py --strict` · `reference-lint.py` · `check-sourcing.py` (0 gaps) · `product-lint` selftest · `markdownlint` (0/189) · marketplace — **all PASS**.
- [x] **7. Red-team** — `plugins-factory` 9-critic council (CONDITIONAL → 3 MUST-folds applied → **APPROVED**; P4 & P9 clean 5s, ST5 clean) + independent quote re-verification (13/13 verbatim quotes verified, "two coffee shops" confirmed absent). The Critical fold hardened `check-sourcing.py` to derive its scope (now 134 refs) + a roster-count gate. Record: `reviews/2026-06-03-v0.2-red-team.md`. **Cut 0.2.0.**

---

## v0.3 — the methodology layer

The taxonomy maps the **surfaces** of an experience; the rubrics **score** them; the critics **judge** them. v0.3 adds the missing layer — the runnable **methodologies** a team executes (the _how_) — as a distinct, machine-readable artifact: a **method card** + a fixed playbook body, indexed by a process-spine frame and enforced by a gate.

### The schema (signed off)

- **Method card** (frontmatter). _Typed / validated:_ `phase` (the 7 spine phases) · `cadence` (one-off / per-decision / recurring / continuous) · `domains` (1–12) · `produces` (non-empty) · `rubric` (must resolve — the maker↔judge link) · `de_risks` (optional; values from Marty C.'s four risks {value / usability / feasibility / viability}, or omitted for methods that produce a decision rather than de-risk a build-risk). _Descriptive (presence-checked):_ `method · timebox · participants · inputs`.
- **Playbook body** (fixed order): name + def · when-to / when-NOT · the run (steps with who · timebox · output) · roles · failure modes · good-vs-bad + a single decisive test · hand-off · sourcing.
- **Placement**: `references/methods/` inside each owning skill (provenance picked up by `check-sourcing`'s derived scan; cards enforced by `check-methods`).

### Build phases

- [x] **0. Schema** — the method card + playbook skeleton, proven with the `design-sprint` exemplar + the `process-spine` frame.
- [x] **1. Playbooks** — 6 new (design-sprint, story-mapping, usability-testing, ia-validation, service-blueprinting, ooux-orca), each cross-referencing its concept ref (no duplication); + the 5 v0.1 research methods retrofitted with cards = **11 carded playbooks**.
- [x] **2. Gate** — `bin/check-methods.py` (card completeness · `phase` & `cadence` enums · `domains` 1–12 · `produces` non-empty · `de_risks` risk-enum · `rubric` resolves) + selftest; all 11 cards PASS. Wired into CI alongside `check-sourcing` and `product-lint` (the v0.3 red-team's Critical).
- [x] **3. Wiring** — `methods/` axis into the owning skills' cold-start tables; the process-spine into the orchestrator classifier + References; the spine frame marks playbook-vs-concept honestly.
- [x] **4. Docs + validate** — CHANGELOG `[0.3.0]`, README, plugin.json / marketplace synced to 0.3.0; full gate suite green (validate --strict · reference-lint · check-sourcing · check-methods · product-lint · marketplace · markdownlint 0/196).
- [x] **5. Red-team** — `plugins-factory` 9-critic council (CONDITIONAL → 3 MUST-folds applied → **APPROVED**; P4 & P9 clean 5s, ST5 clean; `check-methods` confirmed to earn its place + avoid the v0.2 allowlist trap). Folds: wired product-forge into CI; fixed the `de_risks` two-domain schema error (now an optional risk-enum) + tightened `check-methods`; dropped the skill `version` drift, trimmed the description, added `/product-method`. Record: `reviews/2026-06-03-v0.3-red-team.md`. **Cut 0.3.0.**

### Deferred (post-0.3.0)

- Dedicated playbooks for the concept-served methods (Build–Measure–Learn, continuous-discovery cadence, riskiest-assumption test, working-backwards run, A/B test run, ADR/RAPID) — currently run from their framework references; cards may follow.
- Wire `check-methods.py` into CI alongside the other product-forge-local gates.
