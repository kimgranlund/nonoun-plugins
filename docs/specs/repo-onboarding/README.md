# Repository onboarding

Proposals for preparing a repository that adopts SDLC. The design is implemented, and so are the reorganization's inventory and apply; glob classification is not.

- [Entry files and docs layout](design.md): the `onboard` skill, entry file rules, upsert behavior, default layout, and templates. Ticket T-0160. Role access is ticket T-0162.
- [Goals and KPIs](goals-and-kpi.md): the `goals/` and `kpi/` homes, the file shapes, and checks G-1 to G-5. Ticket T-0392.
- [Document reorganization](../../planning/repo-onboarding/reorganization.md): rules for plan, approval, and apply, with how each open finding was settled. Spike T-0161, apply T-0233.
- [Reorganization plan procedure](../../planning/repo-onboarding/reorganization-plan-procedure.md): a read-only inventory, a model-written plan, then `reorg.py` applies the approved plan. Tickets T-0232 and T-0233.
- [Docs schema](../../planning/docs-schema/README.md): the strict folder schema that reorganization targets.
- [Layered context pattern](../../references/layered-context-pattern.md): reference on how Claude Code and Codex load nested entry files.

Evidence:

- [Design review](../../reports/repo-onboarding-design-review.md): independent review of design v0.1.
- [Design review, second round](../../reports/repo-onboarding-design-review-2.md): independent review of design v0.4.
- [Design review, third round](../../reports/repo-onboarding-design-review-3.md): independent review of design v0.5.
- [Nested entry file loading](../../reports/nested-entry-file-loading.md): live probe on both hosts.
- [Onboard live run](../../reports/onboard-live-run.md): live run gate on both hosts, with the negative control.
- [Reorganization inventory live run](../../reports/reorg-inventory-live-run.md): `inventory.py` on two repositories and one plan, with a spot check.
- [Reorganization apply live run](../../reports/reorg-apply-live-run.md): `reorg.py` moving four documents in a clone of this repository, with the refusals and link counts.
