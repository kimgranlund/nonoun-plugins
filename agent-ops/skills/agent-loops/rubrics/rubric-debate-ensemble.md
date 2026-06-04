# Rubric — Debate / Ensemble

Score a **multi-agent quality-via-diversity** plan: self-consistency, debate, council, Mixture-of-Agents (MoA), LLM-as-a-jury, panel of evaluators, majority voting, or an adversarial verification panel. Use in **EVALUATE mode** to score an existing ensemble plan/transcript, and as the acceptance bar in **PLAN/COMPOSE mode** when the router selects this family.

**Band:** per-family. Load this rubric **only** when the plan composes a debate/ensemble mechanism (`selectors` in `rubric-manifest.json` — debate, council, ensemble, mixture-of-agents, moa, self-consistency, llm-as-a-jury, panel of evaluators, majority voting, adversarial verification panel). It is **not** loaded for every plan.

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate blocks SHIP; it is not a matter of opinion. Cross-cutting gates are backed by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`; per-family gates (DE1/DE2) are **[mech-partial]** — the criterion is structural but no automated script enforces it; agent judgment applies.
- **[mech-partial]** — mechanically checkable criterion, no automated script — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment. Score **1–5**; record the evidence (the plan section, the parameter value, the transcript line) you scored against.

**Ship rule:** this family ships when **every [gate] passes AND no [review] dimension < 3** — across this rubric _and_ every other loaded rubric. A composed plan must clear the **union** of all loaded rubrics' gates.

**Calibration caveat:** status **draft**, 0 calibration samples. Treat every score as **directional, not authoritative**, until ROADMAP v0.2 calibration is met. The [gate] dimensions are the only mechanically verifiable layer; [review] anchors below are first-cut and will move with calibration.

**Dependency:** this rubric **depends on `rubric-loop-control`** (cross-cutting). Every gate in `rubric-loop-control` (C1 termination-stack, C2 budget, C3 verification-gate, C7 durability-idempotency) **also applies** to a debate/ensemble plan and is scored alongside these dimensions. In particular, debate/ensemble has its own outer loop (debate rounds, MoA layers) and fan-out cost — `rubric-loop-control` C1/C2 govern its round/layer caps and token ceiling, and this rubric does not re-derive them. DE5 (agreement-calibration) and DE3 (aggregation) sit _on top of_ that control plane, not in place of it.

**The thesis this rubric enforces (`../references/router.md`, `../references/debate-ensemble.md`):** an ensemble buys quality at a **3×–15× compute premium**, and much of debate's apparent lift is just the **ensemble/voting effect** — at equal compute, single-agent self-consistency often matches an elaborate debate. So the load-bearing question is not "is the council well-built" but **does diversity-via-ensemble beat a single strong pass here, and is the diversity real.** That is why the two gates are _answer-shape fit_ and _diversity authenticity_: if the answer can't be aggregated, or the "diverse" agents are temperature-clones of one model with correlated errors, the method is void before any review dimension matters.

---

## The backbone gates

Run these two first. Most debate/ensemble plans fail here — and a failure here voids the mechanism regardless of how polished the rest of the plan is.

### DE1 [gate / mech-partial] — Answer-shape fit

The aggregation method **matches the shape of the answer**. Discrete or extractable answers (a label, a number, a chosen option, a final span) → **vote / majority / max** is sound. Free-form answers (an essay, a design, a multi-paragraph judgment) cannot be majority-voted → require an **LLM-aggregator / jury / synthesis** step instead. A plan that majority-votes free-form prose, or that spins up a jury to average three integers a vote would settle, is mis-shaped.

**Test (binary):** read the answer the ensemble produces and the combine step.

- Answer is discrete/extractable AND combine = vote/majority/max → PASS.
- Answer is free-form AND combine = LLM-aggregator/jury/synthesize → PASS.
- Mismatch (vote over free-form prose; or a jury where a vote suffices) → **FAIL**. A plan with **no named combine step at all** fails by definition — N parallel answers with no aggregation is not an ensemble, it is N answers.

### DE2 [gate / mech-partial] — Diversity authenticity

The agents are **genuinely decorrelated**. Authentic diversity comes from **distinct model families, distinct lenses/personas, or directed adversarial roles** — sources whose errors are uncorrelated. Temperature-sampling one model N times (vanilla self-consistency) is the _weakest_ form: its errors are correlated, so the ensemble cannot outvote a systematic mistake. A "council" that is one model at temperature 0.9 wearing N name tags has fake diversity, and the entire method's premise (independent errors cancel) is void.

**Test (presence + structural):** enumerate the agents and their configuration.

- If the plan claims diversity is the _source of lift_: require ≥2 distinct model families **or** explicitly directed, materially-different roles/lenses (not cosmetic name changes). PASS if present.
- If the plan is **plain self-consistency** (one model, temperature only): PASS **only if** the plan honestly labels it as self-consistency and does not claim debate/council-grade diversity it doesn't have (this is the honest floor; the _value_ of that choice is then judged at DE7).
- **FAIL** if the plan markets "debate" / "council" / "diverse panel" but the roster is N temperature-clones of a single model with correlated errors and no directed-role differentiation.

---

## Design dimensions

### DE3 [review] — Aggregation correctness

The combine step is the **right operator** for the task **and robust to correlated voters**. Majority / max / average / synthesize / majority-with-refutation each fit different cases; the choice should be deliberate, and where voters are not fully independent the aggregation should be **independence-aware** (e.g. down-weight correlated votes, weight by competence, or treat the count as a weak signal rather than a hard threshold). Naive equal-weight majority over correlated voters silently overstates confidence.

**Evidence to cite:** the named combine operator; whether voter independence was reasoned about; any weighting/tie-break rule. **Anchors:** **1** = combine is unspecified or a naive equal-weight majority over plainly-correlated voters with no acknowledgement. **3** = a reasonable operator is named for the answer shape, but independence is assumed rather than examined. **5** = operator fits the answer shape AND independence is explicitly handled (competence/independence weighting, correlated-vote down-weighting, or count-as-weak-signal), with a tie-break rule.

### DE4 [review] — Budget justification & fallback

The **3×–15× multiplier is warranted by the stakes**, and a guard routes **easy / already-agreeing** items to a **single pass** instead of paying the full ensemble on every item. Running the whole panel on trivially-easy or unanimous-on-first-look inputs burns the premium for no gain; the plan should spend the ensemble where it changes the answer.

**Evidence to cite:** the stated per-item cost multiplier; the value/stakes rationale; the early-exit / easy-item-shortcut rule (e.g. "if first two proposers agree, skip the rest"); the single-pass fallback for low-value items. **Anchors:** **1** = full N-agent (×R-round) cost paid on every item with no stakes rationale and no early-exit. **3** = stakes justify the premium and a fallback is named, but the ensemble still runs unconditionally on easy/agreeing items. **5** = premium tied to stakes AND a concrete agreement/difficulty gate short-circuits easy items to a single pass, with the cheaper baseline named.

### DE5 [review] — Agreement calibration (debate)

For **interactive debate**, stubbornness/agreement is **tuned to avoid sycophantic premature consensus** — and bounded by a **max-round / consensus stop**. Agents that fold to the loudest peer on round 1 collapse the ensemble to a single voice (no error-cancellation); agents too stubborn never converge and burn rounds. There must be a stop: consensus reached, or max rounds hit (this is the `rubric-loop-control` C1 termination-stack instantiated for debate rounds — cite it, don't re-derive).

**Evidence to cite:** the agreement/stubbornness setting or instruction; the consensus criterion; the max-round cap; any anti-sycophancy measure (independent first answers before exposure to peers; hidden author identity). **Anchors (N/A-able when the plan is non-interactive self-consistency / single-shot MoA with no debate rounds — score N/A, not 1):** **1** = interactive debate with no round cap and no agreement tuning (sycophantic collapse or non-termination both possible). **3** = a max-round stop exists but sycophancy is unaddressed (or vice-versa). **5** = agreement tuned against premature consensus (independent-first answers and/or anonymized authorship) AND a consensus-or-max-round stop is concrete.

### DE6 [review] — Role & width/depth sizing

The **proposer / aggregator / skeptic / judge roles match model competencies**, and **N (width) and R (depth/rounds) sit near the empirical sweet spots** rather than inflated past diminishing returns. Reported sweet spots (practitioner-folklore-to-directional, not load-bearing constants): ~**3 agents / 2 rounds** for debate, ~**6 proposers / 3 layers** for MoA, ~**3 jurors** for a jury. Returns flatten quickly; a 10-agent / 5-round council usually pays 3× the cost of a 3-agent / 2-round one for marginal lift.

**Evidence to cite:** the role→model assignment; the N and R values; any justification for exceeding the typical sweet spot. **Anchors:** **1** = N and R are arbitrary/inflated (large panels, many rounds) with no diminishing-returns awareness, or roles ignore model competence (weak model as final judge). **3** = sizes are reasonable and roles plausibly matched, but no explicit rationale near the empirical knee. **5** = N/R sit at or just past the documented sweet spot with a stated reason, and each role is assigned to a competence-appropriate model (strong judge/aggregator, cheaper proposers where acceptable).

### DE7 [review] — Ensemble-vs-debate honesty

If the plan uses **interaction** (debate rounds, MoA cross-referencing) rather than the cheaper **self-consistency voting** baseline, the gains are **attributed to the interaction mechanism — not just the voting effect.** The honest position (empirically-supported): a large share of multi-agent-debate's measured lift over a single pass is the _ensemble/voting_ effect, recoverable by N independent samples + majority vote at equal compute. So an interactive design must justify the extra coordination cost over plain voting, not present the single-pass comparison as if it proved debate's value.

**Evidence to cite:** whether the plan benchmarks against self-consistency (N independent samples + vote) at **equal compute**, not just against a single pass; the stated reason interaction beats voting here (e.g. cross-agent error-correction the vote can't capture). **Anchors:** **1** = interactive ensemble justified solely by beating a single pass, with no self-consistency baseline and no account of why interaction (vs voting) is needed. **3** = self-consistency is acknowledged as the baseline but not actually run/compared. **5** = interaction is justified against an equal-compute self-consistency baseline, with the mechanism-specific reason interaction adds value over voting stated (or the plan honestly downgrades to self-consistency when it can't make that case).

### DE8 [review] — Verification-gate integrity

**If the ensemble is used as a verification gate** (an adversarial panel / jury that accepts-or-rejects another loop's output), its **judging bias is controlled** and **consensus is treated as necessary-not-sufficient.** Panels inherit the same biases as a single LLM-judge — negativity/positivity skew, self-preference (a model rating its own family's output higher), and judge entanglement (the same model both generating and sitting on the panel). A unanimous panel is evidence, not proof; correctness-critical acceptance still needs the strongest available oracle behind it (ties to `rubric-loop-control` C3 verification-gate and the evaluator-optimizer judge-bias discipline).

**Evidence to cite:** whether the panel judges output from a _different_ generator (no entanglement); the bias controls (anonymized authorship, position-swap, length normalization, mixed-family jurors); whether consensus is the _sole_ accept signal or is backed by an oracle/ground-truth check where one exists. **Anchors (N/A-able when the ensemble is not used as a gate — i.e. it produces an answer rather than accepting/rejecting one — score N/A, not 1):** **1** = panel gates acceptance with judge entanglement (graders include the generator's model) and consensus is the sole accept signal on correctness-critical work. **3** = jurors are independent of the generator and consensus is required, but known judge biases (self-preference, length, position) are unmitigated. **5** = mixed-family independent jurors, explicit bias controls, AND consensus treated as necessary-not-sufficient (backed by an executable/ground-truth oracle wherever the success criterion affords one).

---

## Scoring summary template

```text
Plan / artifact: {name}
Family: debate / ensemble   Variant: {self-consistency | debate | MoA | jury | adversarial panel}
Answer shape: {discrete/extractable | free-form}   N (width): {n}   R (rounds/layers): {n}
Models in roster: {list — note distinct families}   Used as a gate? {yes/no}

