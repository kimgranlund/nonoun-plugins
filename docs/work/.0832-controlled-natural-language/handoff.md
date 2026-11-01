---
id: T-0832
title: "Add the controlled-natural-language (CNL) skill to the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: done       # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0831]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
claimed_by: nonoun-author 2026-11-01
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The context plugin ships `controlled-natural-language`, a skill that governs sentence patterns in high-stakes documents (STE, EARS, Attempto traditions) with evidence-gated stages and a linter that resolves slots against the KOS vocabulary, as specified in the brief.

## Intent
- Do: build the skill exactly per the brief `docs/specs/new-skills/controlled-natural-language.md`, reading the vocabulary schema and validator that T-0831 shipped, then package it.
- Non-goals: grammar parsers, NLP semantics, translation, casual or narrative writing (the brief's Out of scope); cross-links to `knowledge-modeling` (user decision 2026-11-01).
- Done when: the brief's Definition of done holds and the plugin packaging check passes.

## Context
- The brief is the spec: `docs/specs/new-skills/controlled-natural-language.md`. Its Process says to write a one-page spec first and proceed; put that spec at the top of your report, not in a file.
- Dependency: `plugins/context/skills/knowledge-organization-system/` (T-0831): its `templates/vocabulary.yaml` is the template vocabulary, its `references/model.md` the field semantics. Use its field names exactly; never define, redefine or alias terms in this skill.
- Target: `plugins/context/skills/controlled-natural-language/`. Packaging rules: `docs/specs/doc-standards/plugins.md`; plugin guidance: `plugins/context/AGENTS.md`.
- PyYAML 6.0.3 and Python 3.9 are on this machine; the linter must run on Python 3.9.
- SKILL.md names `knowledge-organization-system` as the hand-off whenever the problem is what a term means or which term to use.

## Do
1. Build `templates/rules.yaml`, then `scripts/lint_cnl.py` with `fixtures/violations.md` (one violation per rule) and a clean sample doc for the pass case, then the three references (including the Stage 0 to Stage 1 walkthrough), then SKILL.md (300 lines at most), per the brief.
2. Package: `agents/openai.yaml`, the skill row in `plugins/context/AGENTS.md`, a context CHANGELOG `[Unreleased]` Added entry.
3. Add a small unittest (`tests/test_lint_cnl.py`) for the pass and the fail case.

## Acceptance criteria
- The linter run with `templates/rules.yaml`, the KOS `templates/vocabulary.yaml` and the clean sample doc exits 0.
- `cd plugins/context/skills/controlled-natural-language && python3 -B scripts/lint_cnl.py fixtures/rules.yaml fixtures/vocabulary.yaml fixtures/violations.md` exits non-zero with one distinct message for each of the 5 error rules in the brief, each naming file, line, rule id and fix; the fixture vocabulary passes `validate_kos.py` (replan 2026-11-01: the template vocabulary has no retired labels, so the pass run cannot trip `hidden-label` or `unknown-concept`).
- `python3 -B -m unittest discover -s plugins/context/skills/controlled-natural-language/tests` exits 0.
- `test $(wc -l < plugins/context/skills/controlled-natural-language/SKILL.md) -le 300`
- `references/trigger-tests.md` lists 10 activating and 5 non-activating prompts, each with an expected outcome.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit `knowledge-organization-system` except to fix a defect the linter exposes; report any such edit.
- Keep SKILL.md domain-neutral.

## Outcome

2026-11-01 · lane: solo L3 · verdict: closed by reason (delivered by the solo agent (level L3); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 3ed3c57bf209
- Changed: see commits
- Commits: e744398 T-0832: replan criterion 2 to the fixture-companion run (verifier plan defect); f69f204 T-0832: record lane T-0832-t0832
- Check: 1 Linter with `templates/rules.yaml`, KOS `templates/vocabulary.yaml` and the clean sample exits 0: pass
- Check: 2 Fixture run exits non-zero with one distinct message per brief error rule, each naming file, line...: pass
- Check: 3 `python3 -B -m unittest discover -s plugins/context/skills/controlled-natural-language/tests` exi...: pass
- Check: 4 `test $(wc -l < SKILL.md) -le 300`: pass
- Check: 5 `references/trigger-tests.md` lists 10 activating and 5 non-activating prompts, each with an expe...: pass
- Check: 6 `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean: pass
- Follow-up: note: Live fresh-session trigger evaluation of the 15 prompts was not... -> notes.md
