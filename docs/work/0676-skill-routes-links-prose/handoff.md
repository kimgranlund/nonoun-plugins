---
id: T-0676
title: "repo_skill_routes reads markdown-link and nested AGENTS.md prose skill routes"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.repo_skill_routes` finds the skill routes a repo actually writes: a markdown link to a SKILL.md counts as a skill span, and a prose line in a nested AGENTS.md that names a path and a skill after a routing cue (read, follow, use) is a route. Then `routed_skills` returns the skill for a routed path, prepare adds the `Repo skills for this step:` line, and `steps.py lint` can refuse a step that edits a routed path without its skill.

## Intent
- Do: in `repo_skill_routes` (`plugins/sdlc-lite/scripts/steps.py`, near line 1542), collect skill spans from markdown links `[x](<path>/SKILL.md)` as well as code spans, keeping the existing cue rule (ROUTE_CUE_RE, line 1519) for the text before the skill span.
- Do: in a nested AGENTS.md (not the root one), also accept a prose line (not a list item or table row) that holds a path or glob span, a skill span, and a cue before the skill span; resolve a skill path against the AGENTS.md folder when it exists there, else against the repo root, so `.agents/skills/x/SKILL.md` cited from `packages/styles/AGENTS.md` resolves to the root skill. Update the docstring and the lint help text near line 177 to match.
- Do: add selftest cases next to the `(rt)` cases (near line 5525): a root bullet ``- `src/styles/` follows [recipe](.agents/skills/recipe/SKILL.md)`` yields `('src/styles/', '.agents/skills/recipe/SKILL.md')`; a `src/AGENTS.md` prose line ``Before editing `styles/`, read `.agents/skills/recipe/SKILL.md`.`` yields `('src/styles/', '.agents/skills/recipe/SKILL.md')`. Both fail with the change reverted.
- Non-goals: the `steps.py routes` command and the onboard warning (T-0677); routing from a keyword with no path.
- Done when: the criteria pass.

## Context
Source: GitHub issue #11, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- ui-kit-neue routes skills in two forms: root `AGENTS.md` bullets with markdown links ("follows the repo skills [token-authoring](.agents/skills/token-authoring/SKILL.md)") and package `AGENTS.md` prose ("Before editing `src/`, read `.agents/skills/recipe-authoring/SKILL.md`"). `repo_skill_routes` returns `[]` for both, so all 11 solo briefs under 0.28.1 lacked the `Repo skills` line (T-0192 edits `packages/styles/src`), and `repo_skill_routes(<lane>)` returned `[]` in four lanes.
- Confirmed on main: `repo_skill_routes` (`steps.py:1542`) skips any line that is not a `- `, `* ` or `|` line, and reads skill paths only from code spans (`SPAN_RE`, `steps.py:522`; `SKILL_PATH_RE`, `steps.py:1518`). It also prefixes every span in a nested AGENTS.md with that folder, so a root-relative `.agents/skills/...` cited from a nested file resolves to a path that does not exist.
- Callers: `routed_skills` (`steps.py:1592`), `repo_skills_line` in `plugins/sdlc-lite/scripts/dispatch.py:404` (prepare and solo_run.py briefs), and the lint routing check near `steps.py:2228`.
- The T-0672 negative case (`steps.py` near line 5552: a prose bullet that mentions a skill beside paths with no cue before it) must still yield no route.

## Constraints
The T-0647 and T-0672 `(rt)` cases keep passing unchanged. A root AGENTS.md prose line stays no route; only list items, table rows, and nested-AGENTS.md prose lines with a cue count.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with the two new cases, and each new case fails with the change reverted.
2. The T-0672 case still passes: `python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1 | grep -F 'ok: (rt) T-0672'` prints one line.
3. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
5. `git diff --check <base sha>` exits 0.
