---
id: T-0833
title: "Add the evaluation-system skill to the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: claimed       # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
claimed_by: nonoun-author 2026-11-01
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The context plugin ships `evaluation-system`, a skill that governs case sets, graders, metrics and gates with evidence-gated stages, a suite validator and a runtime-agnostic suite runner, as specified in the brief.

## Intent
- Do: build the skill per the brief `docs/specs/new-skills/evaluation-system.md`, reading the KOS (`plugins/context/skills/knowledge-organization-system/references/model.md`) and CNL (`plugins/context/skills/controlled-natural-language/references/patterns.md`, `templates/rules.yaml`) schemas, then package it.
- Non-goals: the brief's Process step 4 (retrofit the KOS and CNL trigger suites) is T-0834, not this ticket; hosted platforms, dashboards, load benchmarking.
- Done when: the criteria below hold.

## Context
- The brief is the spec: `docs/specs/new-skills/evaluation-system.md`. The typed spine field names (Case, Grader, Suite, Run, Gate) are frozen once published; T-0834 and T-0835 build on them.
- KOS label resolution for `expected` labels: read the vocabulary with the same field semantics as `plugins/context/skills/knowledge-organization-system/scripts/validate_kos.py` (prefLabel, altLabel, hiddenLabel, deprecated). Do not import across skill folders; a skill is self-contained.
- PyYAML 6.0.3 and Python 3.9 are on this machine; scripts must run on Python 3.9.
- The brief's Process says to write a one-page spec first and proceed; put that spec at the top of your report, not in a file.
- Packaging rules: `docs/specs/doc-standards/plugins.md`; plugin guidance: `plugins/context/AGENTS.md` (skill table, tests line, CHANGELOG `[Unreleased]`, `agents/openai.yaml` like the KOS skill's).
- A fail case may use fixture companions (a fixture vocabulary, gates or rules file) when a rule cannot fire against the templates without breaking the pass case; `controlled-natural-language/fixtures/` shows the pattern.
- No cross-links to `knowledge-modeling` (user decision 2026-11-01).

## Do
1. Build `references/model.md` (typed spine), then `scripts/validate_suite.py` with `fixtures/broken-suite.yaml`, then `scripts/run_suite.py` with `templates/suite.yaml`, `templates/gates.yaml` and a trivial echo target, then `references/graders.md`, `references/growth.md` (with the Stage 0 to Stage 1 walkthrough for a prompt), `evals/trigger-activation.suite.yaml`, and SKILL.md (300 lines at most).
2. Package it and add `tests/test_evaluation_system.py` covering the validator pass and fail cases and one runner run.
3. Add a context CHANGELOG `[Unreleased]` Added entry.

## Acceptance criteria
- `python3 -B plugins/context/skills/evaluation-system/scripts/validate_suite.py plugins/context/skills/evaluation-system/templates/suite.yaml` exits 0, and the same validator exits 0 on `plugins/context/skills/evaluation-system/evals/trigger-activation.suite.yaml`.
- The validator run on `plugins/context/skills/evaluation-system/fixtures/broken-suite.yaml` (with any fixture companions it needs, named in the report) exits non-zero with one distinct message for each of the 7 error rules in the brief.
- `run_suite.py` on the template suite with the echo target writes `run.json` and `report.md`; the report shows n, value and a Wilson interval per slice and at least one gate with status `insufficient_n`.
- `evals/trigger-activation.suite.yaml` holds 10 activating and 5 non-activating cases, each with `expected`, `added_because` and a `human` grader.
- `python3 -B -m unittest discover -s plugins/context/skills/evaluation-system/tests` exits 0 and `test $(wc -l < plugins/context/skills/evaluation-system/SKILL.md) -le 300`.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills; T-0834 converts the KOS and CNL suites.
- Keep SKILL.md domain-neutral.
