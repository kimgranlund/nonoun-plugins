# Native Codex role execution

SDLC Lite supports native Codex pipeline roles and predefined project subagents. Both are generated from the existing role contracts, so responsibilities and output formats have one source.

## Use

```sh
# Register project agents; start a fresh Codex session afterwards.
python3 /path/to/sdlc-lite/scripts/codex_roles.py install /path/to/project

# Opt in to SDLC Lite conductor guidance for the main session in this project.
python3 /path/to/sdlc-lite/scripts/codex_roles.py install /path/to/project --conductor
# Later, remove only that guidance while keeping the project agents.
python3 /path/to/sdlc-lite/scripts/codex_roles.py conductor-off /path/to/project

# From the target project, run a pipeline step and retain its artifacts.
SDLC_BACKEND=codex /path/to/sdlc-lite/scripts/run.sh builder L2 .sdlc/example/step-1/handoff.md
SDLC_BACKEND=codex /path/to/sdlc-lite/scripts/run.sh verifier L1 .sdlc/example/step-1/handoff.md

# The same selection applies to conductor-driven workflows.
SDLC_BACKEND=codex python3 /path/to/sdlc-lite/scripts/fanout.py run lane=T-0001 --gate 'npm test' --dry-run
SDLC_BACKEND=codex /path/to/sdlc-lite/scripts/bench.sh example
```

There are 25 project agent definitions: 21 base definitions and four alternate definitions (three verifier levels and the plan reviewer). The project agents include `sdlc-builder-l1` through `sdlc-builder-l5`, three levels each of planner/verifier/researcher, `sdlc-plan-reviewer-l1`, and one each of scout/architect/archaeologist/filer/conductor/messenger. Ask Codex to delegate to one by name and give it a self-contained handoff. Direct delegation returns a report; the pipeline runner additionally validates and records that report. Use the runner for build/verify steps and the board.

`sdlc-messenger-l1` is a native subagent that polls `messages/new/codex` every 10 seconds through `messages.py`. On Codex it has its own lifetime and no Claude tools or hooks, and no Claude hook enforces anything on Codex. The Claude messenger lives only while its session runs, and its polling needs Monitor or a loop. One host working says nothing about the other. A subagent, including the messenger, can report only into a parent turn that is still running. It cannot wake an idle host on Claude Code or Codex. Keep the parent in an active turn: on Codex run `/goal` or have the parent wait on the messenger and spawn it again; on Claude Code keep the foreground session working. The live runs covered only an active parent.

The `--conductor` option adds a short managed block to the project's top-level `developer_instructions` in `.codex/config.toml`. It tells the main session to load the installed `sdlc-lite` skill and coordinate delivery through the configured workflows and roles. Existing developer instructions, settings, and comments are preserved; repeated setup is idempotent, and `conductor-off` removes only the managed block. Ordinary `install` never opts an existing project in. Run `install ... --conductor --check` to check both agent definitions and conductor guidance. Codex loads project config only for trusted projects, and a new session is needed to pick up changes. This is developer guidance for the main session, not a native named-main-agent binding. See the [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Default model mapping

| Role | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Builder | Luna low | Sol 6.1 low | Sol 6.1 medium | Sol 6.1 high | Sol 6.1 xhigh |
| Planner | Sol 6.1 medium | Sol 6.1 high | Astra high | | |
| Verifier | Luna low | Luna medium | Astra high | | |
| Plan reviewer | Astra high | | | | |
| Researcher | Luna medium | Sol 6.1 medium | Sol 6.1 high | | |
| Scout | Terra 5.6 low | | | | |
| Architect | Astra high | | | | |
| Archaeologist, filer | Luna medium | | | | |
| Conductor | Astra medium | | | | |
| Messenger | Terra 5.6 low | | | | |

These are initial configurable Codex defaults, not claimed equivalents of Claude models. `adapters/codex/models.json` owns the mapping. Regenerate the agent files after changes. A change also needs a new eval in `.sdlc/evals/` and `evals.py lock`, or `check.py` fails; see [the evals entry file](../../.sdlc/evals/AGENTS.md). When a pipeline verifier's model matches the latest builder's model, the Codex verifier switches to the model that `verifier_alternates` in `adapters/codex/models.json` maps the builder's model to. The latest builder result is the newest in the verifier's handoff dir; a verifier launched at the task dir, whose dir holds none, reads the newest builder result of the highest-numbered `step-<n>/` under it that holds one, leaving out `step-<n>.superseded-<k>/` dirs, the same rule run.sh applies on Claude Code. With no alternate configured, the verifier keeps the builder's model and the runner records `shared_with_builder` in the result header and `runs.jsonl`. The selected model is recorded in the result and run log. The current alternates map `gpt-6-luna` and `gpt-6-astra` to `gpt-6.1-sol`, so a verifier that would share its builder's model runs on `gpt-6.1-sol` at the verifier's configured effort. With the default allocation the only builder and verifier pair that shares a model is builder L1 and verifier L1, both Luna; other role defaults stay as listed above. The same map pairs the plan reviewer with the newest planner result's recorded model: Astra high reviews Sol plans, and `gpt-6.1-sol` high reviews Astra plans. The `shared_with_builder` field keeps its name; for the plan reviewer it means the reviewer shares the planner's model.

