---
id: T-0507
title: "bug: Codex exchange: enforce the dispatched profile binding"
type: bug
status: done
size: L3
priority: P2
depends: ["T-0506"]
created: 2026-10-12
budget_usd: 60
---

## Goal
Bind each native request to its dispatched profile fingerprint. Reject missing or stale fingerprints in normal responses.

## Intent
Do:
- Persist the expected profile fingerprint in the request and relevant attempt record.
- Validate normal responses against that captured binding.
- Describe pre-edit checking accurately; a final-report check does not prove it happened before edits.

Non-goals: change approved model/effort defaults, redesign unrelated workflows, or modify concurrent work.

## Repro
1. Run `python3 docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` from the repository root.
2. Compare missing, stale, and current fingerprint cases.
3. Compare helper classifications with exchange acceptance.

## Expected
A normal response is accepted only when its fingerprint matches the binding captured at dispatch. Explicit execution failures remain reportable.

## Actual
The helper reports unknown, refused, and ready respectively. All three exchanges still exit 0 and record `received`.
The request carries no expected fingerprint. Manual conductor instructions provide the current freshness check.

## Context
Host scope: Codex. Finding F5 in the [Astra review](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md).
- `plugins/sdlc-lite/scripts/codex_roles.py:117` implements the handshake helper.
- `plugins/sdlc-lite/scripts/codex_exchange.py:53` builds the request.
- `plugins/sdlc-lite/scripts/codex_exchange.py:89` accepts responses.
- Read lifecycle ownership and cancellation contracts before changing exchange state.

## Evidence
The saved probe script is diagnostic and requires PyYAML, Git, Bash, and jq. Its exit code alone does not verify a fix.
Compare the relevant observations with the acceptance criteria; add discriminating assertions to the owning regression suite.

- [Review finding F5](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md#f5--p2-bind-codex-freshness-checks-to-the-native-exchange).
- [Reproduction script](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py) and [observed results](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.txt).
- [Source hashes](../../docs/reports/2026-10-12-sdlc-lite-astra-review/source-snapshot.json) bind the review to HEAD `a3e2cd9b273ade52a66978f8e1938ad8e7fae948`.
- [Check summary](../../docs/reports/2026-10-12-sdlc-lite-astra-review/checks.txt) distinguishes passing focused checks from the incomplete full suite.

## Acceptance criteria
1. Given a captured binding, a matching normal response succeeds; missing and stale fingerprints cannot become accepted normal results.
2. Given profile files changed after dispatch, validation still uses the original request binding.
3. Given an explicit failed spawn, `--failed` releases the waiter and retains the failure reason without requiring a fabricated valid profile report.
4. Existing ownership, duplicate-response, destination, cancellation, and timeout controls still discriminate correctly.
5. Add actual exchange subprocess tests for all fingerprint cases; observe baseline missing/stale cases fail the new assertions.
6. `codex-selftest.py`, `lifecycle-selftest.py`, and packaging checks pass.
7. A fresh callable named-agent Codex run completes the bound exchange. Record unavailable host capabilities as unverified, without nesting a CLI or widening permissions.

## Constraints
- Read repository and scoped plugin guidance before changes. Pick the execution lane with `steps.py lane` before implementation.
- Preserve user edits, concurrent runs, worktrees, and approved model/effort settings.
- Edit authoritative sources and regenerate derived declarations; never hand-edit generated agents.
- Keep the dated report immutable. Store new validation evidence in a new dated report.
- Retain a rejecting defect case and a passing fixed case. Report required live checks as unverified if unavailable.
- The existing Progressive Context performance-contract link failure is unrelated; do not fix it in this ticket.

## Closed

2026-10-12: warnings acknowledged: all steps verifier pass; criterion 7 (live Codex named-agent exchange) is unverified and the report says so; the worktree-based control used a git archive export because the stray-worktree hook denied git worktree add; full suite ran in the land gates

> - Handoff criterion 7 is unverified. It asks for a fresh callable named-agent Codex run that completes the bound exchange. That run can't happen on this Claude host without nesting a CLI. The new dated report marks it unverified. The fingerprint cases were checked only with real waiter subprocesses and the `codex_exchange.py` CLI.
> - Step 1 criterion 3 was met by a substitute. `git worktree add` was denied by `block-stray-worktree.sh` because `SDLC_TMP_WORKTREES` was unset. Builder and verifier used a `git archive` export of base `07a5c289` instead. `cmp` showed its `codex_exchange.py` matched the base byte for byte. Each new test failed there on a real assertion.
> - The full `check.sh` was not run. It is left to the `fanout.py land` gate. `dispatch.py selftest` was run by the step 1 verifier and passed.
> - Steps 1, 2 and 3 all passed verification. There is no `process-deviations.md` in the artifacts dir or any step folder, so there are no process deviations.
