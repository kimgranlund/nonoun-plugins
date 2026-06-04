# Plan-and-Execute / Planner-Executor (with Replanner)

> Mechanism reference for the **plan-execute** loop family. PLAN mode loads this to parameterize the topology after `router.md` selects it. Score the result with `rubrics/rubric-plan-execute.md`.

## 1. One-liner & where it sits

A strong planner writes the **whole** multi-step plan up front; cheaper executors run steps **without re-consulting the planner**; a replanner revises the _remaining_ plan only on failure or new information. You trade per-step adaptivity for **long-horizon coherence, lower cost, and an auditable plan**.

In the taxonomy (`composition.md`) this is **single-agent iteration with explicit, front-loaded decomposition** — the opposite pole from ReAct (`react-reflexion.md`) on the _plan-vs-interleave_ axis. ReAct interleaves think→act→observe and re-feeds the growing history every step; plan-execute computes the plan once and runs steps against it. When the planner / executor / replanner run as distinct roles it borders **orchestrator-workers** (`orchestrator-workers.md`) — the dividing line is that here the decomposition is _foreseeable and largely fixed at plan time_, whereas orchestrator-workers decides the decomposition at runtime. **Spec-Driven / Explore-Plan-Code-Commit** (`spec-driven.md`) is the coding specialization of this family and shares this rubric; the written spec _is_ the plan.

Aliases you may see: Planner-Executor, Plan-then-Execute, Plan-and-Solve (PS / PS+), ReWOO (Planner/Worker/Solver), LLMCompiler (Planner/Task-Fetching-Unit/Joiner), BabyAGI (task-queue lineage), Plan-and-Act.

## 2. Mechanism — the control flow

Three logical roles arranged as an **outer loop**, not ReAct's single interleaved loop. Canonical LangGraph state:

```text
state = { input, plan: list[str], past_steps: list[(step, result)], response: str | None }
```

**1. PLAN — once, strong model.** The planner receives the objective and emits a _complete, ordered_ plan. It is told to think through ALL steps at once. Representation varies (see §4 "Plan representation"):

- list of natural-language steps (basic plan-execute),
- an **evidence-placeholder blueprint** — ReWOO's `Plan/#E1/#E2…` lines where `#En` are evidence slots tools will fill,
- a **dependency DAG** with `$1/$2` placeholders (LLMCompiler) to expose parallelism,
- an explicit **task queue** (BabyAGI).

**2. EXECUTE — per step, cheap model or sub-agent.** Each plan step goes to an executor. In the canonical LangGraph build the executor is a _small ReAct sub-agent_ given only the current step plus minimal plan context. It calls 1+ tools, returns a result, and the result is appended to `past_steps`. **The planner is NOT consulted between steps** — N steps cost ~N cheap calls, not N strong-model think-cycles. Variant control flow at this stage:

- ReWOO's **Worker** fills all placeholders sequentially with **no intermediate LLM reasoning** (reasoning was front-loaded into the plan).
- LLMCompiler's **Task Fetching Unit** resolves satisfied dependencies and dispatches independent tasks **in parallel** to an Executor, substituting `$`-placeholders with real return values as they arrive.

**3. REPLAN / JOIN — after a step (or after the plan exhausts), strong model.** The replanner is re-invoked with `{original objective, original plan, past_steps}` and must return a **typed union**:

- **RESPOND** → emit the final answer, terminate; or
- **REVISE** → drop completed steps, edit/extend the _remaining_ plan, continue.

This is the **load-bearing adaptivity knob**. Variants:

- ReWOO replaces it with a single **Solver** call (plan + evidence → answer; no revision loop).
- LLMCompiler uses a **Joiner** that decides respond-vs-replan and supports recursive/dynamic replanning for tasks whose shape depends on intermediate results.
- Plan-and-Act's dynamic replanner updates the plan **after every executor step** — empirically the single biggest lever (see §4).

The outer loop:

