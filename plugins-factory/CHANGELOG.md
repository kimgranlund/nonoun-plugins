# Changelog

## 0.2.21 — 2026-06-10

- **corpus-reader: four small pattern fixes.** The sidebar wordmark drops a leading separator from the subtitle (`"BZZR — Product Corpus"` → `BZZR` / `Product Corpus`); the sidebar search now also matches page **summaries** (not just title + path); the provenance stats count tags in **prose only** (a doc *about* the tag syntax no longer skews the bar); and `--init` drops a root `index.html` redirect → `site/` when the corpus root has none (never overwrites an existing file) — removing the `/site/`-vs-`/` 404 papercut. Re-synced into the vendored copies.

## 0.2.20 — 2026-06-10

- **corpus-reader: committed `demo-corpus/` + pipeline smoke + JS parse gate.** A tiny synthetic corpus (6 pages — statuses, provenance tags, xrefs, a table, mermaid, a sanitizer probe, `reader.config.json`) now ships with the reader, so a fresh clone renders out of the box instead of an empty shell (the only example was a 43MB gitignored local fixture). CI smoke-builds it every push (`build-sitemap.py` + `--init` into a tmp corpus) and gains a `node --check` parse gate over the reader's ES modules — both proven against planted failures before wiring. Synced into the vendored copies (installed plugins get the working example too).

## 0.2.19 — 2026-06-10

- **`reference-lint.py`: references to deliberately git-ignored targets are exempt from the resolve requirement.** Docs across the catalog cite `agents/.name-map.md` (the obscured-critic provenance file, git-ignored by design) — the linter required it to exist on disk, so it was green on a maintainer tree and structurally red on every fresh checkout (one of the three causes of the 2026-06-05 → 06-10 CI outage). An unresolved reference is now exempt iff `git check-ignore` confirms its target is ignored; outside a git context the strict behavior is unchanged.

## 0.2.18 — 2026-06-08

- **corpus-reader: optional `reader.config.json` for home polish.** A `<corpus>/reader.config.json` (`{"title": …, "sections": {"01-foo": "one-line description"}}`) now sets the corpus title and per-section **card descriptions** on the home — `build-sitemap.py` reads it, the cards render the descriptions, and everything degrades gracefully when there's no config. Re-synced into the vendored copies.

## 0.2.17 — 2026-06-08

- **corpus-reader: the web-component reader gains the new reader's patterns + layouts.** The `<cr-*>` reader now has a sidebar **search** + layer-label nav, a **mobile drawer** (off-canvas + scrim), a home **hero + section cards + a maturity/provenance stats bar** with per-section minibars, and doc **kicker + badges** — plus inline provenance tags (`[KNOWN]/[INFERRED]/[OPEN]/[SEEDED]`) and `path.md` → in-site xref links. `build-sitemap.py` precomputes the status/provenance counts (graceful — the stats bar is omitted when a corpus has neither). Architecture unchanged (web components + OKLCH tokens, served over HTTP). Re-synced into the vendored copies.

## 0.2.16 — 2026-06-08

