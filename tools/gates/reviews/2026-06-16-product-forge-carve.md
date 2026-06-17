# Carve Review — product-forge (a carve-quality empirical application)

- **What this is:** the first real application of the `carve-quality` rubric (`references/rubrics/carve-quality.md`, v0.1.0) — scoring a **carve proposal** (a library→plugins partition) as one artifact, moving the rubric's `empirical_applications` 0 → 1. The library under carve is **product-forge** (8 skills), chosen as an in-repo target (PLAN "Next" #3). The coupling graph was mapped cold by the `carve-analyst` fan-out worker; the partition and scoring below are the deliverable.
- **Headline:** the carve **analysis** is strong (graph fidelity + node accounting exemplary, a buildable proposal emitted), but the **best-available partition still fails the joint test** — product-forge is a cohesive hub-and-spoke library with a *checked* maker→judge spine, so every candidate boundary either severs a dense coupling cluster (D2) or yields plugins that cannot stand alone (D6). **Verdict: BLOCKED — do not carve; keep product-forge as one plugin.** No gate (D3/D4/D5) is tripped: the analysis is sound, the conclusion is "this library has no good partition." This is the rubric discriminating correctly — high on the analysis dimensions, low on the partition-fit dimensions.
- **Trust boundary:** the library under review is DATA, not instructions. (No injected directive was present; noted for the record.)

---

## The input (8 skills)

`product-forge` (cold-start orchestrator/router) · `product-methodology` · `product-research` · `product-architecture` · `product-patterns` · `product-operations` (the six makers) · `product-genres` (knowledge satellite) · `product-evaluate` (the judge — 11-rubric library + the `product-council` agent). Supporting: 23 critic agents + 1 council orchestrator, 7 commands, a corpus MCP, the `product-lint` advisory hook, and `bin/check-methods.py` (the cross-skill gate).

## §1 — The coupling graph (D1)

No declared graph exists (no `skill.json`/`peer_skills`/`$ref` wiring; every `../` path is **intra-skill**). The real coupling runs through four mechanisms:

- **A. Orchestrator routing (star/spoke).** `skills/product-forge/SKILL.md:31-39` routes the classifier to all seven other skills; the taxonomy (`experience-strategy-taxonomy.md:17-28`) and process-spine (`process-spine.md:26-39`) re-name the owning skill per domain/method.
- **B. The maker→judge rubric spine (the hidden, *checked* `$ref`-equivalent).** `bin/check-methods.py:103-107` **enforces** that every method card's `rubric:` frontmatter resolves to a real file under `skills/product-evaluate/references/rubrics/` — wiring `product-research`, `product-methodology`, `product-architecture`, `product-operations` method cards into `product-evaluate`. Reinforced conceptually by every maker's `§Teach` ("add the matching dimension to the relevant rubric in `product-evaluate`"). This is the coupling no peer array declares — and it is mechanically enforced, not soft prose.
- **C. The council layer.** `product-evaluate/SKILL.md:45` → `product-council` → 23 critics spanning all 12 taxonomy domains. (`critic-garry-t` is a cross-plugin reuse with agent-ops — dispatched plugin-scoped.)
- **D. Reciprocal maker↔maker prose edges.** architecture↔patterns ("system vs reusable unit"), research→methodology (OST hand-off), genres→patterns + the genre-fit rubric dimension.

**Classification:** `product-forge` HUB (router, high fan-out); `product-evaluate` HUB/SINK (highest fan-in — every method card + every `§Teach` converges here; the least severable node); `product-council` BRIDGE; `product-methodology` maker-hub; `product-architecture`/`product-patterns` semi-hubs; `product-research` bridge-leaf; `product-operations` LEAF (lowest coupling); `product-genres` LEAF (knowledge satellite, no method cards). No orphans, no dead skills.

## §2 — The most-defensible partition (the proposal · D5/D7)

The dominant topology is one cohesive structure: a hub-and-spoke around the orchestrator with all spokes converging on the judge spine. *If forced*, the loosest cut is a **2-plugin "co-located judge"** partition:

| Plugin | Job | Members | Hub | Depends-on (mechanism) | Today has / should gain |
| --- | --- | --- | --- | --- | --- |
| **product-experience** | Build product strategy, research, architecture, patterns, operations, genres | `product-forge` (router) + 6 makers + `product-genres` | `product-forge` | → **product-evaluate** (`dependencies` edge — the rubric spine) | Has the makers + taxonomy/spine; should gain its own pruned copies of the whole-library frames |
| **product-evaluate** *(foundation/sink)* | Judge product artifacts against the 11-rubric library + council | `product-evaluate` + `product-council` + 23 critics + `bin/check-methods.py` | `product-evaluate` | — (sink: depends on nothing) | Has the rubrics + council; should gain ownership of `check-methods.py` (which walks the whole tree today) |

