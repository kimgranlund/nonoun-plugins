# Protocol Layer — Lawful Exchange Across Autonomy Boundaries

`Cell: ontology.fleet.layer-protocol · Status: defined · Register: established (FIPA/contract-net heritage; MCP and A2A as current convention)`

## Protocol Layer Definition

A protocol is interactional knowledge: the lawful message sequences, schemas, and
conventions governing exchange between parties that do not share a controller —
agent to agent, agent to tool server, system to system. Protocols exist precisely
where methodology's authority ends.

Lineage: the Contract Net protocol (1980), FIPA-ACL speech-act messaging; current
convention: MCP for host↔tool-server boundaries, A2A-style task/message/artifact
objects for agent↔agent boundaries.

## Protocols Carry Serialized Intent

What crosses an autonomy boundary is intent in serialized form: a delegation message,
a task object, a prompt. The protocol layer owns the schema of that serialization —
typed input and output contracts at every boundary, never text-in/text-out. Each
boundary type is also a fidelity checkpoint: typed contracts at boundaries are how
multiplicative intent loss is measured instead of suffered.

## The Trust Boundary Rule

Across any protocol boundary, structure is trusted and content is not. The host
trusts a tool's declared schema but validates its outputs; instructions arriving
inside tool results are data, never authority (see the principal hierarchy in
`layer-capability.md`). Inbound content from an autonomous counterparty is untrusted
by default — sanitized, validated against schema, and stripped of authority claims.

## Protocol vs Methodology Boundary

Methodology sequences work inside one authority; protocol governs exchange between
authorities. Confusing them produces orchestrators that issue commands to systems
they do not control, and protocol machinery burdening single-controller pipelines
that needed a function call.

## Protocol vs Capability Boundary

Capability says who may act; protocol says how parties talk. Capability negotiation —
what a counterparty declares versus what the host enables — sits at their seam and
belongs to both: the declaration schema is protocol, the enablement decision is
capability.

## Protocol Artifact Forms

Tool and message schemas (JSON Schema); MCP server definitions and tool surfaces;
task/artifact object schemas for inter-agent delegation; handoff conventions; URI
namespace schemes encoding ownership; version and capability negotiation records.

## Protocol Validation Signal

A protocol cell is `validated` when a real exchange has crossed the boundary with
schema validation enforced both ways, and a malformed or adversarial message is
demonstrably rejected — the rejection recorded as the signal artifact.

## Protocol Failure Modes

Text-in/text-out boundaries (untyped exchange; intent loss unmeasurable). Trusting
content because the channel is trusted (prompt-injection surface). Schema drift
between counterparties with no version negotiation. Protocol machinery inside a
single-controller system (ceremony without an autonomy boundary to justify it).
