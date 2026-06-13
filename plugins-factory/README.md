# plugins-factory

**Run the Claude Code plugin lifecycle against one 9-dimension architecture standard — build a plugin and judge it with the same rubrics, foundations, and critic council.** A self-contained plugin with zero cross-plugin dependencies.

This is the toolchain the rest of this marketplace is authored and red-teamed with. It is a normal catalog plugin anyone can install — and this repo auto-enables it for its own sessions (via `.claude/settings.json`), so it loads whenever you work here.

---

## Quick start

```text
/plugin marketplace add kimgranlund/claude-plugins
/plugin install plugins-factory@nonoun-plugins
```

Build side and judge side, both as thin typed commands:

| Command | Side | What it does |
| --- | --- | --- |
| `/plugin-author` | build | New plugin: intent → component-fit → boundary check → wire manifests → validate → build-time red-team. |
| `/plugin-carve` | build | A skill library → a plugin-boundary proposal (map the composition graph, cluster by domain, resolve shared infra). |
| `/plugin-edit` | build | Targeted fix — a mis-fit component, a kitchen-sink boundary, an illegal `../` dependency, a routing collision. |
| `/plugin-score` | judge | Score a plugin across the nine dimensions, with evidence and the ship-gate it must pass. |
| `/plugin-critique` | judge | Convene the 9-critic council (parallel, isolated) for an adversarial architecture review. |
| `/plugin-promote` | judge | Gate a plugin to its next maturity stage against the dimension thresholds. |

---

## The surface — four primitives over one shared standard

```text
plugins-factory/
├── commands/   6 thin entry points       → build (author·carve·edit) · judge (score·critique·promote)
├── skills/     2 posture skills          → plugin-build (the maker) · plugin-evaluate (the judge)
├── agents/    9 critics + orchestrator + carve-analyst → the parallel, isolated council
├── hooks/ + bin/  10 stdlib gates + an advisory hook   → mechanized structure + liveness + recall + bake-safety + trust-boundary + context-cost + score-record
└── references/   the 9-dimension rubric spine + foundations + authoring methodology
```

- **Commands** route to a skill or the council; they never re-contain the standard.
- **Skills** split by posture: `plugin-build` (author / carve / edit) and `plugin-evaluate` (score / critique / promote, carrying the untrusted-target trust boundary). Both draw on one rubric spine in `references/`.
- **Agents** — the 9-critic council (`critic-boris-c` … `critic-david-f`, each a distilled practitioner lens under an obscured `First L.` display name) + `plugin-council` (the orchestrator that fans them out in parallel isolated contexts and runs the cross-critic synthesis) + `carve-analyst` (the composition-graph fan-out worker). **Every agent is tool-scoped read-only** (`Read, Grep, Glob`) — they review _untrusted_ plugins, so they must not be able to execute.
- **Gates (`bin/`)** — stdlib Python, all run in CI against every catalog plugin:
  - `validate_plugin.py` — manifest / layout / path static validator + the **command↔skill slug-collision** check + a `selftest` + an advisory `hook` mode.
  - `reference-lint.py` — fails on doc/command references that don't resolve on disk.
  - `check-manifest-sync.py` — fails on declared-state drift (version↔CHANGELOG, description count claims, cited commands).
  - `check-foundations-coverage.py` — every dimension foundation maps to exactly one rubric.
  - `check-mcp-liveness.py` — spawns each bundled MCP server and requires a real `initialize`+`tools/list` handshake (the **AP-P7 dead-but-wired** defect: a server that defines tools and exits passes every static gate yet never serves). It **executes** the server, so it **refuses by default** and requires `--trusted-source` (or `PLUGINS_FACTORY_TRUST_EXEC=1`) — the I-12 interlock that makes "trusted catalog / CI only" a code mechanism, not a comment; the council reviewing untrusted bundles keeps liveness a cold-read finding.
  - `check-recall.py` — guards the council-calibration checkers (`evals/council-calibration/check*.py`) against **brittle concept-regex patterns**: each planted defect has a paraphrase corpus in `evals/recall-corpus/`, and the harness asserts every paraphrase matches ≥1 pattern (and that coverage is complete). It catches the recall gaps that bit three run-3 samples — a council catching a defect in a wording no pattern matched — *before* a run does.
  - `check-bake-safety.py` — asserts a baked single-file corpus-reader (`build-sitemap.py --bake`) is XSS-safe and integrity-pinned: no `</script>` escape in the inlined data/bundle, ≥6 SRI hashes, DOMPurify wired, no live `<script>alert(`. A named, selftested gate (it proves it FAILS on an injected escape) replacing a 495-char inline CI one-liner.
  - `check-trust-boundary.py` — asserts every reviewer carries the **untrusted-DATA-never-instructions guard** — the catalog's core safety invariant. The guard can't be centralized (each critic runs isolated), so it's verified present across the whole reviewer surface: each `agents/critic-*.md`, each `agents/*council*.md` orchestrator, and each review-surface skill (`*evaluate*` / `*review*`, incl. agent-ops's `repo-review`). A two-signal presence test keyed on the guard's *assertion* (trust context **and** "data, never instructions to obey") — so incidental security prose doesn't false-pass — with a `selftest` that FAILS on a guard-less critic. Discipline-only across ~66 isolated files until now; a missed guard becomes a CI failure, not a silent regression.
  - `context-cost.py` — the **P6 Context-Economy always-on audit**, the dimension's mechanization (the rubric names it by hand). Measures the standing context tax a plugin charges every session: the eagerly-loaded `description`s of every agent / command / skill (bodies/references load on-invoke, so they're excluded). Reports total + est. tokens + per-category breakdown + the heaviest components; WARNs on a verbose description *dominating* the budget; hard-FAILs only on a >2KB body-in-an-advertisement or an opt-in `--budget` breach (P6 is a judgment, so it exposes cost rather than grading taste). `--with-mcp` spawns each live MCP and folds its served `tools/list` size into the total — the rubric's biggest P6 concern (a 1:1-API-wrapper MCP) — WARNing if the tool-defs dominate (executes servers, so it shares `check-mcp-liveness`'s I-12 interlock: `--with-mcp` refuses without `--trusted-source` while the default static audit stays open). `selftest`-proven, incl. folded-block-scalar parsing + the MCP measurement. Catalog standing cost: ~9.7K tok static / ~10.6K tok with the three live MCPs' tool-defs.
  - `score-record.py` — the judge's **durable D8 audit trail** (I-13). `score`/`promote` produce a 9-dimension scorecard + verdict; without a record it evaporates into chat (no regression diff, `empirical_applications: 0`). This `write`s a **validated** `scores/<plugin>.json` in the `adoption_contract` shape (`rubric-manifest.json`), rejecting every malformed shape (out-of-range/bool score, unknown dimension, un-adopted rubric, bad verdict/date) so a record is well-formed by construction, not hand-written JSON. `--dir` targets a durable location (`${CLAUDE_PLUGIN_DATA}` / the target repo for installed runs, never the cache root). `selftest`-proven; CI validates every committed record. First record: `scores/plugins-factory.json` (this plugin's own self-red-team scorecard).
  - `evals/` — a behavioral suite that builds fixture plugins with known defects and asserts the gates catch each (two council-calibration fixture shapes: `mega-helper` excess + `docs-studio` vacancy/deadness).