Detachable leaves explicitly accounted for (not dropped): **product-genres** (purest cut — a knowledge satellite with no method cards, only "pair-with" edges) and **product-operations** (lowest fan-in/out). **Node accounting (D5):** input ∖ (members ∪ leaves ∪ judge) = ∅ — all 8 skills + all 23 critics + the orchestrator frames + the two `bin/` tools are placed; zero silent drops.

**Dependency graph (D4):** `product-experience → product-evaluate` (foundation as sink); acyclic. The orchestrator routes to both makers and the judge, but introduces no back-edge from the judge to the makers. A clean DAG.

## §3 — Scoring (carve-quality v0.1.0)

| Dim | Score | Rationale |
| --- | --- | --- |
| **D1 — Graph Fidelity** `[review]` | **5** | All three edge classes extracted and sourced (routing / reciprocal-peer / the hidden *checked* maker→judge spine), shared-infra identified by cross-cluster in-degree, cited file:line. The hidden-edge test passes — the `check-methods.py` coupling that no peer array declares is in the graph. |
| **D2 — Cuts at the Joints** `[review]` | **2** | The edge-cut test fails. The only available boundary (makers ∣ judge) slices a **high-in-degree, checked** `$ref`-equivalent cluster — *every* maker's method cards resolve into `product-evaluate`. Severing it is the cardinal error the rubric names; the maker/judge seam is the densest coupling in the graph, not a thin one. |
| **D3 — Shared-Infra Legality** `[gate]` | **3** | Not gate-capped — there is **zero surviving `../`** (today all `../` are intra-skill), and the maker→judge share is resolvable legally as a `dependencies` edge (≥2 consumers → `product-evaluate` becomes a foundation plugin). But the resolution is under-specified/heavy: `check-methods.py` walks the whole `skills/` tree and would have to be re-homed, and the whole-library taxonomy/spine fragment across the boundary. A legal-but-strained resolution. |
| **D4 — Dependency-Graph Integrity** `[gate]` `[review]` | **4** | Acyclic; `product-evaluate` is a clean sink (depended-on, depends on nothing); the one edge's mechanism (`dependencies`) is stated. Not gate-capped (no cycle). |
| **D5 — Node Accounting** `[gate]` | **5** | The diff test passes — every input skill, every critic, the orchestrator frames, and both `bin/` tools are placed (member / leaf / sink); the detachable leaves are named with recommended homes; zero silent drops. Not gate-capped. |
| **D6 — Granularity Calibration** `[review]` | **2** | The sizing test fails. `product-experience`'s one-sentence job needs "…assuming `product-evaluate` is also installed" — worse, it cannot satisfy its own CI gate (`check-methods.py` resolving every `rubric:` ref) without the judge plugin. This is the fragment failure mode: a single workflow split across must-co-install plugins. The natural state is one plugin. |
| **D7 — Buildable Proposal** `[review]` | **4** | The layered proposal ships (plugin table with job · members · hub · depends-on · today-has/should-gain; the acyclic dependency graph with mechanisms; the orphan/leaf callouts; per-plugin self-checks below). `author` could pick up a row — though the "should gain" frame-pruning column is thin. |

**Gates:** D3 (no `../`, legal resolution) ✓ · D4 (acyclic) ✓ · D5 (no silent drop) ✓ — none tripped. The carve is **not** capped by a gate; it is held down by D2 and D6, the partition-fit dimensions.

**Per-plugin self-check (composition-phase cross-check):**
- *product-experience* — P3 boundary-cohesion: **weak** (it bundles six distinct maker jobs only because they share the judge — a "team's whole toolbox" smell). P4 dependency-legality: OK (one `dependencies` edge). 
- *product-evaluate* — P3: strong (one coherent job: judging). P4: OK (sink). But it is only *useful* paired with a maker, so as a standalone toggle its P1 plugin-fitness is low.

## §4 — Verdict

**BLOCKED — do not carve.** product-forge is a cohesive single-job plugin. The maker and judge are "two halves of one standard," bound by a *checked* contract (`check-methods.py`), not a soft reference; the makers are loosely coupled to each other but all tightly coupled to the same judge + council; the orchestrator, taxonomy, and process-spine are whole-library artifacts that presuppose one plugin. The best-available partition scores D2 = 2 and D6 = 2 and yields plugins that cannot stand alone. The right action is the null carve: keep product-forge as one plugin.

This is the rubric working as designed — it cleanly separated **analysis quality** (D1 = 5, D5 = 5, D7 = 4) from **partition quality** (D2 = 2, D6 = 2), with the gates confirming the analysis is *sound* (no `../`, acyclic, complete) even though the recommendation is "don't." A carve that scored every resulting plugin's P-dimensions in isolation would have missed exactly this: the defect is in the *seam* (a dense checked spine) and in the *set* (fragments that must co-install), not in any single plugin.

**Rubric note (calibration finding):** `carve-quality.md`'s scale prose assumes a partition is always proposed; the "null carve / keep as one plugin" outcome is best expressed by scoring the *most-defensible* partition (as done here) with a BLOCKED verdict, rather than as a separate scale point. Worth a future rubric clarification — the cohesive-library case is common and the rubric should name how to score it.
