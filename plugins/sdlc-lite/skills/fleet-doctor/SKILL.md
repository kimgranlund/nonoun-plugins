---
name: fleet-doctor
description: "Diagnose why runs are slow or stuck right now: a role waiting on stdin, a stalled lane, a slow check.sh, an overloaded machine, a runaway process, a heavy peer repo, or replan cost. Printed by scripts/fleet_doctor.py with evidence per finding, then one AskUserQuestion round of ranked fixes, carried out only on a yes. Use for \"why is it slow\", \"what is stuck\", \"is something hung\", \"fleet doctor\". NOT Claude Code's built-in /doctor; NOT for what is moving (/fleet-status) or what went wrong over a window (/fleet-retro)."
argument-hint: "[<repo>...]"
allowed-tools: Read, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_doctor.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_config.py show:*), SendMessage, AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host's question mechanism; with no way to message another session, print the throttle line for the user to send. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

## Arguments

| Argument | Meaning | Default | Example |
|---|---|---|---|
| `<repo>` | One repo path per word, the first is this repo | the active entries of the fleet registry (`fleet.json` in `.sdlc/`, or under `work_root`), else this repo | `. ../api` |

## 1. Collect and detect

From the project root run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_doctor.py collect <repo>...` (no repos: none on the command line), then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_doctor.py detect`. Both make no model call and change nothing outside `.sdlc/runtime/fleet-doctor/`; collect takes a few seconds. Exit 2: report stderr in one sentence and stop.

## 2. Print it

Print the detect output verbatim inside one fenced `text` block. Render, never compose: one numbered finding per rule hit, its evidence, and its fixed resolutions with cost and risk, the first marked `*`. `fleet doctor: no findings`: say so and stop.

## 3. Ask once

Rank the findings: `stdin-wait` and `stalled` first (work is blocked), then `runaway-proc`, `overloaded`, `heavy-peer`, `slow-check`, then `replan-cost`. Make exactly ONE AskUserQuestion call of 1 to 4 questions, one per finding in that order; with more than 4 findings name the rest in the framing ("4 of 7"). Header chips are at most 12 characters (the rule name), option labels 1 to 5 words. The options are that finding's resolutions in the printed order, each description carrying its cost and risk in one line, the first marked `(Recommended)`, plus `Leave it` last. Offer nothing the detect output did not list.

Headless (`SDLC_HEADLESS=1`, a fanout lane, `claude -p`, or no AskUserQuestion): stop after step 2 and act on nothing. Never a second round in the same turn.

## 4. Act on a yes only

For each approved option, and nothing else:

- `kill pid N`: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_doctor.py resolve --kill N`. It kills only a pid a finding names and still running the finding's command; a refusal is reported, never worked around.
- `restart NAME`: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_doctor.py resolve --restart NAME`. It accepts only a daemon the OS respawns, from the script's `DAEMONS` list, with a `runaway-proc` finding.
- A throttle line: find the repo's conductor in `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_config.py show --active` (second column) and send it one line with SendMessage, for example `fleet-doctor: load 54 on 20 cores, hold browser and test lanes until it drops`. A repo with no named conductor: print the line for the user.
- A ticket: name `/sdlc-lite:ticket` with the finding's evidence as the goal, or the existing ticket it matches; this skill files nothing itself.

Then reply with one line per action and its result.

Rules:
- Never kill by name except a listed daemon through `resolve --restart`. Never `kill`, `pkill`, or `killall` directly.
- Never stop a role, a lane, or another repo's process without a yes for that exact finding.
- Every repo it inspects is read-only; the only write is its own state under `.sdlc/runtime/fleet-doctor/`.
- Thresholds are fixed in the script; its `detect` usage names the flags for a planted test, which this skill does not pass.
