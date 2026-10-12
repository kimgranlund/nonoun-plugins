---
id: T-0505
title: "bug: Claude hooks: freeze handoffs during prepared attempts"
type: bug
status: ready
size: L3
priority: P2
depends: []
created: 2026-10-12
budget_usd: 60
---

## Goal
Activate handoff warning and deny modes throughout prepared attempts. Release protection after completion or recovery.

## Intent
Do:
- Connect the edit hook to one authoritative live-attempt lifecycle.
- Cover prepare, record, explicit failure, and recovery transitions.
- Keep legacy runner marker behavior consistent.

Non-goals: change approved model/effort defaults, redesign unrelated workflows, or modify concurrent work.

## Repro
1. Run `python3 docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` from the repository root.
2. Inspect the prepared attempt status and running-marker count.
3. Compare the handoff guard result before and after the positive-control marker is added.

## Expected
A live prepared attempt activates the configured handoff edit guard. Completed or recovered attempts stop activating it.

## Actual
Prepare creates a running attempt but no `*.running` marker. The deny hook exits 0.
Adding the expected marker makes the same edit fail with exit 2.
Completion-time stale-input hashing still exists; this finding concerns edit-time enforcement.

## Context
Host scope: Claude. Finding F3 in the [Astra review](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md).
- `plugins/sdlc-lite/hooks/warn-handoff-edit.sh:14` reads running markers only.
- `plugins/sdlc-lite/scripts/dispatch.py:815` writes prepared attempt and dispatch records.
- Read `plugins/sdlc-lite/scripts/run_lifecycle.py` and the shared run-operations reference before changing ownership.

## Evidence
The saved probe script is diagnostic and requires PyYAML, Git, Bash, and jq. Its exit code alone does not verify a fix.
Compare the relevant observations with the acceptance criteria; add discriminating assertions to the owning regression suite.

- [Review finding F3](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md#f3--p2-connect-claude-handoff-freezing-to-prepared-attempts).
- [Reproduction script](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py) and [observed results](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.txt).
- [Source hashes](../../docs/reports/2026-10-12-sdlc-lite-astra-review/source-snapshot.json) bind the review to HEAD `a3e2cd9b273ade52a66978f8e1938ad8e7fae948`.
- [Check summary](../../docs/reports/2026-10-12-sdlc-lite-astra-review/checks.txt) distinguishes passing focused checks from the incomplete full suite.

## Acceptance criteria
1. Given a real prepared running attempt, editing its handoff warns in warn mode and rejects in deny mode.
2. Given completed, failed, or recovered attempts, editing the handoff does not report a live attempt.
3. Given a live attempt owned by another run, recovery preserves its ownership and edit protection.
4. The prepared-attempt fixture fails on the reviewed baseline without manually creating markers; the corrected integration passes.
5. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`, `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`, and `bash plugins/sdlc-lite/scripts/hook-selftest.sh` pass.
6. A focused fresh-Claude run observes the handoff guard during a prepared role and its release after recording.

## Constraints
- Read repository and scoped plugin guidance before changes. Pick the execution lane with `steps.py lane` before implementation.
- Preserve user edits, concurrent runs, worktrees, and approved model/effort settings.
- Edit authoritative sources and regenerate derived declarations; never hand-edit generated agents.
- Keep the dated report immutable. Store new validation evidence in a new dated report.
- Retain a rejecting defect case and a passing fixed case. Report required live checks as unverified if unavailable.
- The existing Progressive Context performance-contract link failure is unrelated; do not fix it in this ticket.
