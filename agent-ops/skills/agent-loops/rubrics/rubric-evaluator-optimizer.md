# Rubric — Evaluator-Optimizer

Score a **generate → critique → revise** plan — and its single-model variants **Self-Refine** and **Reflexion** — against the gate-trust and bounding discipline in `../references/evaluator-optimizer.md`. Use in **EVALUATE mode** to score an existing loop/plan/transcript, and as the acceptance bar in **PLAN/COMPOSE mode** before a blueprint emits this family.

**What it scores.** Whether the loop's **verification gate is trustworthy** and the loop is **bounded** — i.e. does the stop condition rest on the strongest gate the success criterion affords, is the judge independent of the generator, is the stop free of a smuggled ground-truth oracle, and does the loop halt with the best-so-far rather than overbake. The gate **is** the technique; everything here makes that gate real and the loop finite. This rubric also covers ReAct/Reflexion (its reflection arm is the same spine) and the in-place Self-Refine variant — `../references/react-reflexion.md` shares it.

**Band: per-family.** Load only when the plan composes an evaluator-optimizer / generate-critique-revise / self-refine / reflexion / ReAct / LLM-as-judge-gate / iterative-self-refinement mechanism (manifest `selectors`). When this loop is nested as the inner refinement of a Ralph/plan-execute/orchestrator loop, or dropped in as an adversarial-verify sub-step, score it here in addition to the outer family's rubric (`../references/composition.md`).

