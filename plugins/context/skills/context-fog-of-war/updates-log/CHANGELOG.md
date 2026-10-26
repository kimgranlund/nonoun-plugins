# Changelog

Newest first. Each row links to its change set's folder; the folder's `changelog.md` holds the detail and front matter.

| Date | Change set | Verification |
|---|---|---|
| 2026-10-25 | [sync the source project to the installed version](20261025-source-project-sync/changelog.md) | Byte parity across all three copies; project 143 tests and skill 51 tests pass |
| 2026-10-25 | [reconcile Claude and Codex skill copies](20261025-claude-codex-reconcile/changelog.md) | Byte parity; 51 tests in each copy; four historical clipped returns detected from each |
| 2026-10-25 | [Claude returned-output truncation markers](20261025-claude-truncation/changelog.md) | 51 tests; four historical clipped returns detected; original SHA256 unchanged |
| 2026-10-20 | [sync reviewed lessons to Claude](20261020-claude-sync/changelog.md) | Source parity; both validators; 81 tests passed |
| 2026-10-20 | [CLI progressive-routing lessons](20261020-cli-routing-lessons/changelog.md) | 49 tests; skill validation; 32 local links; independent scenario review passed |
| 2026-10-16 | [progressive discovery and task-specific entry routes](20261016-progressive-discovery/changelog.md) | 3 real command tasks before/after; 192 tests; benchmark unchanged |
| 2026-10-16 | [reconcile project triage with installed runtime learnings](20261016-project-reconciliation/changelog.md) | project 143 tests; skill 49 tests; unchanged benchmark scores |
| 2026-10-16 | [apply the open items from round 7, the contract audit and the lookup gaps](20261016-open-items/changelog.md) | adversarial challenge (Sonnet) plus rebuttal, then independent verifier L2 pass (2026-10-16); skill tests 46 of 46 |
| 2026-10-16 | [field test of the checklist and the contract audit link mode (round 7)](20261016-round-7-field-test/changelog.md) | field test verified by an independent verifier (L2 pass); findings only, no skill file changed |
| 2026-10-16 | [contract audit mode (static review of guidance and contract surfaces)](20261016-contract-audit/changelog.md) | independent verifier L3, try 1 fail (precision limit), try 2 pass (2026-10-16); skill tests 35 of 35 |
| 2026-10-16 | [shell_lookup false negatives and a merged-output batch fixture](20261016-lookup-gaps/changelog.md) | independent verifier L2 pass (2026-10-16); skill tests 24 of 24 |
| 2026-10-16 | [field test of the script fixes on real CLI traces](20261016-cli-trace-field-test/changelog.md) | field test only, no independent verifier; this entry records findings, no skill file changed |
| 2026-10-16 | [autonomous checklist fixes from the round 6 field test](20261016-checklist-fixes/changelog.md) | independent verifier L2 pass (2026-10-16); skill tests 20 of 20 |
| 2026-10-16 | [field test of the autonomous checklist on a runtime-harness bundle](20261016-round-6-field-test/changelog.md) | field test verified by an independent verifier (L2 pass); this entry records findings only, no skill file changed |
| 2026-10-16 | [SKILL.md restructure for autonomous runs](20261016-skill-md-restructure/changelog.md) | independent verifier L2 pass (2026-10-16); skill tests 20 of 20 |
| 2026-10-16 | [runtime-harness learnings, AGENTS.md, three test fixes](20261016-runtime-harness-learnings/changelog.md) | independent verifier L2 pass (2026-10-16); skill tests 20 of 20 |
