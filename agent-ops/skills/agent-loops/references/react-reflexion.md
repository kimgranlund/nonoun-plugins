# ReAct / Reflexion / Self-Refine — single-agent reason-act-reflect

**One-liner.** A _single_ LLM with _frozen weights_ improves on a task by iterating in-context — interleaving reasoning with tool actions (**ReAct**), critiquing-and-rewriting its own output (**Self-Refine**), or retrying the whole task while carrying verbal lessons in episodic memory (**Reflexion**). No gradient updates. The loop helps **only as far as the feedback signal closing each iteration is trustworthy** — that one variable decides whether it converges to better, no-ops, or actively degrades.

**Where it sits in the taxonomy.** This is the **single-agent iteration** family: in-context self-correction loops, no weights changed, one model wearing one-to-three role-hats. It is the _inner_ loop the larger topologies wrap (`composition.md`): a Reflexion **Actor** is often itself a ReAct agent (the patterns nest); an evaluator-optimizer cycle _is_ a Self-Refine loop with the judge pulled out into a named role; an orchestrator-worker's leaf worker typically _runs_ a ReAct loop. When the router lands here, it usually also nests this inside something else — name the nesting. The family is the canonical home of the skill's third First Principle (_no verification gate, no loop_): these loops are the clearest case where the **gate IS the engine** and an unaudited self-grade quietly degrades output.

The family forms a **ladder of self-correction strength** (cheapest/weakest → strongest), and a builder should climb it only on a concrete reason:

| Rung | Mechanism | Loop? | Feedback | Cost |
| --- | --- | --- | --- | --- |
| CoT | Chain-of-thought, one pass | none | none | 1× |
| Self-Consistency | Sample N reasoning paths, majority-vote | parallel, no feedback | none | N× parallel |
| Self-Refine | Serial self-critique of one output | serial | self-critique | ~iters× |
| ReAct | Ground every step in an external observation | serial | tool/retrieval observation | ~steps× |
| Tree of Thoughts | Search + backtrack over partial thoughts w/ value heuristic | tree | value heuristic | branching× (combinatorial) |
| Reflexion | Retry the whole task, learning verbally across attempts | cross-attempt | evaluator reward + verbal post-mortem | ~trials× |

The decisive variable across **all** rungs is the **quality of the feedback/evaluation signal**, not the cleverness of the topology.

---

## Mechanism — the actual control flow

Three related-but-distinct loops. Pick the one whose _error structure and feedback availability_ match (see Key Parameters → loop topology). All are in-context with frozen weights.

### (1) ReAct — intra-task tool loop (Thought → Action → Observation)

Grounds reasoning in an external environment, one step at a time.

```text
trajectory := few_shot_exemplars            # 1-6 demonstrations of the Thought/Action/Observation trace format
for step in 1..STEP_BUDGET:
    Thought  := M(prompt || trajectory)     # free-form reasoning; does NOT touch the environment.
                                            #   decomposes goal, tracks progress, extracts info from the
                                            #   last Observation, injects commonsense, handles exceptions
    Action   := M(prompt || trajectory)     # emits a tool call from the action space:
                                            #   search[query] | lookup[term] | finish[answer] | think (no-op)
    if Action == finish[answer]: return answer
    Observation := environment(Action)      # tool/API result fed back into the trajectory
    trajectory  += (Thought, Action, Observation)
# step budget hit without finish -> hand to the back-off ensemble (below)
```

- The **action space** is the tool set **plus an explicit `think`/no-op action** so reasoning is a first-class step (this is the design insight — reasoning is an action that emits no environment call).
- **Back-off ensemble** with CoT self-consistency, two directions:
  - `ReAct → CoT-SC`: run ReAct first; if it doesn't `finish` within the step budget (7 for HotpotQA, 5 for FEVER), fall back to CoT-SC (parametric knowledge).
  - `CoT-SC → ReAct`: run CoT-SC first; if the majority answer occurs **< n/2** times (internal knowledge not confident), escalate to ReAct (external grounding).

### (2) Self-Refine — in-place refine loop (one output, three role-prompts)

One frozen LLM plays Generate / Feedback / Refine via three different few-shot prompts.

```text
y0 := M(p_gen || x)                                     # initial output
history := []
for t in 0..MAX_ITERS:                                  # ~4
    fb_t := M(p_fb || x || y_t)                          # CRITIQUE: must localize the flaw AND instruct the fix
    if is_refinement_sufficient(fb_t):  return y_t       # feedback emits a stop marker, or output unchanged
    history += (y_t, fb_t)
    y_{t+1} := M(p_refine || x || y0 || history)         # REWRITE conditioned on the FULL output+feedback trail
return y_last
```

