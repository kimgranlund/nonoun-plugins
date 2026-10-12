# Views and options

`/sdlc-lite:report [view...] [options]`. No arguments is `summary`. Views combine: `tasks signals`. An unknown view or option is refused (exit 2) with this list.

## Views

| View | Prints | Record group |
|---|---|---|
| `summary` (default) | at most 8 lines: state, needs, now, next, hygiene grade, plus recent and unknown lines when not empty | all |
| `full` | `summary tasks signals context cost children identity evidence`, in that order | all |
| `tasks` | `recent`, `now`, `next` | work, timeline |
| `signals` | problems and likely problems with the hygiene grade | health |
| `needs` | only what the person must decide or provide | needs |
| `context` | peak context fill, compactions, re-reads, read-to-use ratio, exploration, workaround chains | health.context |
| `cost` | dollars, tokens, active minutes, priced and unpriced runs, budget percent | cost |
| `children` | running and finished child roles with elapsed time | work.children |
| `identity` | session id, role, level, model, effort, repo, lane, parent, host | identity |
| `evidence` | the pointer behind each line | every group |
| `lanes` | one row per lane worktree or branch from `lanes.py list --all`: lane, ticket, stage, driver alive, commits ahead of main, landed, dir | work |
| `waves` | one block per integration branch (`fanout/waveNN`): tickets with stage and percent, wave percent, commits ahead of main, merged into main | work |

## Lanes and waves

`lanes` and `waves` read `lanes.py list --all --json`, `git rev-list`, `ps` and each lanes dir's `logs/land.jsonl` (else the `merged` lines of `logs/fanout.log`); `full` and `summary` do not print them, and `--format json` adds `lanes` and `waves` only when a view asks. A field that cannot be read prints `unknown`; both views write nothing.

- Driver alive: `yes (pid N)` when a process other than this report names the lane directory in its command line, else `no`.
- Landed: `yes` when `lanes.py` calls the lane closable and it has commits since its base; an integration branch is landed when it is closable and the journal shows a merged ticket.
- Ticket percent, one derivation: closed 100 (ticket `status: done`); merged 90 (journal outcome `merged`); a plan, the mean of the `board.py` step percents (queued 0, building 10, built 50, verifying 70, verified 100) with the weakest step's word; no plan, building 10 (live driver), built 50 (commits since base), queued 0. Wave percent is the mean over its tickets, `unknown` when none has one.

## Options

| Option | Does | Default |
|---|---|---|
| `--since <T>` | window for `recent` and `signals`: `2h`, `today`, a date, `last-report` | `last-report`, else `4h` |
| `--last N` | `recent` entries | 5 |
| `--next N` | `next` entries | 3 |
| `--only <G,...>` | restrict to named groups inside the views | all in the views |
| `--severity problem\|likely\|all` | filter `signals` | `all` |
| `--format text\|md\|json` | output shape; `json` is the raw `session-status/1` record | `text` |
| `--evidence` | append the evidence pointer to each line | off; on in `full` |
| `--compare last` | mark what changed since the stored snapshot | off |
| `--explain` | print each flag's rule, value and threshold | off |
| `--no-snapshot` | do not store this snapshot | stores one |

An option a view does not use is accepted and ignored. Threshold overrides are not options: they live in `.sdlc/config` so a grade means the same thing every run. `--session <name>` (another session) is reserved and refused until the cross-session read exists.

## Entry grammar

One entry: `<verb> <subject> <id> | <outcome or condition> | <time> | <evidence>`. Closed verbs: built, verified, merged, closed, filed, released, blocked, deferred, stopped, queued, waiting. A verb outside the list is a collector error. Tense is the status: past for `recent`, present progressive for `now`, future with a trigger for `next`.
