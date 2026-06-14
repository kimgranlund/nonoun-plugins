# agent-ops

**Author, operate, and review full-spectrum agentic systems — and the repos they live in.** The operations-and-architecture counterpart to the build plugins: it knows how to design agent loops and teams, judge what a running workflow is like to drive, keep a repo's agent-facing memory honest, and review a codebase's architecture.

> **Status: 0.1.12 — carved from four mature skills, now with live retrieval.** Five skills, a 12-critic council, six `/ops-*` commands, an advisory doc-hygiene hook, five gates (`audit-history.py` · `check_blueprint.py` · `check-sourcing.py` · `check-self-contained.py` · `doc-hygiene`), and the **`repo-memory` MCP** (per-instance read-only retrieval over a repo's agent docs + `.brain/audit-history/` ledger). Made self-contained (zero cross-plugin paths, enforced by a gate) and red-teamed with the `plugins-factory` council (CONDITIONAL → folded → APPROVED). See [ROADMAP.md](ROADMAP.md).

## Quick start

```text
/plugin marketplace add kimgranlund/claude-plugins
/plugin install agent-ops@nonoun-plugins
```

**Example prompts** — cold-start in plain language (each routes to the matching `/ops-*` command):

- *"I'm picking up an agentic repo — orient me: what's the system, and where are the gaps?"* → `/ops-orient`
- *"Design the loop and control plane for an overnight refactoring agent — pick a topology and wire termination, verification, and a budget."* → `/ops-loop`
- *"Review my workflow's agentic UX — what's it actually like to drive? Trust, control, observability, reversibility."* → `/ops-ux`
- *"Audit this repo's AGENTS.md and docs for staleness, drift, and orphans."* → `/ops-audit`
- *"Review this codebase's architecture and give me a cascade-ranked refactor backlog."* → `/ops-review`
- *"Run the agentic council on our orchestration blueprint — named practitioners, parallel and isolated."* → `/ops-council`

## What it covers — two seats × two surfaces

|  | Build / author | Operate / review |
| --- | --- | --- |
| **The agent** | `agent-loops` — design & wire the loop/team mechanism (builder seat) | `agentic-ux` — score the running workflow's UX (operator seat) + the council |
| **The repo** | `repo-ops` — author & maintain the doc/memory surface | `repo-review` — audit code architecture → a refactor backlog |

- **Agent loops & teams** — 11 topologies (Ralph · plan-execute · ReAct/Reflexion · evaluator-optimizer · orchestrator-workers · auto-research · debate · self-improving · spec-driven · async) + the router + the control plane (termination · verification · context · budget · durability) + a 14-field Orchestration Blueprint with a mechanical validator.
- **Agentic-workflow UX** — the operator seat: trust, control, observability, steerability, reversibility, autonomy, across the workflow lifecycle — scored by an 8-dimension rubric + a 6-dimension architecture rubric + a named-practitioner council.
- **Repo memory & docs** — AGENTS.md-canonical with thin pointers, the canonical files (README · CHANGELOG · ROADMAP · PLAN · ADRs · ARCHITECTURE · postmortems), ~16 audit patterns (stale / orphan / redundant / drift / token-waste), the five promises, and a queryable audit ledger.
- **Code-architecture review** — the 6-wave Discover → Audit → Synthesize → Adversarial → Polish pipeline → a cascade-ranked refactor backlog (3 P0 / 3 P1 / 6 P2 / ∞ P3) + a tier-1 patterns doc.

## Shape (the five-primitive model)

| Primitive | agent-ops instance |
| --- | --- |
| **Skills** | `agent-ops` (orchestrator) · `agent-loops` · `agentic-ux` · `repo-ops` · `repo-review` |
| **Agents** | a 12-critic **council** + the `agentic-council` orchestrator, fanned out parallel + isolated |
| **Commands** | `/ops-orient · ops-loop · ops-ux · ops-audit · ops-review · ops-council` |
| **Hook** | advisory **`doc-hygiene`** on canonical-file writes (undated docs · entry-file bloat · CLAUDE/AGENTS drift) — reads the written `.md`, prints smell codes (never the file's content) to stderr, exits 0; never blocks |
| **Gates (`bin/`)** | `audit-history.py` (audit ledger: `validate` + `liveness`) · `check_blueprint.py` + `schemas/blueprint.json` (the loop-blueprint validator) · `check-sourcing.py` (council provenance) · `check-self-contained.py` (the de-repo invariant) · `doc-hygiene` (`selftest`) — all stdlib, all in CI |
| **MCP** | **`repo-memory`** — per-instance, read-only retrieval over a repo's agent memory (5 task-level tools: list / search / fetch / outline / read-audit-ledger), scoped to one dir via the `corpus_dir` userConfig; mirrors brand-forge's `brand-corpus` + product-forge's `product-corpus` MCPs |

## The council (12 named critics, three sub-councils)

- **UX & Quality** — Amelia W. · Sarah G. · Geoffrey L. · Karri S.
- **Architecture & Utility** — Walden Y. · Harrison C. · Mitchell H. · the MCP / tool-perimeter lens
- **Agentic-systems builders** — Boris C. · Garry T. · Andrej K. · Simon W.

Each critic is a lens distilled from a real, widely recognized software / AI-agent engineering practitioner; the display names are obscured to `First L.`, and the attributions, bios, and sources live in a git-ignored `agents/.name-map.md` (kept out of the repo by design). Living practitioners are sourced observable-public-only. The verbatim quotes were **verified by hand** (web-fetch) against each practitioner's public work; separately and mechanically, `check-sourcing.py` gates that every critic carries a source signal — it does not itself verify a quote's accuracy (only a human can).

## Provenance

Carved and **de-repo'd** from four mature global skills — `ops-repo`, `arch-repo-review`, `core-agent-loops`, `core-agentic-ux-best-practices` — then made self-contained (cross-references rewired to the plugin's own siblings; ~200 external references neutralized; scripts moved to `bin/`). Authored and red-teamed with [`plugins-factory`](https://github.com/kimgranlund/claude-plugins/tree/main/plugins-factory). **Honesty preserved:** the agentic-UX scores ship **directional** (calibration-sample-light), not authoritative — `[gate]` dimensions are the only mechanically verifiable layer. Likewise `repo-review`'s tiering is **expert judgment by construction** (architecture quality isn't mechanically checkable): it ships discipline — HITL gates, the adversarial wave, file:line citations — not a gate script.
