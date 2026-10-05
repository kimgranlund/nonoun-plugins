# Repository onboarding

Proposals for preparing a repository that adopts SDLC Lite. The design is implemented; the reorganization is not.

- [Entry files and docs layout](design.md): the `onboard` skill, entry file rules, upsert behavior, default layout, and templates. Ticket T-0160. Role access is ticket T-0162.
- [Document reorganization](reorganization.md): draft rules for plan, approval, and apply, with open findings. Spike T-0161.
- [Reorganization plan procedure](reorganization-plan-procedure.md): step 1, a read-only inventory then a model-written plan; apply is not built. Tickets T-0232 and T-0233.
- [Docs schema](../docs-schema/README.md): the strict folder schema that reorganization targets.
- [Layered context pattern](layered-context-pattern.md): reference on how Claude Code and Codex load nested entry files.

Evidence:

- [Design review](../validation/repo-onboarding-design-review.md): independent review of design v0.1.
- [Design review, second round](../validation/repo-onboarding-design-review-2.md): independent review of design v0.4.
- [Design review, third round](../validation/repo-onboarding-design-review-3.md): independent review of design v0.5.
- [Nested entry file loading](../validation/nested-entry-file-loading.md): live probe on both hosts.
- [Onboard live run](../validation/onboard-live-run.md): live run gate on both hosts, with the negative control.
- [Reorganization inventory live run](../validation/reorg-inventory-live-run.md): `inventory.py` on two repositories and one plan, with a spot check.
