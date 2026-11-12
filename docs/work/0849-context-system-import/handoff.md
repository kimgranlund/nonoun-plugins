---
id: T-0849
title: "Import the context-system skill into context"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
branch: lane/T-0849-t0849
worktree: ../sdlc-lite.worktrees/T-0849-t0849
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The context plugin ships the `context-system` skill, copied from the user's MacBook share, with its own tests green.

## Intent
- Do: copy the skill, register it in the plugin guidance and changelog, run its tests and packaging.
- Non-goals: removing or editing any other context skill (T-0850 and T-0851 do that); changing the imported skill's behaviour.
- Done when: the criteria below hold.

## Context
- Source: `/Volumes/kimba/.claude/skills/context-system/` (92 files, about 932K, not a git repo). It is read-only: never write, touch or create anything under `/Volumes/kimba`.
- Target: `plugins/context/skills/context-system/`. Copy with `rsync -a --exclude .DS_Store --exclude __pycache__ <source>/ <target>/`.
- The skill merges five skills already here (progressive-context, context-routing-review, knowledge-modeling, knowledge-organization-system, controlled-natural-language); its `README.md` says so. They stay in place for this ticket.
- Register it: one row in the skill table of `plugins/context/AGENTS.md` (source `/Volumes/kimba/.claude/skills/context-system` (2026-11-12)), and add `context-system` to the list of skills whose tests run with `python3 -B -m unittest discover -s tests` in that file's checks paragraph. Add an `### Added` line under `## [Unreleased]` in `plugins/context/CHANGELOG.md` (create the heading if missing).
- Tests need PyYAML for `validate_kos.py` and `lint_cnl.py` (see the skill's README).
- If `scripts/check-packaging.py` flags something in the imported files (size, links, a skill-folder `README.md`), fix it with the smallest change in the repo copy and say so in your report.

## Do
1. Copy the skill as above.
2. Register it in `plugins/context/AGENTS.md` and the context CHANGELOG.
3. Run the tests and packaging; fix only what packaging flags.

## Acceptance criteria
- `test -f plugins/context/skills/context-system/SKILL.md && test -z "$(find plugins/context/skills/context-system -name .DS_Store -o -name __pycache__)"` exits 0.
- `cd plugins/context/skills/context-system && python3 -B -m unittest discover -s tests` exits 0.
- `grep -q 'context-system' plugins/context/AGENTS.md && grep -q 'context-system' plugins/context/CHANGELOG.md` exits 0.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Never write under `/Volumes/kimba`.
- Do not edit other skills.
