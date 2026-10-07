# Review: docs schema design

## Goal
Independently review docs/planning/docs-schema/design.md (draft v0.1) as an architect. Return a verdict (ready, ready after fixes, or not ready) with numbered findings, each marked blocker or non-blocker, each citing a file and line or section and what you checked. Read-only: edit nothing.

## Intent
- Do: judge whether the schema is coherent, strict enough to be enforced, and consistent with the repository's own facts. Read these first: docs/planning/docs-schema/design.md, docs/specs/repo-onboarding/design.md (current default layout, the `docs/layout.md` format, the rule that a number or folder name never encodes maturity), docs/planning/repo-onboarding/reorganization.md, plugins/sdlc-lite/scripts/onboard.py (the real parser: `_parse_layout_text`, `HOME_FORM`, `SECTIONS`), `.sdlc/AGENTS.md`, this repository's `docs/` tree and `docs/reports/`, and (read-only) /Users/kimgranlund/Projects/maison/ui-kit-maison/docs.
- Check specifically: (1) every factual claim about this repo, maison, `onboard.py`'s parser behaviour (including that a new `## Kinds` or `## Schema` section is ignored by the current parser), `tickets.py close`, and the file counts; (2) whether the planning versus specs split truly avoids encoding maturity in a folder name, or breaks the existing design principle; (3) whether the docs versus `.sdlc/` boundary rules B-1 to B-5 are consistent with how the tooling actually writes files (run.sh, steps.py, tickets.py, messages.py, budget.py, evals); (4) whether each check D-1..D-12 and B-1a..B-3a is deterministic, can be built from names and front matter alone, and has a plausible negative control; (5) the grandfathering rule by first-commit date and the `adopted:` key; (6) the mapping tables for gaps or wrong assignments; (7) migration risks missing; (8) whether the nine fixed homes are right (too many, too few, a wrong name) and whether `other/` as a quarantine with review-by is enforceable; (9) anything that would make a harness or person do the wrong thing when following the schema.
- Non-goals: rewriting the document, building anything.

## Context
This is a design for ticket T-0233. The user asked for a schema for `./docs/*`, a stricter point of view on what lives in `.sdlc/` versus `docs/`, and the folder names to use. The author is a Sonnet fork, so you are a different model family.

## Constraints
Cite evidence for every finding. No em dashes. Be concrete and short; list blockers first.

## Output
Verdict, then findings.
