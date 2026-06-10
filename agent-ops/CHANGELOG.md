# Changelog

All notable changes to **agent-ops** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

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
