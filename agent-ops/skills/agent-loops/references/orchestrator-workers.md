# Orchestrator-Workers / Supervisor

A central agent (orchestrator / supervisor / manager) decomposes a goal at runtime and routes subtasks to specialized worker agents — either by **transferring control** (handoff) or by **calling them as tools** (delegation) — coordinating via shared state or message-passing. The framework supplies the routing, the state channel, and sometimes durable/resumable execution; the builder supplies the dispatch mode, the per-worker contract, and the gate.

**Where it sits in the taxonomy.** This is the **multi-agent control-plane / delegation topology** — the runtime-decomposition cousin of the _fixed_ decomposition patterns in `anthropic-workflow-patterns.md`. The router (`router.md`) reaches here only when decomposition is **unpredictable, decided at runtime**, and the subtasks call for **heterogeneous specialists** — otherwise prefer the cheaper fixed workflow. Two siblings differentiate by deliverable: `auto-research.md` is this topology specialized to breadth-first research with a cited report as output; `debate-ensemble.md` is the _non-hierarchical_ variant where peers vote rather than a supervisor routing. Per `composition.md`, orchestrator-workers is the canonical **wrapper** layer: most fan-out research is `orchestrator + cite/verify`, and an evaluator-optimizer frequently nests _inside_ a worker. Do not re-derive termination/context/verification here — those live in `control-plane.md`; this file parameterizes the topology and points back.

Aliases you will see in the wild: supervisor pattern, manager-worker / manager-agent, lead-agent + subagents, hierarchical agent teams, coordinator-dispatcher, routines-and-handoffs (Swarm), group-chat-manager (AutoGen).

> **The central tension this topology lives inside.** Anthropic's multi-agent research system (Opus lead + Sonnet workers) _outperformed single-agent Opus 4 by 90.2%_ — and burned **~15× the tokens of a chat**. Cognition's _Don't Build Multi-Agents_ argues the opposite: naive sub-agents "have no context of each other's work," so their implicit decisions conflict, and you should prefer a **single-threaded linear agent + a context-compression model**. Both are right, about different tasks. This skill does not pick a side; it forces the builder to choose **dispatch mode** and **context strategy** consciously, and to justify the choice against the read-vs-write nature of the work. The router exists so this isn't a coin-flip.

## Mechanism

Control flow has **two layers**: the orchestration topology, and the per-agent ReAct loop each node runs internally (`react-reflexion.md`). The topology is the supervisor loop:

1. **Plan / decompose.** The orchestrator receives the goal and produces a plan or decomposition. (Persist it — see Context Strategy; Anthropic writes the plan to memory _before_ spawning, because context truncates at ~200k tokens.)
2. **Select + dispatch the next worker.** Dispatch happens in **one of two distinct modes the builder MUST choose between**:
   - **(a) HANDOFF / control-transfer** — the worker _becomes_ the active agent and the loop continues from inside it. The receiver, by default, sees the **full prior conversation**. One agent is active at a time; this is the linear, close-to-Cognition model.
   - **(b) DELEGATION / agent-as-tool** — the orchestrator _calls_ the worker like a function; the worker runs to completion in its **own isolated context window** and **returns only its result**; control returns to the orchestrator. This is what enables parallel fan-out — and what creates the context isolation Cognition warns breaks on shared writes.
3. **Worker runs its inner loop** (its own tool-calling ReAct loop) until it emits a terminal answer — or itself hands off.
4. **Results flow back; the orchestrator decides:** dispatch more workers (serial or **parallel fan-out**), synthesize a final answer, or terminate.
5. **Optional final stage** post-processes — e.g. a citation/QA agent, a validator, a synthesis pass.

