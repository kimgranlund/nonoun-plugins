# Plan reviewer live run

Recorded: 2026-09-30. Live run for ticket T-0171: a cross-cutting or risky plan, or any replan, gets an independent semantic review before a builder starts, and a defective plan is rejected before it costs a build. One trial per arm, on Claude Code and on Codex.

## Environment

- Claude Code 2.1.285 (`claude_code_version` in the role logs), default backend of `plugins/sdlc-lite/scripts/run.sh`. Models from the `"model"` fields of the role logs: plan-reviewer L1 `claude-opus-5-5` (both runs), planner L3 `claude-fable-5-1`, builder L1 `claude-sonnet-5-5`, verifier L1 `claude-opus-5-5`. Result headers: plan-reviewer `model=opus effort=high`, planner `model=fable effort=xhigh`, builder `model=sonnet effort=low`, verifier `model=opus effort=medium`.
- Codex CLI 0.159.2 (`codex --version`), `SDLC_BACKEND=codex`, standalone `codex exec` transport (`"transport": "exec"` in `plan-reviewer-L1.attempt.json`). `codex login status` printed `Logged in using ChatGPT` before the run. The Codex event stream does not name the model, so the model comes from the runner's records: the result header `<!-- role=plan-reviewer level=L1 model=gpt-6.1-sol effort=high -->`, `runs.jsonl`, and the attempt record.
- Plugin commit `def3b33` (T-0171 steps 1 to 4), with no uncommitted change under `plugins/`.
- macOS, Darwin 25.6.0. Throwaway Git projects in a temp folder outside this repository, removed after the run. Role logs are not kept in this repository.

## Projects

- Claude Code: `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/plan-review-probe.3WrEjPYrWb/claude`
- Codex: `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/plan-review-probe.3WrEjPYrWb/codex`
- Family rule fixture: `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/plan-review-probe.3WrEjPYrWb/family`

Each project was set up the same way and committed once (`0d76272 init`):

- `greet.sh`: `#!/usr/bin/env bash` and `echo hello`.
- `.gitignore`: `.sdlc/` and `.worktrees/`.
- Two task dirs, `.sdlc/probe-defective/` and `.sdlc/probe/`, with the same `handoff.md`. Goal: "`greet.sh` prints `hello <name>` for the name given as its first argument (`bash greet.sh Ada` prints `hello Ada`) and `hello world` with no argument". Context names `greet.sh`. Constraints: "one file".

The defective plan was written by hand at `.sdlc/probe-defective/planner-L3.md` with the header `<!-- role=planner level=L3 model=fable effort=xhigh -->`. It has one step at `level: L4`. Its Do says "Add name support to greet.sh; pick the argument convention (positional or `--name`) as you see fit". Its only criterion is `bash greet.sh Ada | grep -q Ada`, so the no-argument default and the `hello` text are uncovered. It has no `## Assumptions`, and `## Risks` is "None". The Codex copy differs only in its header, `model=gpt-6-astra`.

## Method

Every role ran from the project root through a wrapper `W` that unsets `CLAUDECODE`, every `CLAUDE_CODE_*` variable, and `SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON`, then execs this repository's `plugins/sdlc-lite/scripts/run.sh`. A nested run therefore inherits no base sha, attempt id, or temp-worktree prefix from the run that launched it. `<repo>` below is this repository.

Claude Code, defective plan:

```sh
python3 <repo>/plugins/sdlc-lite/scripts/steps.py review .sdlc/probe-defective
W plan-reviewer L1 .sdlc/probe-defective/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py review .sdlc/probe-defective
python3 <repo>/plugins/sdlc-lite/scripts/steps.py split .sdlc/probe-defective
```

Claude Code, sound plan:

```sh
W planner L3 .sdlc/probe/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py review .sdlc/probe
W plan-reviewer L1 .sdlc/probe/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py review .sdlc/probe
python3 <repo>/plugins/sdlc-lite/scripts/steps.py split .sdlc/probe
W builder L1 .sdlc/probe/step-1/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py next .sdlc/probe/step-1
W verifier L1 .sdlc/probe/step-1/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py next .sdlc/probe/step-1
```

The builder level L1 came from the plan's `level: L1`, and the verifier level from `steps.py next`, which printed `verify L1`.

Family rule, no model call, in the fixture project (one commit holding `.gitignore`, and `.sdlc/fam/` holding `handoff.md` and `planner-L2.md`):

```sh
# planner-L2.md header: <!-- role=planner level=L2 model=opus effort=high -->
SDLC_DRY_RUN=1 W plan-reviewer L1 .sdlc/fam/handoff.md
# negative control, header changed to model=sonnet
SDLC_DRY_RUN=1 W plan-reviewer L1 .sdlc/fam/handoff.md
```

Codex, defective plan:

```sh
python3 <repo>/plugins/sdlc-lite/scripts/codex_roles.py install .
python3 <repo>/plugins/sdlc-lite/scripts/codex_roles.py resolve plan-reviewer L1 .sdlc/probe-defective
python3 <repo>/plugins/sdlc-lite/scripts/steps.py review .sdlc/probe-defective
SDLC_BACKEND=codex W plan-reviewer L1 .sdlc/probe-defective/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py review .sdlc/probe-defective
python3 <repo>/plugins/sdlc-lite/scripts/steps.py split .sdlc/probe-defective
```

`codex_roles.py install .` installed 24 project agents.

## Which runs ran

All runs came from one attempt of T-0171 step 5, on plugin commit `def3b33`. Six model calls ran, each once, and none was retried.

