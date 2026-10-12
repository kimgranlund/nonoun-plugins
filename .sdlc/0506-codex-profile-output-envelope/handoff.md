---
id: T-0506
title: "bug: Codex profiles: reconcile fingerprint and report contracts"
type: bug
status: ready
size: L2
priority: P2
depends: []
created: 2026-10-12
budget_usd: 30
---

## Goal
Define a consistent fingerprint envelope and role report body for every generated Codex profile.

## Intent
Do:
- Define the Codex envelope separately from the shared role body, or explicitly exempt it during generation.
- State whether recorded results retain or remove the envelope.
- Regenerate profiles from their authoritative sources.

Non-goals: change approved model/effort defaults, redesign unrelated workflows, or modify concurrent work.

## Repro
1. Run `python3 docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` from the repository root.
2. Inspect the contradictory profile count.
3. Compare the fingerprint instruction with the scout first-heading rule.

## Expected
A role can satisfy its fingerprint requirement and output contract simultaneously. Stored-result handling of the envelope is explicit.

## Actual
Twenty-three generated profiles require both no text before the first heading and a `profile:` first line.
No live malformed report was observed. The source instructions conflict.

## Context
Host scope: Codex. Finding F4 in the [Astra review](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md).
- `plugins/sdlc-lite/scripts/codex_roles.py:104` appends the fingerprint requirement.
- `plugins/sdlc-lite/agents/scout.md:16` requires the first heading first.
- Read `plugins/sdlc-lite/scripts/results.py` and `adapters/codex/instructions.md` for report handling.

## Evidence
The saved probe script is diagnostic and requires PyYAML, Git, Bash, and jq. Its exit code alone does not verify a fix.
Compare the relevant observations with the acceptance criteria; add discriminating assertions to the owning regression suite.

- [Review finding F4](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md#f4--p2-make-the-codex-fingerprint-envelope-compatible-with-role-output).
- [Reproduction script](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py) and [observed results](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.txt).
- [Source hashes](../../docs/reports/2026-10-12-sdlc-lite-astra-review/source-snapshot.json) bind the review to HEAD `a3e2cd9b273ade52a66978f8e1938ad8e7fae948`.
- [Check summary](../../docs/reports/2026-10-12-sdlc-lite-astra-review/checks.txt) distinguishes passing focused checks from the incomplete full suite.

## Acceptance criteria
1. Given every generated profile, its output instructions define one compatible envelope/body format.
2. A current fingerprinted report passes through the actual native exchange and role-result parser without losing required sections.
3. The role-body parser rejects a malformed body even when its envelope is valid.
4. Retain an observed failing contradictory-contract fixture and a passing corrected fixture in `codex-selftest.py`.
5. `codex-selftest.py`, both generated-agent parity checks, and packaging checks pass.
6. A fresh named-agent Codex run returns the envelope and complete role sections. If the host cannot select named roles, record live validation as unverified.

## Constraints
- Read repository and scoped plugin guidance before changes. Pick the execution lane with `steps.py lane` before implementation.
- Preserve user edits, concurrent runs, worktrees, and approved model/effort settings.
- Edit authoritative sources and regenerate derived declarations; never hand-edit generated agents.
- Keep the dated report immutable. Store new validation evidence in a new dated report.
- Retain a rejecting defect case and a passing fixed case. Report required live checks as unverified if unavailable.
- The existing Progressive Context performance-contract link failure is unrelated; do not fix it in this ticket.