Note (2026-09-29, Codex CLI 0.154.0): a ChatGPT account rejected `gpt-6-sol` and `gpt-6-luna`, and `gpt-6-astra` was accepted, so the defaults moved from Sol to Astra. On 2026-09-30 the scout was briefly moved to `gpt-6-astra` on the strength of those 0.154.0 probes. API-key accounts were not tested. After updating the CLI to 0.159.2 on 2026-09-30, account discovery listed `gpt-6.1-sol`, `gpt-6-sol`, and `gpt-6-luna`, and all completed live turns. `gpt-6.1-sol` is now the configured verifier alternate, preserving the existing Astra role defaults. The user then returned scout L1 to `gpt-6-luna` at effort `high`, because luna completes live turns on CLI 0.159.2. On 2026-09-30 the user mirrored the Claude tiers: Opus maps to `gpt-6.1-sol`, Fable to `gpt-6-astra`, Sonnet to `gpt-6-luna`, Haiku to `gpt-5.6-terra`, with the Claude effort, and verifier alternates mirror the Claude family rule. See the [dated account and role validation report](../reports/codex-account-models-2026-09-30.md) for exact IDs, limits, and attempt evidence. Later on 2026-09-30 the user adopted a role-based allocation for planner, builder, and verifier, proposed by the Codex session, replacing the Claude-tier mirror for those roles. It is a proposed setting, not a demonstrated performance equivalent.

## Boundaries

No Claude dependency or fallback exists on the Codex path. Default commands without `SDLC_BACKEND` retain legacy Claude behavior. Authentication and host policies remain the user's Codex configuration; unattended runs cannot request new approval. Read-only roles may report sandbox-blocked checks. Shared role restrictions are not equivalent to Claude hook enforcement.

There are two transports over the same runner. Standalone terminal automation uses `codex exec` with the selected predefined agent configuration. Inside Codex, `SDLC_CODEX_TRANSPORT=subagent` writes a request next to the handoff and waits. The parent reads the request, invokes that named native agent with fresh context, saves the actual report, and submits it through `scripts/codex_exchange.py`. It then awaits the original runner, which validates and records the output. The native SDLC Lite skill describes this sequence; a direct unrecorded subagent response does not advance pipeline state.

Headless conductors prepare the managed project agents before entering their sandbox and use native subagent exchange for role steps. This avoids needing sandbox write access to Codex's private runtime state. Generated agent files have a narrow project-local ignore file, preventing runtime setup from becoming unrelated implementation changes. User-edited managed files, symlinks, or an unrelated existing ignore file cause refusal rather than overwrite.

Project-conductor setup preflights the TOML and managed agents before writing. Malformed config, a non-string `developer_instructions`, or an edited managed block causes refusal. The opt-in TOML editor is a pinned, vendored `tomlkit` 0.13.3 under `scripts/_vendor` so it can preserve arbitrary valid TOML without requiring a package install; ordinary agent setup does not import it. A filesystem write failure may leave refreshed agents with conductor guidance unapplied; rerun the same command after resolving the error.

Native agent format and inheritance: [official Codex subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

## Validation

Offline tests cover artifact creation, rerun ordering, required-section failures, failed/missing/timed-out executions, read-only sandbox flags, no bypass flags, backend propagation, model-independent verification, setup idempotence, refusal to overwrite user edits, generated-source parity, and native fanout routing. A stub Claude executable fails if accidentally called. Live checks on Codex CLI 0.155.0 passed in a throwaway Git project:

- Standalone native scout located `seed.txt:1` and produced its normal result and run record.
- Sol-low builder changed the greeting fixture; Astra-medium verifier returned pass and demonstrated that the acceptance assertion failed against the original code. Model selection, base tracking, result files and usage records were inspected.
- A fresh native session spawned the installed scout and returned a unique marker present only in its agent instructions. This caught and fixed a TOML Unicode serialization defect; the repeated test had no malformed-agent errors.
- A native headless conductor completed the request → predefined scout → response → runner-validation cycle inside its workspace sandbox. The report and run record identified `transport: subagent`.

Project-conductor setup also has focused tests for existing and empty developer instructions, other TOML settings and comments, repeated setup, targeted removal, malformed config, and edited managed text. In an isolated trusted throwaway project, `codex debug prompt-input` showed both the original developer instructions and the managed conductor guidance. After removal, the original instructions remained and the conductor guidance disappeared. This prompt inspection made no model call.

An earlier attempt to nest a Codex CLI inside the conductor sandbox failed on runtime-state writes; the native exchange replaced that approach. No permission widening was used to make that test pass. Full multi-lane live benchmarks and every role/level combination have not been exercised; script regression tests cover their orchestration mechanics.

The conductor does not receive extra network or Codex-home write permissions. Benchmark launchers return nonzero when a conductor process fails.


For fanout or benchmark launchers inside Codex, select the subagent transport too. Their waiting native conductor requests appear in `.sdlc/native-conductor-*.request.json` under each driver's project directory. The parent dispatches them and submits actual reports using the same exchange. This requires sufficient native delegation depth and concurrency; capacity or permission failures must be reported. Standalone terminal launchers use exec for the conductor and native exchange for its children.


The live native builder/verifier sequence also passed using `sdlc-builder-l1` and `sdlc-verifier-l1-alternate`. The initial native verifier reported a sandbox-blocked worktree probe. The fixture then specified an in-memory baseline probe under the same acceptance assertion; a fresh verification passed without permission changes. Both outcomes were retained. [Smoke-test evidence and source hashes](../reports/native-codex-smoke.json) bind these observations to the exercised implementation. Alternate profiles are generated only when `verifier_alternates` in `models.json` configures one. This smoke test predates the alternate mapping described above.

The final `scripts/check.sh` run passed, including all 13 Codex backend tests, shared workflow and runner regressions, hook fixtures, shellcheck, and Claude plugin validation.

## Readiness and recovery

The shared runner now checks local readiness, reserves a durable attempt record, and locks the handoff directory for both host backends. See [shared run operations](../../plugins/sdlc-lite/skills/handoff-format/run-operations.md) for routing rationale, configuration checks, and interrupted-attempt recovery. Native subagents remain host-managed: stop or await a dispatched agent before retrying after its shell waiter is cancelled.
