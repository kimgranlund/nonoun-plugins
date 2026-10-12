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
