---
id: GS-P01
type: spec
status: implemented
created: 2026-10-11
target: references/generation-and-revision.md
---
# Choose generation constraints by task fit

## Problem and evidence boundary

The skill explains editable seams but does not explicitly help a system designer choose constrained composition, templates, or free generation. The reviewed design document also confused rejecting invalid output with preventing its generation.

Source: the Oct 11, 2026 coverage review of Closed-loop generative UI system (`/Users/kimgranlund/Downloads/Closed-loop generative UI system.md`). This is a proposed reasoning improvement based on a documentation gap; no measured skill-efficacy gain is claimed.

## Scope and owner

Owner: `references/generation-and-revision.md`. Insert a short section before “Define the seam”. Use the existing routing from `SKILL.md`; no new mandatory read or entrypoint expansion is needed.

Keep host APIs, tool names, shell commands, framework bindings and CI configuration in the design document or the consuming project's implementation. Do not add a runtime, schema framework or new tracking system to this skill. This spec authorizes no evaluation dispatch or publication; it records proposed text only.

## Proposed skill text

## Choose the generation boundary

Choose the narrowest representation that expresses the authorized task without hiding required behavior. Constrained composition suits supported combinations with explicit limits; template seams suit stable mechanics with bounded edits; free generation suits authorized logic outside those boundaries. Weigh recurring failure evidence against the maintenance cost of schemas, compilers and adapters. A repair-rate plateau alone does not justify a compiler.

State whether a mechanism prevents an invalid choice, rejects an invalid submission, or merely reports it after execution. Structural constraints do not prove runtime behavior. If the representation cannot express the outcome, route the capability gap rather than silently escaping its boundary.

## Acceptance and review cases

- A fixed document template with a few editable fields routes to its existing seams; the proposal does not prescribe a component-tree compiler.
- A task needing unsupported behavior is recorded as a gap or authorized extension, not forced into a supposedly complete schema.
- A generated tree with an unknown node rejected by validation is described as rejected output, not impossible-to-generate output.

- Review the insertion in context for duplication and conflicting requirements. Preserve existing scope, evidence and authorization limits.
- Keep the inserted guidance under 150 words and within its existing reference. The deployed skill remains unchanged until this proposal is implemented.
- Review cases are intended reasoning checks, not completed independent evaluations. Implementation can use a focused walkthrough; any empirical efficacy claim requires separately authorized, qualified evidence.

## Implementation boundary

Do not copy this whole spec into the skill. Insert only the proposed guidance, adapting adjacent wording to avoid duplication. Preserve historical evidence and keep the proposal's status distinct from shipped guidance. If several proposals land together, GS-P03 and GS-P05 share a file: merge their changes sequentially and retain intent validation before enforcement and checker qualification.

## Disposition, 2026-10-11

Conditional generation-boundary guidance added; no compiler prescribed. Evidence: implementation and research report (`resources/reports/context-architecture-research-2026-10-11.md`). Documentation implementation does not demonstrate efficacy.
