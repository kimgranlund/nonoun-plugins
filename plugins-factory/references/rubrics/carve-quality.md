---
date: 2026-06-12
status: draft
version: "0.1.0"
---

# Carve Quality — Scoring the Partition, Not the Plugins

The rubric for a **carve** — a library→plugins boundary proposal (the output of `/plugin-carve` / `references/carve-method.md`) — scored **as one artifact**. `plugins-holistic` scores each plugin a carve _produces_; this scores the **partition itself**: did it map the real coupling, cut at the right seams, resolve every cross-boundary share legally, account for every node, and emit something `author` can actually build? A carve can yield individually-excellent plugins and still be a bad carve (it split a `$ref`-coupled pipeline and wired it with `../`), or score every plugin's P1/P3/P4 in isolation and miss that the _set_ has a dependency cycle or a silently-dropped skill. Those are set-level properties — invisible to per-plugin scoring, and what this rubric exists to catch.

Theory: `../carve-method.md` (the 7-step method) · `../foundations/plugin-cohesion-foundations.md` (granularity) · `../foundations/dependency-and-sharing-foundations.md` (legal sharing). Primary critic: **Steve Y.** (plugin granularity, monolith-vs-fragment, marketplace as platform); **Scott W.** secondary for the D3/D4 legality axis. Fan-out worker: `../../agents/carve-analyst.md`.

---

## §How to score a carve

A carve is a **proposal/report**, usually scored _before_ any plugin is built — so the evidence is the carve document (the plugin table, the dependency graph, the orphan/dead callouts, the per-plugin self-checks), read against the **input skill list** it claims to partition. Two rules:

- **Score the set, then compose with `plugins-holistic`.** This rubric grades the partition; each proposed plugin is then scored on its own with the holistic rubric. A carve that is set-level excellent (D1–D7 high) can still propose a plugin that individually scores P2/P6 low, and vice versa — report both, don't let one stand in for the other.
- **`[gate]` dimensions cap the whole carve.** D3 (shared-infra legality) is the make-or-break axis the method names: a single surviving `../` cross-boundary reference caps the carve at **≤ 2** regardless of how elegant the partition is, exactly as P4 caps a plugin. D4 (a dependency cycle) and D5 (a silently-dropped node) cap likewise — an unsound or incomplete partition is not shippable, however well-clustered.

---

## §The Problem

A carve that looks clean on the page is the dangerous one. Cluster a library by its README layers and prefixes and you get a tidy plugin table — that severs the pipeline coupled through a shared type registry (a coupling no `peer_skills` array ever named), then references that registry with `../shared-types/...`. It validates per-plugin. It ships **dangling references the instant it's installed**. Manifest validation can't see this, and scoring each resulting plugin can't see it either — the defect is in the _seams between_ plugins and in the _accounting across_ them. Carve quality is the judgment that lives at the set level: not "is each plugin good?" but "is this the right set of plugins, cut at the right places, that survives the install boundary as a whole?"

---

## §First Principles

1. **The catalog lies; the coupling graph tells the truth.** Org charts group by name and layer; carves must cut by coupling — including the hidden `$ref`/shared-type edges that bind skills declaring zero peers.
2. **Cut at the joints.** A boundary belongs where coupling is _thin_. Severing a dense cluster is the cardinal error; whatever you sever, you then have to legally re-connect.
3. **`../` is never a sharing mechanism.** Every cross-boundary reference must resolve when the directory is copied _alone_ into the cache. Co-locate, declare in `dependencies`, or symlink-in-marketplace — those three, never a traversal path.
4. **Account for every node.** A reader diffs the input list against the proposal and finds zero unexplained disappearances. Orphans, bridges, and corpses are _named_, never dropped.
5. **A carve recommends; it must be buildable.** The deliverable's job is to let `author` build each plugin without re-deriving its boundary. An analytically-correct carve that emits no buildable proposal is unfinished.
6. **Granularity lives inside boundaries, not across them.** Many well-named skills in one domain plugin is right; one workflow scattered across N must-co-install plugins is fragmentation.

