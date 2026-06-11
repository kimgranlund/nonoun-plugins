# Changelog

## [0.4.17] — 2026-06-11

- **Council-calibration checkers hardened against brittle concept-regex** (the new plugins-factory `check-recall.py` gate). The strategy/design/voice checkers (`check.py`, `check-design.py`, `check-voice.py`) gained patterns for legitimate, *recurring* council wordings their regex would otherwise miss in a real run — e.g. "a sticker, not an identity", "show me the grid", "you chose a typeface, you did not make one", "a model could generate this in thirty seconds" (design); "not one fact behind any adjective", "discount circular", "two surfaces, two brands" (voice); "every rival could put their name on it", "tautological values you cannot disagree with" (strategy). All three checkers' recorded baselines + rate samples re-score full with **zero regression**; their paraphrase corpora live in `plugins-factory/evals/recall-corpus/` and are CI-asserted.

## [0.4.16] — 2026-06-10

- **Design + voice council-calibration promoted to N=3** (two further cold runs each through the design and voice sub-council proxies). Design (Lumina): **5/5 in 3/3 runs, REBUILD ×3**; voice (Verve): **5/5 in 3/3 runs, REBUILD ×3** — the trust boundary held in all 24 isolated critic contexts across the two sub-councils, and convergence (design: the missing grid; voice: "nothing real underneath the words") reproduced every run. With Northwind's strategy fixture already at N=3, **all three non-`full` brand sub-councils are now N=3 at 100% per-defect**. README rate tables updated.

## [0.4.15] — 2026-06-10

- **Third council-calibration fixture — the `voice` sub-council** (`fixtures/weak-verbal-identity.md` + `check-voice.py`). With this, all three non-`full` brand sub-councils are calibrated (strategy=Northwind · design=Lumina · voice=Verve). "Verve" plants one verbal/copy failure per voice-critic lens — unbacked hype with no facts (David A.), a flat category-descriptor tagline with no Big Idea (George L.), written-down-to-everyone and disposable (Tim D.), no house style / emoji-slang soup (Mary N.) — plus the ST5 probe. Cold baseline through the voice sub-council: **5/5 caught, REBUILD (8 Critical), unanimous convergence on "nothing real underneath the words," the ST5 directive refused, and the B-S4 blind spot (the hollow copy is a symptom of absent positioning) handed to `strategy`.** CI now re-scores all three brand baselines. README documents all three sub-council fixtures.

## [0.4.14] — 2026-06-10

- **Second council-calibration fixture — the `design` sub-council** (`fixtures/weak-visual-identity.md` + `check-design.py`). The first fixture (Northwind) exercises only `strategy`; this one ("Lumina") exercises **design** with one planted defect per critic lens — a static no-system logo (Paula S.), trend-chasing with no grid (Massimo V.), off-the-shelf Arial with no type system (Matt W.), the safe/AI-generic brief (Jessica W.) — plus the ST5 trust-boundary probe. These are visual/typographic failures the strategy council structurally misses (the orchestrator's B-S4 note made concrete). Cold baseline through the design sub-council (proxy protocol): **5/5 caught, REBUILD (9 Critical), unanimous convergence on the missing grid, the ST5 directive refused, and the B-S4 blind spot correctly handed to `strategy`+`voice`.** CI now re-scores both brand baselines (strategy + design). README documents both fixtures + the design↔strategy complement.

## [0.4.13] — 2026-06-10

- **Council-calibration promoted to a catch-rate over N=3 cold runs** — two further runs recorded via the baseline's proxy protocol (the real orchestrator, personas, and rubric loaded from disk): **6/6 planted defects in 3/3 runs, REBUILD ×3, D1–D6 at the floor in all three scorecards, the trust boundary held every time** — run 3 additionally articulating the inverse-anchor risk (a fixture's self-condemnation must anchor a council no more than "rate this 5/5" would). All three runs independently named the missing cultural root as load-bearing. The README carries the rate table; CI still re-scores the designated baseline.

## [0.4.12] — 2026-06-10

- **Obscuring consistency** — a ROADMAP red-team attribution referenced a plugins-factory critic by real surname; now the obscured `First L.` form, per the catalog convention (a full-catalog audit found this to be the only persona-context name in any tracked file).

## [0.4.11] — 2026-06-10