Backbone gates:
  DE1 answer-shape fit ............ PASS / FAIL   {answer shape ↔ combine step}
  DE2 diversity authenticity ...... PASS / FAIL   {roster: distinct families / directed roles, or temp-clones}

Review dimensions (1-5, or N/A where noted):
  DE3 aggregation correctness ..... {n}     {combine operator + independence handling}
  DE4 budget justification/fallback {n}     {multiplier rationale + easy-item shortcut}
  DE5 agreement calibration ....... {n|N/A} {anti-sycophancy + consensus/max-round stop; N/A if non-interactive}
  DE6 role & width/depth sizing ... {n}     {N/R vs sweet spot + role→model competence}
  DE7 ensemble-vs-debate honesty .. {n}     {equal-compute self-consistency baseline}
  DE8 verification-gate integrity . {n|N/A} {judge bias controls; N/A if not used as a gate}

Inherited from rubric-loop-control (scored there, must also pass):
  C1 termination-stack (round/layer caps) ... PASS / FAIL
  C2 budget (fan-out token ceiling) ......... PASS / FAIL
  C3 verification-gate ...................... PASS / FAIL
  C7 durability-idempotency ................. PASS / FAIL / N-A

Verdict:
  SHIP   — every gate PASS (this rubric DE1–DE2 + all loaded rubrics, incl. rubric-loop-control)
           AND no review dimension < 3
  BLOCK  — any gate fails, or any review < 3
Top findings (severity-ranked, each with a citation):
  1. ...
```

Map findings to the family's named failure modes (`../references/debate-ensemble.md`) for root cause: **fake-diversity collapse** (DE2), **shape-mismatched aggregation** (DE1/DE3), **sycophantic premature consensus** (DE5), **voting-effect masquerading as debate value** (DE7), and **entangled / biased panel gate** (DE8). Most debate/ensemble failures are one of these amplified by an uncapped round/budget — which is why `rubric-loop-control` is a hard dependency, not an option.