---

## §The Rubric

### D1 — Graph Fidelity `[review]`

Did the carve map the **real** composition graph — declared peers, routing pointers, **and** the hidden shared-type/`$ref` edges — rather than the catalog's org chart?

| Score | Evidence |
| --- | --- |
| **5** | All three edge classes extracted and sourced (peer / routing / `$ref`-shared-type), with the shared-infra nodes identified by cross-cluster in-degree. The proposal cites the `$ref` coupling that no `peer_skills` array declares. |
| **4** | Peer + routing edges mapped; shared-type coupling found, but one `$ref` edge is under-annotated. |
| **3** | Declared peers + routing mapped; the shared-type/`$ref` layer is partial — a real coupling is mentioned but not traced to its boundary impact. |
| **2** | Graph is essentially the catalog (layers/prefixes) plus declared peers; hidden `$ref` coupling missed. |
| **1** | No coupling graph — clusters asserted from names/README alone. |

**Go deeper**: `../carve-method.md` §1; the **catalog-carve** anti-pattern (AP-CQ1). **Test** (hidden-edge test): for each proposed cluster, does its internal `$ref`/shared-type coupling appear in the graph — or only its `peer_skills`? Coupling visible only in schemas = D1 ≤ 2.

---

### D2 — Cuts at the Joints `[review]`

Does every proposed boundary fall on a **thin** seam — few peer/routing/`$ref` edges crossing it — rather than severing a dense coupling cluster?

| Score | Evidence |
| --- | --- |
| **5** | Every boundary lands where the graph is sparse; dense sub-graphs (esp. `$ref`-coupled pipelines) stay intact within one plugin. The edge-cut at each boundary is small and every crossing edge is named for resolution in D3. |
| **4** | Boundaries follow the coupling; one boundary severs a modest edge, justified and resolved. |
| **3** | Mostly cuts at joints; one boundary splits a coupled pair that a reader would expect to toggle together. |
| **2** | A boundary severs a dense cluster (a multi-stage pipeline bound by a shared schema) — high edge-cut, the pipeline now spans plugins. |
| **1** | Boundaries cut across the densest coupling in the graph; the partition fights the structure. |

**Go deeper**: `../carve-method.md` §3; `../foundations/plugin-cohesion-foundations.md`. **Test** (edge-cut test): count the peer/routing/`$ref` edges crossing each boundary. A boundary slicing through a high-in-degree `$ref` cluster = D2 ≤ 2 (and forces a D3 resolution that is often the sign two clusters are really one).

---

### D3 — Shared-Infra Legality `[gate]`

Does **every** cross-boundary reference and shared-infra node have a resolution that survives the install boundary — co-locate, `dependencies`, or marketplace-symlink — with **zero `../`**?

| Score | Evidence |
| --- | --- |
| **5** | Every shared item is resolved by the right one of the three legal mechanisms, stated per item: co-locate (one dominant consumer, small/stable), `dependencies` (≥2 consumers, plugin-worthy → a foundation plugin), or symlink (single file, same marketplace). No `../` anywhere. |
| **4** | All shares resolve legally; one resolution choice is defensible-but-suboptimal (co-located where a `dependencies` edge would be cleaner). |
| **3** | Every share has a mechanism, but one is under-specified (named "shared" without saying which of the three resolutions). No `../`. |
| **2** | A cross-boundary reference is left as a path/`$ref` with no legal resolution — or one `../` traversal survives. **(Gate: any surviving `../` caps the carve here.)** |
| **1** | Sharing is pervasively `../`-based — clean on disk, dangling across the cache on install (AP-P2 at carve scale). |

**Go deeper**: `../carve-method.md` §4 (make-or-break); `../foundations/dependency-and-sharing-foundations.md`. **Test** (install test): for every cross-boundary reference, does it resolve when the directory is copied _alone_ into the version cache? Any `no` = **D3 ≤ 2, and the carve is capped there** regardless of D1/D2/D6/D7.

