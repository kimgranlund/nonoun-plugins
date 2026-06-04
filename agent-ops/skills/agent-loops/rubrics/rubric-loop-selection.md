# Rubric — Loop Selection

Score whether the **right loop / orchestration shape was chosen for THIS goal** — or whether the plan reached for a fancier, more autonomous, or more multi-agent mechanism than the task warrants. This is the builder-seat selection decision the skill exists to get right: a perfect blueprint for the _wrong_ topology still fails. Use this rubric in **EVALUATE** mode to audit a plan/loop/transcript, and as part of the acceptance bar in **PLAN**/**COMPOSE** before emitting an Orchestration Blueprint.

**Band: cross-cutting (always-load).** Apply to every emitted plan regardless of which family it composes (`rubric-manifest.json` → `band: cross-cutting`). It is loaded unconditionally alongside `rubric-loop-control` and `rubric-plan-quality`.

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate blocks SHIP; it is not a matter of opinion. All gates in this rubric (S1/S2/S6) are **[mech-partial]** — the criteria are structural but no automated script enforces them; agent judgment applies. The cross-cutting `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py` does not cover selection-fit checks.
- **[mech-partial]** — mechanically checkable criterion, no automated script — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment. Reviewer reads the plan against the task classification and scores **1–5**.

**Ship rule.** A plan ships on this rubric when **every [gate] passes AND no [review] dimension is below 3** — the global rule from `rubric-manifest.json`. A composed plan must clear the union of all loaded rubrics' gates, so a selection failure here blocks SHIP even if every family rubric passes.

**Evidence discipline.** Record evidence for every finding — the plan field it fails (most often blueprint field 3 _Chosen loop topology + why_, field 4 _Rejected alternatives_, or field 2 _Task classification_), or the classification axis that contradicts the choice. A finding without a citation is an opinion.

**Calibration caveat (draft — directional, not authoritative).** Status `draft`, 0 calibration samples (`rubric-manifest.json` → `calibration_note`). Treat every [review] score as **directional, not authoritative**, until ROADMAP v0.2 calibration is met. The [gate] dimensions are the only mechanically verifiable layer; lean on them. Criteria below are graded **empirically-supported** (the choice rests on measured results) vs **practitioner-folklore** (the choice rests on field heuristics the corpus reports but that are not yet measured) where the distinction is load-bearing.

---

## The backbone gate (run it first)

**S1 is the load-bearing check of this entire rubric.** The dominant failure of agent-loop design is over-engineering — escalating to a loop, then to a multi-agent loop, where one strong pass was correct. Run S1 first; most selection failures surface there. S2 and S6 are the other two structural gates; the four [review] dimensions then grade _how well_ the chosen shape fits the task.

---

## Dimensions

### S1 [gate / mech-partial] — Simplest-sufficient

**Criterion.** A single augmented-LLM call (or no loop at all) was **explicitly ruled out in writing** before any multi-step or multi-agent shape was chosen; complexity is justified by a concrete reason, not adopted reflexively. _"Find the simplest solution and only increase complexity when needed"_ (Anthropic, _Building Effective Agents_, <https://www.anthropic.com/research/building-effective-agents>). **Empirically-supported:** the multi-agent premium (~4×–15× tokens, Anthropic multi-agent-research engineering post, <https://www.anthropic.com/engineering/built-multi-agent-research-system>) and the documented degradation of self-judged loops make "escalate only on demand" a measured stance, not a preference.

**Test (presence + binary).** Read blueprint field 4 _Rejected alternatives_. It **must** contain an explicit line stating why a single strong pass — or the minimal Ralph loop — was or was not enough. **PASS** = that line exists and names a concrete reason the simpler option fails (errors worth iterating on / no oracle for one-shot / horizon exceeds one pass / genuine independent parallelism). **FAIL** = escalation to _any_ loop with no such line, or a hand-wave ("agents are better," "use multi-agent for robustness"). Escalation without the ruling is unjustified by construction.

### S2 [gate / mech-partial] — Workflow-vs-agent discipline

**Criterion.** The plan **defaults to a workflow** (predefined code paths orchestrating LLM calls) and escalates to **agentic autonomy** (the model directs its own steps and tool use in a loop) **only** where the step count is genuinely unpredictable AND the environment is trusted/sandboxed enough to grant that autonomy. Workflows buy predictability and testability; autonomy is the exception you justify, not the default (Anthropic, _Building Effective Agents_ — the workflow/agent distinction). **Practitioner-folklore→empirically-supported:** the distinction is Anthropic's documented design axis; the "default to workflow" stance is corroborated by reproducibility/cost data on autonomous loops.

**Test (binary fit-check).** Classify the chosen topology: is it a **fixed-path workflow** (chaining / routing / parallelization / plan-execute with a known step set) or an **open-ended agent** (ReAct / orchestrator-workers / Ralph-until-done)? Cross-check field 2 _Task classification_ → the `decomposable/open-ended` axis. **PASS** = an open-ended agent was chosen **only** where the classification says steps are unpredictable, OR a workflow was chosen for foreseeable steps. **FAIL** = an autonomous agent loop chosen for a foreseeable, fixed-step task (autonomy tax with no return), OR a rigid workflow forced onto genuinely unpredictable steps. Autonomy granted on an untrusted/un-sandboxed surface without containment is also a FAIL (cross-checks S6).

### S6 [gate / mech-partial] — Brownfield/greenfield & reversibility fit

**Criterion.** Greenfield-only and irreversibility/stakes constraints are respected by the chosen shape. The headline rule: **no brute-force Ralph loop on a brownfield codebase** (it assumes a clean slate and a tolerant blast radius); **no high-autonomy / YOLO loop running unattended on irreversible or production-touching surfaces without containment** (sandbox, allowlist, dry-run, human gate). Match the loop's blast-radius assumptions to the task's reversibility (`../references/router.md` §axes — reversibility/stakes). **Practitioner-folklore:** the Ralph-is-greenfield and don't-YOLO-on-prod heuristics are widely reported field rules (Geoffrey Huntley on Ralph; Anthropic on autonomy + sandboxing) but not formally measured; gate on the presence of the containment, not on an effectiveness number.

**Test (binary fit-check).** From field 2, read `greenfield/brownfield` and `reversible/irreversible`. Then inspect the chosen topology + field 10 _Failure/fallback_. **PASS** = (a) Ralph/brute-force chosen only on greenfield OR with an explicit brownfield-safe containment (file allowlist + commit-per-iteration + clean reset path); AND (b) any high-autonomy/unattended loop on an irreversible/production surface carries a named containment or human gate. **FAIL** = Ralph proposed on brownfield with no containment, OR an autonomous/`--dangerously-skip-permissions`-class loop pointed at irreversible state with no sandbox, dry-run, allowlist, or operator checkpoint. (When containment exists, also confirm `rubric-loop-control` C7 durability and the blueprint's draft-and-stop checkpoint — see Dependency note.)

---

### S3 [review] — Decomposition-shape fit

**Criterion.** The chosen family matches the task's _structure_: **independent / breadth-first** work → fan-out (auto-research, parallel orchestrator-workers); **depth-first / tightly-coupled** work → a single thread (one agent, plan-execute, sequential ReAct); **foreseeable steps** → plan-execute / workflow; **unpredictable decomposition decided at runtime** → orchestrator-workers. Decomposition shape is the primary structural selector once S1/S2 clear (`../references/router.md` decision table). **Empirically-supported:** the breadth-first→multi-agent / depth-first→single-thread split is grounded in the Cognition "Don't Build Multi-Agents" finding that parallel agents fracture on coupled, shared-state work (<https://cognition.ai/blog/dont-build-multi-agents>) and Anthropic's converse result that breadth-first research parallelizes well.

**Evidence to cite.** Field 2's `decomposable/open-ended` + `breadth/depth` axes, against field 3's chosen topology; for composite tasks, the nesting in field 5 _Wiring_.

**1–5 anchor.**

- **1** — Topology fights the structure: fan-out onto coupled/shared-write work (the Flappy-Bird failure), or a single sequential thread forced onto large genuinely-independent breadth.
- **3** — Reasonable fit on the dominant axis, but one mismatch unaddressed (e.g. mostly-independent subtasks with one hidden dependency not called out, or a foreseeable sequence run as an open-ended agent).
- **5** — Topology is the natural shape for the classified structure; independence/coupling is explicitly reasoned, and breadth-vs-depth drives the fan-out/single-thread choice.

### S4 [review] — Verifiability-driven choice

**Criterion.** The **presence or absence of a cheap objective gate drove the topology choice.** An executable oracle exists (tests / compiler / schema / lint / ground-truth) → brute-force and evaluator-optimizer loops become viable, because the gate makes convergence-to-working measurable. No oracle exists → the plan does **not** reach for a self-judged iterative loop on correctness; it routes to ensemble/jury, human-in-the-loop, or a single careful pass instead. Verifiability is the second structural selector (`../references/router.md` A1×A4 matrix). **Empirically-supported:** the corpus is consistent that self-judgment on non-verifiable tasks **degrades** output and that the "oracle-label illusion" inflates loop gains that then fail to reproduce in deployment — so letting oracle-availability gate the loop choice is a measured discipline, not taste.

**Evidence to cite.** Field 1's success criterion (is it objectively checkable?) and field 8 _Verification gate_ type, against the chosen topology in field 3.

**1–5 anchor.**

- **1** — A self-judged iterative loop chosen for a correctness-critical task with **no** real oracle, presented as if it converges (the loop will polish slop).
- **3** — Oracle availability is implicit: the choice happens to fit, but the plan never reasons from "is there a gate?" to the topology.
- **5** — The choice is visibly downstream of gate availability: oracle present → an iterative loop with that oracle as the engine; oracle absent → ensemble/HITL/single-pass chosen _because_ no trustworthy self-gate exists, with the limitation stated.

### S5 [review] — Cost/value justification

**Criterion.** The compute premium of the chosen shape is **justified by the task's value**, and a cheaper fallback is named for the simple/low-value case. Multi-agent and debate/ensemble shapes carry a roughly **~4×–15× token premium** plus reproducibility loss; they earn it only on high-value, breadth-first, genuinely-parallel work (Anthropic multi-agent-research post, <https://www.anthropic.com/engineering/built-multi-agent-research-system>). **Empirically-supported:** the premium figures are measured; the corollary that much of multi-agent debate's apparent lift is the ensemble/voting effect (so single-agent at equal compute often matches it) is reported in the debate/ensemble literature and is why an unjustified premium scores low.

**Evidence to cite.** Field 6 _Parameters_ (fan-out width × depth × model tier → implied spend), field 5 _Wiring_, and any cost rationale in field 3/4 — against field 1's stakes.

**1–5 anchor.**

- **1** — An expensive shape (large fan-out, debate panel, orchestrator) on a low-value or trivially-parallel task, with no cost rationale and no cheaper fallback named.
- **3** — The premium is plausibly worth it but unstated; no explicit cheaper fallback for the low-value branch.
- **5** — The premium is explicitly weighed against task value, the multi-agent/debate choice is reserved for the high-value breadth-first case, and a named single-agent (or single-pass) fallback covers the simple/low-value path.

### S7 [review] — Composition coherence

**Criterion.** When multiple families are combined — an orchestrator whose workers each run plan-execute; an evaluator-optimizer wrapping a parallel generator; auto-research = orchestrator + cite/verify pass — the **nesting is coherent and each layer's gate is preserved.** No layer swallows or bypasses the gate of the layer beneath it; the handoff/return contract between layers is explicit; the composition is named, not emergent (`../references/composition.md`). **Practitioner-folklore:** composition discipline is a design heuristic drawn from the worked patterns (Auto-Research's research→single-synthesis split, evaluator-in-orchestrator), not a benchmarked result; score on structural coherence.

**Evidence to cite.** Field 3 _Nested topologies_ + field 5 _Wiring_ (where each layer's gate sits); cross-check that each composed family's own rubric is listed in field 12 _Scoring_.

**1–5 anchor.**

- **1** — Layers are stacked but a gate is lost in the seam (e.g. an outer orchestrator accepts worker output with no inner verification, or two layers' stop conditions contradict), or the composition is implicit and unnamed.
- **3** — A coherent composition, but one seam is under-specified (handoff schema vague, or one inner gate's relationship to the outer stop is unclear).
- **5** — Each layer's role, gate, and handoff contract is explicit; every composed family is named and carries its own rubric; the outer loop's termination respects the inner loops' completion. (For single-family plans where no composition exists, score **N/A** and exclude from the ship check.)

---

## Scoring summary template

```text
Plan: {goal short name}     Mode: {PLAN | COMPOSE | EVALUATE}
Chosen topology: {primary}  Nested: {secondary, or none}
Task classification (field 2): {greenfield/brownfield · decomposable/open-ended · breadth/depth ·
                                verifiable/subjective · reversible/irreversible · repeated/one-shot}

Gates:
  S1 simplest-sufficient ............. PASS / FAIL   {field 4 line ruling out single pass}
  S2 workflow-vs-agent discipline .... PASS / FAIL   {workflow vs agent, vs step-predictability}
  S6 brownfield/reversibility fit .... PASS / FAIL   {containment present where required}

Review dimensions (1-5; directional — draft calibration):
  S3 decomposition-shape fit ......... {n}   {evidence}
  S4 verifiability-driven choice ..... {n}   {evidence}
  S5 cost/value justification ........ {n}   {evidence}
  S7 composition coherence ........... {n | N/A for single-family}   {evidence}

Verdict (this rubric):
  PASS  — all gates PASS and no review < 3
  BLOCK — any gate FAILs, or any review < 3
  (SHIP for the whole plan also requires every other loaded rubric's gates — see Dependency note.)

Top findings (severity-ranked, with citations):
  1. ...
```

Map a selection failure back to the router: a FAIL here usually means returning to `../references/router.md` and re-deriving the topology from the task classification, not patching the chosen loop's parameters. An over-engineered choice (S1/S5) is fixed by _dropping a layer_; a structure mismatch (S3) by _changing the family_.

---

## Dependency note

This rubric is **cross-cutting and depends on `rubric-loop-control`** — as does every per-family rubric in the library (`rubric-manifest.json` → each family's `dependencies: ["loop-control"]`). **`rubric-loop-control`'s gates also apply** to any plan scored here: even a plan with a perfectly-selected topology does **not** SHIP unless `rubric-loop-control`'s gates (C1 termination-stack, C2 budget, C3 verification-gate, C7 durability-idempotency) **also** pass, plus `rubric-plan-quality`'s gates and those of every per-family rubric the plan composes. The global ship rule is the **union**: a plan ships only when every [gate] across all loaded rubrics passes and no [review] < 3. Selection is necessary, not sufficient — it answers "right loop?", while control answers "bounded, gated, durable?" and plan-quality answers "runnable?".

**Builder-seat boundary.** This rubric scores the _mechanism-fit decision_ only. It does **not** score the human/operator experience of the running workflow (trust, steerability, observability-as-UX, reversibility-as-felt-control) — that is the sibling `agentic-ux` skill. Where a selection finding touches operator posture (e.g. an unattended high-stakes loop), record the _containment_ check here (S6) and **hand off** the UX evaluation rather than scoring it. (The operator-handoff check itself lives in `rubric-plan-quality` Q6, which verifies the blueprint _hands off_ to the sibling — it likewise does not score UX.)
