---
id: T-0840
title: "Update the classify-and-resolve cascade for observed evidence and decision-questions"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0839]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
claimed_by: nonoun-author 2026-11-01
branch: lane/T-0840-t0840
worktree: ../sdlc-lite.worktrees/T-0840-t0840
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`classify-and-resolve` cascades gain an observed-evidence step, model steps backed by `decision-questions` question sets, a broader-before-unclassified fallback and a rule-repair route, and the validator enforces them.

## Intent
- Do: apply every delta in the updated brief to the spine, templates, validator and references.
- Non-goals: any change to `decision-questions` or other peers.
- Done when: the criteria below hold.

## Context
- Brief: `docs/specs/new-skills/classify-and-resolve.md`. Deltas: the five-step cascade (rules, observed, decision model, expensive model, human); Classification `level`, typed `evidence[]` and `model_version`; Pipeline `kind: observed`, `question_set`, `fallback`, `rule_repair_route`; rules for broader-before-unclassified, disagreement repairs rules first, hard cases stay human; Stage 2 needing role `suggester`; four new validator rules; the `decision-questions` hand-off.
- Skill: `plugins/context/skills/classify-and-resolve/` (`references/model.md`, `templates/pipeline.yaml`, `templates/log.schema.json`, `scripts/validate_pipeline.py`, `fixtures/`, `tests/`).
- Question sets and their validator: `plugins/context/skills/decision-questions/` (T-0839); call `validate_questions.py` as a subprocess by path, never import it.
- Plugin guidance: `plugins/context/AGENTS.md` (skill table, tests line, CHANGELOG `[Unreleased]`). Packaging rules: `docs/specs/doc-standards/plugins.md`.
- PyYAML 6.0.3 and Python 3.9 are on this machine; scripts must run on Python 3.9 with the standard library plus PyYAML.
- A fail case may use fixture companions when a rule cannot fire against the templates without breaking the pass case; `controlled-natural-language/fixtures/` shows the pattern.
- No cross-links to `knowledge-modeling` (user decision 2026-11-01).

## Do
1. Update `references/model.md`, `templates/pipeline.yaml`, `templates/log.schema.json` and the references.
2. Add the four validator rules with fixture cases and tests; keep every earlier rule firing once.
3. Update SKILL.md (300 lines at most) and add a CHANGELOG `[Unreleased]` Changed line.

## Acceptance criteria
- `validate_pipeline.py` exits 0 on `templates/pipeline.yaml` with its starter scheme and an empty `gates.yaml`.
- `validate_pipeline.py` on the broken fixtures (with companions, named in the report) exits non-zero and prints one distinct message for each of the four new rules, besides every earlier rule.
- `python3 -B -m unittest discover -s plugins/context/skills/classify-and-resolve/tests` exits 0, `test $(wc -l < plugins/context/skills/classify-and-resolve/SKILL.md) -le 300`, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills. Existing field names stay unchanged.