---

### D4 — Dependency-Graph Integrity `[gate]` `[review]`

Is the proposed dependency graph **acyclic**, with foundation plugins as sinks and every edge carrying the **right mechanism**?

| Score | Evidence |
| --- | --- |
| **5** | The graph is a DAG; foundation/shared plugins are sinks (depended-on, depend on nothing); every edge names its mechanism (`dependencies` vs symlink vs co-location) and points the right way (domain → foundation). |
| **4** | Acyclic and well-directed; one edge's mechanism is implied rather than stated. |
| **3** | Acyclic, but a foundation plugin carries an outward dependency it shouldn't, or an edge's direction/mechanism is ambiguous. |
| **2** | A near-cycle (mutual dependency dressed as two edges), or foundation/domain layering is muddled. |
| **1** | A dependency **cycle** — plugins that can't be installed or versioned independently. **(Gate: a cycle caps the carve.)** |

**Go deeper**: `../carve-method.md` §7(b). **Test** (acyclicity test): topologically sort the proposed graph. A cycle, or a "foundation" plugin with an outbound edge, = D4 ≤ 2.

---

### D5 — Node Accounting `[gate]`

Is **every** input node accounted for in the output — member, orphan, bridge, or dead — with **zero silent drops**?

| Score | Evidence |
| --- | --- |
| **5** | A reader can diff the input skill list against the proposal and find every node: each is a named member, or explicitly an orphan (with a recommended home), a bridge (both pulls stated + an ownership/`dependencies` recommendation), or dead (flagged for cleanup before packaging, not bundled). Zero unexplained disappearances. |
| **4** | Every node accounted for; one orphan named but its recommendation is thin. |
| **3** | Nearly complete; one node appears in the input but its disposition is implicit rather than stated. |
| **2** | A node is silently absent from the proposal — present in the input, unexplained in the output. |
| **1** | Multiple silent drops, or a retired/dead skill bundled into a plugin (a corpse). **(Gate: a silent drop caps the carve.)** |

**Go deeper**: `../carve-method.md` §6. **Test** (diff test): set-difference the input skill list against the union of (members ∪ orphans ∪ bridges ∪ dead) in the proposal. Non-empty = D5 ≤ 2.

---

### D6 — Granularity Calibration `[review]`

Is the **number and size** of proposed plugins right — between the kitchen-sink (too few, too broad) and fragmentation (too many, must-co-install) failure modes — with granularity _inside_ boundaries?

| Score | Evidence |
| --- | --- |
| **5** | Each plugin is one coherent toggle with rich internal granularity (many well-named skills); no plugin is a team's whole toolbox, and no single workflow is scattered across plugins that only work together. The plugin count fits the library's distinct jobs. |
| **4** | Well-calibrated; one plugin is slightly broad or one split is borderline, but the toggles still make sense. |
| **3** | One mild mis-sizing — a separable concern fused in (mild kitchen-sink) or a lockstep concern split out (mild fragment). |
| **2** | Clear mis-sizing across the set: a kitchen-sink plugin, or a workflow fragmented across N must-co-install plugins with no `dependencies` discipline. |
| **1** | The whole partition is mis-grained — one monolith, or a cloud of single-skill plugins for one workflow. |

**Go deeper**: `../carve-method.md` §5; `../foundations/plugin-cohesion-foundations.md`; cross-check each plugin's P3/P6. **Test** (sizing test): for each plugin, is it independently useful as one toggle (✓) — or does its one-sentence job need "…assuming sibling X is also enabled" (fragment) or "…and also" clauses spanning domains (kitchen-sink)? Either = D6 ≤ 3.

---

### D7 — Buildable Proposal `[review]`

Does the output give `author` what it needs to build each plugin — without re-deriving the boundary?