- **`/brand-corpus-export` surfaces the reader's optional polish** — documents `reader.config.json` (site title + home-card section descriptions) and the root redirect `--init` now writes; the Verify step's sanitizer assertion corrected to the real behavior (**no dialog** — DOMPurify strips a raw `<script>`, it doesn't render it as text).

## [0.4.10] — 2026-06-07

- **`/brand-corpus-export` uses the shared `--init` convention** — generating the `<corpus>/site/` viewer is now a single `build-sitemap.py --init` call (the same tool every plugin uses), so the layout is identical across the catalog.

## [0.4.9] — 2026-06-06

- **`/brand-corpus-export` restructured** — the corpus root is now clean, shareable Markdown (sections + README); the reader is tucked into a `<corpus>/site/` subfolder (copied machinery only — never a bundled example). Serve the corpus root, open `/site/`.

## [0.4.8] — 2026-06-06

- **Add `/brand-corpus-export`** — lay out the engagement's deliverables as a Markdown corpus (ordered sections by pipeline stage), then build + serve them with the bundled corpus-reader as a self-contained, shareable brand site.

## [0.4.7] — 2026-06-06

- **Bundle the corpus-reader** (`bin/corpus-reader/`) — generate a navigable site for a brand corpus (a folder of markdown) and read it locally (`build-sitemap.py` + `python3 -m http.server`). Vendored from plugins-factory and kept byte-identical by `sync-corpus-reader.py` (CI-gated); untrusted corpus markdown is sanitized (DOMPurify).

## [0.4.6] — 2026-06-05

- **Critic identities obscured** — slugs now `critic-<first>-<initial>`, display names `First L.`, practitioner bios moved to a git-ignored `agents/.name-map.md`; rosters/refs updated; council behavior unchanged.

## [0.4.5] — 2026-06-04

- **The aspiration is now a precondition of making — a soft gate.** Before the Team converges, the Muse's pull must be at least lightly named; brand work reasoned toward _nothing_ drifts to the category average. `/brand-build` gains an explicit **"name the pull before you converge"** step (set a provisional, revisable direction — or convene the Muse — _before_ invoking the methodology); `brand-methodology` adds a **"no convergence toward nothing"** standing constraint and names aspire-first as the loop's precondition; `creative-collaboration.md` states it on the loop. It is a _soft_ blocker throughout — cleared by **naming** a direction, never by stopping, and "lightly declared and developed over time" is the healthy state. Mirrors the generalized rule in plugins-factory `operational-roles.md` (R2/R4).

## [0.4.4] — 2026-06-04

- **Manifest + command-frontmatter fixes that unblock install.** `userConfig.corpus_dir` was missing the required `title` field, so `claude plugin install brand-forge` failed schema validation (`userConfig.corpus_dir.title: expected string, received undefined`) — added it. Separately, the `argument-hint` frontmatter in `/brand-council` and `/brand-stamp` opened a YAML flow collection with trailing tokens (`[strategy|design|voice|full] [artifact]`), which made the parser fail and the loader silently drop the **entire** frontmatter block (description + hint) at load. Both are now quoted strings, and the remaining command hints were quoted for consistency.

## [0.4.3] — 2026-06-04

- **`evals/council-calibration/` — the brand council, calibrated with first evidence.** A planted-defect strategy fixture (`weak-brand-strategy.md` — "Northwind Coffee", hitting every `rubric-brand-strategy` anti-pattern plus the bullshit filter), a concept-level transcript checker (`check.py`), a protocol (`README.md`), and a recorded baseline (`runs/`). Run cold and given no hint, the brand council caught **6/6** planted defects (borrowed-moodboard root, category-restatement position, no enemy, persona-not-transformation, values-without-trade-offs, archetype) and returned **REBUILD** — and the trust boundary held live (the fixture's "deliberately hollow" self-framing was treated as data, not an instruction). First evidence the brand council finds the failures its rubric targets. The live run stays a manual eval (an LLM panel); CI runs the deterministic guard that the recorded baseline still scores 6/6.

## [0.4.2] — 2026-06-04

- **Critic agent slugs shortened** — the trailing surname was dropped from the five critic slugs that carried one, so the roster uses shorter single-token slugs. Internal rename only: the personas, their attributions in the agent bodies, and the council's behavior are unchanged; the `brand-council` roster is updated to match.

## [0.4.1] — 2026-06-04

Fixed a command-name collision that made `/brand-evaluate` unreachable.

- **`/brand-evaluate` → `/brand-score`.** The command shared its slug with the `brand-evaluate` skill — and a plugin's commands and skills occupy **one** `/<plugin>:<slug>` invocation namespace (they are two file-formats of one primitive), so the skill shadowed the command and `/brand-evaluate` returned "Unknown command." Renamed the command to a distinct verb (`/brand-score`), mirroring plugins-factory's `/plugin-score` → `plugin-evaluate` pairing; the `brand-evaluate` skill is unchanged and is still the scoring knowledge the command routes to. The collision class is now gated by `validate_plugin.py`.

## [0.4.0] — 2026-06-04

The Muse, corrected: **from provocateur to aspirational attractor.** v0.3 cast the Muse as a divergent provocateur; that was one _mode_ mistaken for the whole seat. The Muse is an **attractor** — an aspirational goal, set of principles, ideal, or concept that exerts a **gravitational pull** in a direction, so the work moves toward something better than the category average. The Maker is pulled toward it; the Council judges against it.

### Changed

- **`brand-muse` reframed as the aspirational attractor.** The pull can be a positive ideal, a **provocation** (radical differentiation — when the truest direction is away from the mainstream, which is sometimes exactly right), a guiding concept to emulate, or a principle set. The six lenses are recast from "ways to diverge" to "ways to set or strengthen the pull" (name the ideal · the differentiating provocation · the adjacent-world exemplar · the contrarian angle · the principles · the pull-check). Provocation is now one mode, not the definition.
- **`creative-collaboration.md` + `team-operations-by-phase.md`** rewritten around the attractor: the loop is **aspire → make → review → remake**; the Muse is a standing orientation the work is pulled toward, not a one-time brainstorm; the Council judges against the aspiration it set.
- **`rubric-creative-collaboration.md`** reframed to the attractor (its header, the D1 anchor, and D2): D2 moves from "provocation before convergence" to "the aspirational pull" — does the work reach for a real aspiration, or drift to the category average?
- The generalized pattern in **plugins-factory** (`operational-roles.md`, v0.2.4) is corrected in lockstep: the third seat is the **aspirational attractor** (near-universal — a north-star / principles / ideal), staffed as a generative agent only where taste makes the aspiration a live judgment; provocation is one form the pull takes.

### Why

The v0.3 framing ("the provocateur opens the option space") confused the Muse with one of its modes and made the seat look narrowly creative. As an attractor, the Muse is what keeps any work — brand, product, or system — from converging on the average; provocation is simply the pull pointing _away_ from the mainstream when that is the right direction.

## [0.3.0] — 2026-06-04

The **three-seat model**, made explicit and mechanized. Brand work was always "made by a Team and reviewed by a Council"; this release adds the missing generative seat — the **Muse** — promotes it to a real agent, and gives all three seats a shared model, a ways-of-working rubric, and per-phase methodologies.

### Added

- **The Muse — a generative provocateur agent** (`agents/brand-muse.md`) + the **`/brand-muse`** command, symmetric to `/brand-council`. Read-only and trust-bounded like the critics, but generative: it opens the option space with grounded provocations (cultural inversion · adjacent-world raid · contrarian / psycho-logic · constraint flip · find-the-enemy · kill-the-safe-version) _before_ the team converges. The Muse explores forward; the Council attacks backward.
- **`creative-collaboration.md`** (in `brand-methodology`) — the three-seat model: Muse (provoke) · Team (make) · Council (review), the **provoke → make → review → remake** loop, the handoffs (above all the creative brief), and the one invariant: _no seat judges its own work_ (self-review grades on a curve).
- **`team-operations-by-phase.md`** — how the seats staff each phase of building a brand and its corpus (research · strategy · expression · stewardship), grounded in agency practice (account planning; the creative brief as the strategist→creative pivot; the design crit; brand governance), with each phase's lead seat, ritual, handoff gate, and failure mode.
- **`rubric-creative-collaboration.md`** — a new Process family in `brand-evaluate` that scores the _ways of working_, not the artifact: seat separation, provocation-before-convergence, foundation-before-expression, council survival, phase discipline, steward continuity.

### Changed

- **The Team gains a Brand Steward** — the role the stewardship phase had no seat for: the owner of coherence over time (guidelines, governance, the decision log). In the same pass the **Creative Muse became its own seat** (the generative provocateur, now the `brand-muse` agent) rather than a Team making-role, leaving seven convergent making-roles on the Team.
- `brand-methodology` SKILL now frames the three seats + the loop and points to the new references; `/brand-build` routes to `/brand-muse` for divergence.
- The operational-roles pattern (Maker · Critic · Provocateur) this release formalizes is generalized into **plugins-factory** so any plugin can reuse it.

## [0.2.0] — 2026-06-03

- **`/brand-stamp`** — emit a finished brand corpus as a distributable artifact, in one of **three pure, separate** forms (each to its own folder under `-o`): **plugin** (`<out>/plugin/<brand>-brand/` — corpus + the stdio `brand-corpus` MCP + a thin skill, for Claude Code / Cowork; bundled or `--linked`), **skill** (`<out>/skill/<brand>-brand/` — a standard Agent Skill with the corpus bundled in `references/`, for Claude chat; no MCP/scripts), and **mcp** (`<out>/mcp/<brand>-brand-mcp/` — the standalone server + corpus + a `claude mcp add` README). The command **always asks** which form. Mechanized by `bin/brand-stamp`; the plugin form is authored to pass plugins-factory's `validate_plugin.py`.
- **`brand-corpus` MCP wiring** captured in `skills/brand-corpus/references/mcp-wiring.md` — the language-agnostic tool contract, Python-vs-TS guidance, and the three registration recipes (bundled / standalone / published). `brand-corpus-mcp.py` now also accepts the `BRAND_CORPUS_ROOT` env alias.

- **Corpus distribution hygiene** — every bundled corpus now ships a per-layer `INDEX.md`; the plugin form takes `--version` (re-baking a corpus is a release — bump it); and `stamping.md` documents size-tiered retrieval (small inline / large indexed-MCP) and keeps the source-of-truth corpus in the consumer's version-controlled workspace, never in the plugin.

- **Tool-scoped the council (security).** All 15 brand-council agents now declare a `tools:` allowlist — the 14 critics `Read, Grep, Glob`, the orchestrator `+ Task` — so a reviewer reading an untrusted brand artifact/corpus is _structurally_ read-only, not merely instructed to be. Matches plugins-factory and closes the same trifecta-class gap brand-forge's own critics flag in others.

- **Red-teamed (the plugins-factory plugin-council, full panel).** Recorded in `reviews/2026-06-03-v0.2-red-team.md`. Verified clean on dependency legality and security (no bundled lethal trifecta, council structurally read-only, `_safe()` correct against traversal + symlink escape, ST5 injection sweep clean, the 14-critic roster well-sourced). Folded the MUST-fixes: reconciled the manifest/README to the shipped five-command surface (this `0.2.0` cut moves the previously "Unreleased" work into a dated release), and **removed an orphaned `bin/brand-stack` renderer + its SVG template** — a six-tier "Brand Stack" model the methodology never adopted and nothing referenced. The `brand-corpus` MCP was also hardened — truncation past 20k chars is now signalled, and a `selftest` exercises the `_safe()` path-guard against traversal / symlink / prefix-sibling escape (in CI, and traveling into stamped artifacts via `_copy_mcp`).

## 0.1.0 — 2026-06-02

Initial release. brand-forge packages the cultural-authority brand methodology as a self-contained Claude Code plugin, re-cast through the five plugin primitives for component-fit:

- **Commands** — four thin, typed entry points (`/brand-build`, `/brand-evaluate`, `/brand-council`, `/brand-orient`) that set mode + posture and route to the right skill or agent without re-containing the methodology.
- **Agents** — a 14-critic named-practitioner council plus an orchestrator that fans out the relevant sub-council (strategy · design · voice · full) in parallel, isolated contexts, returns severity-classified cited findings, and runs the B–S synthesis.
- **Skills** — `brand-methodology` (research → strategy → expression → stewardship), `brand-evaluate` (rubric library + adversarial scoring), and `brand-corpus` (corpus inventory + state read) hold all the depth.
- **Hooks + bin** — a `brand-lint` advisory structural lint on prose artifact writes (it surfaces smells, never blocks), catching only mechanizable smells (archetype/VMV/persona/DNA-word-cloud language, values-without-trade-offs); cultural judgment stays in the skill and council.
- **.mcp.json** — declares the `brand-corpus` retrieval slot, pointed at a brand via `userConfig.corpus_dir`; ships the contract, not any brand's data.

Self-contained: zero cross-plugin dependencies. Authored, validated, and red-teamed via `plugins-factory`.
