# SDLC Lite

Vocabulary: the product is `SDLC Lite` in prose; identifiers stay `sdlc-lite`, `SDLC_*` environment variables, `.sdlc/`, and the plugin and skill names.
Bare "SDLC" appears only where it means the software lifecycle in general; "lean lane" names only that one lane (not the product).
`scripts/check.py` fails on the retired spellings outside dated history (docs/reports, closed tickets, run workspaces, bench results).

Proposal, not implemented. Version 0.4, 2026-10-04.

- [Design](design.md): one design for four tickets filed from another repo's feedback: a lean chain (T-0189), topic sub-folders as the default `.sdlc/` layout (T-0190), a single plan record per ticket (T-0191), and a conductor rule for batching and skipping (T-0192). Includes measured baselines, a build order, migration, risks, and a validation plan.
- [Independent review](../../reports/lean-sdlc-design-review.md): the architect role's review of the design.
- [Second review](../../reports/lean-sdlc-design-review-2.md): ready after fixes; applied in v0.4.
- [Cost control addendum](cost-control.md): four items the lean tickets do not cover (spec gate, handoff freeze, replan delta with a planner checklist, per-ticket budget), measured on 2026-10-04 run records.
- [Cost control review](../../reports/lean-sdlc-cost-control-review.md): independent architect review of the addendum.
- [Gate lock admission](gate-lock-admission.md): design for review (T-0386), not implemented: gate_lock.py as the weighted shared admission authority, with the owner split, migration from old plugin paths, and regression cases. The maintainer's decision is pending.
- [Verifier held criteria](verifier-held-criteria.md): design (T-0400), approved and not built: the verifier reports `unmet-dependency <subject>` and `deferred <owner>` apart from fail, steps.py routes them to wait or hold instead of a rebuild, and a ticket cannot close while one is open.
- [plan-verification skill](plan-verification.md): design (T-0405), built in T-0407: a skill that captures an outcome, a measure with its before value, a rubric and a negative control for `plan-goal`, the two new `plan_check.py goal` rules with controls, and the build as its own ticket.
- [Plan doc, plan_done.py and run-plan](plan-doc-executor.md): design (T-0410), not built, awaiting approval: one plan file any builder tier can run with `/goal`, the new `plan_check.py plan` rules with controls, `plan_done.py` and its truth table, the `run-plan` skill, guardrails, the build tickets and the live-run plan.
- [Lane lifecycle](lane-lifecycle.md): design (T-0422), not built, awaiting approval: `lanes.py` open, close, sweep and wait so finished lanes stop piling up as worktrees and branches, the squash-merge landed test with its negative controls, the close truth table, ports, the checks, the build tickets, and a proposal-only cleanup of this repo's pile.
