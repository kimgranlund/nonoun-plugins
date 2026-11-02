---
id: T-0839
title: "Add the decision-questions skill to the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0836, T-0837, T-0838]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
claimed_by: nonoun-author 2026-11-01
branch: lane/T-0839-t0839
worktree: ../sdlc-lite.worktrees/T-0839-t0839
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The context plugin ships `decision-questions`, a skill for designing bounded questions for a decision model and acting on the answers safely, with a question compiler, a validator, an eval-case generator and a fixture adapter, as specified in the brief.

## Intent
- Do: build the skill per `docs/specs/new-skills/decision-questions.md`, consuming the KOS, CNL and evaluation-system schemas, then package it.
- Non-goals: vendor SDKs and request formats, model training, pipeline routing, metric computation. The `classify-and-resolve` update is T-0840.
- Done when: the criteria below hold.

## Context
- The brief is the spec: `docs/specs/new-skills/decision-questions.md`.
- Peer schemas, used by field name and never redefined: `plugins/context/skills/knowledge-organization-system/references/model.md` (`excludes`, T-0836), `plugins/context/skills/controlled-natural-language/references/patterns.md` (decision-question doc type, T-0837), `plugins/context/skills/evaluation-system/references/model.md` (Case `basis`, `kind`, `variant_of`; Gate `question_id`, `pinned_target_version`, T-0838). Call peer scripts as subprocesses by path; do not import code across skill folders.
- Vendor names (Jev, TypeSafe) appear only in `references/decision-models.md` and `references/evidence.md`; SKILL.md stays vendor-neutral.
- The brief's Process says to write a one-page spec first and proceed; put that spec at the top of your report, not in a file.
- Model the packaging on `plugins/context/skills/classify-and-resolve/` (`agents/openai.yaml`, tests).
- Plugin guidance: `plugins/context/AGENTS.md` (skill table, tests line, CHANGELOG `[Unreleased]`). Packaging rules: `docs/specs/doc-standards/plugins.md`.
- PyYAML 6.0.3 and Python 3.9 are on this machine; scripts must run on Python 3.9 with the standard library plus PyYAML.
- A fail case may use fixture companions when a rule cannot fire against the templates without breaking the pass case; `controlled-natural-language/fixtures/` shows the pattern.
- No cross-links to `knowledge-modeling` (user decision 2026-11-01).

## Do
1. Build `references/model.md`, then `adapters/fixture.py`, then `scripts/validate_questions.py` with `fixtures/broken-question-set.yaml`.
2. Build `scripts/compile_questions.py` against the KOS template vocabulary, then `scripts/make_eval_cases.py`.
3. Write `references/shapes.md`, `evidence.md`, `decision-models.md` and `growth.md` (with the Stage 0 to Stage 1 walkthrough and one authored `excludes`), `templates/question-set.yaml` and `evals/trigger-activation.suite.yaml`.
4. Write SKILL.md (300 lines at most) and `tests/test_decision_questions.py`.
5. Package it and add a context CHANGELOG `[Unreleased]` Added entry.

## Acceptance criteria
- `validate_questions.py` exits 0 on `templates/question-set.yaml`, and on `fixtures/broken-question-set.yaml` (with any companions, named in the report) exits non-zero with one distinct message for each of the 7 error rules in the brief.
- `compile_questions.py` builds a question set from the KOS template vocabulary that `validate_questions.py` accepts, and exits non-zero on a scheme with a concept missing its definition.
- `make_eval_cases.py` produces a suite that `plugins/context/skills/evaluation-system/scripts/validate_suite.py` accepts, with `invariance`, `negation` and balanced cases, each with a `basis`.
- A `plugins/context/skills/evaluation-system/scripts/run_suite.py` run of the template question set through the fixture adapter writes a report with bands or margins and coverage.
- `validate_suite.py` exits 0 on `plugins/context/skills/decision-questions/evals/trigger-activation.suite.yaml`, with 10 activating and 5 non-activating cases.
- `python3 -B -m unittest discover -s plugins/context/skills/decision-questions/tests` exits 0, `test $(wc -l < plugins/context/skills/decision-questions/SKILL.md) -le 300`, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills; a defect found in a peer is reported, not fixed.
