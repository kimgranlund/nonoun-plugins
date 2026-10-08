---
name: fleet-retro
description: "Run a retro of how SDLC Lite served several repos at once: collect each repo's fingerprint, detect waste and stalls mechanically, interview each repo's conductor, write one cost-ranked report where every finding carries an evidence pointer and [V] or [U], check the findings with a sampled verifier and the actionability rubric, and file the confirmed ones after one approval round. Use for \"retro across my repos\", \"where is the plugin costing us\", or a periodic fleet review. NOT for one repo's run traces (review-traces), a live status view (board), or unattended filing."
argument-hint: "<repo>..."
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_collect.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_detect.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_config.py show:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*), Agent, Read, Write, Grep, Glob, SendMessage, AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. SendMessage becomes the host's way to message another session; with none, run step 3 as skipped. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (one repo path per word; none means the active entries of `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_config.py show --active`, whose second column names each repo's conductor session).

Every repo is read-only: this skill never writes, commits, or messages into a repo it inspects, and the interview tells a conductor the same. No model call runs before step 3. When launching a role, pass `dispatch.py prepare --routing-reason "<why>"` (or set `SDLC_ROUTING_REASON`) with a short explanation of the chosen role and level; read run operations at `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/run-operations.md` for readiness and interrupted-attempt recovery.

Work folder `W` is `.sdlc/fleet-retro-<date>/` in the repo that runs this skill; the report is `docs/reports/fleet-retro-<date>.md` there. A repo with no `.sdlc` is listed in the report header and skipped.

## 1. Collect

For each repo, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_collect.py collect <repo> --gh > W/<name>.json`, `<name>` the repo folder name. Add `--since DATE` to bound the window, and `--until DATE` only to reproduce an earlier report's numbers (a live repo keeps adding runs). Keep each stderr `runs:` line for the report header. A `--gh` error is recorded in the fingerprint; go on without CI.

## 2. Detect

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_detect.py detect W/*.json > W/findings.jsonl`. Each line is a finding: rule, repo, evidence path into a fingerprint, measured value, threshold. A `scope: machine` finding is the same machine in every fingerprint: report it once.

## 3. Interview

Send the exact text of [the interview template](interview.md) (below its `---` line) with SendMessage to each repo's conductor session, one message per repo, then wait for the one-line replies. Each reply names `.sdlc/fleet-retro-<date>.md` in that repo: read it, never edit it. Wait until every reply is in or 15 minutes pass; a repo with no reply is reported `interview: none` and has no judgment rows. Never message a session you cannot name. With no person present (`SDLC_HEADLESS=1`, a fanout lane, `claude -p`) no reply can arrive: skip this step and say `interview: skipped, no person present` in the header. A report the repo already holds from the same day (for example `.sdlc/root-cause-<date>.md`) stands in for the reply: read it, cite its section as evidence, keep its [V] and [U] marks (any other mark reads as [U], as in the interview's row rules), and name its path in the header.

## 4. Report

Write `docs/reports/fleet-retro-<date>.md` from this template. Counts and costs come from the fingerprints, never from a conductor's memory.

```fleet-report
# Fleet retro <date>

Repos: <name: runs line from step 1, interview state>. Plugin: <env.plugin version and path>, <claude version>. Window: <since, until>.

## Cross-repo table
| Repo | Runs | Spend | Plan-review share | Interrupted + limit | Findings |
|---|---|---|---|---|---|

## Findings
| # | Repo | Symptom | Evidence | Mechanism | Cost | [V] or [U] | Check | Prevention |
|---|---|---|---|---|---|---|---|---|
```

One finding row per `findings.jsonl` line (machine scope: one row) and per interview row. Rank by Cost: dollars, then minutes, then `unmeasured`, a tie going to the larger measured value; at most 20 rows. Evidence is a pointer a reader can run or open: `<fingerprint file> :: <evidence path>` for a detect finding, the conductor's command or log path for an interview row. A detect finding is [V]; an interview row keeps the conductor's [V] or [U]. Cost is the measured dollars or minutes, or `unmeasured`. A row with no evidence pointer is deleted, not repaired by guessing; Grep the table for an empty cell before step 5. Check starts as `-` and step 5 fills it.

## 5. Verify

One verifier run covers the report. Write `W/verify/handoff.md` as a step handoff per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`, level L1, no `### Do` work, with these criteria:

- Sample: with V the number of [V] rows ranked by Cost, take rows 1, 6, 11, and so on (ceil of V/5 rows, at least 1). Per sampled row, one criterion rendering its evidence as a command: a fingerprint path becomes `python3 -I -c` loading `fleet_detect.py`'s `evidence_value(fp, path)` and comparing it with the row's value; a log path becomes `grep -qF '<quoted text>' <log>`.
- Rubric: one criterion per row, [V] and [U], whole report: the row passes every gate of [the rubric](rubric.md) and scores at least 7 of 10.
- Control: one planted [V] row with a real evidence pointer and a value that is wrong, stated as a claim that holds (`The planted claim holds: <command>`). It is not in the report's table. The command must exit non-zero and the verifier must report `fail`. A control that passes means the verifier checks nothing: stop and report that.

Lint with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint W/verify/handoff.md`, then dispatch the verifier at L1 on `W/verify/handoff.md` (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prepare verifier L1 W/verify/handoff.md`, an `Agent` call with the printed `subagent_type`, `name`, `description`, `model`, `prompt`, and `run_in_background` unchanged, then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> --transcript <sub-agent transcript jsonl> --tool-uses <n> --duration-ms <ms>` with the sub-agent's final message on stdin; `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md`, "How you run roles", has the contract; on Codex `SDLC_BACKEND=codex ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh verifier L1 W/verify/handoff.md`). Read the result's `## Criteria` lines, not its overall verdict: Claude: after `record`, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prune`, make each `TaskStop task_id=<name>` call it lists, then `prune --done <name>`; a finished sub-agent stays an idle teammate until stopped.

- A sampled claim that fails: set its row to `[U]`, Check `downgraded`, and name the result file. A [V] row whose reproduction was not run stays [V], Check `not sampled`.
- A row below the rubric: set its Check cell to `not actionable: <failed gate or score>` and list it under `## Not actionable`. The row stays in the table and is not filed. A row whose only failed gate is G4 because its mechanism is `not diagnosed` is marked `needs diagnosis`; `/review-traces <repo>` is its next step.
- No verdict: rerun once; still none, mark every row Check `unchecked` and file nothing.

## 6. File

Findings that pass the rubric and whose mechanism names an sdlc-lite file or rule go to review-traces stage 4 (Propose) and stage 5 (File), skipping its stages 1 to 3: one propose handoff, with the finding row as its Context and the step 5 result as its verify result. Fill `Red check:` with the finding's detect rule going silent on a fresh collect, or a selftest case. Each ticket body also gets `outcome metric: <rule or command>, before: <value>`, which the next retro reads for the rubric's outcome check. Findings about a project, the host, or task text stay in the report.

Stage 5's one AskUserQuestion round, batched four drafts at a time with the recommendation first, is the end of this skill. Unattended (`SDLC_HEADLESS=1`, a fanout lane, `claude -p`) file nothing: list the drafts in the report. Never auto-approve.

## Report

- Report path, repos covered, and each repo's `interview:` state.
- Findings: count by [V] and [U], how many were sampled, how many downgraded, how many passed the rubric.
- Drafts filed with their ticket ids, or `none`.
