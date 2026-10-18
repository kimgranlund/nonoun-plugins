---
id: T-0614
title: "traces wrong-resume-order fires without checking for a replan, once per step pair"
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
1. `python3 plugins/sdlc-lite/scripts/traces.py ingest /Users/kimgranlund/Projects/maison/ui-kit-maison`
2. `python3 plugins/sdlc-lite/scripts/traces.py detect --repo /Users/kimgranlund/Projects/maison/ui-kit-maison`
3. Count `wrong-resume-order` rows: 120, of which 22 read "0541-app-shell-reference-closeout: step N built after step 2 blocked".

## Expected
The detector fires only when no completed planner run (step None) lies between the blocked builder's finished_at and the later builder's started_at, and emits at most one finding per blocked step.

## Actual
`escalation.py:401` is the literal `f'with no replan in between'))`; lines 359-401 contain no `planner`; one finding is emitted per (blocked step, later step) pair, so 6 blocked steps on 0541 gave 120 rows.

## Context
Found by /review-traces on ui-kit-maison (fleet retro 2026-10-17 rows 7 to 11). Diagnosis `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/cluster-2/archaeologist-L1.md`; verify `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/finding-wro/verifier-L1.md` (pass); drafts `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/propose/planner-L2.md` step 1. Code: `plugins/sdlc-lite/scripts/traces/detectors/escalation.py:359-401`, `traces/selftest.py:1302-1313`.
outcome metric: `traces.py detect --repo <ui-kit-maison>` wrong-resume-order row count, before: 120

## Constraints
The failing test lands before or with the fix, never after.

## Read first
- `plugins/sdlc-lite/AGENTS.md`
## Do
Ticket for finding wro. The diagnosis is in `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/cluster-2/archaeologist-L1.md` and the repro is in `.sdlc/runtime/tasks/review-traces-maison-2026-10-18/finding-wro/verifier-L1.md`. Read their Carry forward sections and do not search again.

Change `wrong_resume_order` in `plugins/sdlc-lite/scripts/traces/detectors/escalation.py` (currently lines 359-401) in two ways.
1. Suppress a later builder attempt when a replan lies between it and the block. A replan is a task row with `role == 'planner'`, `step is None` and `status == 'completed'`, whose attempt `finished_at` (read through `ctx.attempt(r)` and `table._stamp`, the same way the function already reads builder stamps) is after the blocked builder's `finished_at` and at or before the later builder's `started_at`. A failed or running planner does not count.
2. Emit at most one finding per blocked step n. Among all builder attempts of steps m > n that started after the block and have no replan before them, keep the earliest-started one. Evidence stays `[{'attempt_id': <blocked>}, {'attempt_id': <that attempt>}]`, and the summary keeps its current wording, naming that attempt's step m.

Then update the `wrong-resume-order` entry of the module docstring (lines 33-35) so it says that a completed planner run between the block and the later build suppresses the finding, and that there is one finding per blocked step.

Add two selftest cases in `plugins/sdlc-lite/scripts/traces/selftest.py` next to the `_ESC` block, using `_esc_repo`, `_e`, `_builder_text`, `_PLANNED` and `_esc_detect`:
- `escalation: wrong-resume-order quiet after a completed replan`: a task-dir `planner-L2` with started_at 06:02 and finished_at 06:03, `step-1` blocked (default finish 06:01:30), and `step-2` built at 06:05. It asserts no finding.
- `escalation: wrong-resume-order fires once per blocked step`: `step-1` blocked, then `step-2` built at 06:05 and `step-3` at 06:07, with no planner. It asserts exactly one finding, with evidence blk plus the step-2 attempt.

The existing `_fx_wrong_resume_order` and `_ck_wrong_resume_order` (selftest.py:1302-1313) stay valid and unchanged.

Dependents: `git grep -n "wrong-resume-order\|wrong_resume_order"` outside `.sdlc` finds only escalation.py, selftest.py and `thresholds.py:35` (a severity number, which stays unchanged). `traces.py` and the docs have no hit.

Depends on: none.

Validation scope: `traces.py selftest -k escalation` and the full `traces.py selftest`. check.sh is the land gate.
## Acceptance criteria
- (red) A completed planner between the block and the later build suppresses the finding: `python3 -c "import sys,tempfile; sys.path.insert(0,'plugins/sdlc-lite/scripts'); from traces import selftest as s; t=tempfile.mkdtemp(); r=s._esc_repo(t,{'':[s._e('planner-L2','pl',s._PLANNED,started_at='2026-09-30T06:02:00+00:00',finished_at='2026-09-30T06:03:00+00:00')],'step-1':[s._e('builder-L2','blk',s._builder_text('blocked'))],'step-2':[s._e('builder-L2','nx',s._builder_text('done'),started_at='2026-09-30T06:05:00+00:00',finished_at='2026-09-30T06:06:00+00:00')]}); g=s._esc_detect(r,'wrong-resume-order'); sys.exit(1 if g else 0)"` exits 0.
- (red) One blocked step with two later built steps yields one finding, citing the earliest later attempt: `python3 -c "import sys,tempfile; sys.path.insert(0,'plugins/sdlc-lite/scripts'); from traces import selftest as s; t=tempfile.mkdtemp(); late=lambda a,m: s._e('builder-L2',a,s._builder_text('done'),started_at='2026-09-30T06:0%d:00+00:00'%m,finished_at='2026-09-30T06:0%d:30+00:00'%m); r=s._esc_repo(t,{'step-1':[s._e('builder-L2','blk',s._builder_text('blocked'))],'step-2':[late('n2',5)],'step-3':[late('n3',7)]}); g=s._esc_detect(r,'wrong-resume-order'); sys.exit(0 if len(g)==1 and g[0]['evidence']==[{'attempt_id':'blk'},{'attempt_id':'n2'}] else 1)"` exits 0.
- (guard) A failed planner in the window does not suppress the finding: `python3 -c "import sys,tempfile; sys.path.insert(0,'plugins/sdlc-lite/scripts'); from traces import selftest as s; t=tempfile.mkdtemp(); r=s._esc_repo(t,{'':[s._e('planner-L2','pl',s._PLANNED,status='failed',started_at='2026-09-30T06:02:00+00:00',finished_at='2026-09-30T06:03:00+00:00')],'step-1':[s._e('builder-L2','blk',s._builder_text('blocked'))],'step-2':[s._e('builder-L2','nx',s._builder_text('done'),started_at='2026-09-30T06:05:00+00:00',finished_at='2026-09-30T06:06:00+00:00')]}); g=s._esc_detect(r,'wrong-resume-order'); sys.exit(0 if len(g)==1 else 1)"` exits 0.
- (red) The quiet-after-replan case exists and passes: `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation | grep -qF 'ok: escalation: wrong-resume-order quiet after a completed replan'` exits 0.
- (red) The once-per-blocked-step case exists and passes: `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation | grep -qF 'ok: escalation: wrong-resume-order fires once per blocked step'` exits 0.
- (red) The detector docstring names the replan check: `sed -n '/^  wrong-resume-order/,/^  exit-3-result/p' plugins/sdlc-lite/scripts/traces/detectors/escalation.py | grep -qF 'completed planner'` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest` exits 0.
- (guard) Only the two traces files changed: `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc' | grep -vxE 'plugins/sdlc-lite/scripts/traces/(detectors/escalation|selftest)\.py')"` exits 0.
- (guard) No new untracked files: `test -z "$(git ls-files --others --exclude-standard -- . ':(exclude).sdlc')"` exits 0.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/traces` exits 0.
