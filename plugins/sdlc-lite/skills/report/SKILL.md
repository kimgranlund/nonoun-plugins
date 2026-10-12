---
name: report
description: "Report the state of this agent thread: an executive summary by default, or the views you name (tasks, signals, needs, context, cost, children, identity, evidence, lanes, waves, full). It shows what finished, what is in progress, what comes next, what needs the person, and where the thread has problems or likely problems (late failure, context sprawl, stalls), then a hygiene grade. The lanes and waves views show the fanout and solo lane state of the repo. Printed by scripts/report.py from records and the transcript, never composed by hand. Use for \"/report\", \"status\", \"what are you doing\", \"what did you finish\", \"what is wrong\", \"how is this session going\". NOT for a repo task table (/board); NOT for the state of every repo (fleet-status); NOT for a retro across runs (fleet-retro)."
argument-hint: "[view...] [--since T] [--last N] [--next N] [--only G,...] [--severity problem|likely|all] [--format text|md|json] [--evidence] [--compare last] [--explain] [--no-snapshot]"
allowed-tools: Read, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/report.py:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host's question mechanism. The Codex transcript mapping is unverified: the script finds a transcript only from Claude Code's session id (or `SDLC_REPORT_TRANSCRIPT`), so on Codex the context fields list under `unknown`. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (views and options; none means the executive summary).

## 1. Run

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/report.py render $ARGUMENTS` from the project root. The script reads this session's records (`.sdlc` tickets, attempts, `runs.jsonl`, `git`, `gate_lock.py status`) and, for the context views, its transcript. It makes no model call, writes one snapshot under `.sdlc/runtime/` (unless `--no-snapshot`), and takes a few seconds.

Exit 2 is a refusal: an unknown view or option, or an unreadable record. Print stderr (it lists the valid views and options) and stop. Never guess a view.

## 2. Print it

Print stdout verbatim as the reply, in one plain `text` block when the format is `text`. Render, never compose: do not summarize, reorder, shorten, translate or add a line. A line the script marks `[U]` stays marked. The one thing you add is nothing.

The default, with no arguments, is the executive summary: at most 8 lines (state, needs, now, next, grade, plus recent and unknown lines when they are not empty). A view prints only its own section; `lanes` and `waves` read the repo's lanes, not the thread. `full` prints every section in a fixed order. [The view and option reference](references/views.md) lists them; [the record schema](references/record-schema.md) defines every field and where it comes from.

## 3. If the report shows `needs`

The `needs` lines are the only reason to ask. None: stop after the output. Otherwise make one AskUserQuestion call (1 to 4 questions, 2 to 4 options each, recommendation first only when the line's source supports it), then relay the answer in one line. Do not act on the answer in this skill.

## Rules

- Every non-trivial line carries an evidence pointer that resolves; `--evidence` prints it.
- A value the collector could not read is listed under `unknown`, never shown as 0. An unpriced run is `unpriced`, not `$0`.
- State is derived (pid liveness, time since the last tool call, an open question in the transcript), never asserted by the session about itself.
- Status lines use the closed verb list and tense rule of [the entry grammar](references/views.md#entry-grammar): past tense for what finished, present progressive for what runs, future with a trigger for what comes next.
- `next` comes from ticket `depends:`, the ready queue and `steps.py next`. An item with no ticket or step is marked `intended`, not `planned`.
- A grade is a band over measured flags and names the flags that set it. Thresholds live in `.sdlc/config`; `--explain` shows each rule, value and threshold. A flag is `[U]` until its threshold is calibrated.
