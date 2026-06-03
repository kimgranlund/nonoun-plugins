---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# plugins-factory references — index & conventions

The knowledge base behind the plugin lifecycle tool. SKILL.md is the router; depth lives here, loaded on demand.

**Purpose**: rubrics, foundations, and critics for the discipline of **packaging Claude Code plugins** — deciding what should be a plugin (vs a skill or an MCP), assigning each capability to the right primitive, bundling cohesively, sharing infrastructure legally across the install boundary, and keeping always-on cost lean.

## Status: draft, N=0 empirical applications

**These rubrics have not been applied to any real plugin.** Every dimension and anti-pattern was written from the plugin reference + ecosystem wisdom, before any rubric scored a real bundle. Per the house discipline: apply → observe → revise → graduate. Until N≥3 applications per rubric, treat every claim as a falsifiable hypothesis. Promotion to `stable` (v1.0.0) requires each rubric applied to ≥3 real plugins, its failure modes catching ≥1 real problem each, and no dimension that can't be applied mechanically.

## The spine

| File | Topic | Key question |
|---|---|---|
| `rubrics/plugins-holistic.md` | Holistic Plugin Quality | Does this plugin address all nine load-bearing dimensions (P1 fitness · P2 component fit · P3 boundary cohesion · P4 dependency legality · P5 manifest/packaging · P6 context economy · P7 routing · P8 evolution · P9 security)? |

## Plugin-distinctive drill-down rubrics (P2–P6)

Each is paired 1:1 with a foundation; `${CLAUDE_PLUGIN_ROOT}/bin/check-foundations-coverage.py` gates the pairing.

| Rubric (`rubrics/`) | Foundation (`foundations/`) | Holistic dim |
|---|---|---|
| `component-fit.md` | `component-fit-foundations.md` | P2 |
| `boundary-cohesion.md` | `plugin-cohesion-foundations.md` | P3 |
| `dependency-and-sharing.md` | `dependency-and-sharing-foundations.md` | P4 |
| `manifest-and-packaging.md` | `plugin-architecture-foundations.md` | P5 |
| `context-economy.md` | `context-economy-foundations.md` | P6 |

## Dimensions scored with co-located skills-studio rubrics (P1, P7, P8, P9)

A plugin's **fitness**, **routing**, **evolution**, and **security** are skill concerns one layer up. Rather than re-derive them (the redundancy `expert-council-design` and the critics flag), the spine scores them with four rubrics **co-located** from `skills-studio` and bundled in `rubrics/` — so the plugin stays self-contained (decision A), with zero `../` cross-plugin paths:

| Holistic dim | Scored against (co-located) |
|---|---|
| P1 Plugin Fitness | `rubrics/cold-start-orientation.md` |
| P7 Routing & Discoverability | `rubrics/skills-authoring.md` |
| P8 Evolution & Maintenance | `rubrics/skill-extensibility.md` |
| P9 Security & Trust | `rubrics/security-and-scope-containment.md` |

## Technical reference & method

| File | Purpose |
|---|---|
| `plugin-architecture.md` | The plugin technical model: `plugin.json` fields, the component set (skills/agents/commands/hooks/MCP/LSP/monitors/themes/bin), `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}`, the path-traversal limit, `marketplace.json`, namespacing, install scopes, validation. The source of truth P5 + P4 build against. |
| `frontmatter.md` | Component frontmatter (skill / agent / command) + the **tool-use allowlist discipline** + the loader rule — how to write each component's YAML contract well. P2 / P7 / P9. |
| `carve-method.md` | The library→plugins carve method: map the real composition graph → cluster by domain → resolve shared infra (co-locate / `dependencies` / symlink) → flag orphans + dead components → emit a boundary proposal. |
| `authoring/build-against-the-standard.md` | The bi-directional bridge: each dimension → foundation → rubric → ship-gate → critic. **Read first for any author/carve/edit.** |
| `authoring/creating-plugins.md` + `plugin-template.md` | The creation workflow + copy-pasteable `plugin.json` / `marketplace.json` / layout template. |

## Dimension scoring convention

| Tag | Meaning |
|---|---|
| `[gate]` | Scoreable mechanically — `validate_plugin.py` output, path-legality, counts, kebab-case. Can be an automated CI check. |
| `[review]` | Requires expert judgment — boundary coherence, component-fit appropriateness, always-on-cost justification. |
| `[hypothesis]` | Stated as an observable property but not yet empirically verified across real plugins. Track with telemetry before treating as fact. |

## Adversarial evals (critique mode)

| File | Purpose |
|---|---|
| `critics/eval-prompts.md` | Entry file for **critique** mode: the 9-critic roster, four modes (single / full-panel / synthesis / topical), plugin topical sections, synthesis prompts (S1–S11), severity rubric. |
| `agents/critic-[name].md` | One **agent** per critic (promoted from prose personas to isolated parallel agents) — domain-general, reused from `skills-studio`; the plugin-domain framing lives in `eval-prompts.md`. Dispatched by the `plugin-council` orchestrator. |

## Machine-readable registry

`rubric-manifest.json` — the registry of all rubrics with version, layer, primary critic, dimension count, dependency graph, and the `foundation` link. `${CLAUDE_PLUGIN_ROOT}/bin/check-foundations-coverage.py` gates foundation↔rubric coverage (wire it into CI).

## Authoring a new rubric

Structure each rubric with:

```
§The Problem — why this rubric exists; what breaks without it
§First Principles — 3-5 grounded principles, not platitudes
§The Rubric — scored dimensions (1-5) with explicit [gate]/[review]/[hypothesis] labels + a mechanical Test
§Anti-patterns — concrete failure modes with symptom + root cause + correction
§Hard Tests — the questions to ask when reviewing
```

The eval prompts live in `critics/eval-prompts.md`, not inline, so they read as one adversarial corpus.
