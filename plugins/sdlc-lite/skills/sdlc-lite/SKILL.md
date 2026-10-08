---
name: sdlc-lite
description: "Run SDLC Lite workflows in Codex: tickets, handoffs, plans, builds, verification, chains, boards, and parallel lanes. Use for structured software delivery or SDLC Lite status. Includes native Codex role execution and project-scoped predefined subagents. Requires authenticated Codex CLI for pipeline roles."
---

# SDLC Lite in Codex

This is a host adapter over the existing workflows, not a second workflow implementation. Resolve the plugin root as the directory two levels above this skill directory (`skills/sdlc-lite`). Do not infer it from the project working directory.

## Route and load only what is needed

Read the matching `skills/<name>/SKILL.md` under that plugin root:

| Request | Workflow |
|---|---|
| Status or progress | board |
| Status across every active repo, what needs the user, what is stuck | fleet-status |
| Create, inspect, prioritize tickets | ticket |
| Capture work context | handoff |
| Clarify one ask / explore design decisions | clarify / grill |
| Decompose settled scope | decompose |
| Plan / implement a step / verify | plan / build / verify |
| Small fix / execute a whole task | fix / chain |
| Research / repository map / history | research / scout / dig |
| Architecture / finish and file work | architect / file |
| Parallel ticket lanes / benchmark | fanout / bench |
| Launch one SDLC Lite agent by name on instructions | agent |
| Resolve outstanding questions / sweep questions and blockers | open-questions / ask |
| Plan a goal, loop, or fanout run and get a paste-ready command | plan-goal / plan-loop / plan-fanout |
| Set up or check entry files and docs layout | onboard |
| Review sdlc run traces for sdlc-lite waste and bugs | review-traces |
| Retro of how the plugin served several repos, one cost-ranked report | fleet-retro |

Read referenced rubric, handoff format, templates, or scripts only as required. The selected file owns workflow decisions, output format, and completion conditions. Apply the following host translations to its Claude-specific syntax.

## Host translations

- `${CLAUDE_PLUGIN_ROOT}` means the resolved installed plugin root. Substitute its absolute path before using a command or reading a file; quote paths. It is not a Codex-provided environment variable.
- `$ARGUMENTS` means the arguments in the user's current request.
- `/name` or `/sdlc-lite:name` means load that workflow file, not a Codex slash command.
- Read/Grep/Glob/Write/Edit/Bash mean the available Codex file and shell tools. `allowed-tools` in the source is Claude metadata, not a Codex permission grant.
- AskUserQuestion means ask using the host's supported question mechanism or ordinary chat. Respect its question-count limits. For approvals use a supported approval channel or ordinary chat; never substitute an unavailable tool. Existing user authorization still applies.
- Ignore Claude-specific background/Monitor instructions for the outer Codex session. Start shell processes with Codex's execution tool and await completion using its returned session ID. If the tool yields, resume/poll that session. Do not end the turn with a required run still active. Do not use `run_in_background` or a fictional notification mechanism.
- A launcher skill's Claude dispatch (`dispatch.py prepare`, an `Agent` spawn, `dispatch.py record`) has no Codex counterpart: use its Codex line, the `SDLC_BACKEND=codex` runner call and the native exchange under "Native execution" below. `dispatch.py` and the `sdlc-lite:<role>-L<n>` sub-agent definitions are the Claude backend only.
- Native Claude agent frontmatter, output styles, and statusline installation are not Codex features. Do not invoke root agent files as Codex subagents.

## Lane per ticket

Before work on a ticket, run `python3 "<plugin-root>/scripts/steps.py" lane <ticket dir>` and follow its first line: `solo` means run the `solo` session agent at the solo level for the ticket level (L1, L2, L3; the Codex agents are `sdlc-solo-l1`, `sdlc-solo-l2`, `sdlc-solo-l3`), `lean` the lean chain in the chain workflow, and `full` the chain workflow. Run it again after the planner result and after every append to the ticket handoff's `## Plan review` section; a lean ticket that meets a mandatory condition prints `full` from then on. Each run appends its result to `<ticket dir>/skips.md`, and its `reason:` lines name the facts that decided it.

## Native execution

On Claude Code every role is a sub-agent, dispatched as `agents/conductor.md` ("How you run roles") says; this section is the Codex path.

Read shared run operations at `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/run-operations.md` for readiness, routing rationale, and safe recovery. Pass `--routing-reason` to `dispatch.py prepare` (Codex: set `SDLC_ROUTING_REASON`) when launching a role; do not invent a task-specific rationale when none was supplied.

