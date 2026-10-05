## Goal
Independently verify T-0243: branch boundary adds checks B-1a, B-2a, B-3a (and `--only boundary`) to plugins/sdlc-lite/scripts/docs_check.py. Spec: .sdlc/0243-sdlc-boundary-checks/handoff.md and the Enforcement table in docs/docs-schema/design.md.

## Acceptance criteria
1. Own throwaway fixtures (not the builder's) for each rule with a positive and a clean negative: B-1a names (runs.jsonl, skips.md, budget-ack.md, <role>-L<n>.md, <role>-L<n>-<k>.md, *.attempt.json, *.request.json, *.running, *.log) under docs/; B-2a (.sdlc folder not a ticket folder, a task folder with handoff.md or step-N/, or a known record folder: tickets messages evals proposals supervisor _templates decompose; loose .md other than AGENTS.md CLAUDE.md notes.md roadmap.md board.md; warnings only); B-3a (docs md linking into .sdlc/ by relative path, warning, fenced code ignored). Legacy: exempts B-3a, never B-1a or B-2a. Exit code: warnings alone give 0; any B-1a gives 1. `--only boundary` selects only B rules.
2. Retry files under .sdlc/ are not B-1a violations; the info line counts them. Run read-only on this repository: counts match docs/reports/2026-10-05-docs-check-run.md (B-1a 61, B-3a 5, B-2a 0, 50 retry files under .sdlc). Run writes nothing.
3. `docs_check.py selftest` passes and one extra negative control of your own (break a rule, see a gate fail, revert); check.py guard 33 flags a removal of B-1a from docs_check.py (observe it).
4. `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `git diff --check main`, no em dashes in added lines.

## Constraints
Read-only except throwaway experiments you revert. No push or publish.
