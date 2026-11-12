---
id: T-0851
title: "Retire knowledge-organization-system and controlled-natural-language into context-system"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0849]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`knowledge-organization-system` and `controlled-natural-language` are retired into `context-system` without losing the features this repo added to them, and their dependents point at `context-system`.

## Intent
- Do: bring this repo's later KOS and CNL changes into `context-system`, delete both folders, repoint `decision-questions`, `evaluation-system` and `classify-and-resolve`.
- Non-goals: `progressive-context`, `knowledge-modeling`, `context-routing-review` (T-0850); behaviour changes beyond carrying the two features over; dated reports, closed tickets, CHANGELOG history.
- Done when: the criteria below hold.

## Context
- `context-system` (landed by T-0849 at `plugins/context/skills/context-system/`) has a vocabulary layer (`references/vocabulary/`, `scripts/validate_kos.py`, `templates/vocabulary.yaml`) and a statements layer (`references/statements/`, `scripts/lint_cnl.py`, `templates/rules.yaml`). It was merged from older copies and lacks two repo changes:
  - T-0836 (commit `7756dceb`): the `excludes` field in `knowledge-organization-system` (`validate_kos.py` EXCLUDES_FIELDS, `_read_excludes`, the `excludes-neighbor` and `excludes-statement` checks, tests, fixtures and reference text). `decision-questions` depends on it for authored contrast.
  - T-0837 (commit `ea904410`): the decision-question doc type in `controlled-natural-language` (rules, references, tests).
  Read both commits with `git show`, carry them into the matching `context-system` files, keep `context-system`'s layer wording ("the vocabulary layer"), and add the tests to `context-system/tests/`.
- Dependents: `decision-questions` (SKILL.md, references, scripts, tests, fixtures), `evaluation-system` (SKILL.md, references, `validate_suite.py`, eval suite), `classify-and-resolve` (scripts messages, tests: `test_classify_and_resolve.py` resolves `PEERS / 'knowledge-organization-system' / 'scripts' / 'validate_kos.py'`, repoint it to `context-system`). Messages that say "through knowledge-organization-system" say "through context-system's vocabulary layer"; a CNL mention says "context-system's statements layer". Find all with `git grep -nE "knowledge-organization-system|controlled-natural-language" -- plugins scripts README.md .claude-plugin .agents ':!*CHANGELOG.md'`.
- `docs/specs/new-skills/knowledge-organization-system.md` and `controlled-natural-language.md` describe retired skills: add one line at the top of each saying the skill now lives in `context-system` (vocabulary or statements layer) and fix their links; do not rewrite them.
- Update `plugins/context/AGENTS.md` (table rows, tests list) and add `### Changed` and `### Removed` lines under `## [Unreleased]` in `plugins/context/CHANGELOG.md`. T-0850 edits the same two files in parallel; keep your edits to the KOS and CNL lines.
- Note in your report that `context-system` now differs from the MacBook source by these two changes, so the user can sync upstream.

## Do
1. Carry T-0836 and T-0837 into `context-system` with their tests.
2. `git rm -r` both folders and repoint every dependent.
3. Update the plugin guidance and changelog, then run every named test.

## Acceptance criteria
- `test ! -e plugins/context/skills/knowledge-organization-system -a ! -e plugins/context/skills/controlled-natural-language` exits 0.
- `grep -q excludes-neighbor plugins/context/skills/context-system/scripts/validate_kos.py` exits 0, and `context-system`'s tests include a case where an `excludes` entry naming an unknown neighbor is reported.
- `python3 -B -m unittest discover -s tests` exits 0 in each of `context-system`, `decision-questions`, `evaluation-system` and `classify-and-resolve`, and the classify-and-resolve KOS test is not skipped (`python3 -B -m unittest discover -s tests -v 2>&1 | grep -c skipped` prints 0 there, or the skip reason no longer names knowledge-organization-system).
- `git grep -nE "knowledge-organization-system|controlled-natural-language" -- plugins scripts README.md .claude-plugin .agents ':!*CHANGELOG.md' ':!plugins/context/skills/context-system/README.md'` prints nothing.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Never write under `/Volumes/kimba`.
- Keep validator behaviour identical for inputs that passed before, apart from the carried-over features.
