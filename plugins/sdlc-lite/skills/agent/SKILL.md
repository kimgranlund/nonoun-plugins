---
name: agent
description: "Launch an SDLC Lite agent by name on instructions: solo delivers a ticket, scout, researcher, architect, and archaeologist answer a question. Other names point to their own skill. NOT for creating agents."
argument-hint: "{agent-name} [--tier S|M|L | --level L1|L2|L3] {instructions}"
allowed-tools: Bash, Read, Write, Grep, Glob
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

The first word is the agent name. Everything after the optional `--tier` or `--level` flag is the instructions. Match the name against this list and nothing else; never guess a near match.

| Name | Start path | Default |
|---|---|---|
| `solo` | The `## Start` section of `${CLAUDE_PLUGIN_ROOT}/agents/solo.md`: a headless Bash session on Claude Code, `sdlc-solo-l1` to `l3` on Codex | tier M, or the tier `steps.py lane` gives when the instructions name a ticket |
| `scout` | `scripts/run.sh scout L1 <handoff>` | L1 |
| `researcher` | `scripts/run.sh researcher <level> <handoff>`, level per the `researcher` section of the level-rubric skill | per the rubric |
| `architect` | `scripts/run.sh architect L1 <handoff>` | L1 |
| `archaeologist` | `scripts/run.sh archaeologist L1 <handoff>` | L1 |

Other SDLC Lite agents have their own path; answer in one line and stop: `planner` to `/sdlc-lite:plan`, `builder` to `/sdlc-lite:build`, `verifier` to `/sdlc-lite:verify`, `plan-reviewer` to `steps.py review`, `filer` to `/sdlc-lite:file`, `messenger` to `.sdlc/messages/AGENTS.md`. Refuse `conductor`: it is the session you are in. For any other name, print the names above and stop.

Workflow:
1. Resolve the tier or level from the flag, else the default in the table. For `solo`, size S is tier S, M is tier M, L is tier L.
2. Print one line before launching: `Lane: <name> <tier or level> because <reason>`. Set `SDLC_ROUTING_REASON` to the same reason for any `run.sh` launch.
3. For `solo`, write a typed brief from the instructions (the ticket or task, the files it needs, the check commands, the done criterion) and start it as `agents/solo.md` says, from the project root, with the tier's model and effort from its table. Never spawn it with the Agent tool from a conductor: `hooks/block-role-spawn.sh` denies that.
4. For the read-only roles, create a task folder under the ticket root (`.sdlc/<slug>/`, or `.sdlc/tickets/<slug>/` when `.sdlc/config` has `ticket_root: tickets`) and write `handoff.md` from the instructions per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`, with the instructions under `## Question`. Then run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh <role> <level> <handoff.md>`.
5. Follow the interactive vs headless rule in `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md`: in an interactive session start the agent in the background and keep talking with the user; headless, run it in the foreground and do not end your turn until it finishes.
6. When it finishes, report the result file path and a three-line summary. On failure, report the error and the log path. Do not redo or extend the agent's work yourself.