**Dependency.** This rubric **depends on `rubric-loop-control`** (manifest `dependencies`). A plan emitting this family must clear `rubric-loop-control`'s gates too (termination stack C1, budget C2, verification-gate strength C3, durability C7) — they are not restated here; they always also apply. EO5 below is this family's _instantiation_ of C1/C2, not a replacement.

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate **blocks SHIP**; it is not a matter of opinion. Cross-cutting gates are backed by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`; per-family gates (EO1/EO2/EO5) are **[mech-partial]** — the criterion is structural but no automated script enforces it; agent judgment applies.
- **[mech-partial]** — mechanically checkable criterion, no automated script — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment; score **1–5**. Reviewer cites evidence from the plan/transcript and rates against the anchors.

**Ship rule.** This family ships when **every [gate] passes AND no [review] dimension < 3**, _and_ the `rubric-loop-control` gates it depends on also pass. A composed plan must clear the **union** of all loaded rubrics' gates. Record evidence (the parameter value, the stop-condition line, the judge model, the transcript turn) for **every** finding — a finding without a citation is an opinion.

**Calibration caveat.** This rubric is **draft (v0.1, 0 calibration samples)**. Treat every score as **directional, not authoritative**, until the ROADMAP v0.2 calibration set exists. The [gate] dimensions are the only mechanically verifiable layer; [review] anchors are practitioner-folklore-plus-citations, not a tuned scale.

---

## The three backbone gates

These are the load-bearing checks for this family — the gate-trust trio. Run them first; an evaluator-optimizer plan that fails any of the three is unsound regardless of polish. (Grounded in `../references/evaluator-optimizer.md` §2 trust ladder, §5 termination, §6 failure modes.)

### EO1 [gate / mech-partial] — Gate soundness

**Criterion.** The stop condition rests on an **executable/environmental oracle wherever one is obtainable** (tests pass, compiles, type-checks, lint clean, schema/contract validates, eval metric ≥ target, tool/env returns success — rung 1 of the §2 trust ladder), **not** an unaudited LLM-judge verdict. A correctness-critical task with **no real verifier** scores low: intrinsic self-correction on reasoning _degrades_ output (Huang et al. 2024, DeepMind: GSM8K 75.9%→75.1%→74.7%; CommonSenseQA 75.8%→38.1%). An LLM-judge is a **fallback**, never a default. (empirically-supported)

**TEST (binary).** Identify the gate's implementation and place it on the rung ladder. **PASS** iff: (a) the gate is rung 1 (executable/environmental) — automatic pass; OR (b) the gate is rung 2–4 (LLM-judge) AND the task is genuinely non-verifiable (no executable oracle obtainable — open-ended generation, style/translation) AND ≥1 executable check is still reserved where any sub-property _is_ checkable. **FAIL** iff: a correctness-critical task is gated by an LLM-judge while an executable oracle was obtainable but not used; OR the plan names "the agent will know when it's right" / a bare self-grade as the sole gate on correctness. Cite the gate rung and the success criterion.

### EO2 [gate / mech-partial] — Oracle-independence of the stop

**Criterion.** Termination does **NOT** secretly depend on a ground-truth label the deployment won't have — the **oracle-label illusion** (`../references/evaluator-optimizer.md` §6; Huang et al. 2024). Prior self-correction "wins" were inflated because the loop used ground-truth to decide _when to stop_ revising (only revise answers known wrong); a random-relabel baseline matched it, proving the lift came from the oracle, not the critique. Gains claimed by the plan must **reproduce at deployment**, on signals available then. (empirically-supported)

**TEST (binary).** Trace the _stop_ decision's inputs. **PASS** iff every signal the stop condition reads (gate verdict, score threshold, no-change detector) is computable from data present **at deployment time**, not from a held-out label. **FAIL** iff the loop "revises only items known to be wrong," consults a gold label to decide whether to continue, or otherwise routes a ground-truth signal into the stop logic while presenting the gains as if the critique earned them. (If the only real signal genuinely _is_ an oracle, that oracle must be the **gate** itself, rung 1 — own it via EO1, don't smuggle it into the stop.) Cite the stop-condition inputs.

### EO5 [gate / mech-partial] — Termination & budget discipline

**Criterion.** The loop is provably finite and degradation-safe (`../references/evaluator-optimizer.md` §4–§5; this family's instantiation of `rubric-loop-control` C1/C2). It carries **all four**: (1) a **hard iteration cap** (default 3; Self-Refine capped at 4; most gains land in rounds 1–2) plus a **token/wall-clock ceiling**; (2) a **no-improvement guard** (stop after K≈2 flat rounds); (3) an **anti-oscillation guard** (break on a repeated previously-rejected state, preventing A→B→A); (4) **return BEST-so-far, not LAST** on every non-PASS exit. The return-best policy is **non-optional** — extra rounds can talk a correct answer into a wrong one.

**TEST (presence — all four required).** Confirm each is specified with a concrete value/mechanism: max-iterations is a number (not "until done") AND a token/cost ceiling exists; the no-improvement K is a number; the anti-oscillation break is described; the exit path returns the best-scoring attempt (tracked every round), not the final candidate. **FAIL** if any of the four is missing or left as "tune as needed" — in particular, a plan that returns the **last** candidate, or whose only bound is `max_iterations`, fails. Cite each parameter value (or its absence).

---

## Design dimensions

### EO3 [review] — Judge independence

**Criterion.** The evaluator is **separated from the generator** — a different model/family, or a tool/validator, or at minimum a **blinded, fresh-context** judge (`../references/evaluator-optimizer.md` §4, §5). Same-model self-judging is empirically biased upward: self-recognition causally drives self-preference (Panickssery/Wataoka et al. 2024, _LLM Evaluators Recognize and Favor Their Own Generations_), and on pure reasoning it _degrades_ accuracy. Penalize same-model self-judging on correctness-critical or reasoning work. The judge should also be **isolated** (no edit/attempt history) to avoid refinement-aware inflation. (empirically-supported)

**Evidence to cite.** The generator model/family, the evaluator model/family, whether the judge sees the attempt history, and the task type (reasoning/correctness vs open-ended generation).

**Score.** 1 = same model self-judges its own reasoning output with full edit history visible (maximal self-preference + refinement-aware inflation). 3 = same family but a **blinded, fresh-context** judge (no history), or an explicitly-acknowledged self-judge confined to a non-reasoning, low-stakes property. 5 = a **different model/family** judge, OR a tool/executable validator, run **stateless** each round with candidates anonymized — gate independence is structural, not promised.

### EO4 [review] — Feedback actionability

**Criterion.** Critique is **localized to the flaw AND prescriptive of a fix** — the localize+instruct contract — not a bare scalar score or a sycophantic "looks good, minor tweaks" (`../references/evaluator-optimizer.md` §4, §6). Self-Refine's ablation: specific/actionable feedback beats generic (Sentiment Reversal 43.2% vs 31.2%), and "no feedback" collapses to ~0% lift. The evaluator prompt should be **decomposed** into separately-scored sub-dimensions (e.g. correctness, complexity, style judged on their own), rubric-anchored with calibration exemplars. (empirically-supported)

**Evidence to cite.** The evaluator prompt / feedback schema; whether feedback names _where_ and _how to fix_; whether criteria are decomposed; a sample critique from the transcript if available.

**Score.** 1 = a bare scalar/verdict with no fix guidance, or bland generic praise (≈ no feedback). 3 = feedback identifies the flaw but is thin on the fix, or criteria are monolithic rather than decomposed. 5 = critique localizes each flaw and prescribes a concrete fix, against decomposed rubric-anchored sub-dimensions with exemplars — the generator can act on it without guessing.

### EO6 [review] — Regression protection

**Criterion.** The loop cannot make a correct answer worse (`../references/evaluator-optimizer.md` §4, §6: degradation-by-revision — CommonSenseQA 75.8%→38.1% after one self-correction round). Carries **best-of-N retention** (never accept a revision scoring below the best seen) AND/OR a **monotone-improvement check** AND/OR an **output-stabilization stop** (Self-Refine `stop(fb_t, t)` — feedback says "no further changes needed," or the revision is near-identical to the prior round). These guard the spiral where extra rounds degrade a passing answer. (empirically-supported)

**Evidence to cite.** The acceptance rule for a revision; whether a best-by-gate-score is tracked; the output-stabilization / monotone-improvement signal, if any.

**Score.** 1 = revisions are accepted unconditionally; a later round can silently overwrite a better earlier one. 3 = one guard present (e.g. a no-improvement stop) but no best-of-N retention, so a single regressing round between two flat rounds can still slip through. 5 = best-of-N retention (monotone, revision-below-best is rejected) **plus** an output-stabilization or no-change stop — regression is structurally impossible.

### EO7 [review] — Judge-bias mitigation

**Criterion.** Where an LLM-judge gates, its biases are actively controlled, and the generator is prevented from **reward-hacking the rubric** (`../references/evaluator-optimizer.md` §4, §6; Park/Ye et al. 2024, _Justice or Prejudice?_ — the 12 CALM biases). Hardening: **position-swap-and-require-agreement** (pairwise), **length normalization**, candidate **anonymization**, refinement/edit **history hidden from the judge**, rubric-anchored few-shot, meta-judge/panel where stakes warrant. The generator must not be able to satisfy the _letter_ (length, hedging, citations, sentiment, CoT formatting) instead of the substance. Without these, the verdict is security theater. (empirically-supported)

**Evidence to cite.** The named anti-bias controls (or their absence); whether the criteria are gameable by surface features; for pairwise judging, whether position is swapped.

**Score.** 1 = a raw LLM-judge gate with no controls; criteria are trivially gameable by length/format/citations (reward-hacking unguarded). 3 = some controls (e.g. a rubric + anonymization) but a known gap — e.g. no length normalization, or pairwise position not swapped. 5 = the relevant control set for the gate shape is present (length-norm + anonymization + position-swap-with-agreement + history-hidden, panel/meta-judge on high stakes) AND a substance-vs-letter check resists reward-hacking.

### EO8 [review] — Loop-vs-one-shot justification

**Criterion.** Running this loop **at all** is warranted, and the choice is benchmarked against cheaper baselines (`../references/evaluator-optimizer.md` §3–§4; Anthropic's two litmus tests). The triad must hold: **first-draft quality is reliably below bar** AND **refinement demonstrably helps** (a human can articulate feedback and the model can act on it) AND **the latency/token budget permits** the ~2N-call cost. And it must beat the obvious alternatives: a **single strong pass** (if the first draft already meets the bar, the loop is wasted spend), and **self-consistency voting** (Huang et al.: multi-agent debate only marginally beats self-consistency at equal compute — much apparent refinement lift is the sampling effect, not the critique). (empirically-supported)

**Evidence to cite.** The stated rationale for iterating; the named cheaper baseline and why it loses; the budget posture; the first-draft-below-bar claim.

**Score.** 1 = a refinement loop reflexively applied with no evidence the first draft is below bar or that refinement helps — pure ceremony / wasted 2N calls. 3 = the loop is plausibly warranted but the cheaper baseline (single pass / self-consistency) is not explicitly ruled out, or the "refinement helps" claim is asserted not shown. 5 = the triad is met with evidence, and the loop is explicitly justified over both a single strong pass and self-consistency voting — iteration earns its premium. (Ties to `rubric-loop-selection` S1-simplest-sufficient.)

---

## Scoring summary template

```text
Plan/artifact: {name}        Family: evaluator-optimizer (incl. self-refine / reflexion / ReAct-reflect)
Variant: {two-role G/E | single-model self-refine | reflexion cross-attempt | ReAct reflection arm}
Gate rung: {1 executable/env | 2 reference-judge | 3 rubric-judge | 4 self-judge}
Depends on: rubric-loop-control (its gates C1/C2/C3/C7 also apply — score separately)

