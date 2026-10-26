---
id: GS-P05
type: spec
status: implemented
created: 2026-10-11
target: references/verification-and-drift.md
---
# Validate intent independently of generated implementation

## Problem and evidence boundary

The skill derives checks from the requested outcome but provides limited guidance for detecting an incomplete or contradictory intent. Without an independent outcome basis, a generator and checker can agree on the wrong implementation.

Source: the Oct 11, 2026 coverage review of Closed-loop generative UI system (`/Users/kimgranlund/Downloads/Closed-loop generative UI system.md`). This is a proposed reasoning improvement based on a documentation gap; no measured skill-efficacy gain is claimed.

## Scope and owner

Owner: `references/verification-and-drift.md`. Expand the existing opening paragraph with the proposed paragraph below; keep “Find the failing boundary” after it. Use the existing routing from `SKILL.md`; no new mandatory read or entrypoint expansion is needed.

Keep host APIs, tool names, shell commands, framework bindings and CI configuration in the design document or the consuming project's implementation. Do not add a runtime, schema framework or new tracking system to this skill. This spec authorizes no evaluation dispatch or publication; it records proposed text only.

## Proposed skill text

Before generation, connect the requested outcome to representative scenarios: starting conditions, action, observable result and relevant failure or recovery. Trace acceptance criteria to those scenarios or authoritative constraints. Surface assumptions and resolve contradictions that would change implementation. Require a particular structure only when the outcome or owning contract requires it. A legitimate alternative should pass; a plausible-looking result that misses the outcome should fail. Preserve intent ownership: changing criteria to fit generated output requires a justified scope decision and re-evaluation of affected evidence, not a silent relaxation.

## Acceptance and review cases

- Two different supported layouts complete the same task: both can pass unless layout is an explicit requirement.
- A visually correct artifact has an inert action: its outcome scenario fails despite structural or screenshot checks passing.
- Conflicting requirements change what success means: retain the unresolved intent and seek the necessary decision while continuing independent work.
- A changed requirement is legitimate: preserve its provenance and re-evaluate affected evidence rather than prohibiting all criteria changes.

- Review the insertion in context for duplication and conflicting requirements. Preserve existing scope, evidence and authorization limits.
- Keep the inserted guidance under 150 words and within its existing reference. The deployed skill remains unchanged until this proposal is implemented.
- Review cases are intended reasoning checks, not completed independent evaluations. Implementation can use a focused walkthrough; any empirical efficacy claim requires separately authorized, qualified evidence.

## Implementation boundary

Do not copy this whole spec into the skill. Insert only the proposed guidance, adapting adjacent wording to avoid duplication. Preserve historical evidence and keep the proposal's status distinct from shipped guidance. If several proposals land together, GS-P03 and GS-P05 share a file: merge their changes sequentially and retain intent validation before enforcement and checker qualification.

## Disposition, 2026-10-11

Outcome scenarios and legitimate alternatives precede generated implementation. Evidence: implementation and research report (`resources/reports/context-architecture-research-2026-10-11.md`). Documentation implementation does not demonstrate efficacy.
