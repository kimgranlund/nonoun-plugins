# Changelog

All notable changes to **agent-ops** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.1.0] — 2026-06-03

Initial release — the operations-and-architecture plugin for agentic systems and the repos they live in. Carved and de-repo'd from four mature global skills into one self-contained catalog plugin.

### Added

- **5 skills** — `agent-ops` (orchestrator: classify the meta-task → route) + `agent-loops` (builder-seat loop mechanism design: 11 topologies, the router, the control plane, the 14-field Orchestration Blueprint), `agentic-ux` (operator-seat UX: the 8-dim + 6-dim rubrics, lifecycles, techniques), `repo-ops` (the repo-as-brain memory layer: AGENTS.md-canonical, ~16 audit patterns, doc-type standards, the five promises), `repo-review` (the 6-wave architecture audit → cascade-ranked refactor backlog).
- **12-critic council** — the `agentic-council` orchestrator + UX & Quality (Amelia W. · Gibbons · Litt · Karri S.), Architecture & Utility (Yan · Chase · Mitchell H. · the MCP lens), and agentic-systems builders (Cherny · Tan · Karpathy · Willison) — all read-only (`Read, Grep, Glob`) and trust-bounded.
- **6 commands** — `/ops-orient · ops-loop · ops-ux · ops-audit · ops-review · ops-council`.
- **Advisory hook** — `bin/doc-hygiene` (canonical-doc smells: undated / entry-bloat / drift / no-frontmatter; `PostToolUse` on `Write|Edit`, never blocks).
- **5 gates** — `audit-history.py` (the audit ledger: `validate` + `liveness`), `check_blueprint.py` + `schemas/blueprint.json` (the loop-blueprint validator), `check-sourcing.py` (council provenance), `check-self-contained.py` (the de-repo invariant — no source-skill / foreign-namespace leftovers in the functional surface), `doc-hygiene` (canonical-doc smells; reads the written file, prints codes not content, exits 0). Stdlib-only Python; all wired into CI.

### Provenance & honesty

- De-repo'd from `ops-repo`, `arch-repo-review`, `core-agent-loops`, `core-agentic-ux-best-practices`: cross-references rewired to the plugin's own siblings, ~200 external references neutralized, the two scripts moved to `bin/`, self-contained (zero cross-plugin paths).
- The full agentic-UX council (all 8 source critics) is **activated** — and the source's **directional / calibration-sample-light** caveat is preserved (scores are structured judgment, not verification).
- The living-practitioner critics are sourced observable-public-only; verbatim quotes verified before ship; `check-sourcing.py` gates the provenance.

### Planned (v0.2)

- A read-only MCP for per-instance retrieval of a repo's memory / audit history.
