---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# The library → plugins carve method

**`carve` answers one question: given a pile of skills (or a whole library), what coherent domain plugins should they become — and how does shared infrastructure survive the install boundary?** It is not a sorting exercise. The catalog lies: it groups by name and layer, while the real coupling lives in `peer_skills`, "use X" routing pointers, and — the part that breaks carves — shared `$ref`/type wiring that no `peer_skills` array ever mentions. A clean-looking carve that splits two skills coupled through a shared schema, then references that schema with `../`, ships **dangling references on first install**. This method exists to prevent exactly that.

Carve is scored by applying **P1** (each proposed plugin's fitness), **P3** (each boundary's cohesion), and **P4** (every shared-infra resolution's legality) _across the whole set_. P4 is the make-or-break axis — see step 4. The proposal **as one artifact** is then scored against **`rubrics/carve-quality.md`** — the set-level rubric for the partition itself (graph fidelity · cuts-at-the-joints · shared-infra legality · dependency-graph integrity · node accounting · granularity calibration · buildability), where a surviving `../`, a dependency cycle, or a silently-dropped node each caps the whole carve.

> **Read order**: this file → `authoring/build-against-the-standard.md` (for the P1/P3/P4 gates the proposal must pass). For each plugin the carve proposes, `author` (`creating-plugins.md` + `plugin-template.md`) builds it.

---

## When to carve

| Signal | Carve? |
| --- | --- |
| "What plugins should these N skills become?" / "package our library for distribution" | **Yes** — this is the job. |
| A library has outgrown one-skill-at-a-time consumption; users want to enable _capabilities_, not pick 40 skills | **Yes.** |
| "Package _this one_ skill-set into _a_ plugin" (boundary already decided) | No — that's `author`. |
| "Should this be a plugin or a skill?" (single capability) | No — that's a P1 fitness call inside `author`. |

Carve produces a **proposal**, not a packaged plugin. It decides boundaries and shared-infra resolution; `author` then builds each plugin, and `skills-refactor` executes any library restructuring the carve implies (a rename, a merge). Carve never silently moves or deletes a skill — it _recommends_.

---

## The method (7 steps)

### 1. Map the REAL composition graph — not the catalog

The catalog (README, layer tables) is an org chart; the carve needs the _coupling_ graph. Extract three edge classes, because each reveals a different kind of "these toggle together":

| Edge class | Where it lives | What it means |
| --- | --- | --- |
| **Declared peers** | `skill.json` `peer_skills` / `depends_on` / `composition.peer` arrays; `SKILL.md` "Peers with…" prose | The author _says_ these are related. |
| **Routing pointers** | `SKILL.md` / `description` "use X for Y", "delegates to X", "hands off to X" | One skill names another as the next move. |
| **Shared-type / `$ref` wiring** | `schemas/*.json` `$ref` targets; a shared type registry (`meta-type-registry`); `shared-types`; identical schema filenames across skills; a `## Typed Interface` referencing a sibling's `output.json` | **The hidden coupling.** Tightly-coupled skills often declare ZERO peers but are bound through a shared schema. |

The third class is the one that breaks carves. **Example**: a UI pipeline (`ui-schema-ui` → `ui-build-tokens` → `ui-build-components` → `ui-verify-*`) may show sparse `peer_skills`, yet every stage `$ref`s the same type registry — they are one coupled cluster _through the types_, invisible to a peer-array sweep. Miss it and you split the pipeline across plugins, then wire it with `../meta-type-registry/...` — a P4 break.

**Use a fan-out subagent for the sweep.** Dispatch `agents/carve-analyst.md` (one analyst per skill, or per cluster for large libraries): each reads its skill's `skill.json` + `SKILL.md` + `schemas/`, and returns `{skill, peers[], routing_pointers[], ref_targets[], hub_or_leaf, is_shared_infra}`. Merge the returns into one edge list. Fan-out beats a serial read because the graph is wide and each node's extraction is independent — exactly the `agent`-for-parallel-fan-out case (P2).

Output of step 1: a directed multigraph — nodes = skills, edges typed (peer / routing / ref), each edge annotated with its source so step 4 can act on it.

### 2. Classify hubs vs leaves; find bridges + shared infrastructure

Walk the graph and label each node:

- **Hub** — broad, multi-mode, orchestrator, or high in-degree (many skills route into it / `$ref` it). Hubs anchor clusters; a domain plugin usually has exactly one hub as its named entry point. _(e.g. an orchestrator skill, a `_-studio`.)\*
- **Leaf** — narrow, linear, single-purpose, low degree. Leaves attach to the hub whose job they serve.
- **Cross-cluster bridge** — a node with strong edges into _two+_ would-be clusters. A bridge is a carve decision: does it belong to one cluster (and the other depends on its plugin), or is it itself shared infra?
- **Shared infrastructure** — a node many clusters reach into (high cross-cluster in-degree), especially via `$ref`. Type registries, shared schema libraries, a cross-cutting convention skill. These do **not** belong to one domain plugin — they become a _foundation plugin_ others `dependencies`-declare (step 4).

Heuristic: **in-degree from ≥3 distinct clusters, mostly via `$ref` → shared infra, not a cluster member.**

### 3. Cluster by DOMAIN / JOB (toggle-together), not by org chart

Group nodes into candidate plugins using one test, applied per candidate cluster:

> **The toggle test**: would a user enable or disable this _whole set_ as one coherent capability?

If yes, it's a plugin boundary. Cluster by the **job-to-be-done**, not by naming prefix or library layer. A shared `ui-` prefix does not make one plugin; a shared _job_ ("compose a themed component system") does. Conversely, two differently-prefixed skills that a user always wants together belong in one plugin.

What clustering is **not**:

- Not "one plugin per layer" (the Decompose/Compose/Audit layers cross-cut domains).
- Not "one plugin per naming prefix" (prefix is a convention, not a capability).
- Not "one plugin per team" (org chart → kitchen-sink, AP-P1).

Edges guide clustering: a dense sub-graph (many internal peer/routing/ref edges, few crossing out) is a natural cluster. A skill with edges split evenly across two clusters is a _bridge_ — resolve it in step 4.

### 4. For EACH shared-infra item, decide the LEGAL resolution — make-or-break

**This is the step a carve lives or dies on.** Every edge that crosses a proposed plugin boundary, and every shared-infra node, MUST get a resolution that survives the install boundary. Installed plugins are copied into a version-keyed cache and **cannot reference files outside their own directory** — so a `../shared-types/foo.json` path or a cross-plugin `$ref` is correct in the monorepo and **broken the instant it's installed**. There are exactly three legal resolutions, and `../` is never one of them:

| Resolution | When | How it resolves at install |
| --- | --- | --- |
| **Co-locate** | The shared item has one dominant consumer; duplicating it is cheaper than a dependency. Small, stable schemas. | The file physically lives inside the plugin root; nothing crosses the boundary. |
| **Declare in `dependencies`** | The shared item is consumed by ≥2 plugins and is itself plugin-worthy (a type registry, a shared methodology). | The depended-on plugin is installed too; the manifest names it: `"dependencies": [{"name":"core-types","version":"~1.0.0"}]`. Skill-level, not file-path-level. |
| **Symlink within the marketplace** | A _file_ (not a whole plugin) is shared across sibling plugins _in the same marketplace_. | The symlink is **dereferenced/copied** at install — the target's content lands inside each plugin's cache copy. Same-marketplace only. |
| ~~`../` traversal path~~ | **Never.** | **Breaks at install.** Resolves in the repo, dangles in the cache. This is AP-P2. |

Decision order per shared item:

1. One dominant consumer + small/stable? → **co-locate** (tightest consumer).
2. Consumed broadly + plugin-worthy? → promote to a **foundation plugin**, others `dependencies`-declare it.
3. A single file, same marketplace? → **symlink** (dereferenced at install).
4. Otherwise reconsider the boundary — a shared item you can't legally resolve is often a sign two clusters are actually one.

**The trap**: a carve that is clean on disk but uses `../` for sharing _looks_ done and ships dangling refs. Every cross-boundary reference must be re-asked against "does this resolve when the directory is copied _alone_ into the cache?" (the install test, P4). If the answer is no, the carve is not done.

### 5. Decide granularity — between kitchen-sink and fragmentation

Two failure modes bound the right answer:

- **Kitchen-sink (AP-P1)**: one plugin = a whole team's tooling. High always-on cost (P6), a "which capability?" routing tax (P7), and a user who wants a third of it pays for all of it. Symptom: the one-sentence job needs "and also…" clauses.
- **Fragmentation**: one workflow split across N plugins that only function when all N are installed. Symptom: plugin A's job sentence contains "…assuming B and C are also enabled," with no `dependencies` declaration.

The resolution is almost always: **ship internal granularity (many well-named skills) inside one domain plugin.** A domain plugin with 12 skills, 2 agents, and a command is _one_ toggle and _one_ coherent job — that is correct, not bloated. Granularity belongs _inside_ the boundary (the skills), not _across_ boundaries (don't make 12 single-skill plugins for one workflow).

The split test (P3): _would a user ever want exactly half this plugin and none of the other half?_ If yes → split. _Does this plugin only work with an undeclared sibling?_ If yes → either merge or declare the dependency.

### 6. Handle orphans + dead components EXPLICITLY — no silent drops

A carve sweep surfaces nodes that fit no cluster. Every one is **named in the output**, never quietly omitted:

| Class | Definition | Carve action |
| --- | --- | --- |
| **Orphan** | A live, healthy skill that no cluster's job claims. | **Name it.** Recommend: a home cluster (if a weak edge exists), a standalone single-skill plugin (if genuinely independent and shareable), or "keep unbundled for now." Never drop it from the report. |
| **Bridge (unresolved)** | A node with strong edges into two clusters. | State both pulls; recommend ownership + a `dependencies` edge, or promotion to shared infra. |
| **Dead / retired** | A skill marked retired, superseded, or with no live inbound edges and stale content. | **Flag for cleanup before packaging** — hand to `skills-refactor` to retire. Do NOT bundle it; a dead component in a plugin is a P4 finding (dead-weight) and a maintenance liability (P8). |

The rule: **a carve report accounts for every node.** A reader can diff the input skill list against the proposal and find zero unexplained disappearances.

### 7. Emit the OUTPUT — a layered boundary proposal

The deliverable is a **layered proposal**: foundation/shared plugins (depended-on) listed first, domain plugins after, then the dependency graph and the orphan/dead callouts.

**(a) The plugin table** — one row per proposed plugin:

| Plugin | One-sentence job | Member skills | Hub | Depends-on | Today has / should gain |
| --- | --- | --- | --- | --- | --- |
| `core-ui-types` | Shared design-system type registry consumed by the UI plugins. | `meta-type-registry`, `shared-types` | `meta-type-registry` | — | has: schemas · should gain: `validate_types` command |
| `ui-pipeline` | Compose a themed, token-driven component system from a UI schema. | `ui-schema-ui`, `ui-build-tokens`, `ui-build-theme`, `ui-build-components`, `ui-verify-*` | `ui-orchestrator` | `core-ui-types` (`dependencies`) | has: skills · should gain: a `/compose` command + a perf hook |

The **"today has / should gain"** column drives the `author` follow-up: it names where the plugin currently has only skills but a _command_ (user-named entry point, P7), _hook_ (a must-run gate, P2), _agent_ (fan-out, P2), or _MCP_ (external perimeter, P2) would complete it.

**(b) The dependency graph** — which plugins depend on which, and _by what mechanism_ (`dependencies` vs symlink vs co-location). Must be acyclic. Foundation plugins are sinks (depended-on, depend on nothing).

```text
core-ui-types ◄── ui-pipeline
core-ui-types ◄── ui-audit         (both via `dependencies`)
```

**(c) Orphan / dead callouts** — the step-6 table, verbatim, in the report.

**(d) Per-plugin P1/P3/P4 self-check** — for each proposed plugin: one-sentence job (P1), split/merge verdict (P3), and every cross-boundary reference's resolution (P4). No proposal ships with an unresolved `../`.

### Publish — assemble the library's `marketplace.json`

Once the proposal is built into real plugin directories, **assemble the multi-plugin marketplace and validate the wiring in one mechanical step** — don't hand-write the `marketplace.json`:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/bin/assemble-marketplace.py assemble <library-dir> \
  --name <kebab-marketplace-name> --owner "<owner>" [--allow-external <name> …] --out <library-dir>/.claude-plugin/marketplace.json
```

It discovers every `<library-dir>/*/.claude-plugin/plugin.json`, emits one entry per plugin (`source: ./<dir>`, `tags` from `keywords`, `category` from a `category` field), and **fails unless the carve is legal**: every plugin manifest validates, the assembled marketplace validates (including the cross-plugin **agent-name collision** check — D-13, so a carved library can't ship two councils that silently drop a critic), and the **`dependencies` graph resolves and is acyclic** (every dep is in the library or `--allow-external`-vouched; foundation plugins are sinks — the carve-quality D4 invariant, mechanized). This is the publish gate the proposal's step-7(b) dependency graph is checked against; a surviving `../`, an unresolved dep, or a cycle stops the publish, not the install.

---

## Worked micro-example (4 skills → 2 plugins + a shared dep)

**Input**: four skills — `tokens-extract` (pull tokens from a design), `tokens-build` (compute token math), `tokens-audit` (find drift/orphans), `token-schema` (the DTCG type definitions every other skill `$ref`s).

**Step 1 (graph)**: `peer_skills` show `extract↔build` and `build↔audit`. Routing: `extract` says "for math, use `tokens-build`." The hidden edge: all three `$ref` `token-schema/schemas/dtcg.json` — `token-schema` has **zero declared peers** but in-degree 3 via `$ref`. The analyst flags it `is_shared_infra: true`.

**Step 2 (classify)**: `tokens-build` is the hub (multi-mode, both other skills route through it). `token-schema` = shared infra (in-degree from every node, all `$ref`).

**Step 3 (cluster)**: `extract + build + audit` toggle together as one job ("manage this project's design tokens"). `token-schema` is not part of that _job_ — it's the substrate. → one domain cluster + one infra node.

**Step 4 (legal resolution)**: `token-schema` is consumed by all three and is itself reusable → **promote to a foundation plugin** `design-token-types`; the domain plugin declares `"dependencies": [{"name":"design-token-types","version":"~1.0.0"}]`. **Not** `../token-schema/...` — that would break on install.

**Step 7 (output)**:

| Plugin | Job | Members | Hub | Depends-on | Should gain |
| --- | --- | --- | --- | --- | --- |
| `design-token-types` | DTCG type registry shared by token tooling. | `token-schema` | `token-schema` | — | a `validate_tokens` command |
| `design-tokens` | Extract, build, and audit a project's design tokens. | `tokens-extract`, `tokens-build`, `tokens-audit` | `tokens-build` | `design-token-types` (`dependencies`) | a `/tokens` command + a CI drift **hook** |

Graph: `design-token-types ◄── design-tokens`. Orphans: none. Dead: none.

Two plugins, one legal dependency, zero `../`. A user enables `design-tokens` (and the dep comes with it), toggles it as one capability, and nothing dangles in the cache. That is a carve that survives install.

---

## Carve anti-patterns (recap)

| Anti-pattern | Symptom | Correction |
| --- | --- | --- |
| **Catalog carve** | Clustered by README layer/prefix; missed the `$ref` coupling. | Map the real graph incl. shared-type edges (step 1) before clustering. |
| **`../` shared dep** (AP-P2) | Clean on disk, dangling on install. | Co-locate / `dependencies` / symlink — never `..` (step 4). |
| **Kitchen-sink** (AP-P1) | One plugin = a team's tooling; "and also…" job. | Split by job; internal granularity inside each (step 5). |
| **Fragment carve** | One workflow across N must-co-install plugins, undeclared. | Merge, or declare the `dependencies` edge (step 5). |
| **Silent drop** | A skill vanished between input and proposal. | Account for every node — orphan/bridge/dead, all named (step 6). |
| **Bundled corpse** | A retired skill packaged into a plugin. | Flag for `skills-refactor` cleanup _before_ packaging (step 6). |
