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
- [Lean SDLC cost control](lean-sdlc/cost-control.md): proposed addendum with a spec gate, handoff freeze, replan delta with a planner checklist, and per-ticket budgets, measured on 2026-10-04 run records.
- [Lean SDLC cost control review](validation/lean-sdlc-cost-control-review.md): dated independent architect review of the cost-control addendum.
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
- [Handoff freeze live run](validation/handoff-freeze-live-run.md): dated live run for T-0212 (warn mode) showing the hook allows and logs an edit of a running handoff on Claude and blocks it in deny mode, plus the runner's stale_input flag and known limits.
- [Release 0.20.6](validation/release-0.20.6.md): solo-first fanout (`--lane`, `--max-lanes`, `--stagger`), unique `check.py` guard numbers, the skips guard for solo and full lanes, and the solo vs lean benchmark record, with upgrade notes and known limits.
- [Solo close live run](validation/solo-close-live-run.md): dated live run for T-0224 showing a conductor-started size M solo ticket closing with `tickets.py close --reason` while the skips guard is live, with the models used and the limits.
- [Fanout solo-first live run](validation/fanout-solo-live-run.md): dated live run for T-0221 showing four lanes (three size S, one size M) delivered by solo sessions through `fanout.py run`, merged, gated, and closed, with the models used and the limits.
- [Release 0.20.5](validation/release-0.20.5.md): the conductor rules, solo start path and routing texts, handoff freeze (warn mode), per-ticket budget, and the solo live run, with upgrade notes and known limits.
- [Release 0.20.4](validation/release-0.20.4.md): the supervisor, evals lock, proposals, lane script, spec gate, runner family rule, and the solo operator agent, how they were verified, upgrade notes, and known limits..
- [Release 0.20.3](validation/release-0.20.3.md): `messages.py wait`, the role-result schema, `footprint.py`, the lean lane text, and the idle-host limit, how they were verified, upgrade notes, and known limits.
- [Release 0.20.2](validation/release-0.20.2.md): the ticket root and router, mailbox, and messenger agent, how they were verified, upgrade notes, and known limits.
- [Solo vs lean benchmark](validation/solo-vs-lean-benchmark-2026-10-04.md): dated head-to-head of a single-session solo agent and the orchestrated chain on three real tickets, with cost, time, replans, caveats and the default-lane implication.
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
- [Runner family task dir live run](validation/runner-family-task-dir-live-run.md): dated live run for T-0195 showing that a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in step-1/, where the pre-fix run.sh kept Sonnet.
- [Carry forward live run](validation/carry-forward-live-run.md): dated live run for T-0202 in which a planner given a scout result with a Carry forward section cited its path and did not repeat the scout's search, while a planner given no scout result ran that search; the first planner read the result through a glob (`.sdlc/cf/*.md`), so the specified read_scout_result metric, which looks for the file name in tool inputs, recorded no.
- [Supervisor live run](validation/supervisor-live-run.md): dated live run for T-0183 in which supervisor.py woke an idle Claude Code host and an idle Codex host on new mail, in ephemeral and attached mode, with a dry-run control and a push-denial probe, after a first run that found a wake prompt gap and two probe defects, and three Codex wake reruns after a prompt fix; Claude Code pass, Codex pass. Codex wake arm after the fix: 3 of 3 passed.
- [Solo live run](validation/solo-live-run.md): dated live run for T-0216 in which `steps.py lane` printed `solo` for a size-M ticket and the `solo` agent delivered it at tier M on Claude Code (Sonnet xhigh, Fable verifier) and Codex (`sdlc-solo-l2` on gpt-6.1-sol high, gpt-6-astra verifier); both passed a hidden check and their verifier, and the Codex solo did not launch its own verifier.
- [Dual-host readiness and recovery validation](readiness-recovery-validation.md): dated live trials, oracle outcomes, routing history, and scope limits.
