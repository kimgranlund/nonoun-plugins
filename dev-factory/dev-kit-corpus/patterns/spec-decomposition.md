# Seed pattern — spec decomposition along real seams

`Cell: pattern.system.spec-decomposition · family: corpus · register: seed (shipped by dev-kit-corpus to warm the pattern layer + the compass cold-start priors)`

A `spec.system` cell that fans out into sub-specs validates faster and cheaper when the decomposition follows **real seams** — independent sub-capabilities with a clean join — rather than fabricated sections that secretly depend on each other (the conflict at merge is the proof the split was unsound).

**When the compass sees this pattern apply** (a `spec`/`system` target with independent sub-parts), the dispatch policy escalates to `orchestration_shape: orchestrator-workers` at `delegation.mode: team`, fanning the sub-specs out in parallel — maximal width, bounded depth. An irreducible spec (one atomic intent, no internal seams) collapses to `single-pass` instead; forcing a team onto an atom is waste.

**Provenance:** this is a seed prior, not a validated cell. It earns `validated` only once the ledger shows decompositions that followed it cost less per signal than those that didn't — at which point `pattern-distiller` promotes it and `spec-regenerator` may fold it upstream into the spec methodology.
