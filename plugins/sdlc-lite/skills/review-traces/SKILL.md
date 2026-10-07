---
name: review-traces
description: "Review a project's sdlc run traces for waste and bugs caused by sdlc-lite, with no model call in the ingest and detect stages, then diagnose, verify, propose, and file each confirmed finding as a ticket after approval."
argument-hint: "<repo> [--lanes-dir DIR]... [--max N]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traces.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*), Agent, Read, Write, Grep, Glob, AskUserQuestion
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

When launching a role, set `SDLC_ROUTING_REASON` to a short explanation of the chosen role and level (user selection, task scope, or escalation evidence). `dispatch.py prepare` (Codex: `run.sh`) reads it and records the resolved model and effort separately. Read [run operations](../handoff-format/run-operations.md) for readiness and interrupted-attempt recovery. To dispatch a role, follow the three steps of `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md` ("How you run roles"): `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prepare <role> <level> <handoff.md>` runs the gates and prints the dispatch JSON; an `Agent` call passes its `subagent_type`, `name`, `description`, `model`, `prompt`, and `run_in_background` unchanged; `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> --transcript <sub-agent transcript jsonl> --tool-uses <n> --duration-ms <ms>`, with the sub-agent's final message on stdin, validates and records the result at `<role>-<level>.md` next to the handoff. On Codex a role runs through `SDLC_BACKEND=codex ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh <role> <level> <handoff.md>`.

Create a review task dir `.sdlc/<review task>/` from the arguments per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`, with a `handoff.md` naming the repo, every `--lanes-dir`, and `--max`. All stage outputs below go under it.

## 1. Ingest and detect

These commands spend no model call.

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traces.py ingest <repo> [--lanes-dir DIR]...`, passing each `--lanes-dir` from the arguments.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traces.py detect`.
3. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traces.py clusters --max N`, with N from `--max` (default 5).

If no clusters come back, report that and stop.

## 2. Diagnose

For each cluster k, write `.sdlc/<review task>/cluster-<k>/handoff.md` from this template:

```cluster-question
## Goal
Find the cause of trace cluster <k>.

## Context
Findings in this cluster:
- <finding id>: <summary> (evidence: <path>, <path>)

Read only the evidence paths listed above; nothing else.

## Question
Which layer causes these findings: sdlc-lite, project, host, or task text? If sdlc-lite, name the plugin file or rule at fault.
```

Dispatch the archaeologist at L1 on `<cluster handoff.md>`, or the scout at L1 when the question is where a rule lives. Read the result's `## Summary` for the layer and the file. Keep only findings whose layer is sdlc-lite for stage 3; the rest go to the stage 5 report.

## 3. Verify

A finding whose evidence cannot be rendered as commands is dropped before any run.

For each finding kept by stage 2, write `.sdlc/<review task>/finding-<id>/handoff.md` from this template, a step handoff per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`. Write one criterion line per evidence entry, replacing `<evidence command>` with that entry rendered as a runnable check:

- a `{path, line}` entry becomes `sed -n '<line>p' <path> | grep -qF '<quoted text>'`
- an `{attempt_id}` entry becomes `grep -q '<attempt_id>' <attempt.json path>`

```finding-step
## Task goal
Review the sdlc run traces of the repo named in the review handoff and confirm each finding caused by sdlc-lite from its evidence.

## Step 1: Reproduce finding <id>
level: L1
### Do
Nothing to build. This step only reproduces finding <id> from its evidence: run each criterion below and report whether it holds.
### Acceptance criteria
- `<evidence command>`
```

Lint it with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint <finding handoff.md>` and fix any finding before the run. Then dispatch the verifier at L1 on `<finding handoff.md>`.

- A `fail` verdict drops the finding from the propose list.
- A `pass` verdict keeps it for stage 4.
- No verdict reruns the verifier once; still no verdict drops the finding.

Dropped findings go to the stage 5 report with the reason.

## 4. Propose

Write `.sdlc/<review task>/propose/handoff.md` from this template, with one Context entry per finding kept by stage 3. Fill `Actual:` with text quoted verbatim from the finding summary and its evidence, never paraphrased. Fill `Red check:` with one command that fails today and passes once the defect is fixed: a `traces.py selftest` case, a script selftest case, or a fixture.

```propose-handoff
## Goal
Draft one ticket per confirmed sdlc-lite finding listed below.

## Context
Finding <id>:
- detector: <detector>
- summary: <summary>
- evidence: <path>, <path>
- diagnose result: <cluster result path>
- verify result: <finding verifier result path>

Ticket for finding <id>:
Repro: <steps from the evidence>
Expected: <what sdlc-lite should have done>
Actual: <quoted verbatim from the finding summary and evidence>
Red check: <one command that fails today and passes once fixed>

## Constraints
- Drafts only: no code, no filing.
- One `## Step` per ticket, each at level L1.
```

Dispatch the planner at L2 on `<propose handoff.md>` once. Each `## Step` of the result is one ticket draft: its title is the ticket title, its Do is the ticket body, and its acceptance criteria are the red check.

## 5. File

Model-call cap: at most `clusters + findings + 1` role runs per review (one archaeologist or scout per cluster, one verifier per finding, one planner), bounded by `--max N`. The ingest and detect stages spend none.

Findings whose layer is not sdlc-lite, and findings dropped in stage 3, go to `.sdlc/<review task>/report.md`, one section per finding: layer, evidence, diagnose summary (and the drop reason, if any). They are never filed.

A session with no person present (`SDLC_HEADLESS=1`, a fanout lane, or `claude -p`) writes every draft to `report.md` and files nothing.

Otherwise ask one AskUserQuestion round over the drafts: at most 4 options per question, so batch the drafts four at a time, recommendation first. For each approved draft:

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py new bug <slug> "<title>"`. Numbered mode follows `<root>/config`.
2. Write the ticket's `handoff.md` body from the draft:
   - Repro: the draft's repro steps.
   - Expected: the draft's expected behavior.
   - Actual: the draft's quoted actual behavior.
   - Context: the evidence paths, the diagnose result path, and the verify result path.
   - Constraints: the red check lands before or with the fix.

Drafts not approved go to `report.md`.

## Report

- Findings path: the file written by `traces.py detect`.
- Clusters: each cluster id with its findings and diagnosed layer.
- Drafts filed: each title with its ticket id.
- Report path: `.sdlc/<review task>/report.md`.