```text
plan ──▶ ( execute step )* ──▶ replan ──▶ { respond ⇒ DONE | revise ⇒ loop }
              │                                  ▲
              └──── past_steps (step,result) ────┘
```

The `should_end` edge terminates when the replanner produces a non-null `response`. **Contrast with ReAct:** ReAct has no separate plan object and re-feeds the full growing observation history on every step (one strong call per tool call) — which is exactly why plan-execute is cheaper for N>~3 steps, and why ReWOO claims ~5× token efficiency: it never re-contextualizes prior observations.

## 3. When it fits / when it fails

**Fits (empirically-supported):**

- Long-horizon, multi-step tasks that decompose cleanly into a **known sequence** — research reports, multi-hop QA, scripted web tasks, ETL-like pipelines, SWE tasks with stable structure.
- Dependency structure largely **foreseeable at plan time** (the planner can write a correct-enough plan without seeing intermediate results).
- **Cost/latency-sensitive** workloads with many tool steps: `(1 strong plan) + (N cheap executes)` beats ReAct's N strong calls once N exceeds ~3.
- An **explicit, inspectable plan is itself a requirement** — governance, audit, compliance, human-in-the-loop approval before execution, replayability.
- **Parallelizable** tool calls with a clear DAG → use the LLMCompiler variant (up to ~3.7× latency, ~6.7× cost wins vs ReAct).
- You can afford a strong planner but want execution on a cheap/fast model.
- Plan quality dominates: Plan-and-Act shows a _trained planner with an UNTRAINED executor_ still hits 44% — structured plans substantially lift weak executors.

**Fails (route elsewhere):**

- **Highly uncertain / exploratory** environments where the right next step genuinely can't be known until you observe the last — the planner writes a happy-path plan that diverges from reality. → ReAct, or per-step replanning.
- Tasks where intermediate observations **reshape the goal** — pure plan-execute (especially ReWOO with no revision loop) can't foresee the reasoning path and degrades.
- **Tight-budget, short tasks (N ≤ 2–3 steps):** the up-front strong-model planning call is pure overhead; ReAct is cheaper and lower-latency to first action (_cost inversion_).
- Plan must adapt mid-run but **replanning is disabled or coarse** — the agent commits early to a flawed plan and later steps entrench it (cascade error). Static-plan systems are brittle by construction.
- **Serial-tool bottleneck:** basic plan-execute and ReWOO still execute tools sequentially — no latency win on independent calls unless you adopt the LLMCompiler DAG.
- Planner's **world-model is wrong** (miscalibrated uncertainty, no contingency branches) → confident-but-wrong plans, poor exception handling.
- **Untrained planning domains** (niche web automation) — naive planning is weak; Plan-and-Act needed synthetic grounded plan data to reach SOTA.

## 4. Key parameters (the knobs you set)

The highest-value section. Set each to a concrete value in the blueprint; deviations from the default need a stated reason.

