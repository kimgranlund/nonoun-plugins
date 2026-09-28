# Generative constructs: specification set

Status: proposal, version 0.1. Date: 2026-09-26.

This set develops the conversation about ICM, progressive disclosure, reusable constructs, a browser-based JavaScript harness, and A2UI. These are proposed design contracts, not claims that a system has been implemented or validated. “Must” describes a requirement of this proposed design. Decisions remain editable through explicit revisions.

## Read in this order

1. [System brief](01-system-brief.md): purpose, hypothesis, scope, and design principles.
2. [Construct model and ontology](02-construct-model.md): shared concepts, records, identities, and relationships.
3. [Lifecycle and evaluation](03-lifecycle-and-evaluation.md): evidence, transitions, acceptance, and publication.
4. [Context and JavaScript harness](04-context-and-harness.md): progressive disclosure, tools, persistence, and operation boundaries.
5. [A2UI composition and runtime](05-a2ui-composition-and-runtime.md): catalog boundaries, instantiation, rendering, and interaction.
6. [Prototype and validation](06-prototype-and-validation.md): a bounded implementation and experiment.

## Related specification and foundation

- [Progressive Context skill specification](progressive-context-plugin.md): v0.3 proposal covering lifecycle, domain profiles, adapters, and qualification.
- [Folder-native Gen UI ontology](../../../gen-ui-system-svelte-lite/docs/references/folder-native-gen-ui-ontology.md): the existing UI element-contract foundation, owned by the sibling UI project.

The initial authoring plugin is now implemented; see [shipped scope and validation](../plugin-compatibility.md). The six numbered documents preserve the initial proposal. The skill specification records subsequent refinements; remaining differences should be reconciled before implementation.

## Ownership of definitions

Document 2 owns terminology and record semantics. Document 3 owns lifecycle and publication rules. Document 4 owns context operations and persistence behavior. Document 5 owns the A2UI adapter contract. Document 6 owns prototype scope and experimental thresholds. Changes that cross these boundaries must update the affected documents together.

The example throughout is an overdue-invoice review workspace built from an invoice table, customer summary, and a panel of supported actions. It uses synthetic fixtures and local actions. The domain definitions are explicit prototype assumptions, not universal accounting rules.

## Decisions made for this draft

- Storage-independent construct records are the core abstraction; folders are an optional representation.
- Stable construct identity, immutable revision snapshots, and runtime instances are distinct.
- Acceptance for one purpose and publication for reuse are separate decisions.
- A2UI compositions are reusable data; adding a renderer component requires an implementation step.
- Publication requires fresh evidence, a bounded public contract, and a successful independent reuse exercise.
- The first prototype is a single-user browser application with a persistence adapter and a version-pinned A2UI adapter.

## Sources and attribution

The architecture is an extension proposed in this session. Its terminology, publication rules, and construct schema are not attributed to ICM's authors.

- [Van Clief and McDermott, ICM paper, v2](https://arxiv.org/html/2603.16021v2): filesystem-based context hierarchy and staged workflows. The paper's evidence is preliminary; it does not establish this proposal's effectiveness.
- [Anthropic, effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): selective retrieval and progressive disclosure.
- [Anthropic, agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): outcome evaluation and different grader types.
- [W3C PROV primer](https://www.w3.org/TR/prov-primer/): entities, activities, and responsibility as provenance concepts.
- [A2UI overview](https://a2ui.org/concepts/overview/) and [glossary](https://a2ui.org/concepts/glossary/): declarative surfaces, data binding, and catalogs. Exact protocol syntax is deliberately delegated to a pinned adapter.
- [MDN, IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API): browser persistence option.

The AdiaUI implementation notes in document 5 additionally reference the installed plugin's `gen-ui-wiring` skill, version 0.8.51. Those notes are adapter-specific, not general A2UI requirements.
