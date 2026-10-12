---
id: T-0503
title: "bug: Claude agents: serialize valid YAML descriptions"
type: bug
status: ready
size: L2
priority: P1
depends: []
created: 2026-10-12
budget_usd: 30
---

## Goal
Serialize valid YAML descriptions for generated Claude agents and the shared conductor. Preserve role behavior and approved model settings.

## Intent
Do:
- Parse the source description and serialize the complete augmented value once.
- Fix the shared conductor description and regenerate derived agents.
- Add real YAML parsing to declaration validation.

Non-goals: change approved model/effort defaults, redesign unrelated workflows, or modify concurrent work.

## Repro
1. Run `python3 docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` from the repository root.
2. Inspect the agent YAML errors in the output.
3. Inspect `plugins/sdlc-lite/agents/builder-L2.md:3` and `plugins/sdlc-lite/agents/conductor.md:3`.

## Expected
Every agent frontmatter block parses as YAML. Generated descriptions retain their complete text.

## Actual
The reviewed baseline has 23 invalid agent frontmatter blocks: 22 generated declarations and the shared conductor.
The builder description appends `Level L2: opus low.` outside its quoted scalar.
The conductor description contains an unquoted colon-space sequence.
Claude plugin validation passes; actual agent-loading impact is unverified.

## Context
Host scope: Claude. Finding F1 in the [Astra review](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md).
- `plugins/sdlc-lite/scripts/claude_roles.py:104` retains source scalar quoting.
- `plugins/sdlc-lite/scripts/claude_roles.py:180` appends the level suffix.
- `plugins/sdlc-lite/agents/conductor.md:3` needs valid scalar serialization.

## Evidence
The saved probe script is diagnostic and requires PyYAML, Git, Bash, and jq. Its exit code alone does not verify a fix.
Compare the relevant observations with the acceptance criteria; add discriminating assertions to the owning regression suite.

- [Review finding F1](../../docs/reports/2026-10-12-sdlc-lite-astra-review.md#f1--p1-repair-invalid-yaml-in-claude-agent-definitions).
- [Reproduction script](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py) and [observed results](../../docs/reports/2026-10-12-sdlc-lite-astra-review/probes.txt).
- [Source hashes](../../docs/reports/2026-10-12-sdlc-lite-astra-review/source-snapshot.json) bind the review to HEAD `a3e2cd9b273ade52a66978f8e1938ad8e7fae948`.
- [Check summary](../../docs/reports/2026-10-12-sdlc-lite-astra-review/checks.txt) distinguishes passing focused checks from the incomplete full suite.

## Acceptance criteria
1. Given every current agent file, when its frontmatter is parsed, then every parse succeeds and required fields retain their values.
2. Given the saved malformed description, when declaration validation runs, then it rejects that fixture; the corrected scalar passes.
3. `python3 plugins/sdlc-lite/scripts/claude_roles.py selftest` and both generators' `generate --check` pass.
4. `python3 scripts/check-packaging.py` passes.
5. In a fresh Claude session, discover the generated agents and complete one prepared scout dispatch in a throwaway project. Retain actual discovery and result evidence.

## Constraints
- Read repository and scoped plugin guidance before changes. Pick the execution lane with `steps.py lane` before implementation.
- Preserve user edits, concurrent runs, worktrees, and approved model/effort settings.
- Edit authoritative sources and regenerate derived declarations; never hand-edit generated agents.
- Keep the dated report immutable. Store new validation evidence in a new dated report.
- Retain a rejecting defect case and a passing fixed case. Report required live checks as unverified if unavailable.
- The existing Progressive Context performance-contract link failure is unrelated; do not fix it in this ticket.