- **corpus-reader: its own README + a staleness-gated CHANGELOG.** The reader now ships a `README.md` (rewritten for the sidebar-nav layout) and a `CHANGELOG.md`. `sync-corpus-reader.py` gains `--changelog "…"` (prepend a dated entry + refresh a source fingerprint) and `--fingerprint`; its `--check` CI gate now also **fails if the reader's code changed without a CHANGELOG entry** — so the changelog can't silently go stale. Also fixed the sidebar wordmark to derive from the corpus title (it was hardcoded `"BZZR"`, so the generic reader showed the example's brand). Re-synced into the vendored copies.

## 0.2.15 — 2026-06-07

- **corpus-reader: one common `<corpus>/site/` convention.** `build-sitemap.py --init <corpus>` now scaffolds the standard `site/` viewer (machinery only — never a bundled example) and builds its sitemap in a single command. Every plugin's `*-corpus-export` command calls this one tool, so generated corpus sites use an identical layout everywhere. Re-synced into the vendored copies.

## 0.2.14 — 2026-06-06

- **corpus-reader: viewer-in-a-subfolder layout.** `build-sitemap.py ..` now generates the sitemap for a reader living in a `<corpus>/site/` subfolder (content in the parent) — `../`-relative paths, the viewer's own dir excluded from the scan. Lets an exported corpus keep its root as clean, browsable markdown with the app tucked into `site/`. Reader unchanged; the standalone content-beside-`index.html` layout still works. Re-synced into the vendored copies.

## 0.2.13 — 2026-06-06

- **corpus-reader: the home uses the width.** The section-tile home now spans a wider track (90rem, vs the 51rem prose-reading width) with `align-items: start`, so wide viewports get more tile columns and short tiles keep their natural height instead of stretching to the tallest in the row. Reading pages are unchanged (still the 51rem measure). Re-synced into the vendored copies.

## 0.2.12 — 2026-06-06

- **corpus-reader: graceful `file://` guidance.** Opening `index.html` directly (`file://`) blocks ES modules + `fetch()`; the reader now detects this and shows a "serve over HTTP" instruction (with the exact command) instead of a blank page + console errors. Re-synced into the vendored copies.

## 0.2.11 — 2026-06-06

- **corpus-reader hardened + shared.** The bundled `bin/corpus-reader/` (a buildless static site that renders a markdown corpus) now sanitizes untrusted corpus markdown with **DOMPurify** and pins every CDN dependency with **Subresource-Integrity** hashes (fail-safe: prose degrades to escaped text if a script fails its integrity check). New `bin/sync-corpus-reader.py` makes plugins-factory the single source of truth and vendors the reader into brand-forge + product-forge; its `--check` drift gate runs in CI (cross-plugin symlinks don't survive install, so each plugin ships its own synced copy).

## 0.2.10 — 2026-06-05

- **Critic identities obscured** — slugs now `critic-<first>-<initial>`, display names `First L.`, practitioner bios moved to a git-ignored `agents/.name-map.md`; orchestrator roster + eval-prompt corpus + README updated; council behavior unchanged.

## 0.2.9 — 2026-06-04

- **`operational-roles.md` — the aspiration is now the Maker's _precondition_, a soft blocker if absent.** A Maker that converges toward no declared pull has nothing to converge toward, so "converge" degrades to the category average. The doctrine adds an explicit precondition: before substantive making, the domain attractor (Muse / Vision / design-principles) must be **at least lightly named** — one sentence, expected to evolve — and it is a _soft_ gate, cleared by naming a provisional direction, never a hard stop, realized as the first move of every `/x-build` entry. The check is behavioral, not mechanical (the aspiration lives in the work, not the plugin's files, so no static gate sees it). Rubric **R2** now fails a maker that reasons straight to a finished artifact with no declared direction; **R4** requires aspire-to-precede-make. `plugin-build` applies the rule to itself — naming the plugin's one-sentence job (its intent) is the aspiration-precondition before the component-fit table. Wired in lockstep into every catalog plugin's maker flow.

## 0.2.8 — 2026-06-04

- **`validate_plugin.py` now catches the two manifest/frontmatter classes that previously passed every gate.** (1) **userConfig option schema** — each `userConfig` option must declare `title` + `type` (`string|number|boolean|directory|file`) + `description`; a missing `title` is exactly what made the sibling `brand-forge` un-installable while CI stayed green. (2) The **frontmatter flow-collection trap** — an unquoted `argument-hint: [a] [b]` (or any `[`/`{`-opening value that is unterminated or has trailing tokens) makes YAML fail to parse, so the loader silently drops the whole command/agent/skill frontmatter block; a clean `[..]` collection in a string key (`description`/`argument-hint`/`name`/`title`) warns (quote it). Both run in the on-save advisory hook and under CI `--strict`. Selftest extended (userConfig fixtures + flow-trap unit test + on-disk command fixture). `references/plugin-architecture.md` and `references/authoring/plugin-template.md` now document the userConfig schema and the quoting rule. (All command `argument-hint`s in this plugin were quoted to match.)

## 0.2.7 — 2026-06-04

- **`evals/council-calibration/` — the council-calibration eval, with first evidence.** The non-deterministic half of the behavioral suite: a planted-defect fixture (`build-fixture.py` → `mega-helper`, gate-clean but a kitchen-sink bundling four unrelated domains with a 1:1 API-wrapper MCP), a concept-level transcript checker (`check.py`), a protocol (`README.md`), and a recorded baseline (`runs/`). Run cold and given **no hint**, the `plugin-council` caught **2/2** planted judgment defects (P3 boundary, P2 component-fit) that every deterministic gate passes, BLOCKED the fixture, and surfaced emergent findings (an unscoped destructive CRUD MCP → P9, copy-pasted tool schemas, a non-functional server loop). First concrete evidence the council finds the defects no regex can. The live council run stays a periodic manual eval (an LLM panel is not a CI gate); CI runs the deterministic guards — the fixture must stay gate-clean (so it isolates judgment) and the recorded baseline must still score 2/2.

## 0.2.6 — 2026-06-04

- **Added a README.** The lifecycle tool now ships the documentation it requires of every plugin — the command / skill / agent / gate surface, the nine-dimension standard, honest scope, and provenance. (It was the one catalog plugin missing one.)
- **`evals/behavioral-gates.py` — the deterministic behavioral-eval suite** (ROADMAP'd). Builds throwaway fixture plugins, each carrying one known structural defect, runs the `bin/` gates against them, and asserts each is caught — plus a golden clean fixture that must pass every gate. Covers the `../`-dependency (P4), command↔skill collision (P7), agent-smuggling-`mcpServers` (P9), version↔CHANGELOG drift (P8), description count-claim (P5), and dangling-reference classes; wired into CI. It turns "the harness catches a bad plugin" from an assertion into a tested property. The non-deterministic other half — asserting on the critic council's emitted scorecard — stays a documented manual eval (see ROADMAP).

## 0.2.5 — 2026-06-04

- **`validate_plugin.py` — command↔skill slug-collision gate.** Commands (`commands/*.md`) and skills (`skills/<name>/`) are two file-formats of one primitive sharing the `/<plugin>:<slug>` invocation namespace; a command and a skill with the same slug collide (the skill shadows the command → `Unknown command: /<plugin>:<slug>`). The validator now errors on this within a plugin (selftest fixture added; runs in CI via the existing `--strict` steps). This is the gate that would have caught the brand-forge `/brand-evaluate` and product-forge `/product-evaluate` · `/product-research` collisions (fixed in brand-forge 0.4.1 / product-forge 0.3.1).
- **`plugin-architecture.md` — namespacing & naming doctrine corrected against the Claude Code docs.** Made explicit that commands and skills are one namespace (`skills/` preferred for new plugins), that the `/<plugin>:` prefix handles cross-plugin collisions automatically (don't hand-prefix for that reason), that slugs must be unique across `commands/` + `skills/`, that agents are a separate dispatch surface, and the verb-command / noun-skill convention with distinct slugs.

## 0.2.4 — 2026-06-04

- **`operational-roles.md` — the third seat reframed from Provocateur to the aspirational Muse / attractor.** v0.2.3 cast the third seat as a "Provocateur" (divergence); that confused the seat with one of its modes. The third seat is an **attractor** — an aspirational goal / principles / ideal that exerts a **gravitational pull** in a direction; **provocation is one form the pull takes** (when the right direction is away from the mainstream). This makes the seat _near-universal_ rather than narrowly creative: every domain has a north-star (a Muse for brand, a written Vision / PR-FAQ for product, a design-principle set for engineering), so the decision is not _whether_ to have an attractor but how to **right-size** it — a generative agent only where taste makes the aspiration a live judgment, a written principle set otherwise. The "not the red team" distinction holds and is sharpened: the Muse pulls _forward_ toward an aspiration that doesn't exist yet; the red team attacks a converged artifact _backward_. Embedded rubric R2/R3/R5 updated; the cross-links in `agent-architecture.md` + `plugin-build` follow.

## 0.2.3 — 2026-06-04

- **`references/authoring/operational-roles.md` — the Maker / Critic / Provocateur pattern.** A new authoring reference for plugins that _orchestrate_ work: the three operational seats (who makes · who reviews · who provokes), the **provoke → make → review → remake** loop, and the one invariant (no seat judges its own work — realized structurally, not as prose). Generalizes the seat model brand-forge ships (Muse · Team · Council): the Maker+Critic split is universal; the **Provocateur** is a domain-named, optional third seat whose value scales with taste-dependence — a Muse for brand, a ritual like the PR-FAQ for product, a bounded spike (often nothing) for convergent engineering. Names the trap this audience hits most — **the Provocateur is not the red team** (the red team attacks a converged artifact, the Critic seat, _backward_; the provocateur generates options _forward_). Ships an embedded triad rubric (R1 seat-separation + R3 provocateur-≠-red-team are `[gate]`s). Cross-linked from `agent-architecture.md` and `plugin-build`.

## 0.2.2 — 2026-06-04

- **`bin/check-manifest-sync.py` — a new CI gate against declared-state drift.** Mechanizes CLAUDE.md's "keep the four descriptions in sync — drift is a defect" rule and the version↔CHANGELOG honesty the manifest validator can't see (it checks each manifest in isolation). Three checks per plugin: **C1** `plugin.json` version equals the latest dated CHANGELOG release and no "Unreleased" section carries shipped content; **C2** every "N commands / N-critic" count stated in the description / README / marketplace entry matches the real `commands/` + `agents/critic-*.md` counts; **C3** every cited `/command` resolves to a file (sibling plugin names and path fragments are excluded). Ships a `selftest` (clean + drifted fixtures, proven to bite) and runs over all six catalog plugins in CI. This is the gate that would have caught the brand-forge v0.1→v0.2 drift the 2026-06-03 red-team found by hand.

## 0.2.1 — 2026-06-03

- **`skill-architecture.md` — "Harden with structure, not prose."** Made explicit the discipline of moving every guarantee into a structure rather than a prose instruction, in order of strength: mechanized check · tool-scope · **embedded output rubric** (named dimensions, `[gate]` labels, an explicit pass threshold) · named verify target · §SelfAudit · anti-pattern gallery · progressive disclosure. The test: _if a requirement is enforced only by a polite sentence, it is not hardened._ The not-thin checklist now requires an embedded output rubric for judgment-heavy output and that every requirement be carried by a structure. Rubrics and gates over traditional prompting.

## 0.2.0 — 2026-06-03

Evolved **skill + agent authoring** — closing the methodology gap that was producing thin, single-`SKILL.md` skills.

- **`references/authoring/skill-architecture.md`** — the construction methodology (the successor to the standalone `skills-studio`): the five layers (metadata · seed · references · scripts · evals); the required `SKILL.md` seed surface (cold-start mode table, Quick Start, posture, modes, loading manifest, per-mode verify targets, anti-pattern gallery, §SelfAudit, §Teach); size tiers; the `references/` taxonomy with per-file `load-when`/`required-for` frontmatter; the mechanization threshold; voice/posture; and the not-thin checklist. `plugin-build` now builds skills against it.
- **`references/authoring/agent-architecture.md`** — the agent-authoring discipline the plugin lacked: when an agent earns its isolated context (else it's a skill), the role taxonomy (critic · worker · analyst · orchestrator · actor), tool-scope minimal-sufficiency + the lethal trifecta, the in-agent trust boundary, persona design, isolation/memory, and the council orchestration pattern.
- **`references/rubrics/agent-fit.md`** — the scoring face (8 dimensions; tool-scope/trifecta + loader-rule are `[gate]`). Registered in `rubric-manifest.json`; `plugin-evaluate` loads it when a plugin bundles agents.
- Wired into `plugin-build` (new first principle: _components are authored to depth, not stubbed_; the author/edit sub-modes read the new docs) and cross-linked from `frontmatter.md` (the field contract → the structure methodology).

## 0.1.0 — 2026-06-02

Initial release as a **plugin**. plugins-factory was re-cast from a single mega-skill into a self-contained Claude Code plugin, authored by (and against) its own standard — the dogfood test of the tool. Re-shaped through the five plugin primitives for component-fit:

- **Commands** — six thin, typed entry points (`/plugin-author`, `/plugin-carve`, `/plugin-edit`, `/plugin-score`, `/plugin-critique`, `/plugin-promote`) that set mode + posture and route to a skill or the council, without re-containing the methodology.
- **Skills** — split by posture: `plugin-build` (the maker — author/carve/edit) and `plugin-evaluate` (the judge — score/critique/promote, carrying the untrusted-target trust boundary). Both draw on one shared standard.
- **Agents** — the 9-critic council promoted from prose personas to **isolated parallel agents** (`critic-boris-c … critic-david-f`) plus a `plugin-council` orchestrator that fans them out and runs the cross-critic synthesis; `carve-analyst` (the composition-graph fan-out worker) retained.
- **Hook** — an advisory `validate_plugin.py hook` on `plugin.json` / `marketplace.json` writes (surfaces manifest/layout/path smells, never blocks).
- **Shared spine (`references/`)** — the 9-dimension rubric library, the 5 foundation↔rubric pairs, `plugin-architecture.md`, `carve-method.md`, the authoring bridge, and the critic prompt corpus (`eval-prompts.md`), referenced by both skills via `${CLAUDE_PLUGIN_ROOT}`.
- **Bin** — `validate_plugin.py` (plugin + marketplace static validators, `selftest`, and the advisory `hook` mode), `check-foundations-coverage.py`, and `reference-lint.py` (fails on doc/command references that don't resolve on disk).

**Decision A (self-contained):** the four cross-cutting rubrics that score P1/P7/P8/P9 (`cold-start-orientation`, `skills-authoring`, `skill-extensibility`, `security-and-scope-containment`) are **co-located** from `skills-studio` rather than referenced across the install boundary — zero `../` cross-plugin paths, zero `dependencies`. (Future: promote the shared critics + cross-cutting rubrics to a foundation plugin both studios depend on, once skills-studio is also packaged.)

Status **draft, N=0 empirical applications** — every rubric dimension is a falsifiable hypothesis until applied to ≥3 real plugins. Build-time red-team (full 9-critic panel, given it bundles a hook and is a meta/orchestrator plugin) returned **CONDITIONAL**; all Critical/Major findings folded — every council agent tool-scoped to read-only (closing the P9 trifecta), `scripts/`→`bin/` drift and dead persona pointers fixed, hook invocation + injection-framing hardened, and a `reference-lint.py` + CI workflow added to gate the regression class. Structural items (council-calibration eval, dimension MECE audit) tracked in ROADMAP. See `reviews/2026-06-02-plugin-red-team.md`.