| Host | Run | Result file |
| --- | --- | --- |
| Claude Code | plan-reviewer L1 on the defective plan | `claude/probe-defective/plan-reviewer-L1.md` |
| Claude Code | planner L3 on the sound task | `claude/probe/planner-L3.md` |
| Claude Code | plan-reviewer L1 on the sound plan | `claude/probe/plan-reviewer-L1.md` |
| Claude Code | builder L1 on step 1 | `claude/probe/step-1/builder-L1.md` |
| Claude Code | verifier L1 on step 1 | `claude/probe/step-1/verifier-L1.md` |
| Codex | plan-reviewer L1 on the defective plan | `codex/probe-defective/plan-reviewer-L1.md` |

The evidence folder [plan-reviewer-live-run/](plan-reviewer-live-run/) holds each task dir's result files, `handoff.md`, `planner-*.md`, `runs.jsonl`, `*.attempt.json`, and `step-1/`, without role logs.

## Results

| Host | Arm | Result | Evidence |
| --- | --- | --- | --- |
| Claude Code | `steps.py review` before the defective plan's review | `review L1` | reason `a plan review is required (planner-L3.md is a planner L3 plan; a step is at builder L4 or L5) and none counts after planner-L3.md` |
| Claude Code | defective plan rejected | yes, Verdict `replan` | `claude/probe-defective/plan-reviewer-L1.md`: five findings on step 1: goal coverage (no-argument `hello world` uncovered), builder readiness (argument convention left to the builder), acceptance criteria (the grep accepts output without `hello`), builder readiness (L4 does not fit a one-file edit), scope (no scope criterion). Missing decisions: None |
| Claude Code | `steps.py review` after the rejection | `replan` | reason `the newest plan review plan-reviewer-L1.md says replan; replan at planner L3` |
| Claude Code | split refusal | refused, exit 1 | stderr `steps: .sdlc/probe-defective/planner-L3.md: the newest plan review plan-reviewer-L1.md says replan; a rejected plan is never split` and `plan defect: plan review: replan; run steps.py review (/chain 3)`. No `step-1/` was written |
| Claude Code | defective plan reviewer model | `model=opus effort=high` | result header, and `runs.jsonl` holds `"role":"plan-reviewer","level":"L1","model":"opus","effort":"high"`. The planner header said `model=fable`, so the reviewer kept Opus |
| Claude Code | family rule, Opus planner | `--model fable --effort high` | dry-run command line `claude -p --plugin-dir <repo>/plugins/sdlc-lite --agent sdlc-lite:plan-reviewer --model fable --effort high --dangerously-skip-permissions ...` |
| Claude Code | family rule, negative control with a Sonnet planner | `--model opus --effort high` | dry-run command line `claude -p ... --agent sdlc-lite:plan-reviewer --model opus --effort high ...` |
| Claude Code | `steps.py review` before the sound plan's review | `review L1` | reason `a plan review is required (planner-L3.md is a planner L3 plan) and none counts after planner-L3.md` |
| Claude Code | sound plan verdict | `pass` | `claude/probe/plan-reviewer-L1.md`: Findings None, Missing decisions None. Header `model=opus effort=high`; the planner ran on Fable. No replan was needed |
| Claude Code | `steps.py review` after the pass | `split` | reason `the newest plan review plan-reviewer-L1.md passed planner-L3.md`; `steps.py split` exit 0, wrote `step-1/handoff.md` |
| Claude Code | build verdict | Status `done` | `claude/probe/step-1/builder-L1.md`: `greet.sh` became `name=${1:-world}` and `echo "hello $name"`. `steps.py next` printed `verify L1` |
| Claude Code | verify verdict | Verdict `pass` | `claude/probe/step-1/verifier-L1.md`: all six criteria pass, each shown red at base `0d76272` or on a fixture. `steps.py next` printed `done` |
| Codex | resolve | `gpt-6.1-sol high` | `codex_roles.py resolve plan-reviewer L1 .sdlc/probe-defective` with a planner header `model=gpt-6-astra` |
| Codex | `steps.py review` before the review | `review L1` | same reason as the Claude Code defective plan |
| Codex | defective plan rejected | yes, Verdict `replan` | `codex/probe-defective/plan-reviewer-L1.md`: five findings on step 1: goal coverage (no-argument output uncovered), interfaces (`--name` conflicts with the positional argument), acceptance criteria (the grep accepts `Ada` without `hello`), builder readiness (convention left to the builder), builder readiness (L4 exceeds the fitting level). Missing decisions: None |
| Codex | alternate reviewer model | `model=gpt-6.1-sol effort=high` | result header, `runs.jsonl` `"model":"gpt-6.1-sol","effort":"high"`, attempt record `"transport": "exec"`, `"status": "completed"` |
| Codex | `steps.py review` after the rejection, and split | `replan`; split refused, exit 1 | same reason line and the same two stderr lines as on Claude Code |

## Limits

- One trial ran per arm, on one machine and one account per host. The defective plan was written by hand to hold known defects; the run shows the reviewer catches those defects, not that it catches defects a planner makes.
- The sound plan was reviewed once and passed on the first review, so the replan loop of /chain 3 (append `plan review: replan:` lines, planner L3, review again) did not run live. The Codex arm reviewed only the defective plan; no Codex planner, sound-plan review, build, or verify ran.
- The family rule to Fable was shown only in a dry run. No live plan-reviewer ran on Fable, because both live Claude Code reviews followed a Fable planner or a hand-written Fable header and kept Opus.
- The Codex result had a blank line after `## Verdict`; the verdict readers skip blank lines, so the verdict still parsed as `replan`.
- The Codex `runs.jsonl` line records `"transport":"codex"`; the attempt record is the source for `"transport": "exec"`.
- No benefit is claimed: completion time, replans, rebuilds, and correctness are not yet measured against the same tasks without the reviewer.
