---
id: T-0647
title: "Plan steps carry a Read first line from AGENTS.md skill routing"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A planned step that changes a path the repository's AGENTS.md routes to a repo skill lists that skill under its `### Read first`, and `steps.py lint` refuses a step that edits a routed path without it.

## Intent
- Do: (1) In `plugins/sdlc-lite/scripts/steps.py` add `repo_skill_routes(top)` (parse every `AGENTS.md` under the tree, root included, for routing lines: a list item or table row holding one backticked skill path, a `SKILL.md` file or a folder under a `skills/` directory, plus at least one other backticked path or glob) and `routed_skills(top, paths)` (the skill paths whose globs match the given repo-relative paths; a trailing `/` matches the folder prefix, otherwise `fnmatch`). (2) `lint_steps` adds a finding `steps: <plan> step <n>: plan defect: edits routed path <p> without its skill under ### Read first: <skill>` when a path from the step's `scope_entries` matches a route whose skill path is not in `read_first_paths(block)`. (3) `agents/planner.md` (Entry files rule and the output template) and `skills/handoff-format/SKILL.md` (the `### Read first` paragraph) say the subsection also lists the routed skill of each changed file, root AGENTS.md included, and that a step cites the skill section instead of restating its rules; regenerate the planner level variants.
- Non-goals: keyword (non-path) routing; the prepare-side injection of skills into role prompts (T-0648 consumes `routed_skills`); changing the existing nearest-AGENTS.md rule or its lint.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #11, ui-kit-neue audit 2026-10-20. This ticket is part a (planner template, handoff-format and plan lint); part b is T-0648 (prepare and role prompts).
- Evidence: 81 builder step handoffs, only 15 name a repo skill; of 40 step handoffs touching `packages/styles/src`, 8 cite recipe-authoring; 0 Skill-tool calls across 93 builders and solos; conventions restated instead of cited (`data-scope` in 36 handoffs).
- Already in this repo: steps carry an optional `### Read first` subsection (`plugins/sdlc-lite/agents/planner.md:59` rule, `:92` template; `plugins/sdlc-lite/skills/handoff-format/SKILL.md:162` template, `:189` rule), parsed by `read_first_paths` (`plugins/sdlc-lite/scripts/steps.py:1466`) and existence-checked in `lint_steps` (`plugins/sdlc-lite/scripts/steps.py:2065`). It lists only the nearest non-root `AGENTS.md`, so a skill routed from the root entry never reaches a step. No script parses AGENTS.md routing lines today.
- The step's changed files come from its scope allow-list: `scope_entries(block)` (`plugins/sdlc-lite/scripts/steps.py:3454`). A step with no scope span gets no routing finding.
- The real lint home is `steps.py lint_steps`, not `plan_check.py` (`check_plan` at `plugins/sdlc-lite/scripts/plan_check.py:589` checks plan docs, not planner step plans). The plan-reviewer already reads every `### Read first` file (`plugins/sdlc-lite/agents/plan-reviewer.md:15`).
- `planner-L1.md` to `planner-L3.md` are generated from `planner.md` by `claude_roles.py generate`; Codex agents by `codex_roles.py generate`.

## Constraints
A repository with no routing lines lints exactly as before. Existing `### Read first` and lint behavior is unchanged. No model or effort change.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0. Its new cases: a fixture repo whose root `AGENTS.md` has the line ``- `src/styles/` uses `.agents/skills/recipe/SKILL.md` ``, a plan whose step scope names `src/styles/a.css` with no `### Read first` fails lint with `without its skill under ### Read first: .agents/skills/recipe/SKILL.md`; the same step listing that path passes; a fixture with no routing lines passes. The failing case fails with the change reverted.
2. `grep -n 'routed' plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/skills/handoff-format/SKILL.md` prints at least one line in each file.
3. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0 and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
4. `python3 scripts/check-packaging.py` exits 0.
5. `git diff --check` exits 0.

## Outcome
- `plugins/sdlc-lite/scripts/steps.py`: `repo_skill_routes(top)` parses routing lines (list item or table row, one backticked skill path plus at least one other path or glob) from every AGENTS.md, root included; paths in a nested AGENTS.md resolve against its folder. `routed_skills(top, paths)` returns the matching skills (trailing `/` is a folder prefix, else fnmatch). `lint_steps` adds `plan defect: edits routed path <p> without its skill under ### Read first: <skill>` for a scoped path whose skill is not listed (a skill folder and its `SKILL.md` count as the same). Selftest cases `(rt)` added; the refusal case fails with the lint check disabled.
- `agents/planner.md` (Entry files rule, template) and `skills/handoff-format/SKILL.md` (`### Read first` paragraph) state the routed-skill rule; planner L1 to L3 and Codex planner agents regenerated.
- Checks: `python3 plugins/sdlc-lite/scripts/steps.py selftest` exit 0; `grep -n 'routed' plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/skills/handoff-format/SKILL.md` exit 0; `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exit 0; `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check` exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0.
- Open: this repo's `plugins/sdlc-lite/AGENTS.md:17` prose line now parses as a route (levels.json, run.sh, check.py, models.json, evals/ to `skills/level-rubric/SKILL.md`), so a step scoping `scripts/check.py` must list that skill. Reword that line if the route is unintended.
- verify: needed

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: decide: plugins/sdlc-lite/AGENTS.md:17 now parses as six routes to skills/level-rubric/SKILL.md (levels.json, run.sh, check.py, models.json, evals/); any later step scoping `scripts/check.py` must list that skill. The builder flagged this under Open; reword the line if the route is unintended.) · verifier: verifier-L2 (sonnet) · base: 92b2df57cd83
- Changed: see commits
- Commits: f512a4b T-0647: plan steps carry a Read first line from AGENTS.md skill routing
- Check: 1 steps.py selftest exits 0 with the new (rt) cases: pass
- Check: 2 grep 'routed' in planner.md and handoff-format SKILL.md: pass
- Check: 3 claude_roles.py and codex_roles.py generate --check: pass
- Check: 4 scripts/check-packaging.py: pass
- Check: 5 git diff --check: pass
