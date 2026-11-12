---
id: T-0850
title: "Retire progressive-context, knowledge-modeling and context-routing-review"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0849]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
branch: lane/T-0850-t0850
worktree: ../sdlc-lite.worktrees/T-0850-t0850
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The context plugin no longer ships `progressive-context`, `knowledge-modeling` or `context-routing-review`; every live reference points at `context-system` instead.

## Intent
- Do: delete the three skill folders and repoint each live reference at the matching `context-system` file.
- Non-goals: `knowledge-organization-system` and `controlled-natural-language` (T-0851); rewriting dated reports, closed `.NNNN-*` tickets, CHANGELOG history or the dated `context-fog-of-war/updates-log/`.
- Done when: the criteria below hold.

## Context
- `context-system` (landed by T-0849 at `plugins/context/skills/context-system/`) replaces them: routing is `references/routing/` (it holds the old progressive-context references such as `tier-model.md`, `traversal.md`, `semantic-handoff.md`, `capability-contracts.md`, `evidence.md`, `sdlc.md`, `a2ui.md`, `browser-harness.md`, `workflow-stages.md`, `performance-contract.json`), review is `references/review/`, modeling is `references/modeling/`. Its scripts `validate.py` and `replay.py` replace progressive-context's.
- Live references, found with `git grep -nE "progressive-context|knowledge-modeling|context-routing-review" -- ':!docs/reports' ':!docs/work/.[0-9]*' ':!*CHANGELOG.md' ':!plugins/context/skills/context-fog-of-war/updates-log' ':!plugins/context/skills/context-system'`: `plugins/context/AGENTS.md` (table rows, the `## progressive-context` section, which becomes a short `## context-system` section with the same maintenance rules where they still apply, and the tests list), `plugins/context/HARNESS-NOTES.md`, `plugins/context/.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` if they name them, `scripts/check-packaging.py`, root `README.md`, `context-fog-of-war/references/learnings/cli-routing.md`, other skills' eval suites, and docs such as `docs/specs/generative-constructs/*.md`, `docs/specs/repo-onboarding/design.md`, `docs/planning/docs-schema/design.md`, `docs/work/NOTES.md`. A link into an old skill file goes to the matching `context-system` file; prose naming the skill names `context-system`. The phrase "progressive context" as a concept (not the skill name) can stay.
- `docs/reports/broken-links-allowlist.md` may hold rows for the old paths: delete rows that no longer match anything.
- Add `### Removed` lines under `## [Unreleased]` in `plugins/context/CHANGELOG.md`.

## Do
1. `git rm -r` the three folders.
2. Repair each live reference found by the grep.
3. Add the CHANGELOG lines and run the checks.

## Acceptance criteria
- `test ! -e plugins/context/skills/progressive-context -a ! -e plugins/context/skills/knowledge-modeling -a ! -e plugins/context/skills/context-routing-review` exits 0.
- `git grep -nE "skills/(progressive-context|knowledge-modeling|context-routing-review)|\`(progressive-context|knowledge-modeling|context-routing-review)\`" -- ':!docs/reports' ':!docs/work/.[0-9]*' ':!*CHANGELOG.md' ':!plugins/context/skills/context-fog-of-war/updates-log' ':!plugins/context/skills/context-system/README.md'` prints nothing.
- `python3 -B -m unittest discover -s tests` exits 0 in `plugins/context/skills/context-system` and in `plugins/context/skills/context-fog-of-war`.
- `python3 scripts/check-packaging.py` and `python3 plugins/sdlc/scripts/docs_check.py` exit 0, and `git diff --check` is clean.

## Constraints
- Never write under `/Volumes/kimba`.
- Touch only reference lines outside the deleted folders; no behaviour change in other skills.
