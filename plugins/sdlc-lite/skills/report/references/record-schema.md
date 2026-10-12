# Record schema, session-status/1

One JSON object per snapshot, stored as `.sdlc/runtime/report/<UTC %Y%m%dT%H%M%SZ>.json`. `report.py collect` prints it, and `render --format json` prints it after `--only`. Text views are renderings of it. Each field below names its source; a field the collector cannot read goes in `unknown`.

Top-level keys: `schema` (always `session-status/1`), `generated_at`, `since` (the window start), `evidence` (pointer per group), and the nine groups below.

| Group | Fields | Source |
|---|---|---|
| identity | `session_id`, `name`, `role`, `level`, `model`, `effort`, `host`, `repo`, `branch`, `parent`, `started_at`, `pid` | transcript, `dispatch` attempt and dispatch files, `git` |
| state | `state`: `working`, `waiting-on-user`, `waiting-on-role`, `stalled`, `blocked`, `idle`, `done` or `dead`; `since`, `last_activity`, `last_tool_call`, `pid_alive`, `evidence` | pid liveness, transcript tail, mailbox |
| work | `goal` (one line), `task`, `ticket`, `ticket_status`, `step` of `steps`, `children` (running and finished roles with elapsed time), `waits_on` | ticket handoff, `steps.py next`, attempt files |
| timeline | `recent` (finished), `now` (one primary, plus children), `next` (ordered, `planned` or `intended`) | closed tickets, passed verifier results, merges, `runs.jsonl`, ticket `depends:`, ready queue |
| health | `signals` (each with `name`, `severity`, `value`, `threshold`, `op`, `rule`, `flagged`, `mark`, `evidence`), `flags`, `grade`, `grade_reason`, `context`, `gate_lock`, `dirty_files`, `unpushed_commits`, `blocked_attempts`, `transcript` | attempts, results, `gate_lock.py status`, `git`, transcript |
| cost | `dollars`, `tokens`, `active_minutes`, `priced_runs`, `unpriced_runs`, `budget`, `budget_percent`, `evidence` | `runs.jsonl`, `budget.py` |
| needs | list of {kind: decision, credential, merge or none; text; source} | open question in the transcript, ticket `decide:` lines, blocked results |
| outcome | `done_when` (the command), `last_result`, `kpi` | ticket handoff, goal |
| unknown | dotted paths of the fields the collector could not read, such as `health.unpushed_commits` or `health.context.compactions` | collector |

`health.context` holds `peak_context_fill` (a fraction of `context_window_tokens`), `compactions`, `re_reads`, `read_to_use`, `exploration`, `workaround_chains` and `noisy_output`. With no readable transcript it is empty and its seven paths are in `unknown`.

## Health signals

Severity is `problem` or `likely`. A `problem` flag sets grade D. `likely` flags are warnings: A no flags, B one, C two or more. The grade names the flags that set it. `--severity` filters by these two words.

| Signal | Severity | Metric | Flag when | Threshold key |
|---|---|---|---|---|
| dead | problem | the session pid (`CLAUDE_PID`) is not alive | dead | fixed |
| late failure | problem | minutes before the first failing check divided by total minutes | over 0.8 on a run over 15 minutes | `late_failure_ratio`, `late_failure_min_minutes` |
| trivial last failure | problem | the failing criterion is a grep, a format line, a missing result file or a stale path | after 20 or more minutes of work | `trivial_failure_minutes` |
| rework | problem | verifier rounds on one step | more than 1 | `rework_rounds` |
| dead-end work | problem | revert commits in the lane inside the window | any | fixed |
| stall | problem | minutes since the last tool call or file change, with no child running and no open question | over 15 | `stall_minutes` |
| retries | likely | the same tool call failing, or attempts of one role on one step | 3 or more | `retries` |
| gate wait | likely | minutes queued in the gate lock | over 5 | `gate_wait_minutes` |
| check first run late | likely | position of the first run of a `(red)` or guard criterion in the transcript span | over 0.9 | fixed |
| peak context fill | likely | input plus cache tokens in the fullest turn, as a percent of `context_window_tokens` (200000) | over 70 | `peak_context_pct`, `context_window_tokens` |
| compactions | likely | compactions in the transcript | 2 or more | `compactions` |
| re-reads | likely | reads of one file with no edit between | 3 or more | `re_reads` |
| read-to-use | likely | files read divided by files edited | over 15 | `read_to_use` |
| exploration | likely | grep and glob calls before the first edit | over 25 | `exploration` |
| workaround chain | likely | failed commands followed by a rewritten command | 2 or more | `workaround_chain` |
| noisy output | likely | tokens in the largest single tool result | over 20000 | `noisy_output_tokens` |

Thresholds are starting values, `[U]` until calibrated against sessions known to be clean or messy. Override one with a `report.<key>: <n>` line in `.sdlc/config`, using a key from the last column; a value that is not a number is a refusal (exit 2). The three `fixed` limits have no key. `--explain` prints each rule, value and threshold. The table is in evaluation order. The transcript signals (check first run late, peak context fill, compactions, re-reads, read-to-use, exploration, workaround chain, noisy output) need the transcript parser and read `n/a`, never flagged, without one.
