# Documentation

- [Progressive Context specifications](generative-constructs/README.md): lifecycle, context architecture and browser/A2UI proposals.
- [Progressive Context plugin specification](generative-constructs/progressive-context-plugin.md): scope and packaging decisions.
- [Plugin compatibility and validation](plugin-compatibility.md): shipped behavior, dependencies and test boundaries.

- [Native Codex role execution](codex-role-execution.md): predefined agents, pipeline backend, setup and validation.
- [Repository onboarding](repo-onboarding/README.md): proposed entry files, default docs layout, document reorganization, and a reference on host loading.

- [Ticket stages and message bus](ticket-stages/README.md): the `.sdlc/` router and the opt-in `tickets/` root (built), the cross-harness mailbox and its `messenger` agent (built); stage folders remain a proposal.
- [Idle-host watcher design](ticket-stages/watcher-design.md): proposed external watcher that resumes an idle host when a message arrives.
- [Idle-host watcher design review](validation/idle-host-watcher-design-review.md): dated independent review of the watcher design, ready after fixes, with four blockers and the decision it needs.

- [Lean SDLC design review, second round](validation/lean-sdlc-design-review-2.md): dated second architect review of the lean SDLC design at v0.3, ready after fixes, and what v0.4 changed.
- [Lean SDLC design review](validation/lean-sdlc-design-review.md): dated independent architect review of the lean SDLC design at v0.1 and the changes made in v0.2.
- [Lean SDLC](lean-sdlc/README.md): proposed lean chain, topic sub-folders as the default `.sdlc/` layout, a single plan record, and conductor batching, with measured baselines.

- [SDLC implementation reference](maintenance/sdlc-internals.md): selectively loaded runner and workflow details.
- [Claude hook maintenance](maintenance/claude-hooks.md): host-specific enforcement and probes.
- [Shared run operations](../plugins/sdlc-lite/skills/handoff-format/run-operations.md): readiness, routing records, and interruption recovery for both hosts.
- [Repository onboarding design review](validation/repo-onboarding-design-review.md): dated independent review of the onboarding design at v0.1.
- [Repository onboarding design review, second round](validation/repo-onboarding-design-review-2.md): dated independent review of the onboarding design at v0.4.
- [Repository onboarding design review, third round](validation/repo-onboarding-design-review-3.md): dated independent review of the onboarding design at v0.5.
- [Codex tier mirror check](validation/codex-tier-mirror-2026-09-30.md): live check of every Codex model and effort pair and of the verifier swap.
- [Planner L3 on Opus xhigh](validation/planner-l3-opus-2026-09-30.md): dated decision moving Claude planner L3 from Fable to Opus xhigh, with recorded-cost basis, reviewer consequence, and limits.
- [Haiku alias probe](validation/haiku-alias-2026-09-30.md): dated probe showing the `haiku` alias resolves to Sonnet 5.5 on a Max login, and the pinned `claude-haiku-4-5` id.
- [Messages idle-host limit](validation/messages-idle-host-limit-2026-10-01.md): dated correction stating that the messenger cannot wake an idle host, the evidence, and the workaround.
- [Release 0.20.3](validation/release-0.20.3.md): `messages.py wait`, the role-result schema, `footprint.py`, the lean lane text, and the idle-host limit, how they were verified, upgrade notes, and known limits.
- [Release 0.20.2](validation/release-0.20.2.md): the ticket root and router, mailbox, and messenger agent, how they were verified, upgrade notes, and known limits.
- [Release 0.20.1](validation/release-0.20.1.md): the scout pin and planner L3 on Opus, how they were verified, and known limits.
- [Release 0.20.0](validation/release-0.20.0.md): what shipped since 0.19.0, how it was verified, upgrade notes, and known limits.
- [Release 0.19.0](validation/release-0.19.0.md): what shipped, how each change was verified, and known limits.
- [Conductor role routing probe](validation/role-routing-probe.md): dated live probe for T-0165, new conductor against 0.18.0.
- [Nested entry file loading](validation/nested-entry-file-loading.md): dated probe of which entry files Claude Code and Codex load, with token cost and limits.
- [Onboard live run](validation/onboard-live-run.md): dated live run of `onboard.py setup` on Claude Code and Codex, with a negative control.
- [Entry files live run](validation/entry-files-live-run.md): dated live run for T-0162 showing that planner, builder, and verifier on Claude Code and Codex list and read the entry file governing a step's files.
- [Agent spawn hook live run](validation/agent-spawn-hook-live-run.md): dated live run for T-0166 showing that a conductor session sends `agent_type` `sdlc-lite:conductor` and that `block-role-spawn.sh` denies an `sdlc-lite:scout` spawn and allows a `general-purpose` one.
- [Plan reviewer live run](validation/plan-reviewer-live-run.md): dated live run for T-0171 showing that the plan-reviewer rejects a defective plan on Claude Code and Codex, `steps.py split` refuses it, and a sound plan passes, builds, and verifies.
- [Ticket root and router live run](validation/ticket-root-router-live-run.md): dated live run for T-0175 showing the router block change as a ticket moves proposed to ready to done under `ticket_root: tickets`, and a fresh-role claim and close run recorded as unverified (the role reached `tickets/AGENTS.md` through nested-memory loading).
- [Messages live run](validation/messages-live-run.md): dated live run for T-0179 showing that a fresh Claude Code role and a fresh Codex role, given only a message path and no skill, read, reply, and ack from the entry files alone, with the messenger on both hosts and a negative control.
- [Messages wait live run](validation/messages-wait-live-run.md): dated live run for T-0181 in which a fresh Claude Code host and a fresh Codex host were each told to make one `messages.py wait` call, then read, reply, and ack; Claude Code pass, Codex pass.
- [Dual-host readiness and recovery validation](readiness-recovery-validation.md): dated live trials, oracle outcomes, routing history, and scope limits.
