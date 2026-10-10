---
id: T-0416
title: "Replay a scope-versus-tests heuristic and decide"
type: spike           # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []
created: 2026-10-09
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
Would a lint that flags tests mentioning an allowed source file's basename have caught the four recorded scope misses without burying them in noise on a step that passed?

## Goal
Replay a scope-versus-tests heuristic and decide. Serves goal G-002 (docs/goals/002-restart-and-blocked-run-cost.md); spec: docs/specs/sdlc-lite/restart-and-blocked-run-plan.md; plan step 6 in .sdlc/plan-reliability-docs/plan.md.

## Intent
Ticket: spike, size L2, candidate 5 of the spec (section 5). Depends on: none. Diagnosis only: no code changes.

Read the two recorded plans read-only: agent-ui T-0060 step 4 (its builder blocked on `mcp-enablement.test.ts` and then asked for `replay.test.ts`; find the step folder from `/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/fleet-retro-2026-10-09-12.md` and a search for `builder-L4` results naming those files, lane worktrees included; at plan time no folder named `*0060*` sat within four levels of agent-ui's `.sdlc/`, `.worktrees/` or `.claude/worktrees/`, so search the T-0060 ticket's `handoff.md` front matter by id, and if the step folder cannot be found, replay from the builder report text the retro answer cites and say so in the report) and ultimate-tokens `/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc/match-peer-lightness/step-2.superseded-1/` (`handoff.md` and `builder-L5.md:31-32`, which name `test/engine/semantic.mjs` and `test/engine/exports.mjs`). For each plan, take the step's scope allow-list and apply the heuristic: for each source path it allows, list the test files in that repository (paths with a `test/`, `tests/` or `__tests__/` segment, or a `.test.` or `.spec.` name) that contain the source file's basename without extension and are not in the allow-list. Also run it on one step of the same plans that passed with its scope unchanged, as the noise control.

Write `docs/reports/<YYYY-MM-DD>-scope-test-lint-replay.md` (the build date): a table per plan of each flagged test and whether it is one of the four known misses, the control step's flags, the commands run, and a last line exactly `Verdict: build` (the heuristic flags at least one of the four known misses and three or fewer tests on the control step) or `Verdict: do not build`. Name all four files in the report whatever the verdict. Do not file the build ticket. Do not edit those two repositories. Validation scope: `docs_check.py`.

## Read first
- `docs/reports/AGENTS.md`

## Done when
- (red) `ls docs/reports | grep -qxE '[0-9]{4}-[0-9]{2}-[0-9]{2}-scope-test-lint-replay\.md'`
- (red) `for t in mcp-enablement.test.ts replay.test.ts test/engine/semantic.mjs test/engine/exports.mjs; do cat docs/reports/*-scope-test-lint-replay.md | grep -qF "$t" || exit 1; done`
- (red) `cat docs/reports/*-scope-test-lint-replay.md | grep -qxE 'Verdict: (build|do not build)'`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'docs/reports/[0-9]{4}-[0-9]{2}-[0-9]{2}-scope-test-lint-replay\.md')"`

## Context
Planner L3 output for the 2026-10-09 retros. KPIs: K-002 restart recovery minutes, K-003 blocked builders per wave, K-004 unsatisfiable criteria caught. The spec marks which candidates may already be fixed or need diagnosis first; follow it.

## Constraints
No em or en dashes. No push or publish. The plan step is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Acceptance criteria
- The dated report `docs/reports/<date>-scope-test-lint-replay.md` exists and names `mcp-enablement.test.ts`, `replay.test.ts`, `test/engine/semantic.mjs` and `test/engine/exports.mjs`.
- It has a flagged-test table per plan (agent-ui T-0060 step 4, ultimate-tokens T-0040 step 2), a control-step table, the commands run, and ends with exactly `Verdict: build` or `Verdict: do not build`, consistent with its stated rule (at least one known miss flagged and three or fewer control flags).
- Only that report changed outside `.sdlc`; `docs_check.py` reports 0 errors.