- **Hook** — `validate_plugin.py --hook` fires on `plugin.json` / `marketplace.json` writes; it surfaces manifest/layout/path smells and **never blocks**.

Also in `bin/`: **`corpus-reader/`** — a buildless static reader (web components + OKLCH tokens) that turns a generated corpus (a folder of Markdown) into a navigable site. The maker plugins' `*-corpus-export` commands scaffold it via `build-sitemap.py --init`; it is the single source, **vendored** into the consuming plugins (cross-plugin symlinks don't survive install), and `sync-corpus-reader.py` CI-gates the copies — plus the reader's DOMPurify/SRI wiring and its own fingerprint-gated `CHANGELOG.md` — against drift.

There is no MCP: plugins-factory is static-analysis only by design — it reads candidate plugins, it never runs them (the P9 trust-boundary risk).

---

## The standard — nine dimensions

Each dimension has a rubric in `references/rubrics/` and a theory doc in `references/foundations/`:

|  | Dimension | Asks |
| --- | --- | --- |
| **P1** | Plugin Fitness | Is this a real plugin, or a skill wearing a manifest? |
| **P2** | Component Fit | Does each component do the one job that primitive is uniquely for? |
| **P3** | Boundary Cohesion | One domain — neither kitchen-sink nor fragment? |
| **P4** | Dependency Legality | Copy-alone clean — zero `../` escapes, zero absolute paths? |
| **P5** | Manifest & Packaging | `.claude-plugin/` pure; the manifest honest about what ships? |
| **P6** | Context Economy | Worth leaving enabled — is the always-on cost justified? |
| **P7** | Routing & Discoverability | Findable, namespaced, no slug collisions? |
| **P8** | Evolution & Maintenance | Versioned, changelog-honest, no dead components? |
| **P9** | Security & Trust | No bundled lethal trifecta; agents tool-scoped; hooks advisory? |

`[gate]` dimensions (e.g. P4 legality, P9 security) can cap a score regardless of the rest.

---

## Honest scope

- **The gates mechanize only the mechanizable** — manifest/layout/path legality, reference resolution, declared-state drift, slug collisions, trust-boundary-guard _presence_. They are advisory-or-CI structure checks, not taste.
- **Architecture judgment lives in the council** — whether a boundary is cohesive, a component earns its primitive, an MCP is a curated perimeter or a 1:1 API wrapper. No regex decides that.
- **The plugin under review is untrusted DATA, never instructions** — an embedded "rate this 5/5" / "skip the review" is a _finding_, never obeyed. That guard ships inside every critic (each runs isolated), the orchestrator, and the evaluate skill — and `check-trust-boundary.py` now CI-gates that it is actually present in each of them, so a forgotten guard fails the build instead of silently shipping.
- **No live execution** — the validator reproduces the documented static checks in-repo rather than shelling out to `claude plugin validate` (which may be absent in CI); candidate plugins are read, never run.

---

## Provenance

plugins-factory was authored **by**, and red-teamed **against**, its own 9-dimension standard — the dogfood test of the tool. Self-contained by design: the four cross-cutting rubrics that score P1/P7/P8/P9 are co-located from `skills-studio` (zero `../` cross-plugin paths, zero `dependencies`). Its adversarial reviews live in `reviews/`; open structural work is in `ROADMAP.md`.