- The refine prompt is conditioned on the **full history** of prior outputs and feedback (`y0, fb0, y1, fb1, …`) so the model sees its mistake trail and does not repeat it.
- **Feedback contract is load-bearing:** specific + actionable — "sentiment is neutral because of phrase X; make it more positive" — **not** a bare scalar. A scalar critique gives the refine step nothing to act on.

### (3) Reflexion — cross-attempt retry loop with verbal memory (three models)

Restarts the _whole_ task between attempts, carrying verbal lessons.

```text
mem := []                                       # long-term episodic memory: verbal reflections
for trial in 1..MAX_TRIALS:                      # ~6-10
    tau := M_actor(task, mem)                    # ACTOR generates a full trajectory (often itself a ReAct/CoT agent)
    r   := M_eval(tau)                           # EVALUATOR scores the completed trajectory -> reward
    if pass(r) or trial == MAX_TRIALS:  return tau
    sr  := M_selfreflect(tau, r)                 # SELF-REFLECTION reads the failed trajectory + reward,
                                                #   writes a verbal post-mortem: what went wrong, what to change
    mem := slide(mem + [sr], window=1..3)        # keep only the last 1-3 reflections (bounded to fit context)
    # tau (short-term memory) is DISCARDED; only sr persists
```

- **Memory split is the whole point:** short-term = the current trajectory (reset every attempt); long-term = a **sliding window of the last 1–3 verbal reflections**, the only thing that crosses attempts.
- All three loops learn **textually, in the prompt** — never in weights.

---

## When it fits / when it fails

