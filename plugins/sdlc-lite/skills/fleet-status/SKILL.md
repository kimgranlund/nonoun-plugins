---
name: fleet-status
description: "The status of every active repo in one screen, in a fixed order: machine load with a verdict, what needs the user, what is really moving, what is stale or stuck, what finished since the last report, and release state. Printed by scripts/fleet_status.py render, never composed by hand, then at most one AskUserQuestion round for the Needs-you items. Use for \"fleet status\", \"status across repos\", \"what needs me\", \"what is stuck\", \"what is running everywhere\". NOT for one repo's task table (/board); NOT for messaging conductors."
argument-hint: "[--repos A,B] [--since last|DATE] [--ping]"
allowed-tools: Read, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_status.py render:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host's question mechanism. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

## 1. Render

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_status.py render` from the project root that holds `.sdlc/fleet.json`, passing the arguments through: `--repos A,B` (registry names), `--since last|DATE` (default `last`, the stored snapshot), `--ping`. Each call stores a snapshot, so the next `--since last` starts from this one. The script makes no model call and only reads the repos it inspects; it takes about 15 seconds on a busy machine.

Exit 2 or 1: report stderr in one sentence (a bad registry, an unknown repo, a bad date, a row with no source) and stop.

## 2. Print it

Print stdout verbatim as the reply, before any question, inside one fenced code block (plain `text`) so the columns keep their alignment. Render, never compose: do not rewrite, reorder, shorten, summarize, or fix a row, and never build a table of your own. The output order is Machine, Needs you, Moving, Stale or stuck, Done since last report, Release state, and Ping with `--ping`. Needs you, Moving, Stale or stuck, and Release state are plain aligned tables the script writes (a header row, a dashed rule, columns Repo, Row, State, Detail, Source padded with spaces, no pipes); Machine is one line. Marks in the State column: 🟢 live, 🟡 idle, 🔴 dead, ⚠️ stale, ⚪ nothing moving. Closed tickets whose board rows still claim work are folded into one row per repo under Stale or stuck (`N closed tickets still shown on the board`). Every row carries its source in brackets, the last column of a table row.

`--ping` lists the conductors with work to report on, to message for a health report. This skill sends nothing; the user or the conductor sends with `messages.py`.

## 3. Ask once

The rows under `Needs you` are the only reason to ask. None (`Needs you: nothing`): stop after the output.

Otherwise make exactly ONE AskUserQuestion call of 1 to 4 questions, one per row, oldest first. With more than 4 rows ask the 4 oldest and name the rest in the framing ("4 of 7"). Header chips stay under 12 characters. For each row write 2 to 3 options whose descriptions carry the consequence in one line, and put an option first marked `(Recommended)` only when the row or the ticket supports it:

- `merge` row (State column): `Merge it` first and recommended when the Detail says APPROVED and CLEAN; otherwise `Look at it first` first. Then `Leave it open`.
- `decision` row: read the ticket's `## Goal` and `## Context` (the row's Source is the ticket folder under that repo's `.sdlc`) and offer the real choices it names. Recommend one only when the ticket states a default.
- `credential` row: `I will provide it` first, then `Skip this ticket for now`.

If AskUserQuestion is unavailable in this session (a headless run, for example), ask the same round as numbered plain-text questions with the same options, then end the turn; say that it is plain text. Never a second round in the same turn.

## 4. Relay, do not act

Reply with one line per answer. Do not merge, message a conductor, edit a ticket, file, or close anything: the user or the conductor acts on the answers.

Rules:
- Render, never compose. The script is the only author of the table.
- The data `render` draws is the `collect` object, and [resources/fleet-status.schema.json](resources/fleet-status.schema.json) (JSON Schema, draft 2020-12) is the authority for its keys, types and allowed values; the script's selftest checks a collected fixture against it.
- `Moving` lists only rows with a live process, a live marker, or activity in the last 15 minutes. A row the board shows as building with none of those is under `Stale or stuck`, whatever the board says.
- A repo the registry excludes never appears; `--repos` naming one skips it.
- The first call after a fresh checkout says `first report` under Done since: pass `--since DATE` for a dated list.
