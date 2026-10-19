---
id: T-0184
title: "One declared result schema per role, validated before the next role reads it"
type: feature
status: done
size: L2
priority: P2
depends: []
created: 2026-10-01
---

## Goal
Every role result file is validated against one declared schema before the pipeline advances, and a malformed result is refused so the pipeline does not move.

## Intent
- Do: add `plugins/sdlc-lite/scripts/results.py` holding one authoritative table that declares, for each role (`builder`, `verifier`, `planner`, `plan-reviewer`, `researcher`, `architect`, `scout`, `archaeologist`, `filer`): the required `## ` sections in order, the section whose first word must be one of an allowed set (builder `## Status`: `done|blocked|inherited red: <tests>`; verifier `## Verdict`: `pass|fail|inherited red: <tests>`; plan-reviewer `## Verdict`: `pass|replan|blocked`), and the first-line `<!-- role=<r> level=<L> model=<m> effort=<e> -->` header. CLI: `results.py validate <result.md> [--role R]` exits 0 or prints one `results.py: <file>: <reason>` line and exits 1; `results.py schema` prints the table. Replace the per-role case table in `plugins/sdlc-lite/scripts/run.sh` (required section and allowed values) by a call to `results.py validate`, and make `plugins/sdlc-lite/scripts/steps.py` (`next`, `review`, `split`) call it for the newest result of the step or task before it prints any action that depends on that result; an invalid result makes `next` print `invalid result: <path>: <reason>` as its first line, which `/chain` and `/fix` treat as a stop (update both skills and `docs/references/sdlc-internals.md`). Extend `plugins/sdlc-lite/scripts/check.py` with a guard that the agent bodies in `agents/*.md` name the same required sections as `results.py schema` (one authoritative place).
- Non-goals: changing any role's output contract or the allowed values; validating the content of sections; changing the Codex backend's own transport checks beyond calling the same validator where it already checks sections.
- Done when: the selftest and negative controls below pass, `run.sh` and `steps.py` use `results.py`, and the common checks pass.

## Context
Today `run.sh` lines around 124 to 134 hold the case table `sect=` and `allowed=` and lines near 451 to 485 check the section after a run; `steps.py` has its own readers (`section`, `first_word`, `build_status`, `verdict`, and their `_or_none` forms). The role contracts are the agent bodies in `plugins/sdlc-lite/agents/*.md`, preloaded by skills where noted. Keep the existing exit codes and messages of `run.sh` that tests pin (`plugins/sdlc-lite/scripts/run-selftest.sh`, `check.py`, `lifecycle-selftest.py`); read them before changing the message text.

Selftest (`results.py selftest`, wired into `check.sh`): a valid result for each role passes; a result missing its required section, a result whose first value under `## Status` or `## Verdict` is not allowed, a result with no header, and an empty file each fail with the right reason; section order is enforced where declared; `steps.py next` on a step whose newest builder result is malformed prints `invalid result` and not `verify`; with a valid result the same step prints `verify`. Negative control: patch a copy of `results.py` so the validator accepts everything, and show the `steps.py next` malformed-result case then fails (the selftest builds the patched copy in a temp dir). Live proof (recorded in `docs/reports/role-result-schema-live-run.md`): a real `run.sh builder L1` run on a throwaway project whose result is forced malformed (for example by a handoff that tells the builder to end without its `## Status` section) is refused by `run.sh` as before and shows the pipeline does not advance; then a normal run advances.

## Constraints
No role contract changes. A pipeline that worked before keeps working: every previously valid result stays valid. `results.py` is the only place the table lives; `run.sh` and `steps.py` carry no copy.

## Common rules
Rules for this ticket, from the user (2026-10-01): every folder this ticket adds is self-describing through its own `AGENTS.md` (with a `CLAUDE.md` containing `@AGENTS.md`), so a role that reads one file learns the system and no skill is added; progressive disclosure holds (a short router line in `.sdlc/AGENTS.md`, details in the folder); every status or state transition is covered by a selftest case that asserts the folder or file state and the stamped fields, plus a negative control that fails when the rule is removed; a live run proves the behavior with a negative control and is recorded in a dated `docs/reports/<name>.md` (environment, exact commands, evidence, limits; an arm that cannot run is recorded unverified, never replaced by a fixture); checks to run before merging locally: `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, and every selftest; update `docs/references/sdlc-internals.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` layout list, and `plugins/sdlc-lite/AGENTS.md` when behavior or layout changes; do not bump versions, tag, push, or publish; generated Codex agent TOML is never edited by hand; no em dashes anywhere.
plan review: replan: .sdlc/0184-role-result-schema/plan-reviewer-L1.md
plan review: replan: step 3: interfaces: `plugins/sdlc-lite/scripts/traces/selftest.py` is an unnamed contract dependent of `steps.next_action`, and the step's change turns its fixtures into `invalid result`. The case `results: on the same fixtures as step dirs, steps.next_action agrees` expects `verify`, `replan`, `inherited`, `rebuild`, `done` and `reverify`. Its builder fixture header has no `level=` token, so it fails the step 1 header regex, and its verifier fixture has no header at all. The step 3 scope guard does not allow that file, no step 3 criterion runs `traces.py selftest`, and step 7 limits fixes to files the earlier steps changed, so `check.sh` goes red with no step allowed to repair it.
plan review: replan: step 1: acceptance criteria: the order criterion is impossible with the step's Do. Reason 8 is `## <B> comes before ## <A>` where declared-earlier A appears after B. For a verifier file with `## Criteria` then `## Verdict`, A is Verdict and B is Criteria, so the Do yields `## Criteria comes before ## Verdict`. The criterion greps for the exact line `## Verdict comes before ## Criteria`. The selftest also requires "their exact reason", so a builder cannot satisfy both. Step 4's example (`## Checks before ## Changes` for a body with those two swapped) follows the Do's direction, not the criterion's.

## Closed

2026-10-04: built and verified by /chain (7 steps), branch L3 verifier passed, merged into main in 433125d
