---
id: T-0672
title: "Skill-route lint treats prose bullets that mention a skill as routes"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0647]    # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lint` refuses a step for a missing routed skill only when an AGENTS.md line actually routes paths to that skill, not when a prose bullet mentions a skill beside other paths.

## Intent
- Do: tighten `repo_skill_routes` in `plugins/sdlc-lite/scripts/steps.py` so a list item or table row counts as a route only when it reads as one (for example a table row whose cells are paths and one skill, or a list item with a routing cue such as `->`, "read", "use" or "follow" before the skill span; pick the smallest rule that keeps the T-0647 selftest routes and drops the prose case).
- Non-goals: rewording `plugins/sdlc-lite/AGENTS.md`; the false positive must go away in the parser, since consumer repos write the same prose.
- Done when: the criteria pass.

## Context
Found by the T-0647 verifier (`decide:` note). `plugins/sdlc-lite/AGENTS.md:17` is a prose bullet that names `skills/level-rubric/SKILL.md` as "the consumer explanation" beside `adapters/claude/levels.json`, `scripts/run.sh`, `scripts/check.py`, `adapters/codex/models.json` and `evals/`. Since T-0647 it parses as six routes, so any plan step scoping `scripts/check.py` is refused unless it lists the level-rubric skill. Parser: `repo_skill_routes` at `plugins/sdlc-lite/scripts/steps.py:1524`; selftest cases are tagged `(rt)`.

## Constraints
The existing `(rt)` selftest cases keep passing unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with a new `(rt)` case: a bullet shaped like `plugins/sdlc-lite/AGENTS.md:17` yields no route, and the case fails with the change reverted.
2. `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import steps; print([r for r in steps.repo_skill_routes('.') if 'level-rubric' in r[1]])"` prints `[]`.
3. `git diff --check` exits 0.
