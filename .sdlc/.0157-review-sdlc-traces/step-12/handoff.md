## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 12: Escalation detectors
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/detectors/__init__.py`, `traces/detectors/thresholds.py` (one dict `THRESHOLDS`; every detector reads its numbers there), and `traces/detectors/escalation.py` with `detect(rows, aux, thresholds)` over the persisted rows, reading raw files only where a row's `sources` names them (the task `handoff.md` and the result files). Detectors, each building findings with `findings.make`:
- `replan-loop`: a task dir with two or more planner rows, or any `superseded` row; evidence: each superseded dir's newest builder or verifier result path (`order.newest`) and the planner attempt ids; severity 3 at two or more replans, else 2; cause `agents/planner.md`.
- `recurring-finding`: a `recurring finding:` line under `## Plan review` in the task handoff; evidence the path and line; cause `agents/planner.md`.
- `unchanged-verdict-bump`: in one step, a verifier fail after a build at level n, a builder at level n+1, then a verifier fail whose `next_note` (lowercased, whitespace collapsed) equals the earlier fail's; evidence both verifier paths; cause `skills/level-rubric/SKILL.md`.
- `plan-defect-refusal`: each `## Plan review` entry holding `plan defect`, grouped by the steps.py lint rule its text names (`compares a count over a changing set`, `pins a commit sha`, `joins two checks with ||`, `clean porcelain status`, `clean whole-tree diff`, `does not parse`, `Read first lists a path`, else `other`), evidence the handoff path and line, cause `scripts/steps.py` with the rule name; and each builder or verifier row with `plan_defect` True, evidence the result path, cause `agents/planner.md`.
- `wrong-resume-order`: a step n whose newest builder is blocked while a higher step m holds a builder attempt whose `started_at` is later than that blocked attempt's `finished_at`; evidence both attempt ids; cause `skills/chain/SKILL.md`.
- `exit-3-result`: an attempt with `exit_code` 3; evidence the attempt id; cause `agents/<role>.md`.
- `statusless-builder` and `no-verdict-verifier`: a builder row with status None, or a verifier row with verdict None; evidence the result path; cause `agents/builder.md` or `agents/verifier.md`.
- `attempt-without-run-row`: an attempt record with an `attempt_id` whose status is not running and that no run record joined; evidence the attempt id and its status; severity 3 for failed, 2 otherwise; cause `scripts/run.sh`.
- `stale-running-marker`: a `.running` marker whose attempt record is not `running`, or a `running` record whose `owner_pid` is not alive on this host (`os.kill(pid, 0)`, errors caught); evidence the marker path or attempt id; cause `scripts/run_lifecycle.py`.
Register the `escalation` cases: for each detector name above, one positive fixture that fires exactly one finding of that detector holding a `path` plus `line` or an `attempt_id` evidence entry and a `cause_hint.file`, printed as `ok: escalation: <detector> fires`, and a paired negative control (the same fixture minus the defect) that fires none, printed as `ok: escalation: <detector> quiet on control`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation`
- `for d in replan-loop recurring-finding unchanged-verdict-bump plan-defect-refusal wrong-resume-order exit-3-result statusless-builder no-verdict-verifier attempt-without-run-row stale-running-marker; do python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation | grep -qF "ok: escalation: $d fires" || exit 1; python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation | grep -qF "ok: escalation: $d quiet on control" || exit 1; done`
- `test -f plugins/sdlc-lite/scripts/traces/detectors/thresholds.py && test -f plugins/sdlc-lite/scripts/traces/detectors/escalation.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