|  |  |
| --- | --- |
| **FITS** | Errors are **localizable** — feedback can point at a specific flaw and prescribe a fix (survey 2406.01297 finds self-correction works "even with in-context learning" on such tasks). |
|  | A **reliable feedback signal exists**: unit tests / compiler / runtime, a search API or KB (ReAct), a checker / constraint validator, a strong reward function, or a fine-tuned critic. **Single strongest predictor** of whether the loop helps. |
|  | Task needs **grounding in fresh external info** the model lacks (multi-hop QA, fact verification, tool use, web/file navigation) → **ReAct**: reasoning steers the search; observations correct hallucination. |
|  | Quality is **monotonic in revision** and the model is strong enough to give itself actionable feedback (GPT-4-class) → **Self-Refine** for drafting, rewriting, code improvement, constrained generation (~20% avg gain). |
|  | **Repeated end-to-end attempts are affordable** and a pass/fail or scalar reward is computable each attempt → **Reflexion** (code w/ self-generated tests: 91% HumanEval Pass@1 vs GPT-4's 80%; ALFWorld +22%; HotpotQA +20%). |
|  | A **usable state-evaluation heuristic** + benefit from backtracking → **Tree of Thoughts** (Game of 24: 4% CoT → 74%). |
|  | **Initial accuracy is LOW and difficulty is HIGH** — reflection's marginal value is largest exactly here (2405.06682). |
| **FAILS** | **Intrinsic self-correction with NO external feedback** on general reasoning: "no prior work shows reliable evidence of successful self-correction with in-context learning" (2406.01297); performance often **degrades** because models can't judge their own correctness (DeepMind 2310.01798). |
|  | The **stop decision secretly relies on a ground-truth ORACLE** to know when to stop revising — remove the oracle and the gains often vanish (the **oracle-label illusion**, the family's signature failure). |
|  | **Initial output already strong / easy task / high-performing model**: reflection makes **false-positive edits** to correct answers and net-degrades (diminishing-to-negative returns). |
|  | **Weak base model** (e.g. Vicuna): can't produce useful actionable feedback → Self-Refine/Reflexion stall or worsen. The loop inherits the ceiling of the model's self-evaluation ability. |
|  | **Vague / scalar-only feedback**: nothing for the refine step to act on → no-op or oscillation. |
|  | **Noisy/unreliable feedback** actively _misleads_ the loop into confident wrong "corrections" — **worse than no loop**. |
|  | **Degenerate loops**: ReAct repeats the same Thought→Action when a non-informative search "derails reasoning"; refine loops thrash between two outputs. |
|  | **Cost/latency blow-up**: serial iterations multiply tokens + wall-clock with no convergence guarantee; ToT branching multiplies calls combinatorially. |

**Confidence note:** the _positive_ benchmark numbers above are **empirically-supported** (named papers, reported tasks) but several were obtained under oracle-gated stopping — treat the _magnitude_ as an upper bound, not a deployment guarantee. The _failure_ findings (intrinsic self-correction degrades; oracle-gated gains evaporate) are the **strongest, most replicated** results in the family and should be treated as load-bearing constraints, not caveats.

---

## Key parameters (the knobs a builder sets) — highest-value section

Defaults are anchors from the canonical sources; deviations need a stated reason.

| Parameter | What it controls | Default | Rationale |
| --- | --- | --- | --- |
| **Feedback/evaluation source** | What signal closes each iteration: executable check (tests/compiler) · retrieval/tool observation · external/fine-tuned critic · self-critique | **Highest-trust the success criterion affords**, in that order. Self-critique is the _last_ resort, never the default | THE load-bearing knob. An external/verifiable signal is what flips the loop from harmful to helpful; self-critique alone is the documented failure case (2406.01297, 2310.01798). |
| **Loop topology** | Which template fits: ReAct (ground each step) · Self-Refine (revise one output in place) · Reflexion (restart the whole task w/ verbal lessons) · ToT (search + backtrack) | Pick by error structure: needs-tools/fresh-info → **ReAct**; one improvable artifact → **Self-Refine**; expensive whole-task retry w/ scalar reward → **Reflexion**; needs backtracking + a value fn → **ToT** | Mismatched topology wastes every iteration. Most coding/agentic work is ReAct-as-actor inside a Reflexion-or-evaluator-optimizer outer loop. |
| **Iteration / attempt budget** | Caps cost; prevents non-termination | **Self-Refine ≈ 4** refine iters · **Reflexion ≈ 6–10** trials · **ReAct step budget = 7 (HotpotQA) / 5 (FEVER)** before back-off | Gains **saturate fast — most benefit lands in iterations 1–2**. Set low; raising it past ~4 usually buys cost, not quality. |
| **Stop predicate** | How the loop knows it's done _without cheating_ | Evaluator-pass (Reflexion) · feedback emits "sufficient" / output unchanged (Self-Refine) · `finish` action (ReAct) · budget exhaustion. **Plus** a no-progress detector | **Must not depend on a ground-truth oracle** or the reported gains are illusory and won't reproduce. The oracle-label illusion lives here. |
| **Feedback specificity contract** | Whether critique is **localize + instruct** vs a bare score | Require localized + prescriptive feedback; reject scalar-only critique | The difference between a refine step that improves and one that no-ops/oscillates. Enforce it in the feedback prompt. |
| **Memory strategy** | What's carried across iterations | Self-Refine: **append full output+feedback history**. Reflexion: discard trajectory each attempt; keep a **sliding window of the last 1–3 reflections**. ReAct: full trajectory within a task, discarded at task end | Window size trades context cost against forgetting earlier lessons; too large dilutes the signal, too small forgets. (See Context Strategy below + `control-plane.md`.) |
| **Sampling for diversity** (ToT / Self-Consistency) | Temperature + N samples | Moderate temperature; N≈5–40 paths for Self-Consistency (task-dependent) | Self-Consistency/ToT depend on _diverse_ paths then aggregation; too low collapses diversity, too high injects noise. |
| **Back-off / ensemble policy** | When to trust the loop vs a one-shot answer | `ReAct ↔ CoT-SC` switching: fall back to CoT-SC over step budget; escalate to ReAct when CoT-SC majority **< n/2** | Hedges external grounding against parametric knowledge — encodes _when to skip the loop entirely_. Cheapest reliability win in the family. |
| **Action space / tool schema** (ReAct) | What the agent can observe and do; includes the mandatory `think`/no-op | Minimal, well-scoped tool set + an explicit reasoning action | Poorly scoped tools cause derailment and dead-end searches (a named failure mode). Reasoning must be a first-class action. |

---

## Termination / context / verification for this family

These instantiate the cross-cutting control plane — see `control-plane.md` for the general substrate; below is only what is _specific_ to this family.

**Termination (layered, enforced outside the model).** Fires on the first of:

1. **Goal-gate** — evaluator/verifier returns PASS (Reflexion: reward crosses threshold; code: all self-generated unit tests pass), **or** an explicit `finish`/answer action (ReAct), **or** the feedback step emits a "no further refinement needed" marker / two consecutive outputs are unchanged (Self-Refine `is_refinement_sufficient`).
2. **No-progress detector** — repeated-state / identical Thought→Action, or thrashing between two outputs. **Required** here because degenerate loops are a named failure mode (see below).
3. **Hard caps** — iteration/trial budget (Self-Refine ~4, Reflexion ~6–10) or ReAct step budget (7/5) → which **triggers CoT-SC back-off**, not silent continuation.
4. **Confidence gate / skip** — CoT-SC majority ≥ n/2 → accept and _skip the loop_ entirely; < n/2 → escalate to ReAct.

The non-negotiable: **the stop must not secretly depend on a ground-truth label.** That is the oracle-label illusion and it is the difference between a benchmark result and a deployable loop.

**Context strategy.** Accumulating in-context, frozen weights — the loops differ in _what_ they carry:

- **ReAct** — the growing Thought/Action/Observation trace stays in the prompt for the whole trajectory, discarded at task end (no cross-task learning).
- **Self-Refine** — the refine prompt concatenates the **full** history of every prior output + feedback; context grows **linearly per iteration** (a real budget cost — pair the low iteration cap with this).
- **Reflexion** — explicit split: short-term = current trajectory (reset each attempt), long-term = a bounded **1–3-reflection sliding window** (the only thing that persists).
- None update weights; all learning is textual and lives in the prompt. Name the window/budget — it trades token cost against forgetting.

**Verification gate (strongest → weakest).** The gate _is_ the loop's engine; its trustworthiness decides everything:

1. **Executable / symbolic check** — unit tests, compiler, interpreter, constraint validator, arithmetic check. Where the literature _agrees_ self-correction reliably works.
2. **External retrieval / observation** — ReAct's tool/API results ground and correct claims.
3. **Separate verifier / fine-tuned critic** (cross-model) — empirically stronger than self-critique, but doesn't prove a model fixes its _own_ errors.
4. **Self-evaluation by the same frozen LLM** (Self-Refine feedback, Reflexion's LLM evaluator, ToT's value prompt) — convenient but the documented failure point: models "cannot reliably evaluate the correctness of their own responses."

Mechanism-design rule (2406.01297): **never let the stop decision depend on a ground-truth oracle, and report feedback _quality_ directly, not just downstream task score** — a loop can look great only because an oracle told it when to halt. Calibrated practice: prefer an external/executable gate; if forced to self-critique, demand localized+actionable feedback, cap iterations low, keep-best-not-last, and **benchmark against single-pass + self-consistency + generate-and-rank before believing the lift**.

---

## Failure modes (each with its guard)

| Failure mode | Guard |
| --- | --- |
| **Unreliable self-evaluation** — the model judges a wrong answer correct (or vice versa); the gate fires on noise and the loop "corrects" toward error | Use an external/executable gate; if self-critique is unavoidable, label correctness **unverified** and lower confidence. Verifier ≥ generator in strength. |
| **Net-degradation on easy/already-correct items** — false-positive edits flip right answers wrong (the central 2310.01798 result) | **Keep-best-of** / accept-only-if-verifier-improves; **skip-loop-when-confident** (CoT-SC ≥ n/2 gate). Don't iterate a strong initial output. |
| **Oracle leakage** — gains exist only because ground-truth labels secretly gate the stop; remove the oracle and it underperforms one good pass | Make the stop predicate **oracle-free** by construction; test the loop with the oracle removed before trusting reported numbers. |
| **Vague feedback** — scalar/non-localized critique → no-op or oscillation | Enforce the **localize + instruct** feedback contract in the feedback prompt; reject scalar-only critiques. |
| **Degenerate ReAct loop** — repeated identical Thought/Action; a non-informative search "derails reasoning" | **No-progress / repeated-state detector** → break and trigger CoT-SC back-off; well-scope the action space. |
| **Diminishing returns** — nearly all benefit in iterations 1–2; further iters burn tokens for ~zero gain | Cap iterations **low** (Self-Refine ~4); add an early-stop-on-no-improvement check. |
| **Weak-model ceiling** — base model too weak to produce useful feedback → stall/worsen | Gate topology choice on model strength; for weak models prefer an executable gate or drop the loop for a single well-prompted pass. |
| **Cost/latency explosion** — serial refine multiplies tokens; ToT branching multiplies calls | Hard iteration/step/branch caps + a token/cost ceiling (control-plane budget); prefer ReAct/Self-Refine over ToT unless backtracking is essential. |
| **Reward hacking / spec-gaming the evaluator** — passes shallow tests without solving the task | Strengthen the gate (broaden tests, adversarial cases, hidden held-out checks); separate the judge from the actor. |
| **Memory dilution** — too-large reflection/history window buries the signal; too-small forgets | Bound the window (Reflexion 1–3); for Self-Refine, watch the linear-growth budget and summarize if needed. |
| **Mode confusion** — running intrinsic self-refine on a task that _has_ a cheap external verifier | Router/topology check: if an executable or retrieval gate exists, **use it** — don't leave the reliable signal on the table. |

---

## Composition — how it nests and wraps

This family is almost always the **inner** loop (`composition.md`):

- **As a Reflexion Actor** — the Actor `M_actor` is itself a ReAct or CoT agent, so ReAct nests directly inside Reflexion's cross-attempt retry. The patterns compose by construction.
- **As an evaluator-optimizer cycle** — Self-Refine _is_ generate→critique→revise with the critic in-prompt; promote the critic to a named, independent role (different model/family, or an executable check) and you have the evaluator-optimizer topology. The honest version of Self-Refine on correctness-critical work **is** that promotion. Score it with `rubric-evaluator-optimizer`.
- **As an orchestrator-worker leaf** — each worker an orchestrator dispatches typically _runs_ a ReAct loop against its sub-goal; the orchestrator provides the gate the worker reports against.
- **Wrapped by a planning front-end** — Plan-and-Solve / Plan-and-Execute can devise the plan, then a ReAct/Reflexion actor executes each step (cuts missing-step errors). The plan becomes part of this loop's verification.
- **With a CoT-SC back-off sibling** — the ReAct↔CoT-SC ensemble is the family's own built-in composition: a one-shot parallel hedge alongside the serial loop.

When this family is the _only_ topology, the blueprint must still name **which** of the three loops, the gate, the layered stop, and the memory window — a bare "use ReAct" is advice, not a blueprint.

**Scoring.** This family is scored by **`rubric-evaluator-optimizer`** (its selectors include `reflexion`, `react`, `reason-act-reflect`, `self-refine`, `generate-critique-revise`, `iterative self-refinement`) plus the cross-cutting `rubric-loop-control` and `rubric-loop-selection`. The rubric's gates target this family's signature failures: oracle-independence of the stop, gate soundness, judge independence, and termination/budget.

---

## Primary sources

| Source | URL | Load-bearing for |
| --- | --- | --- |
| **ReAct: Synergizing Reasoning and Acting in Language Models** — Yao et al., ICLR 2023 | <https://arxiv.org/abs/2210.03629> | Thought→Action→Observation interleaving, reasoning-as-action, few-shot trajectory prompting, the ReAct↔CoT-SC back-off (step budgets 7/5, n/2 confidence gate). |
| **Reflexion: Language Agents with Verbal Reinforcement Learning** — Shinn et al., NeurIPS 2023 | <https://arxiv.org/abs/2303.11366> | Actor/Evaluator/Self-Reflection architecture, Algorithm 1 cross-attempt retry, short-term-trajectory vs long-term-1–3-reflection memory, 91% HumanEval Pass@1 (vs GPT-4 80%). |
| **Self-Refine: Iterative Refinement with Self-Feedback** — Madaan et al., NeurIPS 2023 | <https://arxiv.org/abs/2303.17651> | Single-LLM Generate/Feedback/Refine loop, full-history concatenation, the localize+instruct feedback contract, `is_refinement_sufficient`, ~20% gain, the weak-model (Vicuna) limit. |
| **When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction** — Kamoi et al., TACL 2024 | <https://arxiv.org/abs/2406.01297> | The decisive mechanism-design source: intrinsic vs external/oracle/cross-model taxonomy, the "unreliable except on verifiable/decomposable tasks" finding, the no-oracle-stop + report-feedback-quality checklist. |
| **Large Language Models Cannot Self-Correct Reasoning Yet** — Huang et al., DeepMind, ICLR 2024 | <https://arxiv.org/abs/2310.01798> | Primary evidence that intrinsic self-correction of reasoning _degrades_ performance — the core caveat gating when these loops should be used. |
| **Tree of Thoughts: Deliberate Problem Solving with LLMs** — Yao et al., NeurIPS 2023 | <https://arxiv.org/abs/2305.10601> | The exploration/backtrack variant (search tree + value heuristic; Game of 24: 4%→74%) builders pick when backtracking + a usable value function exist. |
| **Self-Consistency Improves Chain of Thought Reasoning** — Wang et al., ICLR 2023 | <https://arxiv.org/abs/2203.11171> | The cheap parallel baseline every iterative loop must be benchmarked against, and ReAct's back-off partner (GSM8K +17.9%). |
| **Self-Reflection in LLM Agents: Effects on Problem-Solving Performance** — Renze & Guven, 2024 | <https://arxiv.org/abs/2405.06682> | When reflection helps vs hurts: best when initial accuracy is low + difficulty high; diminishing-to-negative on easy prompts / strong base models. |
| **Plan-and-Solve Prompting** — Wang et al., ACL 2023 | <https://arxiv.org/abs/2305.04091> | The lightweight zero-shot planning front-end (devise-a-plan-then-execute) that composes with ReAct/Reflexion actors to cut missing-step errors. |
