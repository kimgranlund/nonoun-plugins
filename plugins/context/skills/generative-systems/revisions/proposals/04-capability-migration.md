---
id: GS-P04
type: spec
status: implemented
created: 2026-10-11
target: references/maintaining-knowledge.md
---
# Version migration debt and capability retirement

## Problem and evidence boundary

The existing reference retires stale knowledge and preserves evidence. It has little guidance on introducing new constraints into existing artifacts or retiring capabilities while consumers still depend on them.

Source: the Oct 11, 2026 coverage review of Closed-loop generative UI system (`/Users/kimgranlund/Downloads/Closed-loop generative UI system.md`). This is a proposed reasoning improvement based on a documentation gap; no measured skill-efficacy gain is claimed.

## Scope and owner

Owner: `references/maintaining-knowledge.md`. Insert a short conditional section before “Budget and publication”. Use the existing routing from `SKILL.md`; no new mandatory read or entrypoint expansion is needed.

Keep host APIs, tool names, shell commands, framework bindings and CI configuration in the design document or the consuming project's implementation. Do not add a runtime, schema framework or new tracking system to this skill. This spec authorizes no evaluation dispatch or publication; it records proposed text only.

## Proposed skill text

## Migrate existing consumers

When introducing a constraint into an existing system, distinguish reviewed initialization of legacy debt from later regressions. Version the baseline with its rule and source revision. Match debt by qualified occurrence identity: removing one old violation must not authorize a new one elsewhere. Review ambiguous moves or mappings rather than silently resetting the baseline.

For capability deprecation, retain replacement and migration guidance for affected consumers even when new-use discovery excludes the capability. Retirement requires evidence about supported consumers and compatibility, not merely an empty violation baseline. Record unresolved external or dynamic uses and the applicable retirement scope. Keep these controls conditional on migration work; a small authoring change does not require a new baseline framework.

## Acceptance and review cases

- Enabling a new rule may initialize reviewed legacy debt; an ordinary feature change cannot use that exception to reset the baseline.
- One old violation is removed and one new violation introduced: the unchanged count does not establish compliance.
- A baseline is empty but a supported consumer still references a deprecated capability: retirement remains unsupported until migration or an explicit compatibility decision.

- Review the insertion in context for duplication and conflicting requirements. Preserve existing scope, evidence and authorization limits.
- Keep the inserted guidance under 150 words and within its existing reference. The deployed skill remains unchanged until this proposal is implemented.
- Review cases are intended reasoning checks, not completed independent evaluations. Implementation can use a focused walkthrough; any empirical efficacy claim requires separately authorized, qualified evidence.

## Implementation boundary

Do not copy this whole spec into the skill. Insert only the proposed guidance, adapting adjacent wording to avoid duplication. Preserve historical evidence and keep the proposal's status distinct from shipped guidance. If several proposals land together, GS-P03 and GS-P05 share a file: merge their changes sequentially and retain intent validation before enforcement and checker qualification.

## Disposition, 2026-10-11

Conditional migration/deprecation guidance added. Evidence: implementation and research report (`resources/reports/context-architecture-research-2026-10-11.md`). Documentation implementation does not demonstrate efficacy.
