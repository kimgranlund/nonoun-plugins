---
name: agent
description: "Launch an SDLC Lite agent by name on instructions: solo delivers a ticket, scout, researcher, architect, and archaeologist answer a question. Other names point to their own skill. NOT for creating agents."
argument-hint: "{agent-name} [--tier S|M|L | --level L1|L2|L3] {instructions}"
allowed-tools: Bash, Agent, Read, Write, Grep, Glob
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

The first word is the agent name. Everything after the optional `--tier` or `--level` flag is the instructions. Match the name against this list and nothing else; never guess a near match.

| Name | Start path | Default |
|---|---|---|
| `solo` | The `## Start` section of `${CLAUDE_PLUGIN_ROOT}/agents/solo.md`: a background sub-agent on Claude Code, `sdlc-solo-l1` to `l3` on Codex | tier M, or the tier of the named ticket's size (S, M, L) when the instructions name a ticket |
| `scout` | dispatch `scout` L1 on `<handoff>` (Codex: `scripts/run.sh scout L1 <handoff>`) | L1 |
| `researcher` | dispatch `researcher` at `<level>` on `<handoff>` (Codex: `scripts/run.sh researcher <level> <handoff>`), level per the `researcher` section of the level-rubric skill | per the rubric |
| `architect` | dispatch `architect` L1 on `<handoff>` (Codex: `scripts/run.sh architect L1 <handoff>`) | L1 |
| `archaeologist` | dispatch `archaeologist` L1 on `<handoff>` (Codex: `scripts/run.sh archaeologist L1 <handoff>`) | L1 |

Other SDLC Lite agents have their own path; answer in one line and stop: `planner` to `/sdlc-lite:plan`, `builder` to `/sdlc-lite:build`, `verifier` to `/sdlc-lite:verify`, `plan-reviewer` to `steps.py review`, `filer` to `/sdlc-lite:file`, `messenger` to `.sdlc/messages/AGENTS.md`. Refuse `conductor`: it is the session you are in. For any other name, print the names above and stop.

Workflow:
1. Resolve the tier or level from the flag, else the default in the table. For `solo`, size S is tier S, M is tier M, L is tier L.
2. Print one line before launching: `Lane: <name> <tier or level> because <reason>`. Set `SDLC_ROUTING_REASON` to the same reason for any dispatch (`dispatch.py prepare` reads it; Codex: `run.sh`).
3. For `solo`, write a typed brief from the instructions (the ticket or task, the files it needs, the check commands, the done criterion) and start it as `agents/solo.md` says, from the project root, through `scripts/solo_run.py`, which checks the budget and prints the dispatch JSON; spawn the Agent tool with that JSON (`subagent_type sdlc-lite:solo-<tier>`, its model, effort, and prompt). When the run needs a lane worktree and branch, add `--worktree <name>` (with `--exec`): the launcher creates `.worktrees/<name>` on a new branch `<name>` before the session starts, because the solo role cannot (`block-stray-worktree.sh`). When the instructions name a ticket, pass its folder as `--task-dir`; when they name none, pass `--new-task` instead (it creates a small task folder from the brief) so the run is still recorded and metered. A budget stop (exit 4) means the ticket is at 80 percent of its budget: report it and ask the user before `budget.py ack`. For tiers M and L the report says `verify: needed`: run `dispatch.py prepare verifier L2 <task dir>/handoff.md` and spawn its JSON (`hooks/block-role-spawn.sh` still denies a nested spawn from a role).
4. For the read-only roles, create a task folder under the ticket root (`.sdlc/<slug>/`, or `.sdlc/tickets/<slug>/` when `.sdlc/config` has `ticket_root: tickets`) and write `handoff.md` from the instructions per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`, with the instructions under `## Question`. Then dispatch the role from the project root as a sub-agent, in three steps: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prepare <role> <level> <handoff.md>` runs the gates and prints the dispatch JSON; an `Agent` call passes its `subagent_type`, `name`, `description`, `model`, `prompt`, and `run_in_background` unchanged; `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> --transcript <sub-agent transcript jsonl> --tool-uses <n> --duration-ms <ms>`, with the sub-agent's final message on stdin, validates and records the result (the contract is `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md`, "How you run roles"). On Codex run `SDLC_BACKEND=codex ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh <role> <level> <handoff.md>` instead.
5. Follow the interactive vs headless rule in `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md`: in an interactive session start the agent in the background and keep talking with the user; headless, run it in the foreground and do not end your turn until it finishes.
6. When it finishes, report the result file path and a three-line summary. On failure (`record` exit 1 or 3), report the error and the result or `.limit` file path (Codex: the log path). Do not redo or extend the agent's work yourself.
