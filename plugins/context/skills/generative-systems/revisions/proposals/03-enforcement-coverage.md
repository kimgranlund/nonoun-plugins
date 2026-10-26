---
id: GS-P03
type: spec
status: implemented
created: 2026-10-11
target: references/verification-and-drift.md
---
# Separate feedback from enforcement and acceptance

## Problem and evidence boundary

The skill distinguishes validity and behavior, and already requires checker qualification. It does not explicitly distinguish advisory instructions, post-action feedback, prevention and acceptance, or require evidence for claimed execution-path coverage.

Source: the Oct 11, 2026 coverage review of Closed-loop generative UI system (`/Users/kimgranlund/Downloads/Closed-loop generative UI system.md`). This is a proposed reasoning improvement based on a documentation gap; no measured skill-efficacy gain is claimed.

## Scope and owner

Owner: `references/verification-and-drift.md`. Insert a short section immediately before “Checks that discriminate”. Use the existing routing from `SKILL.md`; no new mandatory read or entrypoint expansion is needed.

Keep host APIs, tool names, shell commands, framework bindings and CI configuration in the design document or the consuming project's implementation. Do not add a runtime, schema framework or new tracking system to this skill. This spec authorizes no evaluation dispatch or publication; it records proposed text only.

## Proposed skill text

## Identify what enforces a constraint

Separate advisory instructions, post-action feedback, pre-action blocking and final acceptance. Name the actions and environments each mechanism covers and what happens when it is absent, fails or times out. Feedback after an operation cannot prove that operation was prevented. A completed author session is not an acceptance result.

For a claimed enforcement boundary, qualify an allowed case and a deliberate violation through each materially distinct covered path, including failure of the gate itself. Keep uncovered paths explicit. Where acceptance is required, bind its evidence to the final artifact and relevant dependencies. Bound automatic repair by task-appropriate attempts or time; exhausted repair retains an unaccepted result and a next owner rather than weakening criteria.

## Acceptance and review cases

- A write bypasses a feedback adapter but the final acceptance check rejects it: report delayed rejection and the feedback coverage gap, not universal prevention.
- A gate is unavailable: distinguish its actual failure behavior and leave required acceptance unproven.
- A repair budget ends with unresolved failures: retain diagnostics and an unaccepted disposition rather than treating session completion as success.

- Review the insertion in context for duplication and conflicting requirements. Preserve existing scope, evidence and authorization limits.
- Keep the inserted guidance under 150 words and within its existing reference. The deployed skill remains unchanged until this proposal is implemented.
- Review cases are intended reasoning checks, not completed independent evaluations. Implementation can use a focused walkthrough; any empirical efficacy claim requires separately authorized, qualified evidence.

## Implementation boundary

Do not copy this whole spec into the skill. Insert only the proposed guidance, adapting adjacent wording to avoid duplication. Preserve historical evidence and keep the proposal's status distinct from shipped guidance. If several proposals land together, GS-P03 and GS-P05 share a file: merge their changes sequentially and retain intent validation before enforcement and checker qualification.

## Disposition, 2026-10-11

Enforcement and acceptance separated after intent, before checker controls. Evidence: implementation and research report (`resources/reports/context-architecture-research-2026-10-11.md`). Documentation implementation does not demonstrate efficacy.
