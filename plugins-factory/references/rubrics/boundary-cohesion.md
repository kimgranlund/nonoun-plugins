---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Boundary Cohesion — One Coherent Job, Bounded on Both Sides

The drill-down for holistic **P3**. A plugin's scope is bounded on both sides: too broad (kitchen sink) taxes every install; too narrow (fragment) scatters one workflow across pieces that only work together. This rubric scores whether the bundle is one coherent job with rich internal granularity.

Theory: `../foundations/plugin-cohesion-foundations.md`. Primary critic: **Steve Yegge** (platform vs product, granularity).

---

## §The Problem

"It validates" says nothing about whether the bundle is _one thing_. A plugin can be a perfectly-packaged junk drawer (a team's whole toolbox under one name, taxing every install) or a perfectly-packaged fragment (one-third of a workflow that silently needs two siblings). Both pass `validate`; both fail their users. Cohesion is the judgment manifest validation can't make.

---

## §First Principles

1. **One coherent job; every component serves it.** The job fits one sentence or the scope is wrong.
2. **Bounded on both sides.** Kitchen-sink (too broad) and fragment (too narrow) are equal failures.
3. **Internal granularity ≠ external fragmentation.** Ship many well-named skills _inside_ one domain plugin; don't scatter them across micro-plugins.
4. **Split by job-to-be-done, not by org chart.** The unit of cohesion is the toggle, not the team.
5. **`dependencies` is the release valve** for genuinely separable concerns — not a patch for over-fragmentation.

---

## §The Rubric

### D1 — One-Sentence Job `[review]`

Does the plugin's purpose fit one sentence, with every component serving it?

| Score | Evidence |
| --- | --- |
| **5** | The job states in one sentence ("turn brand intent into a production design system"). Every bundled component demonstrably serves it. |
| **4** | One-sentence job; one component is tangential but defensible within the domain. |
| **3** | The job needs two sentences, or 1–2 components belong to an adjacent job. |
| **2** | The job can't be stated without "and also" clauses spanning distinct domains. |
| **1** | No statable job — components share a directory, not a purpose. |

**Go deeper**: `../foundations/plugin-cohesion-foundations.md` §"The unit of cohesion"; cross-check P1 (Fitness). **Test** (one-sentence test): write the job in one sentence. Do the components fit without "and also" clauses? Forced clauses = D1 ≤ 3.

---

### D2 — No Kitchen Sink (upper bound) `[review]`

Is the scope free of cross-cutting breadth that taxes every install?

| Score | Evidence |
| --- | --- |
| **5** | Scope is one domain. No cross-cutting "all our tooling" breadth. A user who enables it wants the whole capability, not 10% of it. |
| **4** | Coherent domain, slightly broad at one edge, but the toggle still makes sense. |
| **3** | The bundle spans two adjacent jobs that a meaningful population would want separately. |
| **2** | Cross-cutting scope (a team's whole toolbox); most installers use a fraction, paying standing context for the rest. |
| **1** | A monolith — unrelated capabilities fused under one name, the "monolithic plugin problem." |

**Go deeper**: `../foundations/plugin-cohesion-foundations.md` §"Upper bound"; cross-check P6 (the breadth _is_ the always-on cost). **Test** (split test): would a meaningful population want exactly half this plugin and never the other half? Yes = D2 ≤ 3.

---

### D3 — No Fragmentation (lower bound) `[review]`

Does the plugin function as a unit, without silently requiring an undeclared sibling?

| Score | Evidence |
| --- | --- |
| **5** | The plugin is a complete, usable unit. If it builds on another plugin, that's a declared `dependencies` edge — not an unstated assumption that a sibling is co-installed. |
| **4** | Functions as a unit; one soft dependency on a sibling is declared. |
| **3** | Works mostly alone but assumes a sibling is present for a secondary path, undeclared. |
| **2** | Only functions when a specific sibling is also enabled, with nothing declared — a fragment masquerading as standalone. |
| **1** | A shard of a workflow scattered across plugins that each do nothing alone. |

**Go deeper**: `../foundations/plugin-cohesion-foundations.md` §"Lower bound"; cross-check P4 (D4, the undeclared-sibling dependency). **Test** (merge test): does the plugin only function with a specific sibling co-enabled, undeclared? Yes = D3 ≤ 2 (declare the edge or merge).

---

### D4 — Internal Granularity `[review]`

Inside the domain, is the structure appropriately granular — many well-named components, not one mega-skill?

| Score | Evidence |
| --- | --- |
| **5** | Rich internal structure: the domain's work is split into well-named skills/agents/commands, each doing one thing, all serving the plugin's job. Granularity matches the work. |
| **4** | Good internal structure; one component does slightly too much but is still navigable. |
| **3** | Internal structure is coarse — a couple of mega-skills where several focused ones would route better. |
| **2** | The whole domain crammed into one or two sprawling skills; the router can't distinguish sub-capabilities. |
| **1** | One monolithic skill labeled as a plugin — no internal granularity at all. |

**Go deeper**: `../foundations/plugin-cohesion-foundations.md` §"Internal granularity ≠ external fragmentation". **Test**: are the domain's distinct sub-capabilities separate, well-named components — or fused into one? Fused = D4 ≤ 2.

---

### D5 — Split Axis Is the Job `[review]`

Was the plugin boundary drawn by job-to-be-done, not by org chart or convenience?

| Score | Evidence |
| --- | --- |
| **5** | The boundary follows a coherent job a user toggles as a unit. Where the domain contains genuinely distinct jobs (generate vs serialize vs reference vs diagnose), they are _separate_ plugins, each independently useful. |
| **4** | Boundary follows the job; one edge case bundled by convenience rather than job. |
| **3** | Boundary partly follows team/repo structure rather than user job. |
| **2** | Boundary drawn by "what we happen to own" — distinct jobs fused, or one job split arbitrarily. |
| **1** | No discernible axis; the boundary is accidental. |

**Go deeper**: `../foundations/plugin-cohesion-foundations.md` §"The unit of cohesion is the job-to-be-done". **Test**: name the _job_ the boundary follows. If the answer is a team/repo name rather than a user job-to-be-done, D5 ≤ 2.

---

### D6 — Right-Sized via `dependencies` `[review]`

Are genuinely separable concerns split and re-composed through `dependencies` — not fused, not scattered?

| Score | Evidence |
| --- | --- |
| **5** | Separable concerns that are each independently useful are _separate_ plugins with declared `dependencies` edges. Lockstep concerns stay in one plugin. The composition is deliberate, neither over-fused nor over-scattered. |
| **4** | Mostly right-sized; one concern could be split with a dependency edge but isn't causing harm fused. |
| **3** | Either a separable concern is fused in (mild kitchen-sink) or a lockstep concern is split out (mild fragment). |
| **2** | Clear mis-sizing: independently-useful capabilities fused, or tightly-coupled ones scattered, with no `dependencies` discipline. |
| **1** | No sizing logic — fusion and scatter both present. |

**Go deeper**: `../foundations/plugin-cohesion-foundations.md` §"The discriminating tests"; cross-check P4 (legal dependency mechanisms). **Test**: for each major concern, is it independently useful (→ candidate split with a `dependencies` edge) or lockstep (→ keep fused)? Mismatches = D6 ≤ 3.

---

## §Anti-patterns

### AP-BC1 — The kitchen-sink monolith

**Symptom**: One plugin bundles a whole team's tooling (D2 ✗); high always-on cost (P6 ✗); a "which capability?" routing tax (P7 ✗). **Root cause**: Scoping by org boundary instead of by toggle/job. **Correction**: Split by job-to-be-done; ship internal granularity inside each domain plugin; `dependencies` for separable concerns.

### AP-BC2 — The fragment that needs three siblings

**Symptom**: A plugin does nothing alone; it silently assumes two siblings are co-installed (D3 ✗, D6 ✗). **Root cause**: Over-fragmentation — one workflow split into pieces. **Correction**: Merge the pieces into one coherent plugin, or declare the `dependencies` edges if each piece is genuinely useful alone.

### AP-BC3 — The mega-skill "plugin"

**Symptom**: The whole domain is one sprawling skill (D4 ✗); the router can't distinguish sub-capabilities (P7 ✗). **Root cause**: Treating "plugin" as "one big skill" rather than a bundle with internal granularity. **Correction**: Decompose into well-named focused skills inside the one plugin.

### AP-BC4 — The org-chart boundary

**Symptom**: The plugin boundary mirrors a team or repo, fusing distinct user jobs (D5 ✗). **Root cause**: Scoping by ownership, not by what the user toggles together. **Correction**: Redraw the boundary around the job-to-be-done.

---

## §Hard Tests

1. **The one-sentence test** (D1): does the job fit one sentence with no "and also" clauses?
2. **The split test** (D2): would a meaningful population want exactly half and none of the other?
3. **The merge test** (D3): does it only work with an undeclared sibling co-enabled?
4. **The granularity test** (D4): are distinct sub-capabilities separate well-named components or one fused blob?
5. **The axis test** (D5): does the boundary follow a user job or a team/repo name?
