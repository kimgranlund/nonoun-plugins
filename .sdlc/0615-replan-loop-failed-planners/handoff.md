---
id: T-0615
title: "traces replan-loop counts failed planner launches as replans"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-18
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. Same ingest and detect as T-0614 on ui-kit-maison.
2. Finding `abb79a645728` (0541: "25 replan(s): 26 planner run(s)") cites attempt `d40a7cff879843e0be13bb28cb383869`, which is `planner-L1-2.attempt.json` with `"status": "failed"`.

## Expected
replan-loop counts only planner attempts that delivered a result; failed or cancelled launches are not replans.

## Actual
`escalation.py:234` selects `r.get('role') == 'planner' and r.get('step') is None` with no status check, so failed planner-L1-2, L3-3, L3-5 and L3-10 on 0541 count as replans.

## Context
Found by /review-traces on ui-kit-maison. Diagnosis `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/cluster-1/archaeologist-L1.md`; verify `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/finding-rpl/verifier-L1.md` (pass); drafts `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/propose/planner-L2.md` step 2. Build after T-0614 lands or in a separate lane (overlapping files).
outcome metric: 0541 replan-loop replan count, before: 25

## Constraints
The failing test lands before or with the fix, never after.

## Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
## Do
Ticket for finding rpl. The diagnosis is in `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/cluster-1/archaeologist-L1.md` and the repro is in `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/finding-rpl/verifier-L1.md`. Read their Carry forward sections.

In `replan_loop` in `plugins/sdlc-lite/scripts/traces/detectors/escalation.py` (line 234), add `r.get('status') == 'completed'` to the planner filter. With that filter, the threshold, the replan count and the planner evidence ids all count only planners that delivered a result. This uses the attempt lifecycle status (running, completed, failed), per the module docstring at lines 9-11. Legacy rows already carry `status 'completed'` (`table.py:103`), so they still count. Superseded-dir handling stays unchanged.

Contract dependents, found with `git grep -n "replan-loop\|replan_loop"` outside `.sdlc`, describe the counted set as "planner rows". Update each to say "completed planner rows":
- the `replan-loop` entry of the escalation.py docstring (line 15)
- the comment at `plugins/sdlc-lite/scripts/traces/detectors/thresholds.py:11`
- the `replan_loop_planners` row at `docs/references/sdlc-internals.md:205`

The corpus case at selftest.py:2115 expects replan-loop from a superseded dir, which still fires. The threshold values stay unchanged.

Add a selftest case `escalation: replan-loop ignores a failed planner attempt` in `plugins/sdlc-lite/scripts/traces/selftest.py`. The fixture has a task dir with `planner-L3` (completed), `planner-L3-2` (`status='failed'`, `exit_code=1`, no result text) and `_esc_passed_step()` for step-1. The case asserts that `_esc_detect(..., 'replan-loop')` is empty. The existing `_fx_replan_loop` and `_ck_replan_loop` stay valid, because their planners default to completed.

Depends on: none. This is an independent ticket. If step 1 has already been built in the same tree, its files overlap with this step's scope list.

Validation scope: `traces.py selftest -k escalation`, the full `traces.py selftest`, and `git diff --check` on the doc. check.sh is the land gate.
## Acceptance criteria
- (red) A failed planner attempt does not raise the replan count: `python3 -c "import sys,tempfile; sys.path.insert(0,'plugins/sdlc-lite/scripts'); from traces import selftest as s; t=tempfile.mkdtemp(); r=s._esc_repo(t,{'':[s._e('planner-L3','p1',s._PLANNED),s._e('planner-L3-2','p2',None,status='failed',exit_code=1)],'step-1':s._esc_passed_step()}); g=s._esc_detect(r,'replan-loop'); sys.exit(1 if g else 0)"` exits 0.
- (guard) Two completed planners still fire: `python3 -c "import sys,tempfile; sys.path.insert(0,'plugins/sdlc-lite/scripts'); from traces import selftest as s; t=tempfile.mkdtemp(); r=s._esc_repo(t,{'':[s._e('planner-L3','p1',s._PLANNED),s._e('planner-L3-2','p2',s._PLANNED)],'step-1':s._esc_passed_step()}); g=s._esc_detect(r,'replan-loop'); sys.exit(0 if len(g)==1 else 1)"` exits 0.
- (red) The case exists and passes: `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation | grep -qF 'ok: escalation: replan-loop ignores a failed planner attempt'` exits 0.
- (red) `sed -n '/^  replan-loop/,/^  recurring-finding/p' plugins/sdlc-lite/scripts/traces/detectors/escalation.py | grep -qF 'completed planner'` exits 0.
- (red) `grep -qF 'completed planner' plugins/sdlc-lite/scripts/traces/detectors/thresholds.py` exits 0.
- (red) `grep -qF 'completed planner' docs/references/sdlc-internals.md` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest` exits 0.
- (guard) Only the listed files changed: `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc' | grep -vxE 'plugins/sdlc-lite/scripts/traces/(detectors/(escalation|thresholds)|selftest)\.py|docs/references/sdlc-internals\.md')"` exits 0.
- (guard) No new untracked files: `test -z "$(git ls-files --others --exclude-standard -- . ':(exclude).sdlc')"` exits 0.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/traces docs/references/sdlc-internals.md` exits 0.
