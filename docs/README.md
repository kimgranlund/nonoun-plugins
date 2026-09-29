# Documentation

- [Progressive Context specifications](generative-constructs/README.md): lifecycle, context architecture and browser/A2UI proposals.
- [Progressive Context plugin specification](generative-constructs/progressive-context-plugin.md): scope and packaging decisions.
- [Plugin compatibility and validation](plugin-compatibility.md): shipped behavior, dependencies and test boundaries.

- [Native Codex role execution](codex-role-execution.md): predefined agents, pipeline backend, setup and validation.
- [Repository onboarding](repo-onboarding/README.md): proposed entry files, default docs layout, document reorganization, and a reference on host loading.

- [SDLC implementation reference](maintenance/sdlc-internals.md): selectively loaded runner and workflow details.
- [Claude hook maintenance](maintenance/claude-hooks.md): host-specific enforcement and probes.
- [Shared run operations](../plugins/sdlc-lite/skills/handoff-format/run-operations.md): readiness, routing records, and interruption recovery for both hosts.
- [Repository onboarding design review](validation/repo-onboarding-design-review.md): dated independent review of the onboarding design at v0.1.
- [Repository onboarding design review, second round](validation/repo-onboarding-design-review-2.md): dated independent review of the onboarding design at v0.4.
- [Nested entry file loading](validation/nested-entry-file-loading.md): dated probe of which entry files Claude Code and Codex load, with token cost and limits.
- [Dual-host readiness and recovery validation](readiness-recovery-validation.md): dated live trials, oracle outcomes, routing history, and scope limits.
