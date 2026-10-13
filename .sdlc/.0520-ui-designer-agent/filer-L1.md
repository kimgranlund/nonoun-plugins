<!-- role=filer level=L1 model=sonnet effort=low -->
## Warnings
- process deviation: red-checkpoint: retrospective: attempt ed8962fc81a54a4d916b5bc57485e74a, handoff sha256 1b1afbecdf9b, 5 of 5 (red) criteria without a pre-edit red control (step 2: the live-run results validate, the `## Mode` key per file, the status files, the report links, and the `## Release note` heading). `redck.py record` ran after step 1's 30 files were already uncommitted in the tree, so it stored the controls as retrospective. The builder says all five were red before step 2's own edits, and the verifier saw each one red against base by absence or by a mutated /tmp copy. Both steps passed, but the passing verdict does not clear this deviation.
- Step 2 report figures are unverified. The throwaway project was gone when the verifier ran, so the retained `.txt` results could not be compared byte for byte with the run outputs. The per-run `runs.jsonl` behind the report's model, effort, and cost columns could not be read. No criterion names them. The report header's Claude Code version (`2.1.296`) was not re-run.
- The live run is partial. The report's `## Not proven` section lists the Codex host, the sub-agent dispatch path with the generated `ui-designer-L<n>` definitions, whether plan and review modes stay out of the tree (nothing enforces it), and output quality. The generated markup and CSS were not opened in a browser.
- The plan needed one replan. Step 2's first handoff was refused by `steps.py lint`, which read backticked throwaway-project paths as repo paths. Step 1 stayed as built and step 2 was rewritten.

## PR title
T-0520: Add a ui-designer role (plan, review, generate) for semantic DOM and CSS

## PR body
## Summary
Adds `ui-designer`, a pipeline role that plans, reviews, and generates semantic DOM and CSS. It follows the project's design system and the styling around the code it touches. The mode comes from a `mode: plan|review|generate` line in the handoff. Generate is the only mode that edits.

Levels are the user's fixed choices. Claude L1 is opus medium and L2 is opus high. Codex L1 is gpt-6.1-sol medium and L2 is gpt-6.1-sol high.

## Changes
- New role contract `plugins/sdlc-lite/agents/ui-designer.md`. It has Brief, Modes, and Method sections (Inside out and Outside in passes) and six output sections: Mode, Decisions, Findings, Changes, Context used, Carry forward.
- `results.py`: new `ui-designer` schema with key section `Mode` (plan, review, generate, or `blocked: <question>`), plus selftest cases.
- Tables: `adapters/claude/levels.json`, `adapters/codex/models.json`, `run.sh` case rows, and a `ui-designer` section in `skills/level-rubric/SKILL.md`.
- Generators and hooks: `claude_roles.py` and `codex_roles.py` give the role write access like the builder. It is added to `_role.sh`, `block-role-spawn.sh` (no bare conductor spawn), and `hook-selftest.sh`.
- `dispatch.py`: the role is one-shot (`PRUNE_ROLES`).
- `check.py`: new item 61, a phrase guard and agreement check with negative controls.
- Docs: `skills/agent/SKILL.md`, `agents/conductor.md`, `docs/references/{sdlc-internals,codex-role-execution,claude-hooks}.md`.
- Regenerated Codex TOMLs, including conductor, planner, and plan-reviewer, as generator output.
- Evidence: `docs/reports/2026-10-13-ui-designer-role.md` (decision and wiring), `.sdlc/evals/0010-ui-designer-role.md`, and a rewritten `.sdlc/evals/table-lock.json`.
- Live run: `docs/reports/2026-10-13-ui-designer-live-run.md` and its `.txt` result and status files.

## Verification
- Step 1 (verifier: pass)
  - The schema assertion, the selftests (`results.py`, `dispatch.py`, `codex-selftest.py`, `hook-selftest.sh`, `claude_roles.py`), and `check.py` passed.
  - `claude_roles.py generate --check` and `codex_roles.py generate --check` passed.
  - `evals.py check` passed with the lock citing eval 0010.
  - Negative controls: the `results.py` selftest has `a missing ui-designer Mode fails`. A bare conductor spawn of `ui-designer` exits 2, and exits 0 once the role is removed from the hook regex.
- Step 2 (verifier: pass)
  - One live `run.sh` run per mode in a throwaway project. Plan (opus high) ran at L2 and review and generate (opus medium) ran at L1. All three results pass `results.py validate --role ui-designer`.
  - The plan and review status files are empty, and the generate status file lists `index.html` and `styles.css` as modified.
  - `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, and `git diff --check` exited 0. The scope guard printed nothing.
- Not covered: the Codex host, the sub-agent dispatch path, and non-editing enforcement for plan and review. See Warnings.

## Changelog entry
- Added the `ui-designer` role with plan, review, and generate modes. Claude runs it on opus medium (L1) or high (L2), Codex on gpt-6.1-sol medium or high. Its table rows are locked by eval 0010.

## Follow-ups
- decide: Nothing in the tool code stops `ui-designer` from editing in plan or review mode (all write gates key on the role name), so only the role contract and a `check.py` phrase guard hold it. The user decides whether a per-mode gate is worth building.
- fix-now: Route `ui-designer` results into planner intake and `/chain` (`agents/planner.md:16`, `docs/specs/sdlc-lite/design.md` lines 119 and 124). Today a handoff must cite a result by path. Step 1 left both files untouched, as its handoff required.
- note: The live run used the legacy `run.sh` Claude branch. The generated `ui-designer-L<n>` agents, the sub-agent dispatch path, and the Codex host have no live evidence.
- note: Eval number 0010 may collide with another lane's eval after a merge. `evals.py check` reports a duplicate and one eval is renumbered.
