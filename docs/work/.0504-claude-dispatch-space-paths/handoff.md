---
id: T-0504
title: "bug: Claude dispatch: preserve handoff paths containing spaces"
type: bug
status: done
size: L2
priority: P2
depends: []
created: 2026-10-12
budget_usd: 30
---

## Goal
Allow prepared role dispatch from repository and task paths containing spaces. Preserve missing-dispatch rejection.

## Intent
Do:
- Define and parse an unambiguous handoff locator.
- Preserve supported explanatory text outside that locator.
- Quote the execution-tree path in generated shell instructions.

Non-goals: change approved model/effort defaults, redesign unrelated workflows, or modify concurrent work.

## Repro
1. Run `python3 docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` from the repository root.
2. Compare the prepared spawn results for `plain` and `with spaces`.
3. Inspect the rejected handoff locator in the hook diagnostic.

## Expected
The exact payload emitted by prepare passes the spawn hook for both paths. The execution-tree command preserves the complete path.

## Actual
The plain path passes with exit 0. The path containing spaces fails with exit 2.
The hook looks beside a truncated path ending in `/with`, although prepare emitted the complete handoff path.

## Context
Host scope: Claude. Finding F2 in the [Astra review](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md).
- `plugins/sdlc-lite/scripts/dispatch.py:778` emits the absolute handoff path.
- `plugins/sdlc-lite/hooks/block-role-spawn.sh:86` truncates at whitespace.
- `plugins/sdlc-lite/scripts/dispatch.py:780` emits the execution-tree command.
- `plugins/sdlc-lite/agents/conductor.md:41` describes trailing explanatory text.

## Evidence
The saved probe script is diagnostic and requires PyYAML, Git, Bash, and jq. Its exit code alone does not verify a fix.
Compare the relevant observations with the acceptance criteria; add discriminating assertions to the owning regression suite.

- [Review finding F2](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md#f2--p2-preserve-spaces-in-prepared-claude-handoff-paths).
- [Reproduction script](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py) and [observed results](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.txt).
- [Source hashes](../../docs/reports/2026-10-12-sdlc-lite-astra-review/source-snapshot.json) bind the review to HEAD `a3e2cd9b273ade52a66978f8e1938ad8e7fae948`.
- [Check summary](../../docs/reports/2026-10-12-sdlc-lite-astra-review/checks.txt) distinguishes passing focused checks from the incomplete full suite.

## Acceptance criteria
1. Given paths with spaces in the project and task directory, prepare emits payloads accepted unchanged by the actual spawn hook.
2. Given a missing dispatch record, the same hook rejects the spawn with its specific missing-record diagnostic.
3. Given supported explanatory text, the parser preserves the complete handoff path and excludes the explanation.
4. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` and `bash plugins/sdlc-lite/scripts/hook-selftest.sh` pass with these cases wired in.
5. A fresh Claude scout completes a prepared dispatch in a throwaway project whose path contains spaces.

## Constraints
- Read repository and scoped plugin guidance before changes. Pick the execution lane with `steps.py lane` before implementation.
- Preserve user edits, concurrent runs, worktrees, and approved model/effort settings.
- Edit authoritative sources and regenerate derived declarations; never hand-edit generated agents.
- Keep the dated report immutable. Store new validation evidence in a new dated report.
- Retain a rejecting defect case and a passing fixed case. Report required live checks as unverified if unavailable.
- The existing Progressive Context performance-contract link failure is unrelated; do not fix it in this ticket.

## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: .sdlc/0504-claude-dispatch-space-paths/handoff.md:63: "Store new validation evidence in a new dated report" is not done; no new file under docs/reports. A draft fail for this was dropped because line 63 is a Constraint, not one of the five acceptance criteria. The #5 live artifacts sat under the verifier tmp prefix and were removed with it, so this result file is the only record of that run. | plugins/sdlc-lite/scripts/dispatch.py:294: a path holding both whitespace and a literal `"` is emitted bare, so the gate still truncates it at the first space (the builder says the same). | plugins/sdlc-lite/scripts/fanout.py:487: `SOLO_SUBAGENT_PROMPT` still writes a bare `Handoff: {handoff}`. The value is the repo-relative ticket path (fanout.py:1784), which the hook joins to the payload cwd, so a spaced project path is unaffected; only a ticket folder name with a space would truncate.
