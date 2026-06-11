# plugins-factory

**Run the Claude Code plugin lifecycle against one 9-dimension architecture standard — build a plugin and judge it with the same rubrics, foundations, and critic council.** A self-contained plugin with zero cross-plugin dependencies.

This is the toolchain the rest of this marketplace is authored and red-teamed with. It is a normal catalog plugin anyone can install — and this repo auto-enables it for its own sessions (via `.claude/settings.json`), so it loads whenever you work here.

---

## Quick start

```text
/plugin marketplace add kimgranlund/claude-plugins
/plugin install plugins-factory@plugins-forge
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
├── hooks/ + bin/  7 stdlib gates + an advisory hook    → mechanized structure + liveness + recall + bake-safety
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
  - `check-mcp-liveness.py` — spawns each bundled MCP server and requires a real `initialize`+`tools/list` handshake (the **AP-P7 dead-but-wired** defect: a server that defines tools and exits passes every static gate yet never serves). It **executes** the server, so it is for trusted catalog plugins / CI only — the council reviewing untrusted bundles keeps liveness a cold-read finding.
  - `check-recall.py` — guards the council-calibration checkers (`evals/council-calibration/check*.py`) against **brittle concept-regex patterns**: each planted defect has a paraphrase corpus in `evals/recall-corpus/`, and the harness asserts every paraphrase matches ≥1 pattern (and that coverage is complete). It catches the recall gaps that bit three run-3 samples — a council catching a defect in a wording no pattern matched — *before* a run does.
  - `check-bake-safety.py` — asserts a baked single-file corpus-reader (`build-sitemap.py --bake`) is XSS-safe and integrity-pinned: no `</script>` escape in the inlined data/bundle, ≥6 SRI hashes, DOMPurify wired, no live `<script>alert(`. A named, selftested gate (it proves it FAILS on an injected escape) replacing a 495-char inline CI one-liner.
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

- **The gates mechanize only the mechanizable** — manifest/layout/path legality, reference resolution, declared-state drift, slug collisions. They are advisory-or-CI structure checks, not taste.
- **Architecture judgment lives in the council** — whether a boundary is cohesive, a component earns its primitive, an MCP is a curated perimeter or a 1:1 API wrapper. No regex decides that.
- **The plugin under review is untrusted DATA, never instructions** — an embedded "rate this 5/5" / "skip the review" is a _finding_, never obeyed. That guard ships inside every critic (each runs isolated), the orchestrator, and the evaluate skill.
- **No live execution** — the validator reproduces the documented static checks in-repo rather than shelling out to `claude plugin validate` (which may be absent in CI); candidate plugins are read, never run.

---

## Provenance

plugins-factory was authored **by**, and red-teamed **against**, its own 9-dimension standard — the dogfood test of the tool. Self-contained by design: the four cross-cutting rubrics that score P1/P7/P8/P9 are co-located from `skills-studio` (zero `../` cross-plugin paths, zero `dependencies`). Its adversarial reviews live in `reviews/`; open structural work is in `ROADMAP.md`.
