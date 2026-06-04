# Anthropic Workflow Patterns (chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer)

The five-pattern vocabulary from Anthropic's _Building Effective Agents_ — **prompt chaining, routing, parallelization (sectioning + voting), orchestrator-workers, evaluator-optimizer** — all composed from one building block, the **augmented LLM** (a model with retrieval + tools + memory). These are the foundational, code-orchestrated compositions a builder reaches for _before_ handing control to a fully autonomous agent.

**Where it sits in the taxonomy.** This is the **workflow** family — the predefined-orchestration spine of the library. It owns the one load-bearing distinction the router leans on:

> **Workflows** = "systems where LLMs and tools are orchestrated through predefined code paths." **Agents** = "systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks."

All five patterns are workflows: the **builder** writes the control flow; only an autonomous agent lets the model own the loop. Two of these patterns are large enough that this library breaks them into their own references — they appear here only as a pointer, with the full mechanism + rubric elsewhere:

- **Orchestrator-workers** → `orchestrator-workers.md` (rubric `rubrics/rubric-orchestrator-workers.md`)
- **Evaluator-optimizer** → `evaluator-optimizer.md` (rubric `rubrics/rubric-evaluator-optimizer.md`); its parallel/voting cousin → `debate-ensemble.md`

This reference is the canonical home for **prompt chaining**, **routing**, and **parallelization**, and the canonical statement of the **workflow-vs-agent distinction** and the **three design principles** that govern all of them. For how these nest and wrap each other, see `composition.md`. This family has **no own rubric**: pattern-fit is scored by `rubrics/rubric-loop-selection.md`; the sub-patterns route to their family rubrics above.

---

## 1. Mechanism — the actual control flow

Every pattern is built from the **augmented LLM**: a model that can "independently generate search queries, select tools, and determine what information to retain." The builder's job is to tailor that block's capabilities and give it **clear, documented interfaces** (the ACI principle, §7). The five patterns differ only in how code wires those calls together.

### (1) Prompt chaining — linear pipeline, output→input

> "Decomposes a task into a sequence of steps, where each LLM call processes the output of the previous one." Goal: _"trade off latency for higher accuracy, by making each LLM call an easier task."_

Reference control flow (cookbook `basic_workflows`):

```text
result = input
for prompt in prompts:          # ordered, fixed list of step prompts
    result = llm_call(f"{prompt}\nInput: {result}")   # reassign: each output is the next input
return result
```

Optionally insert programmatic **gates** between steps — deterministic checkpoints that validate intermediate output and can **short-circuit** (proceed / retry / abort) before the next call. _Forward-only_ state: only the previous step's output flows on unless the builder explicitly threads earlier inputs.

### (2) Routing — classify once, dispatch to a specialist

> "Classifies an input and directs it to a specialized followup task." Enables separation of concerns and per-category specialized prompts; also routes easy→cheap and hard→capable models.

Reference control flow (cookbook `route`):

```text
# selector LLM sees the input + the available route keys
selection = llm_call(input, routes.keys())
# emits: <reasoning>...</reasoning><selection>team_name</selection>
route_key = extract_xml(selection, 'selection').strip().lower()
return llm_call(routes[route_key], input)   # run the chosen specialized prompt on the ORIGINAL input
```

One classification + one specialized call. **Not a loop.** The classification reasoning is discarded once the key is chosen (stateless).

### (3) Parallelization — concurrent calls, aggregated in code

LLMs work simultaneously; outputs are joined programmatically. Reference control flow (cookbook `parallel`) submits one `llm_call` per input to a `ThreadPoolExecutor(max_workers=n)` and returns results **in input order**. Two sub-variants:

| Sub-variant | What it does | Canonical use |
| --- | --- | --- |
| **Sectioning** | "Breaking a task into independent subtasks run in parallel." Each branch handles a _different_ facet. | Main call answers while a separate call screens for guardrail violations; or N eval calls each judge a different aspect. |
| **Voting** | "Running the same task multiple times to get diverse outputs," then aggregate by a **threshold**. | Several prompts independently review code for a vulnerability; flag if any / N / majority agree. |

