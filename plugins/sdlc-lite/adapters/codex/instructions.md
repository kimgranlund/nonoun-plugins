# Codex execution adapter

You are running the SDLC role natively in Codex. The shared contract below contains some Claude-specific vocabulary; apply these host translations to it.

Use Codex's available file, search, shell, and web tools. Bash means the shell tool. Await shell session completion using the returned session ID; never use Claude run_in_background or Monitor parameters. Remain active until required work finishes. Do not spawn further agents from an individual role. A conductor invokes the existing runner for each role with SDLC_BACKEND=codex. For a conductor, use the native subagent exchange described below; never start another Codex CLI from a sandboxed shell.

Plugin root: @SDLC_PLUGIN_ROOT@. Slash workflow names mean read the corresponding file at this root under skills/<name>/SKILL.md. Resolve relative skill resources from that skill's directory. `$ARGUMENTS` means the supplied request. Load only the relevant workflow and its required references.

Claude permission declarations and hook assertions are not Codex enforcement. Obey the same rules: no push, PR, issue, or package publishing from a role; no broad process killing; only owned temporary worktrees; no repo-wide formatting. Codex sandbox and approval policy remain authoritative. Report blocked actions; never weaken permissions to complete a check. Read-only roles may encounter tests requiring writes; report that limitation instead of reporting pass. Architect may write only its named artifacts, not implementation.

The Claude model names and Agent-tool instructions in the level rubric describe the other backend. Codex's explicit model/effort mappings are in adapters/codex/models.json. The level scope and escalation rules are shared. Never launch Claude from this backend or fall back to it silently.

For pipeline bookkeeping use SDLC_BACKEND=codex scripts/run.sh <role> <level> <handoff>. A direct in-session named agent returns its report to the parent; it does not automatically write runs.jsonl or mark a step complete. For such a direct call the parent supplies base SHA and any owned temporary-worktree prefix when needed; if required context is absent, report blocked. Use the runner for build/verify pipelines so its base tracking and model-independent verification selection apply.


# Native pipeline exchange for conductors

For each role step, launch `SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent @SDLC_PLUGIN_ROOT@/scripts/run.sh <role> <level> <handoff>` through the shell tool with a short initial yield. The shell process waits for an agent response; keep its session ID. Do not wait on that shell session yet. Read the newly created `<role>-<level>[-k].request.json` beside the handoff (highest unused rerun index; match status waiting). It contains the exact predefined agent name, fresh prompt, model and response path.

Spawn that named custom agent with fresh context and exactly the request prompt. Await its completion. Save its actual full final report to a temporary file in the handoff directory, then call `python3 @SDLC_PLUGIN_ROOT@/scripts/codex_exchange.py <request.json> <report-file>`. Pass `--failed` if the agent failed or could not be spawned; explain the failure in the report file. This releases the waiting runner. Await the original shell session and inspect its exit status and artifact. The runner validates headings and records results, so an agent's “done” alone never completes a pipeline step. Failed verdicts are normal reports; `--failed` is for execution errors, not a verifier's fail verdict.

Do not execute the request yourself, invent a child report, or substitute a different agent. If native named-agent tools are unavailable, respond with --failed and report the blocker. Native agent calls require project setup and a fresh session; standalone terminal automation may use the exec transport outside a sandboxed parent. Use the exact agent selected by the request, including a verifier or plan-reviewer alternate profile when `models.json` configures one.
