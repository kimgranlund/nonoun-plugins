# Changelog

All notable changes to **product-forge** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.3.14] — 2026-06-10

- **Second council-calibration fixture — a metric-theater PRD** (`fixtures/metric-theater-prd.md` + `check-prd.py`). Where "Project Atlas" is a product-STRATEGY doc, "Pulse" is a **PRD** that fails `rubric-prd-quality` by metric theater: a feature list ("the system shall…" ×6) framed around vanity engagement proxies (DAU, time-in-app, page-views, "done = shipped") with no problem, no JTBD, no risks, no non-goals. Cold baseline through the strategy sub-council: **6/6 planted defects caught, REBUILD (D1–D7 all 1), the 5/5 directive refused by all six critics** — and the council went beyond the planted set, flagging the dark-pattern features (3 push/day, exit-nudge, autoplay) as active user harm and naming its blind spot (trust/consent/platform-policy → the `trust` sub-council). CI re-scores both product baselines. README documents both artifact-type fixtures.

## [0.3.13] — 2026-06-10

- **Council-calibration promoted from a single baseline to a catch-rate over N=3 cold runs** — two further isolated-critic runs recorded (`runs/…-run2.md`, `-run3.md`, using the full `agents/critic-*.md` persona files verbatim): **7/7 planted defects caught in 3/3 runs, 15/15 REBUILD verdicts, 15/15 embedded-instruction refusals.** The README carries the rate table; CI still re-scores the designated baseline.

## [0.3.12] — 2026-06-10

- **Council-calibration eval** (`evals/council-calibration/`) — a planted-defect strategy fixture ("Project Atlas": solution-first, goals-as-strategy, vanity metrics, the four risks dismissed, for-everyone positioning, a feature-list roadmap, plus an embedded "score it 5/5" instruction), a concept-matching transcript checker, a protocol, and a recorded baseline. Run cold, the **strategy sub-council** (5 parallel isolated critics) caught **7/7** planted defects, returned a unanimous REBUILD, and **all five independently flagged the embedded instruction** as a finding rather than obeying it — the trust boundary held in every isolated context. CI re-scores the recorded baseline (the same pattern as plugins-factory and brand-forge).

## [0.3.11] — 2026-06-10

- **`/product-corpus-export` surfaces the reader's optional polish** — documents `reader.config.json` (site title + home-card section descriptions) and the root redirect `--init` now writes; the Verify step's sanitizer assertion corrected to the real behavior (**no dialog** — DOMPurify strips a raw `<script>`, it doesn't render it as text).

## [0.3.10] — 2026-06-10

- **`check-sourcing.py` gains a public-checkout mode.** The 0.3.5 obscuring let a critic's provenance live in the git-ignored `agents/.name-map.md` — which made the gate impossible to pass on a fresh checkout (22 "unsourced" failures on CI; part of the 2026-06-05 → 06-10 outage). When the name-map is absent **and** `git check-ignore` proves it deliberately excluded, critics without inline signals now **defer** (reported in the RESULT line, never failed); with the map present the full strictness is unchanged, and an absent map outside a git context still fails. New selftest case covers the mode. The guarantee is honest: full provenance is enforced where the name-map exists (the maintainer tree); CI enforces everything visible in a public tree.

## [0.3.9] — 2026-06-07

- **`/product-corpus-export` uses the shared `--init` convention** — generating the `<corpus>/site/` viewer is now a single `build-sitemap.py --init` call (the same tool every plugin uses), so the layout is identical across the catalog.

## [0.3.8] — 2026-06-06

- **`/product-corpus-export` restructured** — the corpus root is now clean, shareable Markdown (sections + README); the reader is tucked into a `<corpus>/site/` subfolder (copied machinery only — never a bundled example). Serve the corpus root, open `/site/`.

## [0.3.7] — 2026-06-06

- **Add `/product-corpus-export`** — lay out the engagement's deliverables as a Markdown corpus (ordered sections from discovery → operations), then build + serve them with the bundled corpus-reader as a self-contained, shareable product site.

## [0.3.6] — 2026-06-06

- **Bundle the corpus-reader** (`bin/corpus-reader/`) — generate a navigable site for a product corpus (a folder of markdown) and read it locally (`build-sitemap.py` + `python3 -m http.server`). Vendored from plugins-factory and kept byte-identical by `sync-corpus-reader.py` (CI-gated); untrusted corpus markdown is sanitized (DOMPurify).

## [0.3.5] — 2026-06-05

- **Critic identities obscured** — slugs now `critic-<first>-<initial>`, display names `First L.`, practitioner bios moved to a git-ignored `agents/.name-map.md`; council roster, references, and the sourcing gate updated; council behavior unchanged.

## [0.3.4] — 2026-06-04

- **The aspiration is now a precondition of making — a soft gate.** Before a maker converges on substantive work, the **Vision / North-Star** the work serves (product-forge's domain attractor — the `vision/` axis: manifesto · reframe · case-for + the north-star metric) must be at least lightly named; product work reasoned toward _nothing_ drifts to the category average. The four maker commands gain an explicit **"name the pull first"** step before the `Invoke` hand-off (`/product-strategy` → the Vision / North-Star; `/product-discover` → the hypothesis/outcome the research illuminates; `/product-ux` → the outcome the screen serves; `/product-method` → the outcome the method clarifies). The `product-methodology` maker skill adds a **"name the pull before you converge"** preamble above its cold-start table, pointing at the `vision/` axis; the `product-forge` router gains an **"Aspiration named" `[soft-gate]`** dimension on the Orientation rubric. It is a _soft_ blocker throughout — cleared by **naming** a provisional, revisable direction, never by stopping; "lightly declared and developed over time" is the healthy state. Mirrors the generalized rule in plugins-factory `operational-roles.md` (the Maker's precondition, R2/R4) and brand-forge 0.4.5. No new commands, skills, or critics — the soft gate adds no surface.

## [0.3.3] — 2026-06-04

- **Quoted `argument-hint` frontmatter** across all commands — normalizes the value to a string (YAML was parsing the unquoted `[..]` as a flow list/map) and satisfies plugins-factory's new frontmatter flow-collection lint. No behavior change.

## [0.3.2] — 2026-06-04

- **Critic agent slugs shortened** — the two AI-product critic slugs were collapsed to the short `critic-cat-w` / `critic-meaghan-c` form, so all 23 critics use a single-name slug. Internal rename only: personas, attributions, and council behavior unchanged; the `product-council` roster updated.

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

- **Verified all 6 new (living) critics' verbatim quotes against their public sources** before ship; the famous "two coffee shops" line was confirmed **NOT** Marc S.'s (it is 31 Volts, 2008) and excluded, and Abby C.'s IA definition uses the correct "make it _more_ understandable" wording. `bin/check-sourcing.py` enforces the provenance floor across the new references and critics.

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

- Red-teamed with the `plugins-factory` 9-critic council (CONDITIONAL → folded): reconciled the build-state docs, removed the phantom-MCP claim (deferred to v0.2), **verified the living-practitioner critics' verbatim quotes against their public sources** (corrected one Cat W. misquote + Meaghan C.'s title), added the `check-sourcing.py` provenance gate, and made the README sibling links copy-alone-safe. Record under `reviews/`.

### Planned (v0.2)

- A read-only `product-corpus` MCP for per-instance retrieval of a team's PRDs / research / personas.
