# Debate / Council / Ensemble / Mixture-of-Agents

**One-liner.** Run N diverse model instances on the _same_ problem and aggregate their outputs — by voting, layered synthesis, debate-to-consensus, or a jury of judges — buying quality and robustness with a **3×–15× compute multiplier** that beats a single strong pass _only_ under three conditions: genuine answer diversity, a verifiable/aggregatable answer, and true model heterogeneity.

**Where it sits in the taxonomy.** This is the **quality-via-diversity** family in the _multi-agent / parallel-ensemble_ band — a peer of auto-research fan-out (`auto-research.md`) and orchestrator-workers (`orchestrator-workers.md`), and distinct from the single-agent iterative loops (evaluator-optimizer, ReAct/Reflexion). It differs from those siblings in _intent_: orchestrator-workers and auto-research **decompose** one job across heterogeneous subtasks; this family runs the **identical** job N times and **aggregates**. It is the canonical fork-and-aggregate topology. As a sub-step it composes downstream of generation (the **adversarial-verify** droppable sub-step in `composition.md`) and inside larger loops as a verification gate; see §Composition. The router selects this family when the task is _quality-via-diversity on a verifiable/aggregatable answer, or an adversarial verification gate_ (`router.md`). Score every instantiation with **rubric-debate-ensemble** (`rubrics/rubric-debate-ensemble.md`).

> **Honesty flag up front (empirically-supported).** Much of multi-agent debate's apparent lift is just the **ensemble/voting effect**, not the debate. At equal compute, default multi-agent debate often does **not** beat self-consistency (cheap parallel voting) or even strong single-agent prompting. This family must clear that bar before it earns its multiplier; the rubric encodes the bar (DE7-ensemble-honesty).

---

## 1. Mechanism

This family contains **five mechanistically distinct loops** that share one principle — _induce diversity, then aggregate_ — but differ in whether agents interact, how many passes occur, and how outputs collapse to one. A builder picks **one**; do not blend them silently.

### (1) Self-consistency — sample-and-vote _(no interaction)_

The simplest and strongest baseline (Wang et al. 2022). One model, K samples, no agents talk.

1. Sample **K** reasoning chains from **one** model at temperature > 0 on the same prompt.
2. Extract the final answer from each chain.
3. Take the **plurality/majority vote** over the K extracted answers.

Purely parallel; one aggregation step; **no convergence loop**. This is the bar every costlier ensemble in this family must beat.

### (2) Multi-agent debate (MAD) — interact-then-vote

Du et al. 2023. Agents _do_ see each other's work.

1. **A** agents (default 3, canonically copies of the same model) each independently answer round 0.
2. For **R** rounds (default 2): feed each agent a **consensus prompt** containing the _other_ agents' current answers, concatenated — verbatim: _"These are the solutions to the problem from other agents: [other answers]. Using the opinion of other agents as additional advice, can you give an updated response…"_ — and have it revise.
3. Final answer = **majority vote** over agents' last-round answers.

