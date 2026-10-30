# Actionability rubric

The step 5 verifier applies this to every finding of a fleet retro, [V] and [U], not only to the sampled ones. A finding is actionable when it passes every gate and scores at least 7 of 10. Anything else stays in the report under `## Not actionable` with the failed gate or the score, and is never filed.

## Gates (pass or fail)

A failed gate sets the score to 0 and names the gate. Check them in order and stop at the first fail.

| Gate | Passes when |
|---|---|
| G1 Pointer | The row names a command, a log path, a fingerprint path, or `file:line` that a reader can run or open without asking anyone. |
| G2 Current | The evidence was produced by the plugin as it is now: `git log --since=<evidence start> -- <mechanism file>` shows no commit that addresses the symptom, or the row's window starts after that commit. A symptom seen on an older version that a later commit or release fixed fails, even when the symptom was real. A fixture or a replayed finding is graded as of the commit it names (`as of <sha>`): read `git log` up to that commit instead of HEAD. |
| G3 Measured | The cost or count comes from the collector, a command, or a log line. An estimate, a ceiling guess, or an "about" with no source fails. A [U] row can still pass when its number is sourced; it cannot when the number is a guess. |
| G4 Plugin cause | The mechanism names an sdlc file, rule, script, or role. A cause in the project, the host, or the task text fails. |
| G5 Falsifiable | The prevention can be stated as a check that fails today and passes once fixed: a detect rule going silent, a selftest case, a command. |

## Criteria (0 to 2 each, total 10)

| | 0 | 1 | 2 |
|---|---|---|---|
| C1 Cost | unmeasured, or under 5 percent of the repo's measured spend and under 30 minutes | 5 to 20 percent, or 30 to 120 minutes | over 20 percent, over 120 minutes, or work stopped |
| C2 Recurrence | one occurrence | repeated in one repo (two runs or tickets) | seen in two or more repos |
| C3 Mechanism | a symptom class only | the script or skill | the file and the rule or line |
| C4 Fix size | a redesign or several tickets | a few files | one file or one rule |
| C5 Outcome metric | none named | a metric exists but is read by hand | a named detect rule or command whose value will move |

## Outcome check

A closed ticket filed from a retro carries `outcome metric: <rule or command>, before: <value>`; a KPI id (`K-001`) with a runnable `measure:` in `docs/kpi/` meets C5 in place of a rule or command. The next retro re-collects and records one of `moved` (the value is under its threshold, or lower than `before`), `no change`, or `worse`. A `no change` or `worse` finding comes back as a new row with `fix did not hold`, scores C2 as 2, and names the ticket. A ticket with no outcome metric is itself a finding against the retro that filed it.

## Calibration

Scored on the 2026-10-06 evidence at two times: as of 24ef333 (the 0.20.10 release record, 2026-10-05, the plugin the reports ran on) and at HEAD. The scoring rule is the tables above, so a changed rubric is re-run on these rows and on [the fixtures](fixtures.md), and the totals below are updated in the same change. The gen-ui-kit report is not on the machine that wrote this, so its Chromium finding is calibrated through the detect rule's fixture only.

| Finding (source) | As of 24ef333 | At HEAD | Why |
|---|---|---|---|
| Long Bash commands burn hooks (`docs/reports/hook-perf.md`, agent-ui report 1) | gates pass; 1,2,2,1,2 = 8 | G2 fails (T-0291); outcome check `moved` | Three hooks at about 100 percent CPU for 30+ s per call; two lines in four hook files; `hook-selftest.sh` is the red check. |
| Plan review is 55 percent of agent-ui spend (193 runs, $787) | gates pass; 2,1,2,2,2 = 9 | G2 fails (T-0294) | One rule (L4 and L5 plan review only) changed after the runs; `plan_review_share` is the metric; T-0315 re-measures. |
| Chromium over 30 processes in maison (53 processes, 10 GB) | G4 fails, 0 | G4 fails, 0 | The processes are the project's Playwright shards; the plugin only schedules them. T-0292 owns the plugin half. |
| Sane ceiling: cap heavy gates at 2 (agent-ui, marked [U]) | G3 fails, 0 | G2 fails first, 0 (T-0303, `gate_lock.py`) | A guess with no measurement behind either number. It becomes a finding only after a measurement. |
