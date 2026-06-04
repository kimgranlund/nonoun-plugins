# agent-ops — ROADMAP

The build plan and live state. Carve signed off 2026-06-03.

## Scope (signed off)

A single, **full-spectrum plugin for authoring, operating, and reviewing agentic systems and the repos they live in.** It knows how to author all sorts of agentic systems and the nuance of context and harness — agent loops & teams, the control plane (termination · verification · context · budget · durability), harness & context engineering, agentic-workflow UX — and how to manage the repo those agents work in (memory/docs, the canonical files, architecture review, house-cleaning). Carved and **de-repo'd** from four mature global skills: `ops-repo`, `arch-repo-review`, `core-agent-loops`, `core-agentic-ux-best-practices`. Self-contained — zero cross-plugin paths.

## The five-primitive shape

| Primitive | agent-ops instance |
| --- | --- |
| **Skills (5)** | `agent-ops` (orchestrator) · `repo-ops` · `repo-review` · `agent-loops` · `agentic-ux` |
| **Agents** | the named-practitioner **council** (≥12) + an `agentic-council` orchestrator, fanned out parallel + isolated |
| **Commands** | thin `/ops-*` entry points — `orient · audit · review · loop · agentic-ux · council` |
| **Hook** | advisory doc-hygiene lint on canonical-file writes (staleness / format / drift) — never blocks |
| **Gates (`bin/`)** | `audit-history.py` (repo audit ledger: `validate` + `liveness`) · `check_blueprint.py` + `schemas/blueprint.json` (the 14-field loop-blueprint validator) · `check-sourcing.py` (living-critic provenance, adapted from product-forge) |
| **MCP** | none in the sources → **planned for v0.2** |

## Skills

- **`agent-ops`** (orchestrator) — classify the meta-task (author a loop · operate/score a workflow's UX · audit the doc/memory surface · review the code architecture) → route to the owning skill or the council.
- **`repo-ops`** (from ops-repo) — the repo-as-brain memory layer: AGENTS.md canonical + thin pointers, ~16 audit patterns (stale / orphan / redundant / drift / token-waste), doc-type standards (README · CHANGELOG · ROADMAP · PLAN · ADR · ARCHITECTURE · postmortem), the five promises, the audit ledger.
- **`repo-review`** (from arch-repo-review) — the 6-wave Discover → Audit → Synthesize → Adversarial → Polish pipeline → cascade-ranked refactor backlog (3 P0 / 3 P1 / 6 P2 / ∞ P3) + tier-1 patterns doc.
- **`agent-loops`** (from core-agent-loops) — builder-seat loop mechanism design: 11 topologies (Ralph · plan-execute · ReAct/Reflexion · evaluator-optimizer · orchestrator-workers · auto-research · debate · self-improving · spec-driven · async) + the router + the control plane + the 14-field Orchestration Blueprint.
- **`agentic-ux`** (from core-agentic-ux-best-practices) — operator-seat UX evaluation: the 8-dimension agentic-UX rubric + the agentic-architecture rubric + lifecycles + techniques. (Honesty preserved: ships **directional** — calibration-sample-light — not authoritative.)

## Council (all source critics activated + builders added)

- **UX & Quality:** Amelia W. · Sarah Gibbons · Geoffrey L. · Karri S.
- **Architecture & Utility:** Walden Y. · Harrison C. · Mitchell H. · (the MCP / tool-perimeter lens)
- **Agentic-systems builders (added per sign-off):** Boris Cherny (Claude Code) · Garry T. (YC) · Andrej Karpathy · Simon Willison

All 8 source critics **activated** (no deferral). Living practitioners: observable-public-only sourcing, verbatim quotes verified, `check-sourcing.py` provenance gate — the product-forge anti-fabrication discipline.

## Build phases

- [x] **0. Scaffold + port** — `plugin.json`, marketplace entry, this ROADMAP; 104 files cp'd from the four skills (SKILL.md + references + rubrics + the two gate scripts + blueprint schema).
- [x] **1. De-repo / self-containment** — neutralize ~10 external skill references (`skills-studio`, `core-mcp-best-practices`, `meta-expert-author`, `ui-audit-*`, `arch-pattern`, `plan-*`, …) → the plugin's own siblings or generalized; cross-skill references rewired to the plugin's own skill names; confirm the scripts are stdlib-only; make the "recommends tooling for the _audited_ repo, not the plugin's own deps" boundary explicit.
- [x] **2. Council** — convert `references/council/eval-as-*.md` personas → `agents/critic-*.md` (trust-boundary block, read-only tools); author the four added builder critics (Cherny · Tan · Karpathy · Willison), sourced; the `agentic-council` orchestrator; **verify every living critic's verbatim quotes** against public sources.
- [x] **3. Orchestrator + commands + hook** — the `agent-ops` orchestrator skill; the `/ops-*` commands; the advisory doc-hygiene hook.
- [x] **4. Gates** — wire `audit-history.py` + `check_blueprint.py` + `blueprint.json`; adapt `check-sourcing.py` for the council; add the gates to CI.
- [x] **5. Validate** — `validate_plugin.py --strict` · `reference-lint.py` · `check-sourcing.py` · script selftests · markdownlint · marketplace — all PASS.
- [x] **6. Red-team** — `plugins-factory` 9-critic council → fold MUSTs → **cut 0.1.0**. Record in `reviews/`.