Branches are **isolated** — no branch can see another; all reconciliation lives in the post-hoc aggregation step. (Voting/self-consistency/jury structures are scored by `rubrics/rubric-debate-ensemble.md`; this reference covers the workflow-level wiring.)

### (4) Orchestrator-workers — runtime decomposition

> "A central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results." **Key difference from parallelization:** "subtasks aren't pre-defined, but determined by the orchestrator based on the specific input." Two-phase (plan → execute), hub-and-spoke context.

Full mechanism, parameters, and failure modes live in `orchestrator-workers.md`. **Use that, not this section, when the router selects this pattern.**

### (5) Evaluator-optimizer — generate↔critique loop

> "One LLM call generates a response while another provides evaluation and feedback in a loop." Stop signal is the literal `PASS` string; feedback **accumulates** in memory across attempts. Effective "when we have clear evaluation criteria, and when iterative refinement provides measurable value."

Full mechanism, parameters, and the non-convergence guard live in `evaluator-optimizer.md`. **Use that, not this section, when the router selects this pattern.**

### The workflow-vs-agent distinction (the line this family draws)

|  | Workflow (these 5 patterns) | Autonomous agent |
| --- | --- | --- |
| Who owns the control flow | the **builder**, in code | the **model**, at runtime |
| Step count | **predictable** / bounded | unpredictable — "difficult or impossible to predict the required number of steps" |
| Ground truth | builder-inserted gates / aggregation | **environment feedback** at each step (tool results, tests, compiler) |
| Cost / risk | bounded, reproducible | "higher costs, and the potential for compounding errors" |
| When | the default for anything decomposable | open-ended problems, trusted/sandboxed env, errors detectable + recoverable |

Reserve full agents for genuinely open-ended work. Everything decomposable should be a workflow first. (Autonomous loops themselves are covered by `react-reflexion.md` and `async-oversight.md`.)

---

## 2. When it fits / when it fails

| Pattern | Fits when | Fails when (the misfire) |
| --- | --- | --- |
| **(default) single augmented LLM** | One strong pass with retrieval + tools + in-context examples answers it | — (this is the floor; only escalate "when needed") |
| **Prompt chaining** | Task decomposes into **fixed, cleanly-separable** steps; each call gets easier; accuracy worth the latency | Task does **not** decompose into fixed steps → added latency + brittle hand-offs, no accuracy gain |
| **Routing** | Inputs fall into **distinct categories** that benefit from specialized handling, _and classification is accurate_; cost-routing easy→cheap | Categories overlap or the classifier is inaccurate → **silent misroutes** (no ground-truth correction) |
| **Parallelization — sectioning** | Subtasks are **independent**; concurrency buys speed; guardrail screen runs beside the main call | Subtasks are actually **interdependent** → branches duplicate or conflict; aggregator must reconcile |
| **Parallelization — voting** | Multiple attempts/perspectives raise **confidence** on a checkable answer | Same as above, plus a miscalibrated threshold (any-flag vs majority) skews false-pos/neg |
| **Orchestrator-workers** | Subtasks **cannot be predicted** in advance and depend on the input (multi-file edits, multi-source research) | Decomposition **is** predictable → you pay for a runtime planning call you didn't need (use chaining/parallel) |
| **Evaluator-optimizer** | **Clear eval criteria** + iterative refinement adds measurable value + an LLM can produce useful feedback | Criteria fuzzy or evaluator can't articulate actionable feedback → oscillation / never-PASS / premature PASS |
| **Autonomous agent** | Open-ended, unpredictable step count, **trusted/sandboxed**, errors detectable + recoverable | High-stakes, hard-to-detect-error tasks → "autonomy becomes a liability"; compounding errors, unbounded spend |

**The family's #1 cautioned failure is over-engineering** — reaching for a workflow (or agent) where a single augmented LLM call would do. _"Find the simplest solution possible, and only increase complexity when needed,"_ which "might mean not building agentic systems at all."

---

## 3. Key parameters (the highest-value section)

The knobs a builder sets. Defaults are starting points from the source + cookbook; deviations need a stated reason and feed the Orchestration Blueprint's PARAMETERS field.

