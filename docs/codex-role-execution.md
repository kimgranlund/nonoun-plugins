# Native Codex role execution

SDLC Lite supports native Codex pipeline roles and predefined project subagents. Both are generated from the existing role contracts, so responsibilities and output formats have one source.

## Use

```sh
# Register project agents; start a fresh Codex session afterwards.
python3 /path/to/sdlc-lite/scripts/codex_roles.py install /path/to/project

# From the target project, run a pipeline step and retain its artifacts.
SDLC_BACKEND=codex /path/to/sdlc-lite/scripts/run.sh builder L2 .sdlc/example/step-1/handoff.md
SDLC_BACKEND=codex /path/to/sdlc-lite/scripts/run.sh verifier L1 .sdlc/example/step-1/handoff.md

# The same selection applies to conductor-driven workflows.
SDLC_BACKEND=codex python3 /path/to/sdlc-lite/scripts/fanout.py run lane=T-0001 --gate 'npm test' --dry-run
SDLC_BACKEND=codex /path/to/sdlc-lite/scripts/bench.sh example
```

There are 22 project agent definitions, including three alternate verifier models. The project agents include `sdlc-builder-l1` through `sdlc-builder-l5`, three levels each of planner/verifier/researcher, and one each of scout/architect/archaeologist/filer/conductor. Ask Codex to delegate to one by name and give it a self-contained handoff. Direct delegation returns a report; the pipeline runner additionally validates and records that report. Use the runner for build/verify steps and the board.

## Default model mapping

| Role | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Builder | Sol low | Sol medium | Sol high | Astra high | Astra xhigh |
| Planner | Sol medium | Sol high | Astra high | | |
| Verifier | Sol medium | Sol high | Astra high | | |
| Researcher | Sol medium | Sol high | Astra high | | |
| Scout | Luna high | | | | |
| Architect | Astra high | | | | |
| Archaeologist, filer, conductor | Sol medium | | | | |

These are initial configurable Codex defaults, not claimed equivalents of Claude models. `adapters/codex/models.json` owns the mapping. Regenerate the agent files after changes. A pipeline verifier configured to use the latest builder's model switches between Sol and Astra to preserve independent-model verification; the selected model is recorded in the result and run log.

## Boundaries

No Claude dependency or fallback exists on the Codex path. Default commands without `SDLC_BACKEND` retain legacy Claude behavior. Authentication and host policies remain the user's Codex configuration; unattended runs cannot request new approval. Read-only roles may report sandbox-blocked checks. Shared role restrictions are not equivalent to Claude hook enforcement.

There are two transports over the same runner. Standalone terminal automation uses `codex exec` with the selected predefined agent configuration. Inside Codex, `SDLC_CODEX_TRANSPORT=subagent` writes a request next to the handoff and waits. The parent reads the request, invokes that named native agent with fresh context, saves the actual report, and submits it through `scripts/codex_exchange.py`. It then awaits the original runner, which validates and records the output. The native SDLC skill describes this sequence; a direct unrecorded subagent response does not advance pipeline state.

Headless conductors prepare the managed project agents before entering their sandbox and use native subagent exchange for role steps. This avoids needing sandbox write access to Codex's private runtime state. Generated agent files have a narrow project-local ignore file, preventing runtime setup from becoming unrelated implementation changes. User-edited managed files, symlinks, or an unrelated existing ignore file cause refusal rather than overwrite.

Native agent format and inheritance: [official Codex subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

## Validation

Offline tests cover artifact creation, rerun ordering, required-section failures, failed/missing/timed-out executions, read-only sandbox flags, no bypass flags, backend propagation, model-independent verification, setup idempotence, refusal to overwrite user edits, generated-source parity, and native fanout routing. A stub Claude executable fails if accidentally called. Live checks on Codex CLI 0.155.0 passed in a throwaway Git project:

- Standalone native scout located `seed.txt:1` and produced its normal result and run record.
- Sol-low builder changed the greeting fixture; Astra-medium verifier returned pass and demonstrated that the acceptance assertion failed against the original code. Model selection, base tracking, result files and usage records were inspected.
- A fresh native session spawned the installed scout and returned a unique marker present only in its agent instructions. This caught and fixed a TOML Unicode serialization defect; the repeated test had no malformed-agent errors.
- A native headless conductor completed the request → predefined scout → response → runner-validation cycle inside its workspace sandbox. The report and run record identified `transport: subagent`.

An earlier attempt to nest a Codex CLI inside the conductor sandbox failed on runtime-state writes; the native exchange replaced that approach. No permission widening was used to make that test pass. Full multi-lane live benchmarks and every role/level combination have not been exercised; script regression tests cover their orchestration mechanics.

The conductor does not receive extra network or Codex-home write permissions. Benchmark launchers return nonzero when a conductor process fails.


For fanout or benchmark launchers inside Codex, select the subagent transport too. Their waiting native conductor requests appear in `.sdlc/native-conductor-*.request.json` under each driver's project directory. The parent dispatches them and submits actual reports using the same exchange. This requires sufficient native delegation depth and concurrency; capacity or permission failures must be reported. Standalone terminal launchers use exec for the conductor and native exchange for its children.


The live native builder/verifier sequence also passed using `sdlc-builder-l1` and `sdlc-verifier-l1-alternate`. The initial native verifier reported a sandbox-blocked worktree probe. The fixture then specified an in-memory baseline probe under the same acceptance assertion; a fresh verification passed without permission changes. Both outcomes were retained. [Smoke-test evidence and source hashes](validation/native-codex-smoke.json) bind these observations to the exercised implementation.

The final `scripts/check.sh` run passed, including all 13 Codex backend tests, shared workflow and runner regressions, hook fixtures, shellcheck, and Claude plugin validation.

## Readiness and recovery

The shared runner now checks local readiness, reserves a durable attempt record, and locks the handoff directory for both host backends. See [shared run operations](../plugins/sdlc-lite/skills/handoff-format/run-operations.md) for routing rationale, configuration checks, and interrupted-attempt recovery. Native subagents remain host-managed: stop or await a dispatched agent before retrying after its shell waiter is cancelled.