Convergence to consensus is **empirical, not guaranteed** — this is a multi-agent game, not a fixed-point iteration. Debate length is **tunable by prompt wording**: "stubborn" prompts (trust your own answer over peers') produce longer debates and better final answers; "agreeable" prompts converge fast, often to a _wrong_ shared answer. For **A > 3**, peer responses are **summarized by a model** before being fed back, to stay under context limits (summarization itself slightly improves results).

### (3) Mixture-of-Agents (MoA) — layered feed-forward synthesis

Wang et al. / Together AI 2024. A feed-forward "network" of LLMs.

1. **l** layers (default 3), each with **n** proposers (default 6, **heterogeneous open models**).
2. **Layer 1** proposers answer independently.
3. Each **subsequent layer's** agents receive **all** previous-layer outputs via an **Aggregate-and-Synthesize** prompt — _"synthesize these responses into a single high-quality response… critically evaluate… do not simply replicate"_ — plus the original query.
4. A final **aggregator** emits the single output.

Feed-forward, **no convergence test**. Proposers and aggregators are **different competencies** — some models propose well but aggregate poorly (and vice-versa). MoA-Lite uses l = 2 for cost.

### (4) LLM-as-a-jury / Panel-of-LLM-evaluators (PoLL)

Verga et al. / Cohere 2024. For **evaluation/scoring** tasks, not generation.

1. Replace one large judge with a panel of **~3 smaller models from disjoint families**.
2. Each judges independently — **jurors never see each other** (independence is the whole point).
3. Aggregate via **max-vote** (binary judgements) or **average-pool** (numeric scores).

Beats a single large judge on human-correlation, cuts intra-model self-preference bias, and costs ~7–8× less.

### (5) Adversarial verification panel — N-skeptic refute gate

A **directed-bias** variant of the jury, used as a _gate_ downstream of generation, not a generator.

1. **N** independent skeptics, each prompted to **refute** a claim.
2. **Majority-refute kills** the claim; if the refute-quorum is unreachable, the claim **passes**.

Catches hallucinations a single self-review misses; this is the form `composition.md` calls the droppable adversarial-verify sub-step.

---

## 2. When it fits / when it fails

### When it fits

| Condition | Why it matters |
| --- | --- |
| **Verifiable or aggregatable answer** | Closed-form (math, multiple-choice, extractable final answer) lets self-consistency _vote_; free-form needs an LLM-aggregator (Universal Self-Consistency / MoA synthesis) or a jury. The answer shape _is_ the gate on this family (DE1). |
| **Genuine answer diversity exists** | The problem admits multiple reasoning paths that sometimes reach different answers (hard math, multi-hop reasoning, ambiguous factual claims). Diversity is the **fuel**; without it the ensemble degrades to expensive resampling. |
| **High-stakes output that justifies the multiplier** | Factual claims to be verified, eval/scoring pipelines, safety gates, research synthesis, consensus-generated training data. |
| **True model heterogeneity is available** | Debate and MoA gains are most reliable when agents are _different models_ (e.g. GPT-4o-mini + Llama-3.1-70b), not temperature-clones of one model. |
| **Evaluation / judging tasks specifically** | A jury of diverse smaller models beats a single large judge on human-correlation **and** cuts self-preference bias **and** costs ~7–8× less (PoLL). |
| **As a verification gate** | N independent skeptics, each told to refute; majority-refute rejects — an adversarial filter that catches hallucinations single self-review misses. |
| **Hallucination / factuality reduction** | Inconsistent facts across instances get removed or corrected when models are forced toward consensus (Du et al.'s biography result). |

### When it fails

| Failure condition | What goes wrong |
| --- | --- |
| **Easy / single-knowledge-point problems** | All agents already agree; debate _"degrades to an inefficient resampling method"_ — you pay 3–15× for nothing. |
| **Equal-compute comparison** | Default MAD often does **not** beat self-consistency or even strong single-agent prompting; much of the apparent gain is the voting effect, not the debate. Single-agent matches or beats multi-agent across multiple datasets/architectures when thinking tokens are normalized. |
| **Debate destroys correct answers** | Self-consistency _minimizes_ errors while _preserving_ correct answers; MAD methods _"often fail to preserve correct answers"_ and introduce new ones — a model talked out of a right answer by agreeable peers. |
| **Homogeneous agents** | Temperature-clones share biases → correlated errors → the majority is _confidently wrong_ and the vote launders a shared bias into false confidence. |
| **Agreeableness / sycophancy** | Instruction-tuned models are _"relatively agreeable"_ and converge prematurely to a shared (possibly wrong) answer unless explicitly prompted to be stubborn. |
| **More agents/rounds don't reliably help** | _"Increasing test-time computation does not always improve accuracy"_; MAD frameworks often fail to use larger inference budgets effectively (plateau or degrade). |
| **Entangled judges** | Jury/judge ensembles inherit correlated bias when judges share training; naive majority over correlated judges underperforms independence-reweighted aggregation. Judges also show self-preference and structural negativity/positivity bias. |
| **Latency-sensitive UX** | MoA can't emit the first token until the final layer completes (high TTFT); debate is sequential across rounds. |
| **Verbosity drift** | MoA outputs are _"marginally more verbose"_; aggregation tends to pad. |

---

## 3. Key parameters

The highest-value section: the knobs a builder sets, with a sensible **default** and the rationale. Defaults below are the empirical sweet spots from the canonical sources; deviations need a stated reason. (Confidence: defaults marked _empirically-supported_ trace to a cited ablation; _practitioner-folklore_ are reasonable-but-uncalibrated.)

| Knob | Default | Rationale / evidence |
| --- | --- | --- |
| **Ensemble width N** (agents / samples / proposers / jurors) | **Self-consistency: K ≈ 5–40** · **Debate: A = 3** · **MoA: n = 6 proposers** · **Jury: 3** | _Empirically-supported._ The primary cost driver and the diversity budget. Self-consistency gains saturate (~5–40). MoA ablation: 1 → 47.8%, 3 → 58.0%, 6 → 61.3%. ~3 jurors already beats one big judge (PoLL). Too few = no diversity; too many = cost with no return **+ context overflow**. |
| **Rounds / layers / depth R** | **Debate: R = 2 rounds** · **MoA: l = 3 layers** (MoA-Lite: 2) | _Empirically-supported._ How many times agents see each other's work. More helps until convergence/plateau; each increment **multiplies** cost. Beyond convergence it wastes compute or lets agreeable models drift to a wrong consensus. |
| **Diversity source** | **Distinct model families** (disjoint training) > distinct personas/lenses/prompts > temperature/sampling (weakest) | _Empirically-supported._ Diversity is the _entire_ value proposition. MoA and the MAD review both find heterogeneous models beat temperature-sampling one model. Choose models from **disjoint families** to decorrelate errors and reduce shared bias. Temperature-only diversity is the single most common way to void the method (correlated errors). |
| **Aggregation function** | **Match to answer shape** — discrete: majority/plurality vote · binary judgement: max-vote · numeric score: average-pool · free-form: LLM-synthesizer · gate: majority-refute | _Empirically-supported._ Determines how N outputs collapse to one. **Mismatch breaks the method** (voting on free-form prose silently fails — see DE1/DE3). Correlated voters need **independence-reweighting**, not naive majority. |
| **Agreement / stubbornness calibration** _(debate-specific)_ | **Stubborn-leaning** prompt (trust own answer; require explicit reason to defer) | _Empirically-supported._ Pure prompt engineering and the single **highest-leverage debate knob**. Stubborn → longer debate, better answers; agreeable → fast convergence to a possibly-wrong consensus. Default toward stubborn to resist sycophantic premature consensus. |
| **Role assignment** (proposer / aggregator / skeptic / judge) | **Strongest synthesizer in the aggregator seat; diverse families as jurors; explicit refuter for gates** | _Empirically-supported._ Proposing and aggregating are different competencies (MoA: WizardLM proposes well, aggregates poorly). Adversarial panels _need_ a refuter role; juries need decorrelated judge families. |
| **Context-management strategy** | **Concatenate while it fits; summarize peer responses once N is large** | _Empirically-supported._ Concatenating all peer responses overflows context as N grows. Du et al. summarize peer responses with a model before feeding back (required for many agents; also slightly improves quality). MoA suggests chunk-wise aggregation to cut TTFT. This sets how wide the ensemble can scale. |
| **Compute-budget guard / fallback-to-single** | **Gate the gate: trigger the ensemble only on high-stakes or high-disagreement items; else single pass** | _Empirically-supported._ Because the ensemble _loses_ to single-agent at equal budget on easy/agreeing problems, decide **when** to spend the multiplier. Without this guard the technique is **net-negative on cost**. This is the knob the rubric checks at DE4-budget-fallback. |

---

## 4. Termination · context strategy · verification gate

These instantiate the cross-cutting substrate; the canonical derivation lives in `control-plane.md`. This section gives only the **family-specific** settings — do not re-derive the general theory.

### Termination (→ `control-plane.md` §termination)

Unlike iterative loops, most members here are **single-shot or fixed-depth** — the stop is structural, not a convergence test.

| Member | Stop condition |
| --- | --- |
| **Self-consistency** | Fixed sample budget **K** reached, then vote (single-shot, no convergence loop). Adaptive variants stop early via a posterior over answer tallies once a winner is statistically clear. |
| **Debate** | Fixed round count **R** (default 2) reached, **OR** empirical consensus detected (all agents report the same answer), **OR** a **max-round cap** to bound a non-converging multi-agent game. |
| **MoA** | Fixed number of layers **l** traversed; the final aggregator emits the output (feed-forward, no convergence test). |
| **Jury / adversarial panel** | All jurors voted; the aggregation function fires once (single-shot per item). Threshold-gate variant: **stop and REJECT** as soon as majority-refute is reached; **stop and ACCEPT** if the refute-quorum is unreachable. |
| **All** | **Cost ceiling / budget cap**: hard stop on total tokens or agent-invocations regardless of consensus — the mandatory backstop because the multiplier compounds with N and R. |

The control-plane layering still applies: the goal-gate (the aggregation verdict) sits over a hard cap (token/invocation ceiling). There is no per-round "no-progress detector" for single-shot members; for debate, **premature consensus** is the analog signal and the **max-round cap** is its backstop.

### Context strategy (→ `control-plane.md` §context)

**Fork-and-aggregate, not accumulate.** This is the family's defining context posture and the source of its decorrelated diversity.

- Each agent/sample runs in an **isolated context** on the same query — Anthropic: multi-agent _"distributes cognitive load across separate context windows."_
- Cross-agent information flows **only through the aggregation channel**:
  - **self-consistency** — none (pure parallel);
  - **debate** — peer answers injected into each agent's next-round prompt (concatenated, or **summarized** when N is large to avoid overflow);
  - **MoA** — each layer receives the previous layer's full outputs via the Aggregate-and-Synthesize prompt;
  - **juries** — judges _never_ see each other (independence is the point; entangled judges reintroduce correlated bias).
- **No shared scratchpad/memory file across agents** in the canonical forms — shared memory would _correlate_ the agents and defeat the diversity that justifies the cost. (This is the inverse of Ralph's disk-as-memory posture: here, _not_ sharing state is load-bearing.)
- The **orchestrator holds the only global view** and is where summarization, voting, or synthesis happens.

### Verification gate (→ `control-plane.md` §verification)

This family **is** the verification mechanism in two modes:

- **(a) Consensus-as-verification.** Agreement across independent diverse agents is treated as a correctness signal (self-consistency vote; debate consensus; MoA synthesis). **Strongest** when answers are extractable/discrete and agents are decorrelated; **weak** when agents are correlated (shared bias passes the vote).
- **(b) Adversarial-panel-as-gate.** N independent skeptics each prompted to refute; **majority-refute** kills the claim — a directed-bias jury used downstream of generation. For scoring tasks, the diverse-family jury (PoLL) both produces and validates the score, correlating with humans better than a single judge **and** reducing self-preference bias.

**Critical caveat for the builder (empirically-supported).** **Consensus is necessary-not-sufficient.** Agreeable models converge on wrong answers, and at equal budget the gate may add no value over a strong single-agent self-check on easy items. On the control-plane gate-trust ladder, a _decorrelated diverse ensemble_ outranks a same-model self-grade but still ranks **below** an executable oracle — if an oracle exists, prefer it and use the ensemble only where no oracle is affordable. **Gate the gate:** apply this family only to high-stakes / high-disagreement outputs.

---

## 5. Failure modes (each with its guard)

| # | Failure mode | Guard |
| --- | --- | --- |
| 1 | **Correlated-error collapse** — homogeneous (temperature-cloned) agents share biases, so the majority vote is confidently wrong and laundered as high confidence. | Source diversity from **disjoint model families**, not temperature; treat temperature-only ensembles as a smell (DE2). |
| 2 | **Sycophantic premature convergence** — agreeable models converge fast to a shared answer; a correct minority gets talked out of it. | **Stubborn-leaning** debate prompts; cap rounds; track whether a minority answer was correct before discarding it (DE5). |
| 3 | **Correct-answer destruction** — MAD introduces new errors and fails to preserve correct answers more than self-consistency does. | Prefer **self-consistency** as the baseline; only adopt debate where there's evidence interaction beats voting _for this task_ (DE7). |
| 4 | **Ensemble-effect illusion** — gains attributed to "debate/collaboration" that ablation shows are just the voting effect. | Justify interaction over cheap parallel voting in writing; benchmark against self-consistency at **equal compute** (DE7-ensemble-honesty). |
| 5 | **Budget misattribution** — multi-agent "wins" only because it spent more tokens; at equal compute single-agent matches it. | Normalize for compute when comparing; require a stakes/parallelism justification for the multiplier (DE4). |
| 6 | **Aggregation-mismatch** — majority vote on free-form outputs (no exact-match key) silently fails. | Match the aggregation function to the **answer shape**; free-form → LLM-aggregator, never naive vote (DE1/DE3). |
| 7 | **Judge entanglement & self-preference** — correlated judges or a judge grading its own family inflate scores. | **Disjoint judge families**; independence-reweighted aggregation over naive majority; never let a model judge its own output (DE8). |
| 8 | **Structural verdict bias in panels** — judges over-produce REFUTE (negativity) or over-endorse (positivity). | Calibrate the panel's verdict distribution; balance the refuter framing; treat skew as a gate-integrity finding (DE8). |
| 9 | **Context overflow at scale** — concatenating peer responses for large N hits context limits; naive impls crash or truncate. | Insert a **summarization step** for large N; chunk-wise aggregation; cap N to the context-safe width. |
| 10 | **Latency / TTFT blowup** — MoA blocks first token until the last layer; debate is sequential across rounds. | Budget for high TTFT; use MoA-Lite (fewer layers) or self-consistency where latency matters; hand interactive-UX concerns to the sibling skill. |
| 11 | **Cost runaway** — 15× token usage with no per-item budget guard turns a quality win into an economic loss. | Hard **token/invocation ceiling**; gate-the-gate routing (ensemble only on high-stakes items) (DE4, `control-plane.md` §budget). |
| 12 | **Verbosity inflation** — synthesis/aggregation pads outputs. | Length-constrain the aggregator prompt; verify the final output isn't padded relative to a single pass. |

---

## 6. Composition — how it nests / wraps other layers

This family is rarely the whole system; it is most valuable as a **bounded sub-step inside** a larger loop. See `composition.md` for the full nesting catalog.

- **As a verification gate inside any generating loop.** The adversarial-verify panel (member 5) drops in **downstream of generation** in evaluator-optimizer, plan-execute, or orchestrator-worker pipelines as the _droppable adversarial-verify sub-step_ — the ensemble _is_ the gate. This is its most common composed role.
- **Inside auto-research / orchestrator-workers as the synthesis stage.** A fan-out (`auto-research.md`, `orchestrator-workers.md`) decomposes a job across heterogeneous subtasks; an **MoA-style aggregator** or a **jury** can collapse the parallel returns into one validated output. The fan-out provides breadth; the ensemble provides the _quality/agreement check_ on the merge.
- **As the judge in an evaluator-optimizer loop.** Replace a single same-model judge in `evaluator-optimizer.md` with a **PoLL jury** to harden the gate against self-preference bias — directly addressing that family's EO7-judge-bias risk.
- **Self-consistency as a cheap inner reliability wrap.** Any single model call inside a larger loop that needs a more reliable discrete answer can be replaced by a K-sample self-consistency vote — the lowest-cost member, no orchestration overhead.
- **What it must _not_ wrap:** do not put a shared scratchpad/memory between the ensemble's agents (correlates them, defeats the diversity); and do not stack this family _on top of itself_ (debate-of-debates) without an equal-compute justification — the multiplier compounds and the ensemble-effect illusion (failure #4) deepens.

When this family is composed, the host loop's `rubric-loop-control` gates still apply, **plus** `rubric-debate-ensemble` for the ensemble sub-step — a composed plan must clear the **union** of both gate sets (`rubric-manifest.json` ship rule).

---

## 7. Primary sources

| Title | URL |
| --- | --- |
| Improving Factuality and Reasoning in Language Models through Multiagent Debate (Du, Li, Torralba, Tenenbaum, Mordatch, 2023; ICML 2024) — the foundational debate loop: 3 agents × 2 rounds default, the verbatim consensus prompt, majority-vote finalization, stubbornness-controls-length finding, summarization variant, factuality result. | <https://arxiv.org/abs/2305.14325> |
| Mixture-of-Agents Enhances Large Language Model Capabilities (Wang et al., Together AI, 2024) — layered proposer+aggregator (3 layers × 6 proposers), Aggregate-and-Synthesize prompt, collaborativeness, proposer-count ablation (1→47.8%, 3→58.0%, 6→61.3%), heterogeneity-beats-temperature, MoA-Lite, TTFT/verbosity limits. | <https://arxiv.org/html/2406.04692v1> |
| Self-Consistency Improves Chain of Thought Reasoning in Language Models (Wang, Wei, Schuurmans, Le, Chi et al., 2022) — sample-K-then-majority-vote baseline; +17.9% GSM8K / +11.0% SVAMP; the bar any costlier ensemble must clear. | <https://arxiv.org/abs/2203.11171> |
| Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models (Verga et al., Cohere, 2024) — LLM-as-a-jury: 3 disjoint-family models, max-vote/average-pool, beats a single GPT-4 judge on human-correlation (Cohen's κ 0.763 vs 0.627 on NQ), cuts intra-model bias, ~7–8× cheaper. | <https://arxiv.org/abs/2404.18796> |
| Multi-LLM-Agents Debate — Performance, Efficiency, and Scaling Challenges (ICLR 2025 Blogposts) — the counter-evidence: most MAD fails to beat CoT/self-consistency; the gain is the ensemble/voting effect; MAD fails to preserve correct answers; more budget doesn't reliably help; use MAD only with heterogeneous models, never for single-knowledge-point problems. | <https://d2jud02ci9yv69.cloudfront.net/2025-04-28-mad-159/blog/mad/> |
| How we built our multi-agent research system (Anthropic, 2025) — production economics: orchestrator-worker (lead Opus + 3–5 Sonnet subagents, isolated contexts), ~15× the tokens of chat, token usage explains ~80% of performance variance, +90.2% over single-agent on research evals — worth it only for high-value, parallelizable tasks. | <https://www.anthropic.com/engineering/built-multi-agent-research-system> |

---

**Scoring.** Score every plan that composes this family with **rubric-debate-ensemble** (`rubrics/rubric-debate-ensemble.md`): gates **DE1-answer-shape** (aggregation matches answer shape) and **DE2-diversity-authenticity** (agents genuinely decorrelated, not temperature-clones); review dims **DE3-aggregation**, **DE4-budget-fallback**, **DE5-agreement-calibration**, **DE6-role-sizing**, **DE7-ensemble-honesty** (justified over self-consistency), **DE8-gate-integrity**. Always also load the cross-cutting `rubric-loop-control.md` (termination · budget · verification · durability).
