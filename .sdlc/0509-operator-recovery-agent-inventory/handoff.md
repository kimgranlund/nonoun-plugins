---
id: T-0509
title: "chore: guidance: align recovery behavior and Codex agent counts"
type: chore
status: ready
size: L1
priority: P3
depends: []
created: 2026-10-12
budget_usd: 5
---

## Goal
Align current conductor recovery guidance with implemented no-result retry behavior. Correct the current Codex declaration inventory.

## Intent
Do:
- Correct the conductor recovery paragraph to describe retry and explicit failure closure.
- Derive current inventory counts from generator output, including solo profiles.
- Regenerate agent profiles affected by shared conductor prose.

Non-goals: change approved model/effort defaults, redesign unrelated workflows, or modify concurrent work.

## Context
Host scope: Shared / Codex. Finding F7 in the [Astra review](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md).
- `plugins/sdlc-lite/agents/conductor.md:37` claims no-result recording closes the attempt as failed.
- `plugins/sdlc-lite/scripts/dispatch.py:1128` returns exit 2 and leaves it running unless explicitly failed.
- `docs/references/codex-role-execution.md:25` states 25 total / 21 base; the reviewed source generates 28 / 24.

## Evidence
- [Review finding F7](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md#f7--p3-align-current-operator-guidance-with-implemented-lifecycle-and-inventory).
- [Reproduction script](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py) and [observed results](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.txt).
- [Source hashes](../../docs/reports/2026-10-12-sdlc-lite-astra-review/source-snapshot.json) bind the review to HEAD `a3e2cd9b273ade52a66978f8e1938ad8e7fae948`.
- [Check summary](../../docs/reports/2026-10-12-sdlc-lite-astra-review/checks.txt) distinguishes passing focused checks from the incomplete full suite.

## Acceptance criteria
1. Given a prepared attempt with no result, run the existing dispatch no-result fixture and confirm guidance matches the actual retryable running state.
2. Given an explicit failure closure, confirm guidance distinguishes its terminal state from missing-result retry.
3. Derive base and alternate counts from `codex_roles.py` output and confirm the reference lists the current values and roles.
4. Both generators' `generate --check`, `dispatch.py selftest`, packaging checks, and `git diff --check` pass.
5. Inspect every changed local link. Preserve dated review evidence rather than rewriting historical counts.

## Constraints
- Read repository and scoped plugin guidance before changes. Pick the execution lane with `steps.py lane` before implementation.
- Preserve user edits, concurrent runs, worktrees, and approved model/effort settings.
- Edit authoritative sources and regenerate derived declarations; never hand-edit generated agents.
- Keep the dated report immutable. Store new validation evidence in a new dated report.
- Retain a rejecting defect case and a passing fixed case. Report required live checks as unverified if unavailable.
- The existing Progressive Context performance-contract link failure is unrelated; do not fix it in this ticket.