| Parameter | Applies to | Default | Rationale |
| --- | --- | --- | --- |
| **Pattern selection** (which of 5, or none / full agent) | all | **single augmented LLM**, escalate only on a concrete reason | This is the decision the skill exists to make. Two axes drive it: is the decomposition **predictable** (→ chaining/routing/parallel) or not (→ orchestrator-workers/agent), and are there **clear eval criteria** (→ evaluator-optimizer). Wrong pick = under-powered or wasteful. |
| **Chain steps + gate predicates** | chaining | **2–4 steps**; a gate after any step whose output a later step blindly trusts | Too few steps → each call still too hard; too many → latency with no accuracy gain. Gates convert latency spend into reliability (proceed / retry / abort). |
| **Route taxonomy** (category keys) | routing | **mutually-distinct, collectively-exhaustive** set; a fallback/`default` key | Categories must not overlap and must cover the input space; misclassification has no built-in correction, so an explicit default catches the unclassifiable. |
| **Classifier prompt + reasoning capture** | routing | emit `<reasoning>` then `<selection>`; reasoning surfaced, not hidden | The classifier reliability _is_ the pattern's reliability. Surfacing reasoning satisfies the transparency principle and makes misroutes debuggable. |
| **Aggregation rule + vote threshold** | parallelization | **sectioning:** an explicit merge function. **voting:** threshold tied to error-cost asymmetry — **any-flag** for guardrails, **majority** for quality | The threshold directly trades false-positive vs false-negative rate. A guardrail should trip if _any_ reviewer objects; a quality call should need a majority. |
| **n_workers / concurrency** | parallelization | **3–5**, capped by rate limits + token budget | Voting confidence scales with n; sectioning speed is bounded by the slowest branch. More branches = more cost with diminishing return. |
| **Orchestrator decomposition prompt + worker contract** | orchestrator-workers | see `orchestrator-workers.md` | Shapes subtask count/granularity and whether outputs merge; owned by that reference. |
| **Evaluator criteria + PASS rubric** | evaluator-optimizer | see `evaluator-optimizer.md` | "Only output 'PASS' if all criteria are met and you have no further suggestions." Owned by that reference. |
| **Max iterations / budget cap** | evaluator-optimizer, agents | **iteration ceiling = 3–5** _and_ a token/cost budget; **never** PASS-only | The cookbook stops only on `PASS` — production **MUST** add a ceiling or it can never-terminate. Anthropic frames budget explicitly (≈30–50k tokens ≈ workflow territory). See §5. |
| **Model assignment per role** | all multi-call patterns | **cheap** for classify/section/screen; **capable** for generate/synthesize | The primary cost/latency lever within a fixed pattern. Patterns exist partly to let you mix tiers. |
| **Human-in-the-loop checkpoints** | agents; optional in workflows | a checkpoint **proportional to error-stakes**; read-only scoping by default for high-stakes | The core safety knob. "Read-only access and human-in-the-loop are real mitigations, but they cap how far you can scale." |

---

## 4. Termination / context / verification for this family

These are the cross-cutting concerns; the canonical treatment is `control-plane.md`. Here is only how _this family_ instantiates each — do not re-derive the control plane.

### Termination (per pattern)

| Pattern | Terminates when |
| --- | --- |
| Prompt chaining | the fixed step list is exhausted; a **gate** may abort early on failed validation |
| Routing | the single selected downstream call completes (one classify + one specialized call — not a loop) |
| Parallelization | all spawned calls return and the aggregation/vote function produces a result (in-order join on futures) |
| Orchestrator-workers | every orchestrator-emitted subtask has a worker result (+ optional synthesizer) — subtask count fixed at plan time |
| Evaluator-optimizer | the evaluator emits exactly `PASS`. **In production a max-iteration ceiling or token/cost budget MUST be added** — the reference loop has no other stop and can non-converge on `NEEDS_IMPROVEMENT`/`FAIL` |

Note the asymmetry: four of the five patterns terminate **structurally** (the code path ends). Only **evaluator-optimizer** is an open loop needing an external cap — which is exactly why it lives in its own reference. This is the cleanest tell that a "workflow" has quietly become a loop that the `rubric-loop-control` C1 (termination-stack) gate must catch.

### Context strategy (the cleanest way to tell the patterns apart)

