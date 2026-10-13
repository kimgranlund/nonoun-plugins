<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) result schema holds the role: pass. Evidence: ran the `results.SCHEMA['ui-designer']` assertion, exit 0. `red-checkpoint.jsonl` records it red pre-edit (exit 1); no `process-deviations.md`.
- #2 negative control, schema rejects a missing Mode: pass. Evidence: `results.py selftest` exit 0, output holds `ok: a missing ui-designer Mode fails`, `ok: ui-designer rejects maybe`, `ok: ui-designer accepts blocked: <question>`, ends `results selftest: PASS`.
- #3 (red) both tables hold the user's rows: pass. Evidence: python assertion on `levels.json` and `models.json`, exit 0; pre-edit red recorded in `red-checkpoint.jsonl`.
- #4 (red) role file names modes, passes, edit rule: pass. Evidence: phrase loop printed no MISSING for all 7 phrases; `plugins/sdlc-lite/agents/ui-designer.md` read in full, it holds `## Brief`, `## Modes` with "Generate is the only mode that edits.", `## Method` with Inside out and Outside in, and the six schema sections in order.
- #5 generated definitions current, role can write: pass. Evidence: `claude_roles.py generate --check` ("24 files") and `codex_roles.py generate --check` verified, then the three greps; whole chain exit 0.
- #6 (red) conductor cannot spawn bare `ui-designer`: pass. Evidence: hook exit 2. It bites: with `ui-designer|` stripped from `re_bare` in a copy of the hook, the same payload exits 0. Pre-edit red recorded.
- #7 (guard) write gate lets the role edit: pass. Evidence: Edit as `sdlc-lite:ui-designer-L1` exit 0. It bites: same payload as `sdlc-lite:verifier-L1` exits 2.
- #8 dispatcher treats the role as one-shot: pass. Evidence: `dispatch.py selftest` exit 0 with `ok: prune flag: prepare sets prune True for ui-designer`, plus parity rows for ui-designer L1 and L2.
- #9 (guard) edited scripts' own checks: pass. Evidence: `claude_roles.py selftest` 0, `codex-selftest.py` 0 (30 project agents installed), `hook-selftest.sh` 0 (`hook selftest: PASS`), `prompt_lint.py` 0, `docs_check.py --root .` 0 (0 errors, 30 warnings, none from the new report).
- #10 (guard) role, table, rubric, skill, and lock agree: pass. Evidence: `check.py` exit 0 (`ok: 21 role levels, 10 agents, 24 generated definitions checked`). The new item 61 carries four negative controls plus per-phrase controls (`check.py` diff read). `evals.py check`: `ok (11 evals, lock cites .sdlc/evals/0010-ui-designer-role.md)`.
- #11 (red) eval cites the decision report: pass. Evidence: grep pipeline exit 0. `.sdlc/evals/0010-ui-designer-role.md` has `role: ui-designer`, `evidence: docs/reports/2026-10-13-ui-designer-role.md`, date 2026-10-14. `table-lock.json` diff shows the lock moved to 0010, written by `evals.py lock`. Pre-edit red recorded.
- #12 (guard) scope: pass. Evidence: scope command with `SDLC_BASE_SHA=f09efbd7…` exit 0; `git diff --check` exit 0.

## Out of scope changes
None. The Codex TOMLs for conductor, planner, and plan-reviewer changed only as regeneration output (`codex_roles.py generate --check` is clean), which the `adapters/` scope allows. `docs/specs/sdlc-lite/design.md` is untouched, as the handoff requires; its role lists (lines 119, 124) are the planned follow-up.

## For the next attempt
None

## Notes
- The report has `Recorded`, `## Decision`, `## Wiring`, `## Not proven` (`docs/reports/2026-10-13-ui-designer-role.md` lines 3, 7, 20, 41).
- Steelman: I considered failing #4 or #8 for lacking a runtime check of the role's mode behavior. The handoff places live behavior in step 2, and the criteria name only static and selftest checks. Dropped.
