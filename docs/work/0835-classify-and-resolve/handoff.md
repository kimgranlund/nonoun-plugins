---
id: T-0835
title: "Add the classify-and-resolve skill to the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: claimed       # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0833]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
claimed_by: nonoun-author 2026-11-01
branch: lane/T-0835-t0835
worktree: ../sdlc-lite.worktrees/T-0835-t0835
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The context plugin ships `classify-and-resolve`, a skill for typed classify-and-dispatch pipelines with a cascade, an autonomy matrix and a taxonomy feedback loop, with a pipeline validator, a log-to-cases converter and an unclassified report, as specified in the brief.

## Intent
- Do: build the skill per the brief `docs/specs/new-skills/classify-and-resolve.md`, consuming the KOS, CNL and evaluation-system schemas, then package it.
- Non-goals: queue or broker integration, hosted engines, model training, clustering beyond deterministic grouping, review UIs.
- Done when: the criteria below hold.

## Context
- The brief is the spec: `docs/specs/new-skills/classify-and-resolve.md`.
- Peer schemas, used by field name and never redefined: `plugins/context/skills/knowledge-organization-system/references/model.md` (vocabulary, schemes, deprecated), `plugins/context/skills/controlled-natural-language/references/patterns.md` (rules), `plugins/context/skills/evaluation-system/references/model.md` (Case, Suite, Gate, `gates.yaml`). Validate generated suites with `plugins/context/skills/evaluation-system/scripts/validate_suite.py`; do not import code across skill folders.
- PyYAML 6.0.3 and Python 3.9 are on this machine; scripts must run on Python 3.9.
- The brief's Process says to write a one-page spec first and proceed; put that spec at the top of your report, not in a file.
- Packaging rules: `docs/specs/doc-standards/plugins.md`; plugin guidance: `plugins/context/AGENTS.md` (skill table, tests line, CHANGELOG `[Unreleased]`, `agents/openai.yaml` like the KOS skill's).
- A fail case may use fixture companions (a fixture vocabulary, gates or rules file) when a rule cannot fire against the templates without breaking the pass case; `controlled-natural-language/fixtures/` shows the pattern.
- No cross-links to `knowledge-modeling` (user decision 2026-11-01).

## Do
1. Build `references/model.md` and `templates/log.schema.json`, then `scripts/validate_pipeline.py` with `fixtures/broken-pipeline.yaml`, then `templates/pipeline.yaml`, then `scripts/logs_to_cases.py` and `scripts/unclassified_report.py` against a 30-record sample log in `fixtures/`.
2. Write `references/resolvers.md`, `references/growth.md` (Stage 0 to Stage 1 walkthrough with one KOS change from the unclassified report), `evals/trigger-activation.suite.yaml`, SKILL.md (300 lines at most), and `tests/test_classify_and_resolve.py`.
3. Package it and add a context CHANGELOG `[Unreleased]` Added entry.

## Acceptance criteria
- `validate_pipeline.py` exits 0 on `templates/pipeline.yaml` with the KOS `templates/vocabulary.yaml` (or a starter scheme the report names) and an empty `gates.yaml`.
- `validate_pipeline.py` on `fixtures/broken-pipeline.yaml` (with any fixture companions, named in the report) exits non-zero with one distinct message for each of the 10 error rules in the brief.
- `logs_to_cases.py` turns the 30-record sample log into a suite that `plugins/context/skills/evaluation-system/scripts/validate_suite.py` accepts (exit 0).
- `unclassified_report.py` on the same log prints at least one candidate concept with evidence item ids.
- `python3 -B plugins/context/skills/evaluation-system/scripts/validate_suite.py plugins/context/skills/classify-and-resolve/evals/trigger-activation.suite.yaml` exits 0, with 10 activating and 5 non-activating cases.
- `python3 -B -m unittest discover -s plugins/context/skills/classify-and-resolve/tests` exits 0 and `test $(wc -l < plugins/context/skills/classify-and-resolve/SKILL.md) -le 300`.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit other skills; a defect found in a peer is reported, not fixed.
- Keep SKILL.md runtime-neutral and domain-neutral.
