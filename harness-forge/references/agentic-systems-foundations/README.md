# Agentic Systems Foundations — Knowledge Base

A foundational knowledge base for designing, building, and operating agentic systems:
the vocabulary (ontology), the nine declarative foundation layers, the lattice model
that governs what to build next, the discipline of verification, and the practice of
autonomous long-running operation. Built to serve as Project Knowledge for a Claude
Project and as the seed corpus for an agentic-systems factory.

## How to Use This Knowledge Base

Upload every file to Project Knowledge. In Project Instructions, point Claude at the
entry sequence ("consult `agentic-systems-ontology.md` for vocabulary;
`lattice-model.md` before any prioritization or planning question") rather than
duplicating content. Each document covers one topic and is written in declarative
statements for retrieval precision.

## Document Index

| Document | One-line purpose |
|---|---|
| `agentic-systems-ontology.md` | Vocabulary source of truth: UOW, the Agent class, the nine-layer modality axis, scope ladder, maturity states, core nouns |
| `lattice-model.md` | The Completion Frontier: lattice, maturity, engine, compass, regeneration loop, trajectory rule, operating procedure |
| `layer-spec.md` | Specification layer: what counts as done; intent's canonical residence; decomposition soundness; commitment inertia |
| `layer-rubric.md` | Rubric layer: scoring knowledge; gate vs review checks; calibration; the verifier-maturity precondition |
| `layer-policy.md` | Policy layer: deontic rules; enforcement-as-hooks; budgets; the trust trajectory for staged autonomy |
| `layer-capability.md` | Capability layer: who may act; the principal hierarchy; enforced-not-declared allowlists; agent roster discipline |
| `layer-methodology.md` | Methodology layer: the engine procedure; workflow patterns; the routing law; the trajectory rule |
| `layer-protocol.md` | Protocol layer: typed exchange across autonomy boundaries; serialized intent; the trust-boundary rule |
| `layer-ledger.md` | Ledger layer: append-only provenance; schema-early; staleness propagation; the three loops the ledger closes |
| `layer-pattern.md` | Pattern layer: distilled precedent; anti-patterns and content inversion; exemplars; provenance discipline |
| `evals-and-verification.md` | What good evals are: high-signal anatomy, placement economics, generator/critic split, reward-hacking defenses, false-pass rate |
| `autonomous-long-running-systems.md` | Building unattended systems: harness anatomy, durable state, fresh-context iteration, hooks, budgets, staged autonomy |
| `naming-conventions.md` | Typed naming: three-tier vocabulary, composition grammars, rules, self-hosting enforcement |

## Reading Order

1. `agentic-systems-ontology.md` — the vocabulary everything else composes from
2. `lattice-model.md` — the operating model over that vocabulary
3. `layer-spec.md` → `layer-rubric.md` → `layer-policy.md` — the upstream wavefront,
   in dependency order
4. Remaining `layer-*.md` files as needed per task
5. `evals-and-verification.md` and `autonomous-long-running-systems.md` — the two
   practice guides, before building any loop intended to run unattended
6. `naming-conventions.md` — before creating any named artifact

## Conventions Used Throughout

Every document opens with a status line: its cell ID in this corpus's own lattice,
its maturity, and a register note marking what is established lineage versus
synthesis. This knowledge base is an instance of the system it describes: documents
are cells, they carry maturity, they go stale when upstream documents change, and
revisions are deliberate transitions — never silent edits.

## Maintenance

Current corpus maturity is `defined`: the documents exist and are typed, but have not
yet earned validation signals (use in anger, contradiction hunts, retrieval checks).
When a document's guidance is corrected by experience, the correction is a
regeneration of that cell — update the file, note the change, and flag dependents.
A document that stops regenerating while the field moves is drift wearing the costume
of documentation.
