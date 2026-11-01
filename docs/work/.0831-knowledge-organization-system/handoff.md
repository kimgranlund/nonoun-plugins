---
id: T-0831
title: "Add the knowledge-organization-system (KOS) skill to the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: done       # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-01
claimed_by: nonoun-author 2026-11-01
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The context plugin ships `knowledge-organization-system`, a skill that keeps a corpus's vocabulary consistent through a lightweight SKOS model, evidence-gated growth stages and a validator, as specified in the brief.

## Intent
- Do: build the skill exactly per the brief `docs/specs/new-skills/knowledge-organization-system.md` (deliverables, frontmatter triggers, stages, rules, validator contract, three-domain examples, definition of done), then package it.
- Non-goals: RDF/OWL, NLP extraction, one-pass vocabulary generation (the brief's Out of scope); cross-links to `knowledge-modeling` (user decision 2026-11-01: keep the two skills separate).
- Done when: the brief's Definition of done holds and the plugin packaging check passes.

## Context
- The brief is the spec: `docs/specs/new-skills/knowledge-organization-system.md`. Its Process says to write a one-page spec first and proceed; put that spec at the top of your report, not in a file.
- Target: `plugins/context/skills/knowledge-organization-system/`. Packaging rules: `docs/specs/doc-standards/plugins.md`; plugin guidance: `plugins/context/AGENTS.md` (skill table, CHANGELOG `[Unreleased]`, `agents/openai.yaml` like `plugins/context/skills/knowledge-modeling/agents/openai.yaml`).
- The schema's field names (`id`, `prefLabel`, `altLabel`, `hiddenLabel`, `definition`, `scopeNote`, `broader`, `narrower`, `related`, `scheme`) are a stable contract: T-0832 (`controlled-natural-language`) reads them and the vocabulary file. Keep them exactly.
- PyYAML 6.0.3 and Python 3.9 are on this machine; the validator must run on Python 3.9.
- SKILL.md names `controlled-natural-language` as the hand-off for how a statement is phrased; that skill does not exist yet (T-0832), so name it, do not link it.

## Do
1. Build `templates/vocabulary.yaml`, then `scripts/validate_kos.py` with `fixtures/broken.yaml` (one case per error and warning rule), then the three references, then SKILL.md (300 lines at most), per the brief.
2. Package: `agents/openai.yaml`, the skill row in `plugins/context/AGENTS.md`, a context CHANGELOG `[Unreleased]` Added entry.
3. Add a small unittest (`tests/test_validate_kos.py`) that runs the validator on the template (exit 0) and on the fixture (non-zero, one message per rule id).

## Acceptance criteria
- `python3 plugins/context/skills/knowledge-organization-system/scripts/validate_kos.py plugins/context/skills/knowledge-organization-system/templates/vocabulary.yaml` exits 0.
- `python3 plugins/context/skills/knowledge-organization-system/scripts/validate_kos.py plugins/context/skills/knowledge-organization-system/fixtures/broken.yaml` exits non-zero and prints one distinct message for each of the 7 error rules in the brief.
- `python3 -B -m unittest discover -s plugins/context/skills/knowledge-organization-system/tests` exits 0.
- `test $(wc -l < plugins/context/skills/knowledge-organization-system/SKILL.md) -le 300`
- `references/trigger-tests.md` lists 10 activating and 5 non-activating prompts, each with an expected outcome.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Do not edit `knowledge-modeling` or any other skill.
- Keep SKILL.md domain-neutral (software, operations or policy, research or notes).

## Outcome

2026-11-01 · lane: solo L3 · verdict: closed by reason (delivered by the solo agent (level L3); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 649affd13c2b
- Changed: see commits
- Commits: 268d87a T-0831: record solo lane in skips.md; b5b594b T-0831: record lane T-0831-t0831
- Check: 1 Validator exits 0 on the template: pass
- Check: 2 Validator exits non-zero on the fixture with one distinct message per each of the 7 brief error r...: pass
- Check: 3 `python3 -B -m unittest discover -s .../tests` exits 0: pass
- Check: 4 SKILL.md is 300 lines or fewer: pass
- Check: 5 `references/trigger-tests.md` lists 10 activating and 5 non-activating prompts, each with an expe...: pass
- Check: 6 `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean: pass
- Follow-up: note: references/growth.md:97-190 walkthrough empty repo, Stage 0, Stage... -> notes.md
- Follow-up: note: SKILL.md "The model" field list overlaps the field table in... -> notes.md
- Follow-up: note: Live activation of the trigger tests in a fresh host session was... -> notes.md
