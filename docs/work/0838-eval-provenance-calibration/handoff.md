---
id: T-0838
title: "Add gold provenance, variants, coverage, calibration and stale gates to evaluation-system"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`evaluation-system` records who decided each case's gold, measures questions in both directions with invariance and negation variants, reports coverage and calibration, and marks gates stale when the target's version moves.

## Intent
- Do: apply every delta in the updated brief to the schemas, validator, runner, templates and references.
- Non-goals: any `decision-questions` code; this skill never imports that skill's schemas.
- Done when: the criteria below hold.

## Context
- Brief: `docs/specs/new-skills/evaluation-system.md`. Deltas: Case `basis` (owner, judgment, convention, agent), `kind` (standard, invariance, negation) and `variant_of`; Run metrics `coverage` and optional `calibration` (per-band accuracy and ECE); Gate `question_id`, `basis`, `min_coverage`, `pinned_target_version` and status `stale`; `templates/LESSONS.md`; the new rules (gold has provenance, gate the question, score both directions, coverage beside accuracy, calibration measured, invariance cases, version changes stale gates, lessons ledger); five new validator rules; the one-way relation to `decision-questions`.
- Skill: `plugins/context/skills/evaluation-system/` (`references/model.md`, `scripts/validate_suite.py`, `scripts/run_suite.py`, `templates/`, `fixtures/`, `tests/`).
- `classify-and-resolve` (`plugins/context/skills/classify-and-resolve/`) and the KOS and CNL trigger suites consume this schema. Existing suites must still validate; make new fields optional where the brief allows, and make `basis` required only if every in-repo suite is updated in this ticket. Check with the commands below.
- The brief says "The validator warns when a judgment suite contains convention cases"; the validator rule list says a judgment gate whose slice includes convention cases is reported. Treat the gate case as an error and the suite case as a warning.
- Plugin guidance: `plugins/context/AGENTS.md` (skill table, tests line, CHANGELOG `[Unreleased]`). Packaging rules: `docs/specs/doc-standards/plugins.md`.
- PyYAML 6.0.3 and Python 3.9 are on this machine; scripts must run on Python 3.9 with the standard library plus PyYAML.
- A fail case may use fixture companions when a rule cannot fire against the templates without breaking the pass case; `controlled-natural-language/fixtures/` shows the pattern.
- No cross-links to `knowledge-modeling` (user decision 2026-11-01).

## Do
1. Extend `references/model.md` and the templates (`suite.yaml`, `gates.yaml`, new `LESSONS.md`).
2. Add the five validator rules with fixture cases and tests.
3. Extend `run_suite.py` to report per-direction accuracy, coverage and calibration when the target returns confidence, and to mark a gate `stale` on a version mismatch.
4. Update references and SKILL.md (300 lines at most) and add a CHANGELOG `[Unreleased]` Changed line.

## Acceptance criteria
- `validate_suite.py` exits 0 on `templates/suite.yaml` with `templates/gates.yaml`.
- `validate_suite.py` on the broken fixture (with companions) exits non-zero and prints one distinct message for each of the five new rules, besides every earlier rule.
- A `run_suite.py` run on a fixture with a confidence-returning target writes `coverage` and `calibration` into `run.json` and per-direction accuracy into `report.md`; a gate whose `pinned_target_version` differs from the target's reports `stale`.
- `for f in plugins/context/skills/*/evals/trigger-activation.suite.yaml; do python3 -B plugins/context/skills/evaluation-system/scripts/validate_suite.py $f || exit 1; done` exits 0.
- `python3 -B -m unittest discover -s plugins/context/skills/evaluation-system/tests` and the same in `plugins/context/skills/classify-and-resolve` exit 0; `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills, except in-repo trigger suites when a field becomes required. Existing field names stay unchanged.
