# Record schema, session-status/1

One JSON object per snapshot, stored under `.sdlc/runtime/report/`. Text views are renderings of it. Each field below names its source; a field the collector cannot read goes in `unknown`.

| Group | Fields | Source |
|---|---|---|
| identity | session id, name, role, level, model, effort, host, repo, branch or lane, parent, started_at, pid | transcript, `dispatch` attempt and dispatch files, `git` |
| state | `working`, `waiting-on-user`, `waiting-on-role`, `blocked`, `idle`, `done` or `dead`; since; last activity; last tool call; evidence | pid liveness, transcript tail, mailbox |
| work | goal (one line), ticket id and status, step n of m, running children with elapsed time, what it waits on | ticket handoff, `steps.py next`, `dispatch.py status` |
| timeline | `recent` (finished), `now` (one primary, plus children), `next` (ordered, `planned` or `intended`) | closed tickets, passed verifier results, merges, `runs.jsonl`, ticket `depends:`, ready queue |
| health | late failure, context, stall, retries and replans against caps, blocked or interrupted attempts, gate-lock position, dirty tree, unpushed commits | attempts, results, `gate_lock.py status`, `git`, transcript |
| cost | dollars, tokens, active minutes, priced and unpriced runs, budget cap and percent | `runs.jsonl`, `budget.py` |
| needs | list of {kind: decision, credential, merge or none; text; source} | open question in the transcript, ticket `decide:` lines, blocked results |
| outcome | the done-when command and its last result; the KPI if any | ticket handoff, goal |
| unknown | field names the collector could not read | collector |

## Health signals

| Signal | Metric | Flag when |
|---|---|---|
| late failure | minutes before the first failing check divided by total minutes | over 0.8 on a run over 15 minutes |
| trivial last failure | the failing criterion is a grep, a format line, a missing result file or a stale path | after 20 or more minutes of work |
| check first run late | the first run of a named criterion falls in the last 10 percent of the run | any `(red)` or guard criterion |
| rework | a second verifier round, or a reopened ticket | more than one round |
| peak context fill | highest input plus cache tokens in a turn over the window | over 70 percent |
| compactions | count in one ticket | 2 or more |
| re-reads | one file read with no edit between | 3 or more |
| read-to-use | files read divided by files edited or cited | over 15 to 1 |
| exploration | grep and glob calls before the first edit | over 25 |
| workaround chain | failed command then a rewritten command, on one step | 2 or more |
| retries | the same tool call failing | 3 or more |
| dead-end work | commits or edits later reverted in the lane | any |
| noisy output | one tool result over the size cap | over 20k tokens |
| stall | minutes since the last tool call or file change | over 15 |
| gate wait | minutes queued in the gate lock | over 5 |

Thresholds are starting values, `[U]` until calibrated against sessions known to be clean or messy. The grade: A no flags, B one warning, C two or more warnings, D any problem flag; it names the flags that set it. The records-only signals (late failure, rework, stall, gate wait, retries, dead-end work) come first; the transcript signals (context, re-reads, exploration, workaround chains, compactions, noisy output) need the transcript parser.
