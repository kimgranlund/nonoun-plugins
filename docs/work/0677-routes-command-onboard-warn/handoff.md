---
id: T-0677
title: "steps.py routes prints resolved skill routes; onboard check warns on zero routes"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0676]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A repo can see which skill routes SDLC Lite resolves before any role runs: `steps.py routes [<path>...]` prints them, and `onboard.py check` warns when an AGENTS.md names a repo skill yet no route resolves.

## Intent
- Do: add a `routes` subcommand to `plugins/sdlc-lite/scripts/steps.py` (subparsers near line 7642). With no path it prints one `<glob> -> <skill>` line per `repo_skill_routes(<git toplevel of cwd>)` pair, else `no skill routes`; with paths it prints `<path>: <skill>, ...` per path from `routed_skills`, or `<path>: none`. Exit 0 in both cases. Add selftest cases for a repo with one route and for a repo with none.
- Do: in `run_check` (`plugins/sdlc-lite/scripts/onboard.py:1135`), print one stderr line `warning: AGENTS.md names <skill path> but no skill route resolves; see steps.py routes` when any AGENTS.md under the root holds `.agents/skills/<name>/SKILL.md` and `steps.repo_skill_routes(root)` is empty. The exit code does not change. Add an `onboard.py selftest` gate with a positive case (the T-0672 prose form, which names a skill and yields no route) and a control (a routing bullet, no warning).
- Do: describe the warning in the `check` row meaning of `plugins/sdlc-lite/skills/onboard/SKILL.md` `## Arguments` and add `routes` to the `steps.py` entry of `docs/references/sdlc-internals.md`.
- Non-goals: changing what counts as a route (T-0676).
- Done when: the criteria pass.

## Context
Source: GitHub issue #11, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- In ui-kit-neue `repo_skill_routes` returned `[]` in four lanes while both AGENTS.md levels named `.agents/skills/*/SKILL.md`; nothing told the conductor that routing was silent, and all 11 solo briefs under 0.28.1 lacked the `Repo skills for this step:` line.
- Confirmed on main: `repo_skill_routes` and `routed_skills` live at `plugins/sdlc-lite/scripts/steps.py:1542` and `:1592` and have no CLI; `steps.py` subcommands are registered near line 7642. `onboard.py check` (`run_check`, `onboard.py:1135`; parser at `:2035`) reports managed files and entry links only, and already prints advisory notes on stderr.
- Depends on T-0676 because both edit the routing code in `steps.py` and the warning should reflect the widened parser.

## Constraints
`onboard.py check` keeps its exit code rule; the warning is advisory. `steps.py routes` writes nothing.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with the two `routes` cases.
2. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0 with the new warning gate, and the positive case fails with the warning removed.
3. `python3 plugins/sdlc-lite/scripts/steps.py routes` run in this repo exits 0.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
5. `git diff --check <base sha>` exits 0.
