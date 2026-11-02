---
id: T-0837
title: "Add the decision-question doc type to controlled-natural-language"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
claimed_by: nonoun-author 2026-11-01
branch: lane/T-0837-t0837
worktree: ../sdlc-lite.worktrees/T-0837-t0837
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`controlled-natural-language` defines a governed "decision question" doc type for question instructions, option descriptions, score levels and propositions, and its trigger list covers writing questions for a decision model.

## Intent
- Do: add the decision-question doc type and its patterns per the updated brief, so `lint_cnl.py` can lint decision questions.
- Non-goals: any `decision-questions` skill code.
- Done when: the criteria below hold.

## Context
- Brief: `docs/specs/new-skills/controlled-natural-language.md`; the delta is one trigger line and the decision-question doc type in `references/patterns.md`: one proposition per statement, no negation or double negation, instructions aligned with options, boundary cases stated, no arithmetic, counting or date comparison.
- Skill: `plugins/context/skills/controlled-natural-language/` (`references/patterns.md`, `templates/rules.yaml`, `fixtures/`, `scripts/lint_cnl.py`, `evals/trigger-activation.suite.yaml`, `tests/`).
- `decision-questions` (T-0839) will call `lint_cnl.py` with this doc type; ship a rules example for it (for example `templates/decision-question.rules.yaml` or a fixture) that the next skill can point at.
- Patterns are lintable only as far as `lint_cnl.py` can check them; say which are checked by eye.
- Plugin guidance: `plugins/context/AGENTS.md` (skill table, tests line, CHANGELOG `[Unreleased]`). Packaging rules: `docs/specs/doc-standards/plugins.md`.
- PyYAML 6.0.3 and Python 3.9 are on this machine; scripts must run on Python 3.9 with the standard library plus PyYAML.
- A fail case may use fixture companions when a rule cannot fire against the templates without breaking the pass case; `controlled-natural-language/fixtures/` shows the pattern.
- No cross-links to `knowledge-modeling` (user decision 2026-11-01).

## Do
1. Add the doc type to `references/patterns.md` and the trigger line to SKILL.md and the trigger suite (keep 10 activating and 5 non-activating cases, replacing one activating prompt if needed).
2. Ship a decision-question rules file plus a clean and a violating fixture, and add tests.
3. Add a context CHANGELOG `[Unreleased]` Changed line.

## Acceptance criteria
- `lint_cnl.py` with the decision-question rules file exits 0 on the clean fixture and non-zero on the violating fixture, naming at least a negation and a two-proposition sentence.
- `python3 -B plugins/context/skills/evaluation-system/scripts/validate_suite.py plugins/context/skills/controlled-natural-language/evals/trigger-activation.suite.yaml` exits 0.
- `python3 -B -m unittest discover -s plugins/context/skills/controlled-natural-language/tests` exits 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills. Existing rules and doc types keep working.
