---
id: T-0508
title: "bug: ask: discover blockers in every supported ticket layout"
type: bug
status: ready
size: L2
priority: P2
depends: []
created: 2026-10-12
budget_usd: 30
---

## Goal
Discover blocked and deferred tickets in every supported ticket layout. Resolve task filters from the repository root.

## Intent
Do:
- Resolve configured ticket paths from the project root.
- Apply task filtering separately from root discovery.
- Preserve closed-ticket exclusion and question batching.

Non-goals: change approved model/effort defaults, redesign unrelated workflows, or modify concurrent work.

## Repro
1. Run `python3 docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` from the repository root.
2. Compare the flat-layout blocked-ticket searches.
3. Inspect `plugins/sdlc-lite/skills/ask/SKILL.md:24`.

## Expected
Flat and topics layouts produce the same open-question inventory. Supplying a task directory does not change path resolution.

## Actual
The hard-coded `.sdlc/tickets` search exits 2 and misses the flat blocked ticket.
Searching the actual `.sdlc` root finds it. Later verdict searches cannot recover a ticket without result files.

## Context
Host scope: Shared. Finding F6 in the [Astra review](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md).
- `plugins/sdlc-lite/skills/ask/SKILL.md:24` assumes a ticket root.
- `plugins/sdlc-lite/skills/ticket/SKILL.md:23` supports flat layout and opt-in ticket roots.
- Use existing `tickets.py` layout resolution; do not create another layout authority.

## Evidence
The saved probe script is diagnostic and requires PyYAML, Git, Bash, and jq. Its exit code alone does not verify a fix.
Compare the relevant observations with the acceptance criteria; add discriminating assertions to the owning regression suite.

- [Review finding F6](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md#f6--p2-make-the-open-question-sweep-honor-the-ticket-layout).
- [Reproduction script](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py) and [observed results](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.txt).
- [Source hashes](../../docs/reports/2026-10-12-sdlc-lite-astra-review/source-snapshot.json) bind the review to HEAD `a3e2cd9b273ade52a66978f8e1938ad8e7fae948`.
- [Check summary](../../docs/reports/2026-10-12-sdlc-lite-astra-review/checks.txt) distinguishes passing focused checks from the incomplete full suite.

## Acceptance criteria
1. Given identical blocked and deferred records, flat, ticket-root, and topics fixtures produce the same open-question inventory.
2. Given a supplied task directory, the sweep uses the repository configuration and limits results to the requested scope.
3. Resolved and closed tickets do not contribute unresolved questions.
4. The flat blocked fixture fails against the baseline sweep and passes after the fix; missing directories are surfaced accurately.
5. Run affected ticket/layout regression tests, `python3 plugins/sdlc-lite/scripts/check.py`, packaging checks, and `git diff --check`.
6. Exercise the revised `/ask` instructions against a throwaway flat-layout project with a blocker and retain the observed inventory.

## Constraints
- Read repository and scoped plugin guidance before changes. Pick the execution lane with `steps.py lane` before implementation.
- Preserve user edits, concurrent runs, worktrees, and approved model/effort settings.
- Edit authoritative sources and regenerate derived declarations; never hand-edit generated agents.
- Keep the dated report immutable. Store new validation evidence in a new dated report.
- Retain a rejecting defect case and a passing fixed case. Report required live checks as unverified if unavailable.
- The existing Progressive Context performance-contract link failure is unrelated; do not fix it in this ticket.