| Score | Evidence |
| --- | --- |
| **5** | The layered proposal ships: the plugin table (job · members · hub · depends-on · **today has / should gain**), the acyclic dependency graph with mechanisms, the orphan/dead callouts verbatim, and a per-plugin P1/P3/P4 self-check. `author` can pick up any row and build it. |
| **4** | All present; the "should gain" completion column is thin for one plugin. |
| **3** | The boundaries and members are clear, but the proposal omits one buildability aid (no hub named, or no per-plugin self-check) — `author` must re-derive it. |
| **2** | Boundaries decided but the output is a bare cluster list — no hubs, no depends-on mechanisms, no completion guidance. Analytically right, operationally unusable. |
| **1** | No actionable proposal — clusters asserted with nothing `author` can build from. |

**Go deeper**: `../carve-method.md` §7. **Test** (buildability test): take one proposed plugin row and try to hand it to `author`. Missing its job, hub, depends-on mechanism, or cross-boundary resolutions = D7 ≤ 2.

---

## §Anti-patterns

### AP-CQ1 — The catalog carve

**Symptom**: Clusters mirror the README's layers/prefixes; the `$ref`/shared-type coupling was never mapped (D1 ✗), so a `$ref`-bound pipeline is split across plugins (D2 ✗). **Root cause**: Scoring the org chart instead of the coupling graph. **Correction**: Map the real graph including shared-type edges (method §1) _before_ clustering; let dense `$ref` sub-graphs anchor single plugins.

### AP-CQ2 — The `../` shared dependency

**Symptom**: The partition is clean on disk and every plugin validates, but sharing is wired with `../shared-types/...`; it dangles the instant a plugin is installed alone (D3 ✗). **Root cause**: Treating a monorepo-relative path as a sharing mechanism. **Correction**: Co-locate, declare in `dependencies` (promote the shared item to a foundation plugin), or symlink within the marketplace — never `..` (method §4).

### AP-CQ3 — The silent drop

**Symptom**: A skill present in the input does not appear anywhere in the proposal — not as a member, orphan, bridge, or dead (D5 ✗). **Root cause**: Clustering kept only the nodes that fit; the misfits evaporated. **Correction**: Account for every node explicitly (method §6); a misfit is an _orphan_ to home or a _corpse_ to retire, never an omission.

### AP-CQ4 — The un-buildable proposal

**Symptom**: Boundaries are decided and defensible, but the output is a bare cluster list — no hubs, no depends-on mechanisms, no "should gain" (D7 ✗). **Root cause**: Stopping at the analysis, skipping the deliverable. **Correction**: Emit the layered proposal with the per-plugin build aids (method §7) so `author` can act without re-deriving boundaries.

### AP-CQ5 — The cyclic / fragment carve

**Symptom**: Two "foundation" plugins depend on each other (D4 ✗), or one workflow is split across plugins that each do nothing alone and declare no `dependencies` (D6 ✗). **Root cause**: Over-fragmentation without a dependency discipline. **Correction**: Break the cycle (one is the sink), or merge the fragments / declare the edges so the graph is a DAG with foundations as sinks.

---

## §Hard Tests

1. **The hidden-edge test** (D1): does every cluster's internal `$ref`/shared-type coupling appear in the graph, or only its `peer_skills`?
2. **The edge-cut test** (D2): how many peer/routing/`$ref` edges cross each boundary? A boundary slicing a dense `$ref` cluster fails.
3. **The install test** (D3, gate): does every cross-boundary reference resolve when the directory is copied _alone_ into the cache? Any `../` caps the carve.
4. **The acyclicity test** (D4, gate): does the dependency graph topologically sort, with foundation plugins as sinks?
5. **The diff test** (D5, gate): does the input skill list minus (members ∪ orphans ∪ bridges ∪ dead) come out empty?
6. **The sizing test** (D6): does any plugin's one-sentence job need an "…assuming sibling X" (fragment) or "…and also" (kitchen-sink) clause?
7. **The buildability test** (D7): can `author` build a proposed plugin from its row alone, without re-deriving its boundary?
