# Host compatibility

Both manifests identify the same plugin. Skills share workflow decisions and route Codex through its execution adapter before interpreting Claude-specific syntax.

| Surface | Codex | Claude Code |
|---|---|---|
| Tickets, board, ordering, decomposition | Shared local Python scripts | Same scripts |
| Pipeline roles | `SDLC_BACKEND=codex scripts/run.sh ...` → native `codex exec` | Default runner → `claude -p` |
| Role definitions | Generated TOML agents; same contracts and preloaded skills | Shared Markdown role contracts |
| In-session agents | Project `.codex/agents/sdlc-*.toml` after setup | Claude plugin agents |
| Fanout and benchmarks | Native Codex conductor with `SDLC_BACKEND=codex` | Claude conductor by default |
| Results | Same result files, validation, base SHA, ordering and running marker | Same |
| Cost | Token usage recorded; dollar cost unknown | Reported dollar cost |
| Permissions | Read-only or workspace-write; unattended approval policy `never` | Existing CLI permissions and Claude hooks |
| Hooks, statusline, output style | No equivalent hook/style enforcement claimed | Claude-specific |

## Project setup

From the installed plugin, run `python3 scripts/codex_roles.py install /path/to/project`. This installs 19 namespaced base agents (18 role levels and conductor) plus one alternate verifier profile for each verifier level whose model has an entry in `verifier_alternates`, 22 with the default configuration, and an ownership receipt and a narrow generated-file `.gitignore` into that project's `.codex/agents/`. It changes no global settings and preserves unrelated agents. Existing user edits cause refusal before writes. Start a fresh Codex session afterwards. Repeat setup after upgrading; `install /path/to/project --check` detects stale definitions. Installed instructions contain the plugin's resolved path, so moving the plugin requires setup again.

The files under `adapters/codex/agents/` are generated from shared role Markdown, declared skill bodies, the Codex execution prelude, and `adapters/codex/models.json`. Run `codex_roles.py generate` after those sources change. The runner and installer consume these same definitions. Generated TOML uses a deliberately restricted string-only format so Python 3.9 needs no additional TOML package; edit shared sources rather than generated files.

## Runtime

Requirements: Python 3.9+, bash, Git, and jq; authenticated Codex CLI for standalone exec runs, or native custom-agent tools for in-session runs. Claude is not required for Codex execution. Explicitly prefix commands with `SDLC_BACKEND=codex`, including fanout and bench launchers; invalid backend names fail rather than silently falling back. The legacy default remains Claude for existing callers.

Standalone pipeline roles use a fresh Codex process without conversation history. Inside Codex, use `SDLC_CODEX_TRANSPORT=subagent`: the runner writes a request, the parent spawns the named agent with fresh context and submits its report, then the runner validates and records it. This avoids launching a second Codex CLI inside the host sandbox. Headless conductors install the managed agents before entering the sandbox and use this exchange for their roles. The runner preserves result numbering, required-section validation, base tracking, and cleanup. The latest builder model is compared with the verifier model; matching Codex models switch to the alternate that `verifier_alternates` in `adapters/codex/models.json` maps the builder's model to, at the verifier's effort. With no alternate configured, the verifier keeps the builder's model and the runner records `shared_with_builder` in the result header and `runs.jsonl`. Native direct subagent calls return reports to their parent and do not automatically update pipeline artifacts; use the runner for pipeline steps.

The Codex transport records raw events plus one normalized final result. Missing output, process failure, timeout, and turn failure cannot become a passed result. `SDLC_CODEX_TIMEOUT_SECONDS` sets a positive per-session timeout, default 3600. Cancellation targets only the child process group created for that run. Runs record `backend` and token usage; Codex dollar cost stays null and mixed benchmark totals show `unknown`.

Codex's sandbox is not a port of Claude's command hooks. Publishing restrictions, formatting scope, and process ownership are role instructions. Read-only roles may be unable to run tests requiring writes; they must report the limitation. Architect receives workspace-write for its decomposition artifacts, while its instructions prohibit implementation changes. No automatic permission escalation is used. Direct in-session agents also inherit live parent permission overrides as documented by Codex.

See [native execution and validation](../../docs/codex-role-execution.md).

No extra network or Codex-home write access is added to the conductor sandbox. Benchmark launchers return nonzero when a conductor process fails. Native exchange failures and malformed reports are tested separately from model verdicts.