| Pattern | Posture | What carries state |
| --- | --- | --- |
| Prompt chaining | **forward-only** | the previous step's _output_ is reassigned to input; earlier inputs dropped unless threaded |
| Routing | **stateless** | original input passed once to the selected prompt; classification reasoning discarded after key selection |
| Parallelization | **isolated** | each branch on its own input, **no shared context**; all context lives in the aggregation step |
| Orchestrator-workers | **hub-and-spoke** | orchestrator holds the global plan; each worker gets a scoped slice (not siblings' outputs); convergence at collection/synthesis |
| Evaluator-optimizer | **accumulating** | the _only_ growing-memory pattern: each failed attempt appended to `memory`; the full "Previous attempts… Feedback…" string fed forward |

General guidance (transparency principle): keep context **minimal and explicit**, and **surface** intermediate state (plans, classifications, feedback) rather than hiding it.

### Verification gate (verification is itself one of the patterns)

Rank by trust per `control-plane.md`: **executable oracle > ground-truth > LLM-judge/panel > self-grade.** For this family:

1. **Prompt chaining → programmatic gates.** Deterministic checks between steps (does the outline meet criteria?) that pass/fail intermediate output. Highest trust _when the check is deterministic_.
2. **Parallelization-sectioning → the canonical guardrail/eval mechanism.** A separate LLM instance screens or scores on a dimension the main call doesn't see.
3. **Parallelization-voting → agreement across N runs** against a threshold.
4. **Evaluator-optimizer IS a verification loop** — a second LLM emits `PASS` / `NEEDS_IMPROVEMENT` / `FAIL` + feedback; `PASS` is the gate.

**Confidence caveat (folklore vs. evidence).** The evaluator/voter is typically the **same model class** as the generator, so `PASS` and votes are _self-assessment, not external ground truth_ — strong when criteria are objective/checkable, weak when subjective. The source is explicit (empirically grounded): agents gain real ground truth only from **environment feedback** (tool results, tests, compiler), the most reliable gate; for high-stakes work, prefer **human-in-the-loop** checkpoints over model self-judgment. This is the family's instantiation of the skill-wide **oracle-label illusion** warning — never let a same-model self-grade be the sole gate on correctness.

---

## 5. Failure modes (each with its guard)

| Failure mode | Guard |
| --- | --- |
| **Over-engineering** — a workflow/agent where one augmented LLM call would do (the #1 cautioned failure) | Default to single call; require "rejected alternatives" to state _why_ a single pass wasn't enough before escalating. |
| **Compounding errors** — an early mistake propagates because downstream steps trust upstream output (chains, orchestrator, agents) | Insert chain **gates** that validate before the next call; keep chains short; prefer environment feedback for ground truth. |
| **Silent misroutes** — inaccurate classifier sends input to the wrong specialist, no correction | Distinct + exhaustive categories; surface classifier reasoning; add a `default` route; sample-eval the classifier. |
| **Parallel branch conflict / duplication** — sectioning/voting on interdependent subtasks yields contradictory or redundant output | Fan out **only** on genuinely independent subtasks; make the aggregator reconcile; if interdependent, sequence instead. |
| **Orchestrator over-decomposition** — planner emits too many / low-value / non-mergeable subtasks | Constrain the decomposition prompt (e.g., "2–3 distinct approaches"); cap subtask count; see `orchestrator-workers.md`. |
| **Evaluator-optimizer non-convergence** — never emits `PASS` (oscillation) without a guard; or premature `PASS` from a weak self-evaluator | **Max-iteration ceiling + budget**; return-best-not-last; sharper/objective criteria; stronger judge. See `evaluator-optimizer.md`. |
| **Evaluator gaming / shared blind spots** — generator and evaluator share a model class and miss the same errors | Different model/family for the judge, or an **executable** check; for high-stakes, human checkpoint. |
| **Runaway token cost** — exploration in orchestrator/agent loops without a cap ("exploration costs money") | Hard token/cost ceiling + circuit-breaker (per `control-plane.md`); cheaper model tiers on cheap roles. |
| **Latency stacking** — long sequential chains or sequential workers add up | Parallelize **only** where subtasks are truly independent; trim chain length; assign fast models to non-critical steps. |
| **High-stakes autonomy** — agents on hard-to-detect-error tasks where "autonomy becomes a liability" | Stay in workflow territory; read-only scoping; human-in-the-loop proportional to stakes; sandbox. |

---

## 6. Composition — how this family nests and wraps

These patterns are the **building blocks** other layers assemble; see `composition.md` for the full nesting model. Common compositions:

- **Orchestrator whose workers are chains** — the orchestrator decomposes at runtime; each worker is itself a fixed prompt chain.
- **Evaluator-optimizer wrapping a parallel generator** — generate N candidates in parallel (voting), then run an evaluator-optimizer loop on the aggregate.
- **Routing as a front door** — a router classifies the input and dispatches to _different downstream topologies_ (a simple input → single call; a complex one → orchestrator-workers).
- **Sectioning as a droppable guardrail** — a screening section runs beside any main pattern and can short-circuit it (also see adversarial-verify in `composition.md`).
- **Chain with a gate that is itself an evaluator-optimizer** — the gate between two chain steps runs a generate↔critique loop until the intermediate artifact passes.

**ACI hygiene applies to every nesting.** When patterns wrap each other, the worker/tool interfaces between them must be clearly documented and tested (principle 3) — fuzzy interfaces are where composed patterns leak. Two patterns large enough to be their own references — **orchestrator-workers** and **evaluator-optimizer** — are wired in `orchestrator-workers.md` and `evaluator-optimizer.md`; this reference owns chaining, routing, and parallelization, and the parent vocabulary they all share.

**The three design principles** (govern every pattern and every composition):

1. **Maintain simplicity** in design.
2. **Prioritize transparency** — explicitly show the agent's planning steps.
3. **Carefully craft the agent-computer interface (ACI)** via thorough tool documentation and testing.

---

## 7. Scoring (no own rubric)

This family has no dedicated rubric. Score it through:

- **`rubrics/rubric-loop-selection.md`** — pattern-fit: was the right pattern chosen for the task's decomposition-predictability and eval-criteria availability, and was the **single augmented LLM** explicitly ruled out? (S1-simplest-sufficient, S2-workflow-vs-agent are the relevant gates.)
- **`rubrics/rubric-loop-control.md`** — every selected pattern inherits this (termination, budget, gate, context, durability). For this family, C1 (termination-stack) must catch the evaluator-optimizer open-loop case; C3 (verification-gate) must catch the same-model self-grade caveat.
- Sub-patterns route to their family rubric: **orchestrator-workers** → `rubrics/rubric-orchestrator-workers.md`; **evaluator-optimizer** / ReAct / Reflexion → `rubrics/rubric-evaluator-optimizer.md`; **voting / debate / ensemble** → `rubrics/rubric-debate-ensemble.md`.

---

## 8. Primary sources

- **Building effective agents** — Anthropic Engineering (Erik Schluntz & Barry Zhang, Dec 2024). <https://www.anthropic.com/engineering/building-effective-agents> — THE primary source: the workflows-vs-agents distinction, the augmented-LLM building block, all five patterns + their fit conditions, the autonomous-agent definition, the three design principles, and the cost-latency trade framing. Verbatim wording for each pattern's mechanism.
- **Anthropic Cookbook — patterns/agents** (`basic_workflows`, `orchestrator_workers`, `evaluator_optimizer` notebooks). <https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents> — reference implementations pinning the exact mechanics: the `chain()` reassignment loop, the `route()` XML classifier + dict lookup, `parallel()` via `ThreadPoolExecutor`, the orchestrator's `<analysis>`/`<tasks>` schema + worker contract, and the evaluator-optimizer loop whose stop condition is the literal `PASS` string with accumulating feedback memory.
- **Building effective agents — Simon Willison's annotated read** (Dec 20, 2024). <https://simonwillison.net/2024/Dec/20/building-effective-agents/> — independent corroboration of the load-bearing claims: endorses the workflows-vs-agents definition and the augmented-LLM framing, and amplifies the "start simple / avoid frameworks / agents add cost and compounding errors" counsel — useful for separating empirically-grounded guidance from agent hype.