**Framework mappings** (so PLAN mode can speak the substrate's vocabulary):

| Framework | Topology primitive | Handoff mechanism | Routing | Notable knobs |
| --- | --- | --- | --- | --- |
| **LangGraph** (graph/state-machine) | agents are **nodes** in a `StateGraph` over shared, checkpointed state; a supervisor node decides routing | a handoff tool returns `Command(goto=<agent>, update=<state delta>, graph=Command.PARENT)` — routing is **data**, not a hardcoded edge | LLM supervisor (`create_supervisor`) or explicit graph edges | `output_mode ∈ {full_history, last_message}`; `create_forward_message_tool` (worker's last msg bypasses the supervisor — saves tokens, avoids paraphrase drift); checkpointers (Memory/Sqlite/Postgres/DynamoDB) → resume / time-travel / `interrupt()` HITL |
| **CrewAI** (roles/goals/tasks/crews) | `Process.sequential` (fixed task order, each output injected as next task's context) vs `Process.hierarchical` (a manager assigns dynamically) | delegation realized as built-in tools on delegating agents | manager LLM (`manager_llm=`) or custom `manager_agent` with `allow_delegation=True` | **footgun:** manager must **not** be in the `agents` list; manager **validates outputs** before proceeding |
| **AutoGen** (conversational) | `GroupChatManager` runs a group chat | speaker becomes active | `speaker_selection_method ∈ {auto, manual, random, round_robin}`; `auto` re-queries up to `max_retries_for_selecting_speaker` if the LLM names 0 or >1 agents | a custom selection function encodes a deterministic StateFlow (now merged into Microsoft Agent Framework) |
| **OpenAI Agents SDK / Swarm** (routines + handoffs) | a "routine" = system prompt + tool list | a handoff is a tool `transfer_to_<agent>`; the handoff fn **returns an `Agent` object**, the runner swaps active instructions+tools and (by default) passes the **entire** prior conversation | LLM picks the `transfer_to_*` tool | `handoff()`: `input_type` (structured args the model fills), `on_handoff` (callback), `input_filter` (rewrites how much history the receiver sees). Contrast: `Agent.as_tool(...)` = structured input to a nested specialist **without** transferring the conversation (the delegation pole). Guardrails run input/output checks in parallel, fail fast |

The Swarm formulation is the irreducible mechanism beneath the heavier frameworks: _completion → execute tool calls → append → repeat until none_, with handoff implemented as "a function that returns an Agent."

## When it fits / When it fails

| Fits (fan out) | Fails (stay single-threaded) |
| --- | --- |
| Goal genuinely decomposes into **independent, parallelizable** subtasks with few cross-dependencies (breadth-first research, "fan out then synthesize" — cut research time up to 90%) | Tasks where **all agents must share the same evolving context** or have many interdependencies (Cognition's central claim; Anthropic echoes the caveat) |
| **Read-heavy / read-only** fan-out where workers gather or filter and write **nothing shared** (Cognition explicitly concedes this is the safe case — e.g. Claude Code subtask agents answering questions) | **Parallel writes** to shared artifacts/state — conflicting implicit decisions compound (the **Flappy Bird** failure: one worker builds a Mario background, another a mismatched bird, the coordinator can't reconcile) |
| Task information **exceeds a single context window**, so you _need_ separate context windows per worker to parallelize compression (Anthropic's core justification) | **Most coding tasks** — Anthropic itself: coding has "fewer truly parallelizable tasks than research"; agents aren't good at coordinating/delegating in real time |
| **Heterogeneous specialists** with disjoint tool/permission scopes (refund vs FAQ vs order-status agent) where routing-by-capability beats one mega-agent | **Over-decomposable** queries — orchestrators spawning 50 subagents for a trivial ask, or workers duplicating each other when subtask boundaries are vague |
| **Long-running / resumable** workflows needing durable execution, HITL checkpoints, or audited routing (LangGraph's persistence + `interrupt()` sweet spot) | **Cost/latency-sensitive or low-value** tasks — the 15× token blow-up and synchronous fan-out latency dominate |
| **High-value** tasks where the **~4× (single agent) to ~15× (multi-agent)** token premium is justified by outcome value | **Debuggability-critical** systems — emergent non-determinism: "small changes to the lead agent can unpredictably change how subagents behave"; minor failures become catastrophic on long stateful runs |

**The router's gate, in one line:** is the work **read-heavy and genuinely independent**? Fan out. **Shared-write or interdependent**? Single-threaded with context compression (`plan-execute.md` / a linear ReAct loop). When in doubt, the cheaper hypothesis is "this didn't need a fleet."

## Key parameters

The highest-value section: the knobs a builder sets in PLAN mode, each with a default and the rationale. Defaults assume a **mid-complexity, read-heavy fan-out on Claude Code subagents or LangGraph**; deviate with a reason.

| Knob | What it controls | Default | Rationale |
| --- | --- | --- | --- |
| **Dispatch mode** — handoff (control-transfer) vs delegation (agent-as-tool) | Who owns context and where decisions can conflict. **The single most consequential choice.** | **Delegation (agent-as-tool)** for read-only/independent fan-out; **Handoff** the moment workers share writable state or decisions interlock | Delegation gives isolated context windows → parallelism + bounded token growth, but is exactly the isolation Cognition warns breaks on writes. Handoff keeps one active agent on full history (the safe, linear model) but serializes the work. Match to the **read-vs-write** nature of the task and justify against the single-threaded counter-position |
| **Routing policy** — LLM-chosen vs deterministic function vs round-robin | Reliability, testability, and cost of the **control plane** | **Deterministic / explicit-graph** routing where the dispatch set is knowable; **LLM-supervisor** only when next-worker truly depends on runtime content | LLM routing (LangGraph supervisor, AutoGen `auto`, CrewAI manager) is flexible but non-deterministic and adds **~30–50% tokens** (CrewAI figure). A custom selection function / explicit edges trade flexibility for a deterministic, **testable StateFlow** — and routing you can unit-test |
| **Context-passing granularity** — full traces vs final-result-only vs filtered | Reliability vs token cost on the orchestrator↔worker channel | **Final result + lightweight artifact reference** back to the orchestrator; **full trace** only when a worker's reasoning must survive for the next worker | Cognition's Principle 1 ("share **full** agent traces, not just individual messages") argues full context prevents conflicts; LangGraph `output_mode`, OpenAI `input_filter`, and forward-message tools dial it down to save tokens — but **every reduction reintroduces the "game of telephone."** Anthropic's mitigation: write artifacts to a **filesystem** and pass lightweight references, not paraphrases |
| **Fan-out width / effort budget per query** | Cost and quality — token usage explains **~80%** of performance variance | **Scale to complexity:** simple → 1 agent / 3–10 tool calls; comparison → 2–4 agents / 10–15 calls; complex → 10+ agents. Embed these as **explicit rules** in the orchestrator prompt | Must scale or you get the **50-subagents-for-a-simple-query** failure (and duplicated work). The dominant cost+quality knob; making it a rule in the prompt is what prevents runaway fan-out |
| **Delegation prompt contract per worker** — objective, output format, tool/source guidance, **explicit task boundaries** | Whether fan-out is clean or collides | **Mandatory four-part brief** per worker: objective · output schema · tool/source guidance · what NOT to do (boundary) | "Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information." A crisp **bounded** subtask is what separates clean fan-out from the Flappy Bird collision. This is the orchestrator's core competency |
| **State backend & durability** — in-memory message-passing vs checkpointed shared state vs external artifact store | Resumability, HITL, telephone-resistance | **External artifact store (filesystem) for worker outputs** + **checkpointed state** for any long/unattended run; pure message-passing only for short ephemeral runs | LangGraph checkpointers (Memory/Sqlite/Postgres/DynamoDB) give resume-after-failure + time-travel + `interrupt()`; filesystem artifacts avoid lossy re-summarization; Swarm-style message-passing is lightweight but **ephemeral** (no resume) |
| **Model tiering** — strong orchestrator + cheaper workers | Cost/quality split across seats | **Strong model in the orchestrator seat; cheaper model for workers** | Anthropic's Opus-lead + Sonnet-workers beat single Opus by **90.2%**, and they found **upgrading the model beats doubling the token budget**. Which seat gets the strong model is a primary lever — put it where the routing/synthesis judgment lives |
| **Termination / progress guards** — max iterations, sufficiency check, guardrails | Whether the loop provably halts | **Layered stop** (see below): hard iteration + tool-call caps **plus** a sufficiency heuristic **plus** parallel guardrails | LLM orchestrators "continue when they already had sufficient results" or "scour the web endlessly for nonexistent sources." Without explicit caps + guardrails the loop does **not** reliably halt — the orchestrator's own "is this sufficient?" is the weakest link |

## Termination / context strategy / verification gate

These three are the cross-cutting control plane — fully specified in `control-plane.md`. Here is **only** how this topology instantiates them.

**Termination (instantiate `control-plane.md` §termination).** Layer the stop; never trust the orchestrator's self-judgment alone:

- **goal-gate** — orchestrator judges sufficiency _and proceeds to synthesis_ (the LLM sufficiency decision — the **weakest link**, so it must be backstopped) **or** the handoff model's natural end: no worker emits a further handoff and no pending subtasks remain (Swarm: loop ends when a completion contains no tool/handoff calls) **or** all tasks in a (sequential/hierarchical) list complete and the manager validates the output (CrewAI).
- **no-progress / routing-retry caps** — AutoGen's `max_retries_for_selecting_speaker` (speaker selection returning 0 or >1 agents); detect workers duplicating each other or chasing nonexistent sources.
- **hard caps** — max iterations / max tool calls / per-query **effort budget** exhausted.
- **guardrail / HITL exits** — a safety check trips and **fails fast** (OpenAI guardrails); a HITL `interrupt()` resolves an approve/edit and resumes-or-stops (LangGraph); a durable-execution failure **pauses at the last checkpoint** to resume rather than restart.

**Context strategy (instantiate `control-plane.md` §context).** This topology forces a conscious pick between two opposing philosophies:

- **Shared-state / full-context** (LangGraph default single channel; OpenAI handoff default; **Cognition's prescription**) — every agent operates on the same accumulating context / full traces. Maximizes coherence, minimizes conflicting implicit decisions; **bloats tokens** and risks context-window overflow.
- **Isolated message-passing / final-result-only** (delegation/agent-as-tool; LangGraph `output_mode=last_message` + forward-message; CrewAI task-to-task injection; Swarm stateless routines) — each worker gets a scoped brief and a **fresh context window**, returns a compact result. Enables parallelism and bounded token growth; **reintroduces context isolation.**

Three bridging mitigations (use them, don't choose blind): **(1)** persist the orchestrator's PLAN externally before spawning (Anthropic writes plan to memory — context truncates at ~200k); **(2)** write worker outputs to a **filesystem** and pass lightweight references to fight the game of telephone; **(3)** use a dedicated **context-compression model** to distill long single-threaded histories into key decisions (Cognition). Durability: LangGraph checkpoints the whole state graph at every super-step (`StateSnapshot`) for resume/replay/time-travel; Swarm is deliberately ephemeral; CrewAI threads context through the task list.

**Verification gate (instantiate `control-plane.md` §verification).** **No verification is implicit in the topology — it MUST be added.** The orchestrator's own "is this sufficient?" self-judgment is **not** a reliable gate and is itself a documented failure source. Add the highest-trust gate the task affords:

- a **dedicated verifier/validator stage** after fan-out — CrewAI's manager validates worker outputs; Anthropic adds a separate `CitationAgent` checking every claim maps to a source;
- **guardrails** as parallel fail-fast input/output checks (OpenAI Agents SDK);
- **HITL `interrupt()`** gates that pause for inspect/approve/edit (LangGraph);
- for **system-level** quality (not per-run): LLM-as-judge over a small (~20-query) eval set scoring a rubric 0.0–1.0 (factual accuracy, citation accuracy, completeness, source quality, tool efficiency), backstopped by human eval for failure classes automation misses.

Keep the gate **independent of the orchestrator** (a separate validator seat, an executable check, or a different-family judge) — see `rubric-orchestrator-workers` dim **OW7-verification**.

## Failure modes

Each with its guard. These map 1:1 to the dimensions of `rubric-orchestrator-workers`.

| Failure mode | Guard | Rubric dim |
| --- | --- | --- |
| **Context isolation across workers** → conflicting implicit decisions the coordinator can't reconcile (the canonical multi-agent failure; **Flappy Bird**) | Don't fan out onto interdependent work; choose **handoff/full-context** when decisions interlock; share full traces (Cognition P1) | OW1, OW2, OW3 |
| **Game of telephone** — information degrades through orchestrator→worker→orchestrator re-summarization | Pass artifacts **by reference** (filesystem), not by paraphrase; persist the plan externally | OW3 |
| **Over-decomposition / runaway fan-out** — 50 subagents for a simple query; duplicated work + gaps when boundaries are vague | **Effort rules scaled to complexity** in the orchestrator prompt; crisp bounded per-worker contracts | OW5, OW3 |
| **Non-termination** — orchestrator researches past sufficiency, or workers pursue nonexistent sources, with no hard stop | Layered termination (hard caps + guardrails), not sufficiency-self-judgment alone | OW6 |
| **Token/cost explosion** — ~4× (single) to ~15× (multi) over a plain chat | Cost-justify the premium against task value; **model tiering** (strong orchestrator + cheap workers); per-query effort budget | OW8, OW5 |
| **Emergent non-determinism** — small lead-agent prompt changes unpredictably alter worker behavior; runs differ on identical inputs | Prefer deterministic/explicit routing where possible; capture full traces + routing decisions for diff | OW4, OW8 |
| **Catastrophic statefulness** — a minor mid-run failure corrupts the whole trajectory; naive code-update redeploys break in-flight agents | Checkpoint + idempotent steps; **rainbow / blue-green** deploys for long runs | OW8 |
| **Synchronous fan-out bottleneck** — orchestrator blocks waiting for each worker set, capping throughput/latency | Async dispatch where the substrate allows; size fan-out to the latency budget | OW6, OW8 |
| **Routing pathologies** — LLM speaker-selection returns 0/multiple agents (AutoGen re-query loop); manager mis-assigns capability-mismatched tasks (CrewAI) | Retry cap on speaker selection; deterministic routing for known dispatch sets; capability-typed workers | OW4 |
| **Manager-misconfiguration footguns** — putting the manager in the `agents` list, or forgetting `manager_llm`/`manager_agent`, breaks CrewAI hierarchical at init | Substrate-specific lint: manager **outside** the worker pool; manager model/agent set | OW2 |

## Composition

How this topology nests and wraps others (see `composition.md` for the full layering rules):

- **As the outer wrapper.** Orchestrator-workers is the most common **top layer**. `auto-research.md` _is_ this topology specialized: `orchestrator + parallel research workers + a cite/verify stage`. The orchestrator is the spine; everything else is a worker or a final stage hanging off it.
- **A worker is itself a loop.** Each worker runs an inner ReAct loop (`react-reflexion.md`); a worker whose subtask is "produce a polished artifact" may nest a full **evaluator-optimizer** loop (`evaluator-optimizer.md`) inside itself. The topology composes recursively — _topology-of-loops_, not topology-of-prompts.
- **The verification stage is a droppable sub-step.** The post-fan-out validator/citation/guardrail stage can be a single pass, an **adversarial-verify** step (`debate-ensemble.md`), or a HITL gate — droppable on low-stakes runs, mandatory on high-stakes (`composition.md`).
- **Synthesis is single-threaded.** Fan out for the _gathering_; **synthesize/write on a single thread**. Parallel writes to the shared artifact are the Flappy Bird failure — composition keeps the divergent (read) phase parallel and the convergent (write) phase linear.
- **Don't pick this when a fixed workflow suffices.** If the decomposition is _knowable in advance_, the cheaper composition is the fixed chaining/routing/parallelization patterns in `anthropic-workflow-patterns.md` — orchestrator-workers earns its premium only on **runtime-decided** decomposition.

**Score this topology with `rubrics/rubric-orchestrator-workers.md`** (gates: OW1-independence, OW2-dispatch-mode, OW6-termination-guards; review: OW3-context-passing, OW4-routing-determinism, OW5-effort-scaling, OW7-verification, OW8-durability-cost) **plus the cross-cutting `rubrics/rubric-loop-control.md`** for termination/context/verification/budget/durability.

## Primary sources

- **Don't Build Multi-Agents** — Cognition (Walden Y.) — <https://cognition.ai/blog/dont-build-multi-agents> — the defining counter-position: the two load-bearing principles ("Share context, and share full agent traces, not just individual messages"; "Actions carry implicit decisions, and conflicting decisions carry bad results"), the Flappy Bird failure, the read-only-fan-out concession, and the single-threaded + context-compression alternative. _(empirically-argued practitioner position)_
- **How we built our multi-agent research system** — Anthropic Engineering — <https://www.anthropic.com/engineering/multi-agent-research-system> — the reference orchestrator-worker implementation and the opposing empirical result (Opus lead + Sonnet workers beat single Opus by 90.2%): the delegation contract, effort-scaling rules, the 4×/15× token figures, filesystem-artifact + plan-to-memory context strategy, and the eval approach. _(empirically-supported, single-org)_
- **LangGraph supervisor library** (`langgraph-supervisor-py`) — <https://github.com/langchain-ai/langgraph-supervisor-py> — primary source for the graph/state-machine primitives: `create_supervisor`, `create_handoff_tool` returning `Command(goto=…, graph=Command.PARENT)`, `output_mode` (full_history vs last_message), `create_forward_message_tool`, and the handoff-vs-forward distinction.
- **OpenAI Agents SDK — Handoffs** — <https://openai.github.io/openai-agents-python/handoffs/> — defines handoff-as-tool (`transfer_to_X`), default full-history transfer, the `handoff()` knobs (`input_type`, `on_handoff`, `input_filter`), and the crucial contrast with `Agent.as_tool()` (delegation without conversation transfer). The cleanest articulation of handoff vs delegation.
- **Orchestrating Agents: Routines and Handoffs** — OpenAI Cookbook (Swarm origin) — <https://developers.openai.com/cookbook/examples/orchestrating_agents> — the original minimal formulation: a "routine" = system prompt + tools; the agent loop (completion → execute tool calls → append → repeat until none); handoff as a function that **returns an Agent**, swapping active instructions/tools while preserving context. The irreducible mechanism beneath heavier frameworks.
- **CrewAI — Hierarchical Process** — <https://docs.crewai.com/en/learn/hierarchical-process> — primary source for the manager/worker framing: `Process.hierarchical` vs `Process.sequential`, `manager_llm` vs `manager_agent`, `allow_delegation`, the manager-not-in-agents-list constraint, and manager-validates-before-proceeding.
