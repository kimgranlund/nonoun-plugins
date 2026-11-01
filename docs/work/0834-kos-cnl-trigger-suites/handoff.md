---
id: T-0834
title: "Convert the KOS and CNL trigger tests to evaluation-system suites"
type: chore           # feature | bug | chore | spike | idea
status: ready       # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0833]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`knowledge-organization-system` and `controlled-natural-language` carry their trigger tests as `evals/trigger-activation.suite.yaml` in the `evaluation-system` suite format, as their updated briefs require.

## Intent
- Do: convert each skill's `references/trigger-tests.md` into `evals/trigger-activation.suite.yaml` (10 activating, 5 non-activating cases, each with `expected`, `added_because` and a `human` grader), remove the old file, and repoint every link to it.
- Non-goals: any other change to the two skills.
- Done when: the criteria below hold.

## Context
- Updated briefs: `docs/specs/new-skills/knowledge-organization-system.md` and `docs/specs/new-skills/controlled-natural-language.md` (deliverables and Definition of done lines name `evals/trigger-activation.suite.yaml`).
- Suite format and validator: `plugins/context/skills/evaluation-system/references/model.md` and `plugins/context/skills/evaluation-system/scripts/validate_suite.py` (T-0833). Model the files on `plugins/context/skills/evaluation-system/evals/trigger-activation.suite.yaml`.
- Keep the existing 15 prompts and expected outcomes; `added_because` cites the brief's trigger list.
- Plugin guidance: `plugins/context/AGENTS.md`.

## Do
1. Write both suite files from the existing trigger tests.
2. Delete both `references/trigger-tests.md` and repoint links in SKILL.md, references and tests.
3. Add one line to the context CHANGELOG `[Unreleased]` entry.

## Acceptance criteria
- `for s in knowledge-organization-system controlled-natural-language; do python3 -B plugins/context/skills/evaluation-system/scripts/validate_suite.py plugins/context/skills/$s/evals/trigger-activation.suite.yaml || exit 1; done`
- `! ls plugins/context/skills/knowledge-organization-system/references/trigger-tests.md plugins/context/skills/controlled-natural-language/references/trigger-tests.md 2>/dev/null` and `! grep -rn 'trigger-tests' plugins/context/skills/knowledge-organization-system plugins/context/skills/controlled-natural-language`
- Both skills' unittests exit 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit `evaluation-system`; a defect found there is reported, not fixed.
