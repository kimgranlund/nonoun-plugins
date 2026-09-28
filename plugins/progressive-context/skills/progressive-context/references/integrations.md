# Representations and neighboring workflows

## Files

A directory can hold a capability contract, implementation, and linked evidence. AGENTS.md routes agents to the relevant records and supplies scoped operating instructions. Keep the directory shape appropriate to the project; no universal set of .md files is required.

## Browser JavaScript harness

Represent the same concepts as records with stable IDs and references. An index returns small summaries; explicit reads fetch contracts, implementations, criteria, or evidence on demand. IndexedDB or a service can persist them. Record exactly which revisions were read and assessed. Disclosure follows task relevance and a context budget; storage location does not grant authority. This plugin supplies authoring guidance, not these runtime APIs.

## A2UI

Separate the durable composition contract, versioned composition data, and rendered runtime instance. Pin the renderer/catalog adapter and supported component contracts. Evaluate structure, bindings, rendering, interaction, accessibility, and domain behavior separately. A valid A2UI payload is not proof of a working interface. Adding an unsupported component is renderer work; do not invent catalog entries. Reusable composition data and reusable renderer components have different public interfaces.

## SDLC Lite

Progressive Context owns durable intent, capability boundaries, context routes, and qualification claims. SDLC Lite owns work execution: tickets, plans, runs, verification, and work closure.

- Ticket: a desired change; link the capability contract from its Context section.
- Plan: steps toward that change; derive checks from the contract's criteria.
- Run: implementation attempt; retain its existing handoff and result artifacts.
- Verification: evidence for a named change; reuse it in the assessment when its scope and revision binding suffice.
- Roadmap: generated work ordering plus separately authored priorities. Dependency order cannot infer strategy or user commitment.

One capability can have several tickets; one ticket can touch several capabilities. Ticket closure does not publish a capability, and an accepted capability may still have open enhancement tickets. Do not synchronize independent status flags or duplicate the SDLC board in context files.

Example: a ticket adds keyboard selection to an existing invoice review capability. Its plan links the contract's selection criterion; its verifier result is referenced by a new assessment of the changed revision. The contract retains its stable ID after the ticket closes.