Run from the target project root. For runner calls inside Codex, use `SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent` and follow the exchange below. Standalone terminal launchers use `SDLC_BACKEND=codex`; do not rely on an exported variable surviving between shell tool calls. Example inside Codex: `SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent "<plugin-root>/scripts/run.sh" builder L2 .sdlc/example/step-1/handoff.md`.

Verify `codex`, `python3`, `jq`, and `git` are available. The exec transport runs Codex directly; the in-session transport uses predefined native subagents. Neither falls back to Claude. Use the scope rules in level-rubric; the Codex model/effort mapping lives in `adapters/codex/models.json`. The runner chooses a different model from the latest builder when necessary for verification.

Run `python3 "<plugin-root>/scripts/codex_roles.py" install "<project-root>"` when the user wants predefined in-session agents. This writes managed `.codex/agents/sdlc-*.toml` files, an ownership receipt, and a narrow generated-file `.gitignore`; it refuses to overwrite user edits. Use `install --check` to detect stale definitions after a plugin update. Start a fresh Codex session to load them. The plugin's marketplace installation alone does not register these project agents.

When the user also wants SDLC Lite to guide the main Codex session by default in that project, use `install "<project-root>" --conductor`. This opt-in adds a short managed block to project `.codex/config.toml` developer instructions, preserving existing instructions and other settings. `conductor-off "<project-root>"` removes only that block. Start a fresh Codex session after either change. This is project guidance for the main session, not a named-agent binding; the workflow remains in this skill and its linked files.

Names include `sdlc-scout-l1`, `sdlc-builder-l1` through `sdlc-builder-l5`, `sdlc-planner-l1` through `sdlc-planner-l3`, `sdlc-plan-reviewer-l1`, and corresponding verifier/researcher levels. Each definition sets its instructions, model, reasoning effort, and sandbox. Use native named agents for delegated tasks; a direct subagent's return does not automatically update pipeline state. Use run.sh for pipeline steps so results, base tracking, and independent-model verification are recorded and checked.

Before claiming a ticket or starting a lane, check that its exact role is callable in this session, not only installed: read the agent list the host exposes and run `python3 "<plugin-root>/scripts/codex_roles.py" preflight "<project-root>" <exact role names> --catalog "<names callable now>"`. A not-ready result names the missing role and whether generation, a fresh session, or a launcher repair is required; do not claim, substitute another role, fall back to Claude, or start a nested Codex CLI. The readiness text and the resume packet for a new session are in "Readiness and resume for conductors" in the shared Codex execution instructions below. `install --check` stays the separate test of the generated files.

Before an in-session pipeline call, read the shared Codex execution instructions at `${CLAUDE_PLUGIN_ROOT}/adapters/codex/instructions.md`, especially “Native pipeline exchange for conductors”. Start the runner with a short yield, read its request JSON, spawn the exact named agent with fresh context, wait for its report, submit that report with codex_exchange.py, then await the original runner. This adapter overrides workflow text that assumes a runner call can simply block until completion. Never launch a nested Codex CLI from a sandboxed shell. If setup or native tools are unavailable, report the blocker rather than changing permissions.

The Codex backend preloads the shared role instructions and required skill bodies. It waits for completion and writes the existing result artifacts. Raw Codex events are retained in the log; runs.jsonl records backend and token usage. Dollar cost is unknown rather than estimated.

Claude hooks are not Codex enforcement. Codex roles use read-only or workspace-write sandboxing and cannot request new approvals unattended. Sandbox-blocked checks must be reported; never weaken permissions or claim a pass. Shared publish, scope, and process-ownership constraints remain instructions, with no claim of equivalent hook coverage. Architect uses workspace-write for its assessment artifacts, while its role contract prohibits implementation edits.

On success read the actual result artifact and report its outcome. On nonzero exit report the error and log path. Do not fabricate a passed result or perform a role's work yourself to conceal a failed launch.


## Native fanout and benchmark drivers

Inside Codex, also set `SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent` when starting fanout.py or bench.sh, and keep the shell session active. Each driver publishes `.sdlc/native-conductor-*.request.json` in its working directory (for fanout, inside each lane worktree). Discover waiting requests there, spawn the exact named conductor with its request prompt, and submit its actual report through codex_exchange.py. The request specifies the project working directory; preserve it when dispatching. The conductor services its own role requests using the exchange above. Await driver completion and then the original fanout/bench process. Respect host concurrency/depth limits and report insufficient delegation capacity; do not silently switch to a nested CLI. Terminal automation can use the default exec transport.
