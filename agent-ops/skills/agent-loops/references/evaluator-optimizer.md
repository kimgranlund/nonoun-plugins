# Evaluator-Optimizer (generate → critique → revise, LLM-as-judge gate)

> One generator produces a candidate; one evaluator scores it against explicit criteria and emits actionable feedback; the candidate is revised in a loop until the judge says PASS or a budget is hit. Powerful exactly when the criteria are crisp and the judge's verdict is trustworthy — and dangerous exactly when it is not.

## 1. Where it sits in the taxonomy

This is the **verify-and-revise sub-family of single-agent iterative loops**: a generator paired with an internal verification gate that decides "good enough yet?" each round. It is the topology the router selects when _"clear eval criteria + iterative refinement adds measurable value."_

It sits **directly upstream of multi-agent orchestration** because the evaluator can be a separate agent or model — so this family is the natural hinge between single-agent loops and `composition.md`'s nested topologies. The same generate→critique→revise spine appears as:

- the **inner refinement step** of a per-file Ralph or plan-execute loop (`composition.md`: "evaluator-in-orchestrator", and the per-file inner evaluator-optimizer in `examples/example-a-react-to-hooks.md`),
- the **reflection arm** of ReAct/Reflexion (`react-reflexion.md` shares this rubric — `rubric-evaluator-optimizer`),
- the **adversarial-verify sub-step** that an orchestrator-workers or auto-research run drops in before synthesis (`composition.md`: adversarial-verify as a droppable sub-step).

The defining feature — and the whole ballgame — is **the gate**. Everything below is about making that gate trustworthy and the loop bounded.

## 2. Mechanism — the actual control flow

Two roles in a loop: **GENERATOR (G)** and **EVALUATOR / JUDGE (E)**. Canonical control flow (Anthropic cookbook `evaluator_optimizer.ipynb`):

```text
memory = []                       # accumulating attempts + critiques
context = ""                      # empty on round 0
best = None                       # for return-best-not-last

loop (round = 0, 1, 2, …):
  1. result = G(generator_prompt, task, context)
         # generator is told: "reflect on feedback from previous generations to improve"
  2. verdict, feedback = E(evaluator_prompt, result, task)
         # E returns a structured verdict + critique, e.g.
         #   <evaluation>PASS | NEEDS_IMPROVEMENT | FAIL</evaluation>
         #   <feedback>what to fix and why</feedback>
  3. track best (by gate score) so far
  4. if verdict == "PASS":            return result        # hard stop on the parsed token
  5. if any hard cap hit (max rounds / token / wall-clock): return best  # NOT last
  6. else:
       memory.append((result, feedback))
       context = "Previous attempts: [...] \n Feedback: {feedback}"
       continue                       # loop back to step 1
```

It is a `while True` gated on a **parsed verdict token**, with feedback threaded forward as accumulating context so the generator avoids re-making rejected mistakes.

**Self-Refine (Madaan et al., 2023) is the single-model instantiation:** the _same_ LLM plays generator, feedback-provider, and refiner. Its loop is `generate → FEEDBACK(specific, actionable) → REFINE`, repeated until a `stop(fb_t, t)` signal fires — the feedback itself can emit "no further changes needed" — _or_ a hard cap (max 4 iterations in their experiments). No training / RL required. The same-model variant is cheaper but inherits self-preference bias (§6).

**The judge's "bar" can be implemented four ways, on a trust ladder** (this is the single most important design choice — §4 and §5):

| Rung | Gate implementation | Trust | What PASS means |
| --- | --- | --- | --- |
| 1 (verification) | **Executable / environmental ground truth** — tests pass, code compiles, type-checks, lint clean, schema/contract validates, eval metric ≥ target, tool/env returns success | Highest | PASS means PASS. Anthropic: agents should _"gain 'ground truth' from the environment at each step."_ |
| 2 (estimation) | **Reference-based LLM-judge** — compare candidate to a gold answer/rubric | Good where a reference exists | Estimated against a known target |
| 3 (estimation) | **Reference-free rubric judge** — LLM scores explicit criteria (correctness, complexity, style, …) | Inherits judge bias | An estimate; subject to the 12 CALM biases |
| 4 (estimation) | **Self-judge** — same model, no reference | Weakest | On reasoning it _degrades_ accuracy (§3) |

