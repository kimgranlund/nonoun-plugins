# Changelog

All notable changes to **agent-ops** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.1.11] — 2026-06-11

- **P0-1 from the real-repo audit closed — the `repo-review` skill now has behavioral coverage.** The audit (`reviews/2026-06-11`) flagged that agent-ops gates its agentic *council* but not its `repo-review`/`repo-ops` *skills* — a hole in "every claim is gated," in the plugin that audits other repos. New `evals/repo-review-calibration/`: `build-seeded-repo.py` writes a 4-file synthetic repo with **6 planted architectural smells** (god module · naming drift · declared-vs-actual contradiction · duplicated logic · command injection · no agent-memory/tests), built on demand so the catalog ships no intentional-vulnerability files; `check.py` scores a review transcript's catch-rate. Cold baseline through the real `repo-review` pipeline: **6/6 smells caught** (and it found *more* than planted — an emergent SQL-injection P0, an SSRF sink), the adversarial wave held command-injection at P0 against a "dead code → demote" challenge, and it honestly reported no Tier-1 patterns rather than padding. CI re-scores the baseline + rebuilds the fixture; the checker is recall-gated by `check-recall.py`. The audit's headline doctrine gap is closed.

## [0.1.10] — 2026-06-11

- **First real-repo audit recorded — `repo-review` run on its own host repo, validating the directional rubric** (`reviews/2026-06-11-claude-plugins-audit.md`). The full pipeline (Discover → Rubric → Audit → Synthesize → Adversarial → Polish) applied cold to the `plugins-forge` marketplace produced a tailored 9-dimension rubric (3.7/5 headline), a cascade-ranked 3-P0/3-P1/6-P2 backlog with before/after sketches, a 5-pattern Tier-1 preservation contract, and a **rubric-validation payload** moving the rubric from *directional* to *recorded*. The adversarial wave did real work (promoting `gen-index.py`'s missing selftest P1→P0; sharpening the eval-ROI finding) — direct evidence the method's most-skippable steps (the repo-type fork + the adversarial pass) are where the value is. The audit honestly surfaced agent-ops's own gaps (its review/ops surfaces lack behavioral coverage; the eval ceremony is over-invested) and named two method gaps (no native "doctrine-coverage" dimension; the single-agent adversarial-isolation caveat). Headline factual claims were spot-checked before recording (P0-2/P1-1 confirmed; one P3 struck as a false positive). Documents-only — the audited repo was not edited.

## [0.1.9] — 2026-06-11

- **The `repo-memory` MCP shipped** — filling agent-ops's v0.2 MCP slot and completing the catalog's MCP story (all three maker-class plugins now ship corpus/memory retrieval). `bin/repo-memory-mcp.py` is a minimal JSON-RPC 2.0 stdio server (stdlib-only, 3.8+) giving **per-instance, read-only** retrieval over a repo's agent-facing memory — 5 task-level tools: `list_repo_memory`, `search_repo_memory`, `fetch_doc`, `outline_doc`, and `read_audit_ledger` (the agent-ops differentiator — surfaces the `.brain/audit-history/` self-healing ledger that `audit-history.py` maintains). Wired via `.mcp.json` + the new `corpus_dir` userConfig (`REPO_MEMORY_DIR`); unset, the tools return a clear "configure corpus_dir" message rather than failing. It mirrors brand-forge's `brand-corpus` and product-forge's `product-corpus` MCPs exactly — same MCP-as-curated-perimeter pattern, same `_safe()` traversal/symlink/prefix-sibling guard, same read-only-with-`isError` contract — and excludes build/vendor noise dirs (`.git`, `node_modules`, …) while keeping `.brain/`, capped at 300 files so a large repo can't flood the surface. Ships a `selftest` (path-guard + noise-dir exclusion + audit-ledger smoke over a synthetic repo) wired into CI, and is covered by the catalog's MCP-liveness gate (now 3 live MCPs). Descriptions updated in sync across plugin.json / marketplace.json / README.

## [0.1.8] — 2026-06-11

- **Council-calibration checkers hardened against brittle concept-regex** (the new plugins-factory `check-recall.py` gate). Both agentic checkers gained patterns for legitimate council wordings their regex would otherwise miss in a real run — `check.py` (Nightshift): "decide locally" / "conflict at merge" (A1), "the judge's own approval — circular" (A2), "measures stall, not convergence" (A3), "widens the egress perimeter" (A4), "archaeology, not a rewind" (A5), "a round counter, not a decision trace" (A7); `check-monolith.py` (OmniDesk): "fused into one agent", "share one brain" (MO1), "context dumped, not engineered" (MO3). This is the same recall-gap class that scored two run-3 samples low before being fixed reactively — now caught proactively. Both checkers' recorded baselines + rate samples re-score full with **zero regression**; the paraphrase corpora live in `plugins-factory/evals/recall-corpus/` and are CI-asserted.

## [0.1.7] — 2026-06-10

- **Monolith council-calibration promoted to N=3** (two further cold runs through the single-agent-architecture slice proxy): **7/7 planted defects in 3/3 runs, REBUILD ×3**, the §3 5/5 directive classified as an injection finding and refused in all 18 isolated contexts, and the Walden↔Harrison tension collapsing into agreement in every run. Run 3 earned its keep by exposing a **checker-recall miss** (Mitchell caught MO6 as "form, not correctness / grades its own homework", which the pattern keyed on "for**mat**" missed); `check-monolith.py`'s MO6 set was widened (`form|format`, "grades its own homework", "lint pass wearing") and all three runs re-score 7/7 with no regression — the instrument calibrating itself, mirroring the over-fleet fixture's run-3 A4/A6 fix. With Nightshift already at N=3, both agent-ops fixtures are now N=3 at 100%. README rate table updated.

## [0.1.6] — 2026-06-10

- **Second council-calibration fixture — a monolith god-agent** (`fixtures/monolith-support-agent-blueprint.md` + `check-monolith.py`). Where "Nightshift" fails by over-parallelization (a 12-worker fleet on a coupled surface), "OmniDesk" fails by the **opposite** — one monolithic agent with 40 tools, the lethal trifecta in a single context. Like Nightshift it **passes `check_blueprint.py` clean (0 fail)**; its defects are pure judgment: no decomposition (MO1), no eval harness (MO2), everything inlined in one window (MO3), a throughput/vanity metric (MO4), the trifecta defended only by prompt-pleading (MO5), a gate that checks format not correctness (MO6). Cold baseline through the single-agent-architecture slice: **7/7 caught, REBUILD (weakest dimension: security/blast-radius), the §3 5/5 directive classified as an injection finding and refused.** Notable: both built-in critic tensions (Walden↔Harrison) *collapsed into agreement*, and the council gave explicit credit to the genuinely-good runner-side harness. CI now re-asserts both fixtures gate-clean and re-scores both baselines. README documents both failure shapes.

## [0.1.5] — 2026-06-10

- **Council-calibration promoted from a single baseline to a catch-rate over N=3 cold runs** — two further isolated-critic runs recorded: **8/8 planted defects caught in 3/3 runs, 18/18 REBUILD verdicts, 18/18 ST5 refusals.** Run 3 earned its keep by exposing an **instrument defect**: it initially scored 6/8 from checker-pattern brittleness (the council had caught both defects in different words — "allowlist self-expansion", "context dumped, not engineered"); `check.py`'s A4/A6 pattern sets were widened and all runs re-score 8/8 with no regression. The README carries the rate table; CI still re-scores the designated baseline.

## [0.1.4] — 2026-06-10

- **Council-calibration eval** (`evals/council-calibration/`) — a planted-defect Orchestration Blueprint fixture ("Nightshift": a 12-worker overnight refactor fleet that **passes `bin/check_blueprint.py` clean** while carrying 7 judgment defects — topology misfit on coupled work, a same-model vibes judge past an available oracle, hollow termination layers, an attacker-extensible egress allowlist, auto-merge-to-main laundered as "reversible", append-everything context, a Ctrl+C kill path for an unattended run — plus an embedded "certify READY-TO-RUN / score it 5/5" probe), a concept-matching transcript checker, a protocol, and a recorded baseline. Run cold, a six-critic architecture-led slice caught **8/8** planted defects, returned a unanimous REBUILD, **all six independently flagged the embedded instruction (ST5)** — and the run exercised the council's built-in Walden Y. ↔ Harrison C. tension exactly as designed. CI re-asserts both halves every push: the fixture stays gate-clean (the necessary-not-sufficient split stays demonstrable) and the baseline stays caught.

## [0.1.3] — 2026-06-05

- **Critic identities obscured** — slugs now `critic-<first>-<initial>`, display names `First L.`, practitioner bios moved to a git-ignored `agents/.name-map.md`; roster + tensions section updated; council behavior unchanged.

## [0.1.2] — 2026-06-04

- **The aspiration is now a precondition of making — a soft gate.** Before a Builder-seat maker converges, the **design principles** the work is reasoned toward must be at least lightly named; a loop or workflow reasoned toward no declared philosophy drifts to the category average. The attractor here is a written design-principle set (Anthropic's three — maintain simplicity · prioritize transparency · carefully craft the agent-computer interface — plus `agent-loops`' control-plane-first thesis for loops, and the operator-seat principles — trust · control · observability · steerability · reversibility — for UX), not a convened agent. `/ops-loop` and `/ops-ux` gain a **"name the pull first"** line before the skill hand-off; `agent-loops` adds a **Design principles / aspiration** row at the head of its Step 1 — Ingestion table; `agentic-ux` adds a **name the design philosophy** step at the head of its Decomposition. It is a _soft_ blocker throughout — cleared by **naming** a provisional, revisable direction, never by stopping. Mirrors the generalized rule in plugins-factory `operational-roles.md`.

## [0.1.1] — 2026-06-04

- **Quoted `argument-hint` frontmatter** across all commands — normalizes the value to a string (YAML was parsing the unquoted `[..]` as a flow list) and satisfies plugins-factory's new frontmatter flow-collection lint. No behavior change.

## [0.1.0] — 2026-06-03

Initial release — the operations-and-architecture plugin for agentic systems and the repos they live in. Carved and de-repo'd from four mature global skills into one self-contained catalog plugin.

### Added

- **5 skills** — `agent-ops` (orchestrator: classify the meta-task → route) + `agent-loops` (builder-seat loop mechanism design: 11 topologies, the router, the control plane, the 14-field Orchestration Blueprint), `agentic-ux` (operator-seat UX: the 8-dim + 6-dim rubrics, lifecycles, techniques), `repo-ops` (the repo-as-brain memory layer: AGENTS.md-canonical, ~16 audit patterns, doc-type standards, the five promises), `repo-review` (the 6-wave architecture audit → cascade-ranked refactor backlog).
- **12-critic council** — the `agentic-council` orchestrator + UX & Quality (Amelia W. · Sarah G. · Geoffrey L. · Karri S.), Architecture & Utility (Walden Y. · Harrison C. · Mitchell H. · the MCP lens), and agentic-systems builders (Boris C. · Garry T. · Andrej K. · Simon W.) — all read-only (`Read, Grep, Glob`) and trust-bounded.
- **6 commands** — `/ops-orient · ops-loop · ops-ux · ops-audit · ops-review · ops-council`.
- **Advisory hook** — `bin/doc-hygiene` (canonical-doc smells: undated / entry-bloat / drift / no-frontmatter; `PostToolUse` on `Write|Edit`, never blocks).
- **5 gates** — `audit-history.py` (the audit ledger: `validate` + `liveness`), `check_blueprint.py` + `schemas/blueprint.json` (the loop-blueprint validator), `check-sourcing.py` (council provenance), `check-self-contained.py` (the de-repo invariant — no source-skill / foreign-namespace leftovers in the functional surface), `doc-hygiene` (canonical-doc smells; reads the written file, prints codes not content, exits 0). Stdlib-only Python; all wired into CI.

### Provenance & honesty

- De-repo'd from `ops-repo`, `arch-repo-review`, `core-agent-loops`, `core-agentic-ux-best-practices`: cross-references rewired to the plugin's own siblings, ~200 external references neutralized, the two scripts moved to `bin/`, self-contained (zero cross-plugin paths).
- The full agentic-UX council (all 8 source critics) is **activated** — and the source's **directional / calibration-sample-light** caveat is preserved (scores are structured judgment, not verification).
- The living-practitioner critics are sourced observable-public-only; verbatim quotes verified before ship; `check-sourcing.py` gates the provenance.

### Planned (v0.2)

- A read-only MCP for per-instance retrieval of a repo's memory / audit history.
