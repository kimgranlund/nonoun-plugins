---
id: T-0242
title: "docs_check.py (D-1 to D-12), setup entries for homes, and the default layout template"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2
depends: [T-0241]   # registry parts also wait for T-0248   # T-NNNN, file:<path>, cap:<name>
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A deterministic script, plugins/sdlc-lite/scripts/docs_check.py, runs checks D-1 to D-12 of the design against a repository, `onboard.py` writes entry files for homes and for topics nested under a home (user decision 2026-10-05: setup shows a dry-run diff first and asks once before it writes them, and it changes `docs/AGENTS.md` for every adopter, maison included; maison's `maintenance/` maps to `guides/` or `references/`, `reference/` to `references/`), and the default layout template matches the schema.

## Intent
- Do: (1) docs_check.py imports `parse_layout` from onboard.py, reads `## Homes`, `## Kinds` and `## Legacy`, and implements D-1 to D-12 exactly as the design's Enforcement table defines (including that a legacy glob exempts D-1, D-2, D-3, D-4, D-9, D-10, D-11, D-12 and B-3a but never D-5, D-6, B-1a or B-2a; exit 1 on any error; `--root DIR`; read-only; no model calls). (2) Extend the setup model in onboard.py (the code near the `model` function that today skips every path under a listed home) so entry files and CLAUDE.md imports are created for homes and for topic folders nested under a home once they hold two or more documents, and amend the two sentences in docs/specs/repo-onboarding/design.md that this changes (a home gets no entry file in version 1; and the Number prefixes sentence about status moves, now allowing the single planning to archive transition). (3) Update the default layout template and the docs/AGENTS.md text onboard.py writes to the nine fixed homes and the decision table. (4) Selftest with fixtures: a clean fixture reports no findings; each of D-1 to D-12 has a positive case and a negative control (a mutated script that drops the check fails); wire the selftest into check.sh and add a check.py guard. Do NOT run docs_check.py as a gate on this repository yet (it fails until the migration).
- Non-goals: B-1a, B-2a, B-3a (next ticket), migrating any repo, a version bump, tag, push, or publish.
- Done when: the selftest passes, `onboard.py` selftest passes with entries for homes, a read-only run of docs_check.py on this repository and on /Users/kimgranlund/Projects/maison/ui-kit-maison lists findings by rule id and writes nothing, the full check.sh passes, and an independent verifier passed. Note the setup change alters docs/AGENTS.md output for every adopter: say so in the validation note.

## Context
Part of the docs schema design (docs/planning/docs-schema/design.md v0.4 with the user's decisions of 2026-10-05 under Resolved decisions, ticket T-0240), reviewed once (v0.1) by an independent architect (docs/reports/docs-schema-design-review.md). Build as ONE handwritten solo step under the burn-down rules (lane solo; philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction."); one independent verifier; merge main in first; check.py guard numbers stay unique (guard 23); a new check needs a positive case and an observed negative control.

## Constraints
Registry parts (the shared `render_registry` function rendering the `row` table, `## Decide` list and `card` into `docs/AGENTS.md` and home entries, and the drift checks R-1 and R-2) start only after T-0248 reports a pass; see design.md v0.4 "The context registry pattern". The D-1 to D-12 checks do not wait.
One authoritative location per fact. No em dashes. Do not touch other agents' worktrees.

## Closed

2026-10-05: docs_check.py D-1 to D-12, setup entries for homes, default layout; verifier L3 failed once (depth, design templates, ask once), fixed; full checks pass; merged to main
