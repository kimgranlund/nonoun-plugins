---
id: GS-P02
type: spec
status: implemented
created: 2026-10-11
target: references/materials-and-contracts.md
---
# Close capability gaps and resume the originating task

## Problem and evidence boundary

The current skill identifies gaps and owners but leaves the interim behavior, resolution evidence and return to the original task implicit. A gap may be a retrieval, contract, runtime or intent problem rather than a missing reusable component.

Source: the Oct 11, 2026 coverage review of Closed-loop generative UI system (`/Users/kimgranlund/Downloads/Closed-loop generative UI system.md`). This is a proposed reasoning improvement based on a documentation gap; no measured skill-efficacy gain is claimed.

## Scope and owner

Owner: `references/materials-and-contracts.md`. Insert a short section before “Consume without inventing fidelity”. Use the existing routing from `SKILL.md`; no new mandatory read or entrypoint expansion is needed.

Keep host APIs, tool names, shell commands, framework bindings and CI configuration in the design document or the consuming project's implementation. Do not add a runtime, schema framework or new tracking system to this skill. This spec authorizes no evaluation dispatch or publication; it records proposed text only.

## Proposed skill text

## Resolve a capability gap

Record the originating task and source version, unmet scenario, gap category, owner, disposition and permitted interim behavior using the project's existing tracking mechanism. Distinguish missing capability, failed discovery, contract conflict, runtime defect, evaluator defect and unclear intent. A supported fallback may proceed if it still meets the outcome; an extension must fit the authorized scope. Otherwise mark the affected work blocked while continuing independent work.

Resolve the gap in its owning source, verify the originating scenario and state how the original task resumes. Rejection needs a reason and an explicit fallback, scope decision or continued blocked status. Give temporary exceptions a scope and retirement condition. Closing the record does not establish that the original artifact passes.

## Acceptance and review cases

- A needed capability already exists but its route is broken: repair discovery without proposing a duplicate component.
- A supported fallback satisfies the outcome: continue without demanding a new approval merely because a gap record exists.
- A missing runtime capability has no supported fallback: retain the affected task as blocked; closing a tracking item alone cannot mark it accepted.

- Review the insertion in context for duplication and conflicting requirements. Preserve existing scope, evidence and authorization limits.
- Keep the inserted guidance under 150 words and within its existing reference. The deployed skill remains unchanged until this proposal is implemented.
- Review cases are intended reasoning checks, not completed independent evaluations. Implementation can use a focused walkthrough; any empirical efficacy claim requires separately authorized, qualified evidence.

## Implementation boundary

Do not copy this whole spec into the skill. Insert only the proposed guidance, adapting adjacent wording to avoid duplication. Preserve historical evidence and keep the proposal's status distinct from shipped guidance. If several proposals land together, GS-P03 and GS-P05 share a file: merge their changes sequentially and retain intent validation before enforcement and checker qualification.

## Disposition, 2026-10-11

Gap resolution and resumption added using existing tracking. Evidence: implementation and research report (`resources/reports/context-architecture-research-2026-10-11.md`). Documentation implementation does not demonstrate efficacy.
