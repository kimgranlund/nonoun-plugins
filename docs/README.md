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
- [Repository onboarding design review, third round](validation/repo-onboarding-design-review-3.md): dated independent review of the onboarding design at v0.5.
- [Conductor role routing probe](validation/role-routing-probe.md): dated live probe for T-0165, new conductor against 0.18.0.
- [Nested entry file loading](validation/nested-entry-file-loading.md): dated probe of which entry files Claude Code and Codex load, with token cost and limits.
- [Onboard live run](validation/onboard-live-run.md): dated live run of `onboard.py setup` on Claude Code and Codex, with a negative control.
- [Entry files live run](validation/entry-files-live-run.md): dated live run for T-0162 showing that planner, builder, and verifier on Claude Code and Codex list and read the entry file governing a step's files.
- [Dual-host readiness and recovery validation](readiness-recovery-validation.md): dated live trials, oracle outcomes, routing history, and scope limits.
