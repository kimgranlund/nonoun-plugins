---
id: GS-P07
type: spec
status: implemented
created: 2026-10-11
target: references/rapid-experiments.md
---
# Match isolation requirements to the experimental claim

Priority: high.

## Problem and responsibility

Rapid experiments (`references/rapid-experiments.md`) currently mixes evaluator protection, restrictions on author context, and host sandboxing. Its final paragraph requires an author allowlist even when the experiment only needs private grading protected. The same reference also duplicates runner flags and platform behavior owned by wireframe-review.

Generative Systems owns experiment validity and honest boundary claims. Runner owners maintain configuration, enforcement, and supported-platform instructions.

## Proposed replacement

Replace the current “Evaluator exclusion” section with a compact “Isolation by claim” section:

> Before dispatch, name the claim and the access boundary it requires. Fresh conversational context, protection of private grading, restriction to advertised author inputs, and host sandboxing are separate properties; do not infer one from another.
>
> For private grading, protect private assertions, reports, holdouts, and other lane outputs from author reads and writes. Qualify that boundary with synthetic forbidden-read and forbidden-write controls plus an allowed author-file control. Keep private material out of author prompts, enumerable author workspaces, and author-accessible HTTP endpoints. Folder separation alone is not enforcement.
>
> If the study claims the author had access only to specified inputs, additionally qualify an allowlist with a harmless outside-envelope canary. An unrelated readable file defeats that access claim, but does not alone demonstrate exposure to private grading. Account for every author-accessible tool relevant to the claimed boundary; terminal enforcement does not establish host-wide enforcement.
>
> Stop before dispatch when a boundary required by the frozen protocol cannot be qualified. A separately scoped diagnostic may proceed within existing authorization with its limitation explicit; it cannot confirm the stronger claim. Preserve and count accidental unisolated or contaminated attempts, audit available traces, and report uncertainty when access cannot be observed. Do not silently substitute these attempts for valid efficacy evidence.
>
> Use the selected runner's authoritative instructions for configuration and supported environments. Record its version, qualified boundary, and controls with the experiment; this skill supplies no sandbox guarantee.

Remove the copied CLI flag, configuration schema, and macOS guarantee. When a runner is selected, resolve its maintained instructions then; do not invent an unverified documentation path or require a runner-specific read for every experiment.

## Acceptance and verification

- Protected grading with an unrelated readable canary is distinguishable from a failed author-input allowlist.
- Read denial without write denial cannot qualify private-material integrity.
- Shell-only enforcement cannot support a claim covering unrestricted browser or file tools.
- Failure of a protocol-required boundary stops confirmation dispatch; a weaker diagnostic remains separately labelled.
- Ordinary generation and independent-consumer reuse checks do not automatically become isolated model studies.
- Inspect the proposed decisions through these scenarios. Any claim that enforcement actually works requires observed controls using the selected runner; document review is insufficient.

## Disposition, 2026-10-11

Replaced conflated exclusion section; removed copied runner flags and host guarantee. Evidence: implementation and research report (`resources/reports/context-architecture-research-2026-10-11.md`). Documentation implementation does not demonstrate efficacy.
