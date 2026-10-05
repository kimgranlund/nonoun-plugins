# Context and JavaScript harness specification

Status: proposed v0.1. Depends on the [model](02-construct-model.md) and [lifecycle](03-lifecycle-and-evaluation.md).


> Shipped status: the Progressive Context skill implements a smaller subset of this proposal under different words. This document's terms (construct, revision, instance) map to the skill's capability, contract and assessment as listed in the [vocabulary table](README.md#vocabulary-proposal-and-shipped-skill). The skill specification and the shipped skill record later refinements; reconcile any difference before implementing from this document.

## Responsibility

The harness connects stored construct records to a model, tools, a runtime adapter, and a human editor. It owns resource resolution, context assembly, revision writes, evaluation dispatch, and lifecycle policy. The model proposes interpretations and changes; storage presence alone never implies model awareness.

The same logical interface must work with an in-memory adapter for development and a persistent adapter for continued work. IndexedDB is the initial browser storage candidate; it supports structured records and blobs. [Reference](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API).

## Progressive disclosure contract

| Operation | Required initial context | Available on demand |
| --- | --- | --- |
| Discover | Query, catalog summaries, status, limitations | Candidate manifest |
| Use | Selected public contract, applicability, dependency refs | Examples, exact composition |
| Modify | Intent, contract, relevant semantics, target revision | Realization, decisions, affected dependencies |
| Evaluate | Criteria, target snapshot, fixture refs, evaluator contract | Realization, observations, relevant semantics |
| Diagnose | Failed criteria, findings, effective environment | Provenance, dependency details, prior revisions |

Mandatory constraints must be included even when a model does not request them. Navigation summaries must expose limitations that could disqualify a candidate. Content is fetched by exact reference; relevance search does not replace reference resolution.

Start with lexical search and type/status filters over a small catalog. Semantic retrieval is optional and must not bypass applicability checks. A discovery result is a candidate, not a recommendation guaranteed to fit.

## Proposed tool surface

These are application APIs to implement, not existing A2UI tools:

| Tool | Input | Result |
| --- | --- | --- |
| `discover` | Query, filters, page limit, cursor | Bounded summaries and next cursor |
| `inspect` | Construct ID, optional revision | Manifest, resource IDs, status, limitations |
| `read` | Exact resource ref, optional section | Content, digest, section metadata |
| `create` | Kind, provisional intent, client request ID | New identity and initial snapshot |
| `revise` | Construct ID, expected head, resource changes, rationale, request ID | New immutable snapshot or conflict |
| `instantiate` | Revision, validated input, instance key | Instance ID and runtime result |
| `evaluate` | Target revision, criteria refs, fixture refs, request ID | Run ID; evidence when complete |
| `assess` | Revision and intended scope | Derived findings and transition eligibility |

Acceptance and publication are explicit UI commands invoking the lifecycle policy. They are not exposed as unrestricted status-edit tools. Read APIs for runs, evidence, and instances support inspection and resumable work.

## Operation sequence

1. Resolve the user request and selected operation.
2. Pin resource revisions and load the operation contract plus mandatory constraints.
3. Assemble a bounded context and expose only relevant tool capabilities.
4. Process model tool requests through schema validation and reference resolution.
5. Commit writes as new snapshots using optimistic concurrency.
6. Store observable run records and handoff references.
7. At a stage boundary, assemble a fresh context from authoritative resources and the handoff.

A handoff contains target revision, outcome of the stage, unresolved findings, artifact references, and recommended next operation. It must not depend on the previous conversation remaining available.

The shipped filesystem pilot is narrower than this proposed harness: [Progressive Context's optional stage guidance](../../plugins/progressive-context/skills/progressive-context/references/workflow-stages.md) and its [small repository change example](../../plugins/progressive-context/skills/progressive-context/references/examples/small-repository-change.md) describe reusable handoff boundaries. A [manual SDLC Lite exercise](../reports/workflow-stage-pilot/exercise-run.md) records actual links and tool outputs. No stage scheduler or automatic exit enforcement is implemented by that pilot.

## Context budget

The prototype starts with a configurable 12,000-token input budget per model call, including tool definitions and conversation material. This is an experiment setting, not an asserted optimal value. Record actual input/output tokens where the provider exposes them; label estimates otherwise.

Paginate discovery results and retrieve sections of large documents. When required context does not fit, split the operation or return an explicit budget error. Do not silently omit constraints. At stage changes, discard irrelevant prior tool responses from the next request while retaining their references in the run record.

## Persistence and concurrency

Store construct identities, immutable snapshots, resources, evidence, lifecycle events, runs, and instances separately. Atomically store a snapshot's resource references and advance its draft head. `expectedHead` conflicts return the current head and require reconciliation; last-write-wins is not acceptable.

Use request IDs to make retried creation, revision, and local action commands idempotent. Resume interrupted work from the last committed stage. A partially rendered surface or interrupted evaluation cannot be promoted to a completed result.

Export/import should preserve IDs, revisions, resource digests, and provenance in a versioned JSON bundle. This restores the portability that ordinary files provide. Imported summaries do not override local policy or qualify artifacts automatically.

## Trust and authority

Routing and operation policy come from harness-controlled configuration. Retrieved artifacts, external documents, and generated A2UI are data. Instructions embedded in them cannot expand available tools or change lifecycle guards. Resource reads and writes are scoped to the active workspace. Runtime actions use registered handlers rather than arbitrary generated JavaScript.

## Human inspection surface

Provide a construct browser and detail editor with intent, contract, realization preview, evaluation findings, and revision history. Show the actual resources loaded by a run. Allow explicit changes to intent and criteria with a rationale, and explain which assessments need to be rerun.

A generated UI must not be the sole means of inspecting or recovering its own definition. A stable host editor provides these controls.

## Required checks

- Discovery never returns entire realization bodies by default.
- Required context survives budget enforcement or the operation reports an error.
- Stale-head writes cannot overwrite another revision.
- Restart preserves published records and reports interrupted runs accurately.
- A fresh session resumes from stored references without hidden transcript dependency.
- Evidence cannot be attached as passing to an unresolved or different target revision.
