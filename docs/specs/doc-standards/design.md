# Design documents

Architecture, low-level design, API docs, and decision records: how the system is built and why. [Core rules](core.md) apply to all of them.

| Type | Shape | Machine-checked |
|---|---|---|
| HLD / architecture | C4 model for diagrams and component names. Diagrams as code (Mermaid, Structurizr DSL) so a harness can read them. One decision record per decision. | none |
| LLD | Interface contracts first: OpenAPI, AsyncAPI, JSON Schema, Protobuf, or typed signatures. Prose in the DITA reference shape: purpose, inputs, outputs, errors, examples. Invariants and preconditions as EARS or Design-by-Contract statements. | none |
| API docs | OpenAPI is the source of truth. Descriptions follow the Microsoft or Google developer style guide. One runnable example per endpoint. | none |
| Decision records | ADR, Nygard shape: context, decision, consequences. Template: [adr.tmpl](../../assets/templates/adr.tmpl). | docs_check S-3 |

## Rules

1. A diagram is code in the repository, not an image only. An exported picture goes in `docs/assets/` beside its source.
2. State the contract before the prose. A reader who reads only the contract can call the interface.
3. One decision per file, named `NNNN-slug.md` in `docs/decisions/`, with exactly one `## Decision` heading (S-3).
4. A decision record is immutable once accepted. To change it, write a new record and set the old one to `status: superseded`.
5. A design names the decision records it rests on by number; it does not repeat their reasons.
