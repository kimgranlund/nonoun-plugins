# Progressive context architecture

Use this vocabulary to locate a responsibility, not to prescribe twelve artifacts,
a maturity ladder or a traversal order. A short entry and links may be sufficient.

## Responsibilities

| Tier | Responsibility | Design question |
|---|---|---|
| T0 | Corpus contract | How does an unfamiliar runtime start? |
| T1 | Navigation | What exists in this scope and where should this task go? |
| T2 | Scope | Which constraints and owners govern the work? |
| T3 | Descriptors | What compact identity and summary enable selection? |
| T4 | Registry | Is discovery ambiguous or expensive enough to justify an index? |
| T5 | Depth | What missing requirement justifies another read? |
| T6 | Intent routing | How do action, target and concern select required context? |
| T7 | Procedure | How does the task execute and establish completion? |
| T8 | Assembly | What context actually arrived, and what remains pending? |
| T9 | Working set | Which temporary evidence must stay separate from durable rules? |
| T10 | Integrity | Do references, projections and evidence represent their sources? |
| T11 | Governance | Who resolves conflicts and maintains compatibility? |

## Entry, intent and ownership

Give each supported starting environment one clear entry sequence. Host-specific
files should expose shared guidance through native discovery, not copy its rules.
Do not require a particular filename or command. Verify what the host actually
loads; a valid entry file does not prove native skill or plugin registration.

Route by action and concern as well as target. A documentation review, behavioral
change, styling change and consumer composition may concern the same artifact but
need different contracts. Make workflow terminology explicit; keep it separate
from ownership boundaries. Do not impose these example modes on every corpus.

Root guidance should route to purpose, ownership, workflow and task-specific
contracts. Deliver their bodies only where needed. Local entries summarize and
link; they do not repeat implementation inventories. A known implementation path
remains a legitimate start when governing scope is loaded before action.

## Authority and representation

Distinguish the physical graph (locations), semantic graph (relationships) and
context graph (required retrieval). Support both browsing from broad to specific
and expansion from a known target to governing scope and dependencies.

Use the [semantic handoff](semantic-handoff.md) when definitions or mappings need
modeling work. Keep domain relationships distinct from task-required retrieval edges.

Keep each rule and inventory authoritative in one place. Declare authored inputs,
generated projections and observed behavior separately. Generated output can
establish current behavior without becoming an editing target or deciding intended
behavior. Resolve conflicts by governing scope and ownership, not proximity,
timestamps or a successful example. Operational conflict handling lives in
[traversal](traversal.md).

## Shared machinery, where applicable

- Derive registries and host bundles from canonical sources. Let validation and
  shipping consume the same bounded inventory; declare permitted aliases and
  reject traversal escapes and cycles.
- For composed contracts, use one declared input graph. Validate supported
  reference fragments and final shapes; preserve each link's source provenance.
- For document checking and rewriting, share a syntax-aware model with source
  spans, reference kinds and rendered context. Use one URL resolver; retain query
  strings and whole fragments. Do not substitute regexes or rendered-string
  equality for syntax identity.
- Snapshot navigation and media differently: source-only navigation may retain
  an explicit provenance note, while media needs a usable resource. Preserve
  loading semantics and record unsupported forms explicitly.
- Bind evidence and caches to all inputs actually consumed, including directory
  membership when scanning. Byte identity does not prove semantic correctness.

These are design criteria for systems that perform those operations, not a mandate
to add a generator, parser, cache or registry. Keep provider conventions in adapters;
the core should work from its declared distribution without personal paths or a
source checkout. See [evaluation](evaluation.md#practical-evaluation-criteria) for
observable tests, [contracts](contracts.md) for the optional JSON profile, and
[layout example](../examples/universal-layout.md) only when a layout is useful.