Backbone gates:
  EO1 gate soundness ............ PASS / FAIL   {gate rung vs success criterion}
  EO2 oracle-independence ....... PASS / FAIL   {stop-condition inputs; oracle-label illusion?}
  EO5 termination & budget ...... PASS / FAIL   {cap=_, token-ceiling=_, no-improve K=_, anti-oscillation=_, return-best?}

Review dimensions (1-5):
  EO3 judge independence ........ {n}   {generator vs evaluator model/family; blinded?}
  EO4 feedback actionability .... {n}   {localize+instruct? decomposed criteria?}
  EO6 regression protection ..... {n}   {best-of-N retention? stabilization stop?}
  EO7 judge-bias mitigation ..... {n}   {length-norm / anonymize / position-swap / history-hidden}
  EO8 loop-vs-one-shot .......... {n}   {triad met? beats single-pass + self-consistency?}

Verdict:
  SHIP   — every gate PASS (EO1, EO2, EO5) and no review < 3, AND rubric-loop-control gates pass
  BLOCK  — any gate fails, or any review < 3
Top findings (severity-ranked, each mapped to a §6 failure mode, with citation):
  1. ...
```

Map every finding to a named failure mode in `../references/evaluator-optimizer.md` §6 for root cause: oracle-label illusion, degradation-by-revision, self-preference bias, confidently-wrong judge, reward-hacking the rubric, oscillation/non-convergence, return-last-not-best, sycophantic-feedback collapse, refinement-aware inflation, cost/latency blow-up, family bias in judge panels.

---

## Dependency note

Every per-family rubric — this one included — **depends on `rubric-loop-control`** (manifest `dependencies: ["loop-control"]`, expanded transitively at load). When this rubric is loaded, `rubric-loop-control` is loaded with it, and **its gates also apply**: termination stack (C1), budget governance (C2), verification-gate strength (C3), and durability/idempotency (C7) must pass in addition to EO1/EO2/EO5. EO5 is the _evaluator-optimizer instantiation_ of the C1/C2 control-plane mechanics, scoped to this loop's iteration cap, no-improvement guard, anti-oscillation guard, and return-best policy — it does not relieve the plan of clearing C1/C2 themselves. The ship rule is the **union**: a plan emitting this family ships only when this rubric's gates, `rubric-loop-control`'s gates, and the always-loaded `rubric-loop-selection` + `rubric-plan-quality` gates **all** pass and no [review] across the loaded set is below 3.

**Builder-seat boundary.** This rubric scores the _mechanism_ — gate trust, judge independence, bounding. It does **not** score the human/operator experience of the running loop (trust, steerability, observability-as-UX); that is the sibling `agentic-ux` skill, handed off via `rubric-plan-quality` Q6-operator-handoff. Do not duplicate the operator-UX rubric here — score the gate, then hand off.

---

## Primary sources

| Title | URL | What it grounds |
| --- | --- | --- |
| Building Effective Agents — Anthropic Engineering (evaluator-optimizer workflow; "ground truth from the environment"; the two litmus tests) | <https://www.anthropic.com/engineering/building-effective-agents> | EO1 trust ladder, EO8 fit tests |
| Anthropic Cookbook — `patterns/agents/evaluator_optimizer.ipynb` (reference loop: PASS/NEEDS_IMPROVEMENT/FAIL verdict, parsed-PASS stop, memory accumulation) | <https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/evaluator_optimizer.ipynb> | EO5 stop design, EO3 context split |
| Self-Refine: Iterative Refinement with Self-Feedback — Madaan et al., 2023 (max-4 cap; `stop()`; specific>generic>none ablation; math-reasoning null result) | <https://arxiv.org/abs/2303.17651> | EO4 feedback, EO5 cap, EO6 stabilization |
| Large Language Models Cannot Self-Correct Reasoning Yet — Huang et al., DeepMind, 2024 (oracle-label illusion; intrinsic self-correction degrades; debate≈self-consistency) | <https://arxiv.org/abs/2310.01798> | EO1, EO2, EO6, EO8 |
| Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge — Park/Ye et al., 2024 (12-bias CALM taxonomy; mitigations) | <https://arxiv.org/html/2410.02736v1> | EO7 bias mitigation |
| LLM Evaluators Recognize and Favor Their Own Generations — Panickssery/Wataoka et al., 2024 (causal self-recognition→self-preference link) | <https://arxiv.org/abs/2404.13076> | EO3 judge independence |
