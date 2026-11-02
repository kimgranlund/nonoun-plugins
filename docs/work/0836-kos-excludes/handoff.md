---
id: T-0836
title: "Add the excludes field to knowledge-organization-system"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`knowledge-organization-system` concepts can carry hand-written `excludes` entries that say what a concept is not and name the neighbor it is confused with, and the validator checks them.

## Intent
- Do: add the optional `excludes: [{neighbor, statement}]` field to the model, template guidance and validator, per the updated brief.
- Non-goals: generating contrast text; any `decision-questions` compiler.
- Done when: the criteria below hold.

## Context
- Brief: `docs/specs/new-skills/knowledge-organization-system.md`; the delta is the `excludes` bullet in the concept fields and two new validator errors (an `excludes` neighbor that is not a concept id; an empty statement or one naming the concept itself).
- Skill: `plugins/context/skills/knowledge-organization-system/` (`references/model.md`, `scripts/validate_kos.py`, `fixtures/broken.yaml`, `tests/`).
- `excludes` is added only after an observed confusion and written by hand; say so in `references/model.md` and `references/growth.md`, not at length in SKILL.md.
- Plugin guidance: `plugins/context/AGENTS.md` (skill table, tests line, CHANGELOG `[Unreleased]`). Packaging rules: `docs/specs/doc-standards/plugins.md`.
- PyYAML 6.0.3 and Python 3.9 are on this machine; scripts must run on Python 3.9 with the standard library plus PyYAML.
- A fail case may use fixture companions when a rule cannot fire against the templates without breaking the pass case; `controlled-natural-language/fixtures/` shows the pattern.
- No cross-links to `knowledge-modeling` (user decision 2026-11-01).

## Do
1. Add `excludes` to `references/model.md` and the growth guidance, with one example.
2. Add the two validator errors, extend `fixtures/broken.yaml` so each fires once, and add tests.
3. Add a context CHANGELOG `[Unreleased]` Changed line.

## Acceptance criteria
- `python3 -B plugins/context/skills/knowledge-organization-system/scripts/validate_kos.py plugins/context/skills/knowledge-organization-system/templates/vocabulary.yaml` exits 0.
- The validator on `fixtures/broken.yaml` exits non-zero and prints one distinct message for a dangling `excludes` neighbor and one for an empty or self-naming `excludes` statement, besides every earlier rule.
- `python3 -B -m unittest discover -s plugins/context/skills/knowledge-organization-system/tests` exits 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills. Existing field names stay unchanged.