| Parameter | Default | Rationale |
| --- | --- | --- |
| **Plan representation** | **List-of-strings** for simple foreseeable sequences; switch to **DAG with `$`-placeholders** (LLMCompiler) the moment independent parallel tool calls exist; use **`#E`-placeholder blueprint** (ReWOO) when steps depend on each other but you want zero re-prompting; **task-queue** (BabyAGI) only for open-ended generative task growth | Representation governs parallelism, token cost, and how inter-step dependencies are wired. List is flexible and cheap; DAG is the _only_ form that buys latency; blueprint wires dependencies without re-consulting the planner; queue invites non-termination (see §6). Maps to rubric **PE2-representation**. |
| **Replanning trigger & cadence** | **On-failure + on-plan-exhaustion** as the safe baseline; escalate to **after-every-step** (Plan-and-Act dynamic replanning) for long-horizon/uncertain tasks where it's affordable | The dominant adaptivity lever. Plan-and-Act's per-step replanning added **+10.31pp (43.6%→53.9% on WebArena-Lite)** — more than any other single change. Too rare = brittle; too frequent = collapses back toward ReAct cost. **`never` (ReWOO Solver-only) is only safe when the path is fully foreseeable.** Maps to **PE3-replanning**. |
| **Planner vs executor model split** | **1 strong planner + N cheap executors** | Sets the cost profile and the break-even vs ReAct. Mis-split (strong model on execution) **erases the cost advantage**; too-weak planner emits bad plans a cheap executor can't recover from. Confirm the projected `(1 strong + N cheap)` actually beats ReAct for the expected N. Maps to **PE6-planner-executor-split**. |
| **Executor context scope per step** | **Current step + the objective + a compact summary of relevant prior results — NOT the full conversation history** | Too little → step loses global intent (locally-correct, globally-wrong actions). Too much → you re-incur the token cost plan-execute exists to avoid (ReWOO's win comes precisely from _not_ re-feeding prior observations). Maps to **PE8-context-durability** and `control-plane.md` context posture. |
| **Replan decision schema** | **Typed union `respond \| revise`** where `revise` can drop done steps AND insert/reorder remaining ones | A respond-only schema breaks adaptivity; a revise-only schema breaks termination. The union must let the replanner _both_ finish early _and_ edit the remaining plan. Maps to **PE3-replanning** / **PE1-plan-trigger**. |
| **Step granularity / decomposition depth** | **One verifiable tool-or-reasoning action per step** — coarse enough to avoid plan bloat, fine enough that each step has a checkable result | Too coarse → executor faces the same cognitive overload decomposition was meant to remove. Too fine → plan bloats, more replanning surface, more failure points. Governs whether decomposition actually reduces per-step load. |
| **Parallelism policy (DAG scheduling)** | **Serial by default; concurrent dispatch (LLMCompiler Task-Fetching-Unit) only when the plan is a DAG with independent branches** | The headline 3.7× latency win is _entirely_ from parallel dispatch; without a DAG there is none. Don't promise latency you can't deliver on serial tools. |
| **Stop / interrupt & max-iterations policy** | **Hard `max_replans` cap (e.g. 5–8) + no-progress detector + explicit interrupt threshold on uncertainty/cost** | Receding-horizon replanning plus an explicit interrupt prevents runaway loops when plans keep churning. Without a hard cap and a stall detector, replanning loops indefinitely (BabyAGI's failure). See §5 and `control-plane.md`. |

## 5. Termination / context / verification (this family's instantiation)

These are the cross-cutting `rubrics/rubric-loop-control.md` concerns. **Do not re-derive them** — `control-plane.md` is canonical; below is how this family wires into it.

**Termination** — layered, enforced outside the model (control-plane §termination):

- **Goal-gate (canonical success exit):** the replanner/Joiner emits a final `RESPONSE` instead of a revised plan — LangGraph `should_end` on a non-null `response`.
- Plan / task queue **exhausted** with all steps complete and the replanner judges the objective met (BabyAGI: empty queue).
- **Hard cap:** `max_replans` / max-iterations reached.
- **No-progress / stall detector:** repeated steps yield no new evidence, or the plan stops shrinking across replans.
- **Interrupt:** explicit human/stop policy when uncertainty or cost crosses a threshold.
- **Unrecoverable error** after a bounded number of replanning attempts on the same failed step.
  > Never let the replanner's "I'll respond now" be the _only_ stop — pair it with the cap + stall detector, or replan-thrash (§6) runs free.

**Context strategy** — _hybrid, and this is the family's core efficiency mechanism_ (control-plane §context):

- The **PLAN is the durable shared scratchpad** — written once, carried and edited across the whole run as externalized working memory so long-horizon intent isn't lost. (Plan-and-Act: the evolving plan doubles as a memory mechanism, retaining key info across iterations _without_ a separate memory module; replanning is how context is compacted and propagated.)
- **Per-step EXECUTION is deliberately context-isolated** — the executor sees only its step + minimal context, NOT the full history, so context doesn't accumulate quadratically as in ReAct.
- Completed work accrues in a **compact `past_steps` (step, result) log fed only to the replanner**, never back to every executor.
- ReWOO takes isolation to the extreme: all reasoning is front-loaded into the plan and tool observations are never re-fed into a reasoning model — the explicit source of its ~5× token efficiency.
- Net: strong-model context is small and bounded `(objective + plan + past_steps summary)`; executor context is per-step and ephemeral.

**Verification gate** — _not intrinsic to the base architecture; this is a notable gap_ (control-plane §verification; rubric **PE5-verification-hardness**):

- The **replanner/Joiner is only a de facto gate** — it inspects `past_steps` against the objective, but it _verifies its own work_ and can rationalize a flawed plan (entrenchment/cascade). Self-judgment as the sole correctness gate is exactly the failure `rubric-loop-control` C3 warns against.
- **Builder rule:** insert a _separate_ verifier/critic or executable check (tests, schema, consistency check) between EXECUTE and the respond branch — do not trust the replanner's self-judgment. Stronger builds do this: ReWOO's Solver is a final synthesis/consistency check over plan+evidence; LLMCompiler's Joiner explicitly evaluates whether collected results suffice before responding; Plan-and-Act pushes verification into _training-data curation_ — plans are reverse-engineered from VERIFIED successful trajectories and the planner is trained with an outcome-supervised reward model (ORM).
- Use **receding-horizon replanning** so each cycle re-checks state against the goal rather than committing once.

## 6. Failure modes (each with its guard)

| Failure mode | Guard |
| --- | --- |
| **Brittle happy-path plans** — over-confident world-model writes a plan with no contingencies that diverges from the real environment | Require contingency/exception branches in the plan; raise replan cadence; add an explicit STUCK/abort path (control-plane). Rubric **PE3**. |
| **Plan-foresight failure** — correct path depends on observations the planner couldn't see; fatal for no-replan variants (pure ReWOO) | Do **not** use a no-replan variant on uncertain tasks; enable `revise`; if foresight is fundamentally impossible, the router should pick ReAct instead. Rubric **PE1/PE3**. |
| **Early-commitment cascade** — a flawed early step/plan is rationalized and entrenched by later steps and by the replanner itself; one bad output poisons the rest | A **separate** verifier between EXECUTE and respond (not the replanner's self-judgment); receding-horizon replanning. Rubric **PE5**. |
| **Replan thrash / non-termination** — replanning loops without progress | Hard `max_replans` cap + no-progress/stall detector (plan stops shrinking / no new evidence). Rubric **PE7-drift-control** + loop-control C1. |
| **Cost inversion on short tasks** — up-front strong-model planning is pure overhead when N is small | Router gate: if N ≤ ~3 or the task isn't decomposable, pick a single pass or ReAct, not plan-execute. Rubric **PE1-plan-trigger**. |
| **Serial-tool latency trap** — builders expect speed but basic plan-execute / ReWOO still call tools sequentially | Adopt the LLMCompiler **DAG** for independent calls; otherwise don't claim a latency win. Rubric **PE2**. |
| **Executor context starvation** — steps stripped of global intent act locally-correct but globally-wrong | Include the objective + relevant prior-result summary in each step's context (not zero, not the full history). Rubric **PE8**. |
| **Planner-executor capability mismatch** — too-weak planner emits unrecoverable plans; too-strong executor erases the cost rationale | Hold the `1 strong + N cheap` split; validate the projected cost actually beats ReAct for the expected N. Rubric **PE6**. |
| **Untrained-domain planning** — base models plan poorly in domains absent from training (e.g. web automation) | Ground with synthetic plan data / few-shot exemplars, or raise replan cadence to recover from weak initial plans. |
| **Placeholder/dependency resolution bugs** — malformed `#E`/`$`-variable wiring breaks evidence substitution silently | Validate the plan's dependency graph before execution (every placeholder defined before use, no cycles); fail loud on unresolved placeholders. Rubric **PE2**. |

## 7. Composition — how it nests / wraps

(`composition.md`)

- **Executor as a sub-loop.** Each plan step's executor is itself, canonically, a **small ReAct agent** — plan-execute _wraps_ the per-step loop in `react-reflexion.md`. The plan is the outer structure; ReAct is the inner step.
- **As the planning skeleton of a coding loop.** **Spec-Driven / Explore-Plan-Code-Commit** (`spec-driven.md`) is this family applied to long-horizon coding: the written spec is the up-front plan, `code` is execution, the human approval before `code` is the `respond|revise` gate. Same rubric (`rubric-plan-execute`).
- **Verifier as a wrapped sub-step.** The missing intrinsic gate (§5) is supplied by _nesting_ an evaluator-optimizer or debate step (`evaluator-optimizer.md`, `debate-ensemble.md`) between EXECUTE and the respond branch — a droppable adversarial-verify per `composition.md`.
- **When the planner/executor/replanner become distinct agents** with runtime-decided decomposition, you have crossed into **orchestrator-workers** (`orchestrator-workers.md`) — use that rubric instead; the test is whether the decomposition is foreseeable (stay here) or decided at runtime (go there).
- **Parallel execution** is itself an embedded fan-out (LLMCompiler Task-Fetching-Unit dispatching independent branches concurrently) — bounded by the same isolation/independence discipline as `auto-research.md`.

## 8. Primary sources

- **Plan-and-Execute Agents — LangChain Blog.** Canonical practitioner reference: planner/executor/replanner separation, the concrete LangGraph loop (`plan → execute step → replan → should_end`), the three production variants (basic, ReWOO, LLMCompiler), and the cost/latency/accuracy + serial-tool rationale. <https://www.langchain.com/blog/planning-agents>
- **Plan-and-Solve Prompting** (Wang et al., ACL 2023). Origin of explicit plan-then-execute as a reasoning strategy: devise-plan → carry-out-subtasks, the PS+ detailed-instruction variant, and the three error classes (calculation, missing-step, semantic) motivating decomposition over plain "let's think step by step." <https://arxiv.org/abs/2305.04091>
- **ReWOO: Decoupling Reasoning from Observations** (Xu et al., 2023). Planner/Worker/Solver with a `#E1/#E2` evidence-placeholder blueprint produced _before_ any tool call; the token-efficiency argument (~5× efficiency, +4% on HotpotQA) and tool-failure robustness. <https://arxiv.org/abs/2305.18323>
- **An LLM Compiler for Parallel Function Calling** (Kim et al., ICML 2024). The DAG/parallel variant: Planner emits a task DAG with `$1/$2` placeholders; Task-Fetching-Unit resolves and dispatches independent tasks concurrently; Joiner decides respond-vs-replan with dynamic/recursive replanning. Quantifies up to 3.7× latency, 6.7× cost, ~9% accuracy vs ReAct. <https://arxiv.org/abs/2312.04511>
- **Plan-and-Act: Improving Planning of Agents for Long-Horizon Tasks** (2025). Best mechanism+evidence source for replanning value: planner/executor split for cognitive-load reduction, plan-as-memory, grounded synthetic plan data, and the ablation isolating dynamic per-step replanning as the dominant lever (+10.31pp → 53.94% on WebArena-Lite). <https://arxiv.org/html/2503.09572v2>
- **BabyAGI** (Yohei Nakajima, 2023). The task-list lineage: execution → creation → prioritization loop over a task queue with vector-memory context. Canonical plan-as-queue with continuous replanning — and a cautionary case (educational sandbox, prone to non-termination/thrash) for the failure-mode analysis. <https://github.com/yoheinakajima/babyagi>

---

**Score this topology with `rubrics/rubric-plan-execute.md`** (gates: PE1-plan-trigger, PE4-human-gate, PE5-verification-hardness, PE7-drift-control; review: PE2-representation, PE3-replanning, PE6-planner-executor-split, PE8-context-durability), plus the always-on cross-cutting rubrics (`rubric-loop-selection`, `rubric-loop-control`, `rubric-plan-quality`).
