# Argument hints (T-0463)

| Skill | Old hint | New hint |
|---|---|---|
| agent | `{agent-name} [--level L1\|L2\|L3] {instructions}` | `<agent> [--level L1\|L2\|L3] <instructions>` |
| architect | `<handoff.md \| goal>` | `<handoff.md\|goal>` |
| ask | `[topic or task dir]` | `[<topic\|task-dir>]` |
| bench | `[task name]` | `[<task>]` |
| board | `[task] [--root DIR] [--sort {recent,id,name}] [--lanes]` | `[<task>] [--root DIR] [--sort recent\|id\|name] [--lanes]` |
| build | `[L1..L5] <handoff.md>` | `[L1\|L2\|L3\|L4\|L5] <handoff.md>` |
| chain | `<handoff.md \| goal>` | `<handoff.md\|goal>` |
| clarify | `<ask \| handoff.md>` | `<ask\|handoff.md>` |
| decompose | `<handoff.md \| what to decompose> [--plan] [--strict]` | `<handoff.md\|topic> [--plan] [--strict]` |
| dig | `<handoff.md \| path or question>` | `<handoff.md\|path\|question>` |
| fanout | `<lane>=<ids>... <lane>@<branch>=<ids>... [--base REF] [--integration BRANCH] [--gate CMD]... [--light-gate CMD]... [--lanes-dir DIR] [--rewrite-refs] [--lane auto\|solo\|full] [--max-lanes N] [--stagger SECS]` | `<lane>=<ids>... <lane>@<branch>=<ids>... [options]` |
| file | `<.sdlc/task dir>` | `<task-dir>` |
| fix | `<ticket slug \| one-line ask>` | `<slug\|ask>` |
| fleet-retro | `<repo>...` | `<repo>... [--since DATE] [--until DATE]` |
| fleet-status | `[--repos A,B] [--since last\|DATE] [--ping]` | unchanged |
| grill | `<what is being designed \| handoff.md>` | `<topic\|handoff.md>` |
| handoff | `<goal>` | unchanged |
| onboard | `[setup [--force] \| check]` | unchanged |
| open-questions | `[task dir]` | `[<task-dir>]` |
| plan | `[steps\|doc\|goal\|campaign\|fanout] [L1\|L2\|L3] <handoff.md \| goal \| tickets...> \| compaction [--write-handoff\|--clear] [<prose>]` | `[steps\|doc\|goal\|campaign\|fanout] [L1\|L2\|L3] <handoff.md\|goal\|tickets> \| compaction [options]` |
| plan-campaign | `[the standard to hold across many units]` | unchanged (stub) |
| plan-doc | `[what the plan should achieve]` | unchanged (stub) |
| plan-fanout | `[tickets or the goal to parallelize]` | unchanged (stub) |
| plan-goal | `[what the goal should achieve]` | unchanged (stub) |
| plan-loop | `[what to repeat and how often]` | `[<task>] [<interval>]` |
| plan-verification | `[goal id such as G-001, or the outcome in a sentence]` | `[<goal-id\|outcome>]` |
| report | `[view...] [--since T] [--last N] [--next N] [--only G,...] [--severity problem\|likely\|all] [--format text\|md\|json] [--evidence] [--compare last] [--explain] [--no-snapshot]` | `[view...] [--since T=last-report] [--last N=5] [--next N=3] [--format text\|md\|json] [options]` |
| research | `[L1..L3] <handoff.md \| question>` | `[L1\|L2\|L3] <handoff.md\|question>` |
| review-traces | `<repo> [--lanes-dir DIR]... [--max N]` | unchanged |
| run-plan | `<plan-doc.md>` | unchanged |
| scout | `<handoff.md \| question>` | `<handoff.md\|question>` |
| ticket | `new <type> <slug> \"title\" [--numbered] \| close <slug> [--force] [--reason \"<text>\"] [--ack-warnings \"<why>\"] [--dry-run] [--skip N[,N...]] [--ticket N] [--expect DIGEST] [--numbered] \| roadmap [--numbered] \| check [--numbered] \| archive [--dry-run] [--rewrite-refs] [--force] [--numbered] \| number [--dry-run] \| migrate-layout [--dry-run] [--rewrite-refs]` | `new <type> <slug> \| close <slug> \| roadmap \| check \| archive \| number \| migrate-layout [options]` |
| verify | `[L1..L3] <step handoff.md>` | `[L1\|L2\|L3] <step-handoff.md>` |

`report` (T-0460) and the merged `plan` (T-0467, T-0468) are on the tree and standardized here, so there is no follow-up for them.