The skill's core teaching: **prefer the highest available rung; never let an unaudited LLM-judge be the sole gate on correctness-critical work; always reserve at least one executable check when one is obtainable.**

## 3. When it fits / when it fails

### When it FITS

- Clear, articulable evaluation criteria exist **AND** iterative refinement demonstrably improves the output. Anthropic's two litmus tests: _"LLM responses demonstrably improve when a human articulates their feedback"_ and _"the LLM can provide such feedback."_ (empirically-supported)
- A **cheap, trustworthy verification oracle** is available — unit/integration tests, compiler/linter, type checker, schema/JSON validator, eval harness, retrieval-grounded fact check, or a tool/env returning success/failure. This is the _strong_ case: the gate is real, not estimated.
- **Open-ended generation** where first-draft quality is reliably below bar and the gap is legible: literary/technical translation (Anthropic's named example), long-form writing, code optimization, constrained generation, style/tone rewriting, complex multi-round search.
- Tasks where Self-Refine showed large gains because feedback is concrete and verifiable: Constrained Generation (+30), Dialogue Response (~+49 on GPT-4), Sentiment/Style Reversal (~+32), Acronym Generation (~+26), Code Readability (~+29). (empirically-supported)
- You can **afford the token/latency multiple** (each round ≈ 1 generate + 1 evaluate; N rounds ≈ 2N calls) and the task is not latency-critical.

### When it FAILS

- **Reasoning correctness with NO external verifier** — the headline negative result. Huang et al. 2024 (DeepMind), _"LLMs Cannot Self-Correct Reasoning Yet"_: intrinsic self-correction (judge = the model's own opinion, no ground truth) does not help and often **degrades**. GSM8K GPT-3.5: 75.9% → 75.1% (r1) → 74.7% (r2); CommonSenseQA: 75.8% → 38.1% → 41.8% (catastrophic — the model talks itself out of correct answers); HotpotQA: 26.0% → 25.0% → 25.0%. (empirically-supported)
- The **oracle-label illusion** — prior self-correction wins were inflated because the loop used ground-truth labels to decide _when to stop_ revising (only revise answers known wrong). Remove the oracle and the gains vanish; a random-relabel baseline matched self-correction, proving the lift came from the oracle, not the critique. (This is the same illusion `router.md` and SKILL.md First Principle 5 warn against: the _stop_ decision must not secretly depend on a ground-truth oracle the deployment won't have.)
- **Self-judging bias** — a model rates its own output higher than humans do. _"LLM Evaluators Recognize and Favor Their Own Generations"_ (2024) shows a causal, near-linear link between a model's ability to _recognize_ its own text and the strength of its self-preference. The judge is not neutral. (empirically-supported)
- **Confidently-wrong judge** — passes bad outputs (terminates early on a false PASS) or fails good ones (oscillates / over-edits a correct answer into a worse one — the CommonSenseQA collapse).
- **Reward-hacking the rubric** — the generator satisfies the _letter_ of the criteria (length, hedging, citations, sentiment, CoT formatting) rather than the substance, exploiting the verbosity/authority/sentiment/CoT biases catalogued in _"Justice or Prejudice?"_ (Park et al., CALM; 12 biases). (empirically-supported)
- **Debate-as-substitute-for-a-real-verifier** — Huang et al. found multi-agent debate only marginally beats self-consistency at equal response count (GSM8K 83.2% debate vs 85.3% self-consistency); the gain is from sampling multiple answers, not from critique. (If you reach for a panel of judges to dodge a missing oracle, see `debate-ensemble.md` — it's the same trap.)
- **Subjective/aesthetic criteria**, or when the first draft already meets the bar (wasted cost), or under strict token/latency budgets — Anthropic's stated non-fits.

## 4. Key parameters (the knobs a builder sets)

This is the highest-value section. Defaults are the starting point; **deviations need a reason** and go in the blueprint's PARAMETERS field.

| Parameter | What it controls | Default | Rationale |
| --- | --- | --- | --- |
| **Gate type** (rung 1–4 of §2) | Whether the loop is _sound_ at all | **Highest rung the success criterion affords**; for any correctness-critical task, reserve ≥1 executable check (tests/compiler/schema/eval) | This single choice determines soundness. Executable ground truth makes PASS trustworthy; an LLM-judge makes it an estimate inheriting self-preference + the 12 CALM biases. LLM-as-judge is a _fallback_, never a default. Scored by `rubric-evaluator-optimizer` **EO1-gate-soundness** [gate]. |
| **Generator/evaluator separation** | Whether the judge is independent of the generator | **Different model/family** (or a tool/validator) as evaluator; if same model, at minimum a **blinded, fresh-context** judge | Same-model self-judging is empirically biased upward (self-recognition→self-preference) and on pure reasoning _degrades_ accuracy. Cross-family reduces self-preference and shortcut bias; same-family inherits family bias. Scored by **EO2-oracle-independence** [gate] and **EO3-judge-independence** [review]. |
| **Rubric / criteria spec** in the evaluator prompt | How actionable the feedback is | **Explicit + decomposed** into separately-scored sub-dimensions (e.g. correctness, complexity, style each judged on its own), rubric-anchored with calibration exemplars | Vague criteria → generic feedback. Self-Refine's ablation: specific/actionable feedback beats generic (Sentiment Reversal 43.2% vs 31.2%), and "no feedback" collapses to ~0%. Scored by **EO4-feedback-actionability** [review]. |
| **Max iterations / budget cap** | Runaway cost + the degradation spiral | **Cap = 3** (Self-Refine capped at 4; most gains land in rounds 1–2); **on cap, return BEST-so-far, not LAST** | Diminishing returns hit fast. A hard cap prevents oscillation, runaway cost, and the spiral where extra rounds make a correct answer worse. The return-best policy is non-optional. Scored by **EO5-termination-budget** [gate]. |
| **Stop condition design** | How the loop knows it's done | **Pass the gate AND output stabilized, OR cap reached** | A parsed PASS token (cookbook) is crisp but _trusts the judge_; a numeric score≥threshold needs a calibrated judge; a "feedback says no changes" / output-stabilized signal (Self-Refine `stop()`) guards against over-editing. The conjunction (gate ∧ stabilized) ∨ cap is the most robust. Layering detailed in §5. |
| **Context / memory carry-forward** | Convergence vs token growth vs anchoring | **Generator keeps full attempt+critique history; judge runs stateless/fresh each round** | Full history on the generator prevents re-introducing rejected mistakes; isolating the judge (no edit history) keeps the gate independent and avoids _refinement-aware inflation_ (knowing the edit history inflates the score). Latest-feedback-only is cheaper but loops more. Detailed in §5. |
| **Anti-bias controls** on the judge | Whether the gate is real vs security theater | **On by default for LLM-judge gates**: length normalization + candidate anonymization + (for pairwise) position-swap-and-require-agreement; rubric-anchored few-shot; meta-judge/panel where stakes warrant | Without these the generator reward-hacks and the verdict is unreliable. These are the difference between a real gate and theater. Scored by **EO7-judge-bias** [review]. |
| **No-improvement / regression guard** | Prevents the degradation spiral | **Stop after K=2 rounds with no gate-score improvement; never accept a revision that scores below the best seen** | Extra rounds can talk a correct answer into a wrong one (CommonSenseQA 75.8%→38.1%). Best-of-N retention + monotone-improvement check make regression impossible. Scored by **EO6-regression** [review]. |
| **Judge calibration / audit** | Whether the judge is _trusted on evidence_ | **Sample-validate the LLM-judge against human or executable labels before trusting it as the gate; record the agreement rate** | An unaudited LLM-judge is an assumption, not a gate. A known agreement rate is what licenses (rungs 2–4) at all. |
| **Loop-vs-one-shot justification** | Whether to run this loop _at all_ | **Must hold: first-draft below bar AND refinement demonstrably helps AND latency budget permits** | The router's first question. If the first draft already meets the bar, the 2N-call loop is wasted spend. Scored by **EO8-loop-vs-oneshot** [review] and `rubric-loop-selection` S1-simplest-sufficient. |

## 5. Termination / context / verification (this family's instantiation of the control plane)

The cross-cutting mechanics are defined once in `control-plane.md`; here is how _this_ family instantiates them — do not re-derive them.

**Termination (layered, enforced outside the model — per `control-plane.md`).** Stack these; no single one is sufficient:

- **goal-gate (intended success exit):** judge emits PASS / score ≥ threshold, OR the executable oracle is satisfied (tests green, type-check/lint clean, schema validates, eval metric ≥ target). Only as trustworthy as its rung (§2).
- **output-stabilized:** the revision is (near-)identical to the prior round, or the feedback signals "no further changes needed" (Self-Refine `stop(fb_t, t)`). Guards against over-editing.
- **no-improvement / regression guard:** gate score fails to improve (or drops) for K consecutive rounds → stop and **return the best-scoring attempt seen, not the last**.
- **anti-oscillation guard:** a candidate repeats a previously-rejected state → break (prevents A→B→A cycles).
- **hard caps:** max-iterations (default 3; typical 2–4) + token / wall-clock budget.

**Context strategy (a point on the fresh↔accumulating axis — per `control-plane.md`): accumulating _within_ a single optimization episode, fresh _across_ episodes.** The reference implementation maintains a `memory` list of prior attempts and appends each round's critique, building a running `"Previous attempts: … Feedback: …"` fed to the next generate call. Trade-off: full-history carry-forward improves convergence and stops regressions but inflates tokens and can anchor/over-constrain the generator; latest-feedback-only is cheaper but loops more. The robust split: **the generator keeps the memory; the judge is isolated** — fresh context each round, no edit history, ideally a different model/sub-agent — to keep the gate independent (showing the judge the edit history causes refinement-aware inflation). External state to name in the blueprint: the attempt/critique ledger (the `memory` list), and, if the oracle is executable, the test/eval harness as the durable source of ground truth.

**Verification gate (this family's defining feature).** See the trust ladder in §2. The gate's trustworthiness _is_ the whole technique. Hardening for rungs 2–4: separate the judge model from the generator; anchor the rubric with few-shot exemplars; swap-positions-and-require-agreement for pairwise; normalize for length; anonymize candidates; add a meta-judge or panel/jury; periodically validate verdicts against human or executable labels. **Verifier ≥ generator** in strength (SKILL.md First Principle 3). The skill's invariant: never let an unaudited LLM-judge be the sole gate on correctness-critical work, and never let the _stop_ decision secretly depend on a ground-truth oracle the deployment won't have (the oracle-label illusion).

## 6. Failure modes (each with its guard)

| Failure mode | What goes wrong | Guard |
| --- | --- | --- |
| **Oracle-label illusion** | Gains are an artifact of using ground-truth to decide _when to stop_ revising; remove the oracle and they vanish (Huang et al.). | Make the stop decision depend only on signals available at deployment; if the only real signal is an oracle, the oracle _is_ the gate (rung 1) — own that, don't smuggle it into the stop logic. |
| **Degradation-by-revision** | Extra rounds talk a correct answer into a wrong one (CommonSenseQA 75.8% → 38.1% after one self-correction round). | Best-of-N retention + monotone-improvement check (EO6); return-best-not-last; output-stabilization stop; low cap (3). |
| **Self-preference / self-judging bias** | Model rates its own output higher than humans do; recognition of own text causally drives it. | Separate judge model/family, or an executable check; blind/anonymize candidates (EO2/EO3). |
| **Confidently-wrong judge** | False PASS terminates early on a bad output; false FAIL discards a good one. | Calibrate + audit the judge against ground truth (known agreement rate) before trusting it; reserve an executable check; meta-judge on high stakes. |
| **Reward-hacking the rubric** | Generator games length, hedging, citations, sentiment, or CoT formatting to satisfy the judge's biases instead of the task. | Anti-bias controls (length-norm, anonymization, position-swap); a substance-vs-letter check; robust criteria (EO7, and the reward-hacking-resistance teaching). |
| **Oscillation / non-convergence** | A→B→A loops with no monotone improvement when there's no real gate. | Anti-oscillation guard (break on repeated rejected state) + no-improvement guard (stop after K flat rounds). |
| **Return-last-not-best** | Loop returns the final (possibly regressed) candidate instead of the best-scoring one. | Track `best` by gate score every round; return it on every non-PASS exit (the default in §2's pseudocode). |
| **Sycophantic feedback / critique collapse** | Same-model evaluator emits bland "looks good, minor tweaks"; generic feedback ≈ no feedback ≈ 0% lift. | Decomposed, rubric-anchored, fix-oriented evaluator prompt (EO4); separate/stronger judge. |
| **Refinement-aware inflation** | Showing the judge the edit history makes it score later drafts higher regardless of quality. | Isolate the judge — fresh context, no attempt history (the context split in §5). |
| **Cost/latency blow-up** | 2N model calls with no cap; returns past ~2–3 rounds wasted as spend. | Hard iteration + token/cost ceiling (EO5); justify the loop over one-shot first (EO8). |
| **Family bias in judge panels** | A jury of same-provider judges agrees with each other and the same-provider generator, manufacturing false consensus. | Cross-family panel composition; see `debate-ensemble.md` for jury construction (DE2-diversity-authenticity). |

## 7. Composition — how it nests and wraps other layers

Per `composition.md`, evaluator-optimizer is both a top-level topology and a **reusable sub-step**:

- **As the inner refinement of an outer loop.** Wrapped inside a per-file Ralph / plan-execute / orchestrator-workers loop, it is the "refine until the gate passes" body for one unit of work — e.g. the per-file inner evaluator-optimizer in `examples/example-a-react-to-hooks.md` (iterative + automated oracle + brownfield → per-file loop + inner evaluator-optimizer). The outer loop owns iteration over units; this owns "good enough yet?" for one unit.
- **As the adversarial-verify sub-step before synthesis.** An orchestrator-workers or auto-research run can drop an evaluator pass between worker output and synthesis (`composition.md`: adversarial-verify as a droppable sub-step; `examples/example-b-auth-vendor.md` constructs exactly such a verify gate). Here the evaluator is necessarily a _separate_ agent — the cleanest form of judge independence.
- **As the reflection arm of ReAct/Reflexion.** `react-reflexion.md` is the same generate→critique→revise spine with tool-grounded observations as (part of) the feedback, and shares this rubric (`rubric-evaluator-optimizer`).
- **What it wraps:** a single augmented LLM call as the generator (and, on rung 1, a tool/test-runner as the evaluator). When the _evaluator_ is itself a multi-judge panel, you have composed in `debate-ensemble.md` (LLM-as-a-jury gate) — score both rubrics.

When composing, name the nesting explicitly in the blueprint (WIRING field) and load every matched per-family rubric per `rubrics/rubric-manifest.json`'s `expand: dependencies` rule.

## 8. Primary sources

| Title | URL |
| --- | --- |
| Building Effective Agents — Anthropic Engineering (Evaluator-optimizer workflow) | <https://www.anthropic.com/engineering/building-effective-agents> |
| Anthropic Cookbook — `patterns/agents/evaluator_optimizer.ipynb` (reference implementation: the `while True` loop, PASS/NEEDS_IMPROVEMENT/FAIL verdict, parsed-PASS stop, memory accumulation, G/E prompt templates) | <https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/evaluator_optimizer.ipynb> |
| Self-Refine: Iterative Refinement with Self-Feedback — Madaan et al., 2023 (positive evidence; max-4 cap; `stop()`; specific>generic>none ablation; math-reasoning null result) | <https://arxiv.org/abs/2303.17651> |
| Large Language Models Cannot Self-Correct Reasoning Yet — Huang et al., DeepMind, 2024 (oracle-label illusion; intrinsic self-correction degrades; debate≈self-consistency) | <https://arxiv.org/abs/2310.01798> |
| Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge — Park/Ye et al., 2024 (12-bias taxonomy; CALM attack-and-detect; mitigations) | <https://arxiv.org/html/2410.02736v1> |
| LLM Evaluators Recognize and Favor Their Own Generations — Panickssery/Wataoka et al., 2024 (causal self-recognition→self-preference link) | <https://arxiv.org/abs/2404.13076> |

---

**Scoring:** this family is scored by `rubrics/rubric-evaluator-optimizer.md` (gates EO1-gate-soundness, EO2-oracle-independence, EO5-termination-budget; review EO3-judge-independence, EO4-feedback-actionability, EO6-regression, EO7-judge-bias, EO8-loop-vs-oneshot), plus the cross-cutting `rubrics/rubric-loop-control.md`, `rubrics/rubric-loop-selection.md`, and `rubrics/rubric-plan-quality.md` per `rubrics/rubric-manifest.json`.
