# The Goal→Loop Decision Router

The executable heart of `agent-loops`. Given a goal — canonically _"create the best plan for {feature|task} to achieve {outcome}"_ — this router **classifies the goal on 9 axes, runs ordered first-match gates to pick a loop body, attaches a verification gate, instantiates the control plane, applies the trust-boundary overlay, and emits a blueprint** with the strongest rejected alternative named. It is built to be _run_, not read: an agent applying §2 top-to-bottom on a real goal lands on one route and parameterizes it.

**Seat check.** This selects and wires the _mechanism_. The sibling `agentic-ux` skill evaluates the _operator's human experience_ of the resulting workflow (trust / control / observability / steerability / reversibility). Same vocabulary, opposite job: this router answers **"which loop do I build?"**; the sibling answers **"is the loop I built good to drive?"** When a route lands on a high-autonomy or async shape, hand the result off for the UX pass — do not re-derive it here.

**Convention.** `[gate]` = mechanically/structurally checkable (presence/absence/count). `[review]` = needs judgment. Routes below map to a topology reference (`<name>.md`) and a family rubric (`rubrics/rubric-<name>.md`) per `rubrics/rubric-manifest.json`. Every route additionally inherits the three cross-cutting rubrics (`rubric-loop-selection`, `rubric-loop-control`, `rubric-plan-quality`).

---

## §1 — The 9 discriminating axes

These are the **input features** of the routing procedure. Classify the goal on all eight _before_ routing (§Procedure STEP 0). Write the read down — it is the first thing a reviewer checks, and `rubric-loop-selection` scores whether the route follows from it. Confidence tags: most axis→route mappings are **empirically-supported** (cited briefs/papers); a few are **practitioner-folklore** and tagged inline.

| # | Axis | Poles | Why it routes |
| --- | --- | --- | --- |
| **A1** | **Verifiability / oracle availability** | executable oracle (tests/compiler/schema/lint) ⟷ ground-truth comparison ⟷ LLM-judge ⟷ none | The single strongest discriminator. An oracle unlocks a real _termination_ gate **and** a real _verification_ gate; its absence forces self-judge (weak) and heuristic stops. **Do not guess A1** — ask if unknown. (empirically-supported) |
| **A2** | **Decomposability** | monolithic ⟷ fixed foreseeable sequence ⟷ runtime-discovered subtasks | Monolithic → single call. Fixed sequence → chaining / Plan-Execute. Runtime-discovered → orchestrator-workers. |
| **A3** | **Parallelizability / independence** | tightly-coupled (shared mutable state) ⟷ independent (read-only fan-out) | Independent → fan-out / ensemble. Coupled writes → single-threaded. Fanning out onto shared-write work produces conflicting implicit decisions (Cognition's Flappy-Bird failure). (empirically-supported) |
| **A4** | **Solution-space width** | single likely path ⟷ many diverse paths/answers | Wide + diverse → ensemble / debate / self-consistency. Narrow → single pass; an ensemble buys little when one path dominates. |
| **A5** | **Horizon length** | short (≤2–3 turns) ⟷ long (dozens–hundreds of steps) | Long horizon makes the L5 control plane (context, durability, termination) mandatory; short horizon makes most machinery pure overhead. |
| **A6** | **Reversibility / stakes** | reversible / low-stakes ⟷ irreversible / high-stakes | High stakes forces HITL gates, sandboxing, human-on/in-the-loop; bans unbounded autonomy and draft-and-stop on the _plan itself_. |
| **A7** | **Determinism vs open-endedness** | predictable step count ⟷ unpredictable (open-ended) | Predictable → **workflow** (coded path). Unpredictable → **autonomous agent loop**. This is the Anthropic workflow-vs-agent split. (empirically-supported) |
| **A8** | **Budget posture** | cost / latency-sensitive ⟷ value justifies the premium | Gates whether you may spend the multiplier on fan-out / ensemble / research. Multi-agent buys quality at a **~4×–15× token premium**; cheap fallback is single-agent ReAct. (empirically-supported) |
| **A9** | **Trust boundary / untrusted-content exposure** (overlay — constrains, doesn't pick, the body) | all-trusted inputs ⟷ ingests **attacker-controllable** content (open web / transcript / issue / channel / repo file) | If the loop ingests untrusted content **AND** can take an external/irreversible action, all three legs of the **lethal trifecta** are present → the topology must add a **content/action split** (the untrusted-content reader holds no tool-write capability or credentials; the privileged actor never sees raw content — a Dual-LLM analogue), and field 14 must name the containment. Read-only or all-trusted → no split needed. _Verification "trust" here means integrity under adversarial input, not just honest-condition accuracy._ (empirically-supported) **Default-suspicious posture:** any goal that mentions "fetch", "read from", "ingest", "scrape", "crawl", "summarize [external source]", "process [file]", "web search", "open web", or reads from a repo/channel/issue/transcript **defaults to A9 = yes-untrusted** unless the goal explicitly names a fully-controlled, non-user-supplied source. Shift the burden of proof to "prove it's trusted," not "prove it's untrusted." A goal-author who does not label their own threat model will not label untrusted sources — do not assume trusted because "untrusted" is absent. |

**Secondary axes that refine a route (not primary discriminators):** **codebase state** (greenfield ⟷ brownfield — Ralph is greenfield-only), **attended vs unattended** (foreground ⟷ detached), **single-pass vs iterative** (does refinement _demonstrably_ help, and is the first draft below bar — without both, an evaluator-optimizer loop is overhead).

---

## §2 — Ordered routing procedure

```text
STEP 0  CLASSIFY the goal on A1–A9 (§1). If an axis is unknown AND it gates the
        route (esp. A1 oracle, A2 decomposability, A3 independence), ASK ONE
        QUESTION before routing. Never guess A1.

STEP 1  RUN THE ORDERED GATES Q1–Q9 (§2.1) top-to-bottom. FIRST MATCH WINS THE
        BODY. The gates are ordered CHEAPEST-FIRST by discriminating power:
        simplicity → verifiability → breadth → runtime-decomposition →
        fixed-sequence → refinement → diversity → open-endedness → repetition.

STEP 2  ATTACH THE L4 VERIFICATION/ENSEMBLE GATE (§4) from A1 × A4.

STEP 3  INSTANTIATE THE L5 CONTROL PLANE (§5): termination, context,
        verification, budget, durability. Non-optional — a route without all
        five L5 choices is incomplete by definition.

STEP 4  DECIDE DISPATCH (orthogonal): foreground vs async/background vs
        scheduled, and oversight mode (in-loop gate vs on-loop PR review) from
        A5 + A6. Dispatch never changes the body — only who waits and how it is
        supervised. (See references/async-oversight.md.)

STEP 5  EMIT THE BLUEPRINT SKELETON (§6) and name the 1–2 strongest REJECTED
        alternatives with why-on-THIS-goal's-axes (every route in §3 lists them).
        Then self-score: 3 cross-cutting rubrics + the route's family rubric.
```

### §2.1 — Ordered first-match routing gates (Q1–Q9)

Stop at the first YES. The table is ordered so the cheapest sufficient mechanism wins; escalation past a gate requires a concrete reason, recorded in REJECTED.

| Order | Question | If YES → route | Reference · rubric |
| --- | --- | --- | --- |
| **Q1** | **Does a single augmented call suffice?** Could you describe the whole result in one sentence / one diff, ≤2–3 turns, no decomposition, errors not worth iterating on? (A5 short · A2 monolithic · A4 narrow) | **R0 — Single augmented LLM call.** _Stop. No loop._ (Anthropic's #1 rule: don't build a loop where one call works.) | _(no topology; loop-control trivial)_ |
| **Q2** | Is there a **cheap executable oracle** (tests/compiler/schema/lint) AND is this **coding/artifact** work that decomposes into a checklist? (A1 oracle · A2 sequence) | → branch to **Q2a / Q2b** | — |
| **Q2a** | …and **greenfield**, spec-able as independent verifiable items, with unattended/overnight time, where a cheap re-run beats conflict resolution? | **R1 — Ralph / brute-force** (fresh-context loop) | `ralph.md` · `rubric-ralph-loop` |
| **Q2b** | …and **brownfield** / must respect existing invariants / team-reviewable? | **R2 — Spec-Driven / Explore-Plan-Code-Commit** (human plan-gate) | `spec-driven.md` · `rubric-plan-execute` |
| **Q3** | Is it **open-ended research / breadth-first info-gathering** that splits into **independent** sub-topics exceeding one context window, and is it **high-value** (justifies the ~4–15× premium)? (A2 · A3 · A8) | **R3 — Auto-Research fan-out.** If low-value or depth-first → **R3-lite** (single-agent ReAct research, route R8). | `auto-research.md` · `rubric-auto-research` |
| **Q4** | Does the goal **decompose into subtasks known only at runtime**, run by **heterogeneous specialist** agents/tools? (A2 runtime · A7 open) | **R4 — Orchestrator-workers.** Pick handoff vs delegation by A3 (shared writes → handoff / single-thread; read-only → delegation fan-out). | `orchestrator-workers.md` · `rubric-orchestrator-workers` |
| **Q5** | Does it decompose into a **fixed, foreseeable sequence** where each step is easier than the whole, with N>~3? (A2 fixed sequence) | **R5 — Plan-Execute** (strong planner → cheap executors → replanner). N≤3 → prompt chaining; independent steps → LLMCompiler DAG. _(Plain chaining/routing/parallelization = anthropic-workflow-patterns.)_ | `plan-execute.md` · `rubric-plan-execute` |
| **Q6** | Are there **clear eval criteria**, a first draft reliably below bar, refinement that _demonstrably_ helps, AND a **trustworthy gate** available? (A1 · single-pass→iterative) | **R6 — Evaluator-optimizer** (generate → critique → revise). ReAct/Reflexion is the _open-ended_ sibling of this family. | `evaluator-optimizer.md` · `rubric-evaluator-optimizer` |
| **Q7** | Are there **many diverse reasoning paths/answers**, the answer is **verifiable or aggregatable**, and stakes justify the spend? (A4 wide · A1 · A8) | **R7 — Ensemble**: self-consistency (vote) → debate / MoA / jury, escalating with stakes & needed diversity. | `debate-ensemble.md` · `rubric-debate-ensemble` |
| **Q8** | Is it **open-ended, step-count-unpredictable**, in a **trusted/sandboxed** env where you accept higher cost and can detect/recover errors? (A7 open · A6) | **R8 — Autonomous agent loop** (ReAct; + Reflexion cross-attempt retry **only if** a per-attempt reward exists). | `react-reflexion.md` · `rubric-evaluator-optimizer` |
| **Q9** | Does the **task class repeat** many times, with a cheap **held-out** utility, where fixing the _recurring failure class_ at the harness/prompt/skill level pays off? | **R9 — Self-improving outer loop** wrapping whichever inner body Q1–Q8 selected. | `self-improving.md` · `rubric-self-improving` |
| — | **None matched cleanly.** | **Ask one classifying question before routing** — a clean miss almost always means an axis (esp. A1 oracle availability, A2 decomposability, or A3 independence) is mis-classified. Name the ambiguous axis and ask; never silently default to R8 (the highest-blast-radius, highest-cost body). If A1/A2/A3 are confirmed and no gate matches cleanly, route to **R8 (ReAct)** as the most general fallback — but record it as an unusual forced case in REJECTED ALTERNATIVES so the reviewer knows the gates were exhausted, not skipped. | `react-reflexion.md` |

> **Dispatch is orthogonal — ask AFTER the body is chosen.** _Is the task long-running, independent, and verifiable enough to detach?_ If yes → wrap the chosen body in the async/background wrapper (§5 / `async-oversight.md`). Natural time/event trigger → scheduled/cron. This never changes the body; it changes who waits and how it is supervised. async-oversight has **no own rubric** — it inherits `rubric-loop-control` and hands the UX judgment to the sibling.

---

## §3 — Decision table (compact, for direct lookup)

Read top-to-bottom; first row whose trigger-shape fits wins. Every route names its **strongest rejected alternative(s)** — the REJECTED column is load-bearing: a route chosen without ruling out the cheaper neighbor is unjustified (`rubric-loop-selection` S1).

| Route | Trigger shape (axes) | Loop topology + reference | Compose with (L4 + L5 + dispatch) | Strongest rejected alt(s) + why |
| --- | --- | --- | --- | --- |
| **R0 Single call** | A5 short · A2 monolithic · A4 narrow | One augmented LLM call (retrieval + tools) — _no reference; the null option_ | L5 trivial; run the oracle once if one exists | _Any loop_ — over-engineering; latency/cost with no accuracy gain (Anthropic's primary warning). |
| **R1 Ralph** | A1 oracle · A2 checklist · greenfield · unattended · cost-asymmetric | Fresh-context `while`-loop, one task/iter, state in git + plan + progress file (`ralph.md`) | **L4** commit-gate = tests/typecheck (must test REAL behavior, not a stub). **L5** fresh context per iter; termination = plan-ledger-empty + `--max-iterations` (primary backstop) + no-progress detector; durability = git-per-iter; hard budget cap. **Dispatch** overnight/background. | _Spec-Driven (R2)_ — Ralph tramples brownfield invariants (greenfield-only); _Orchestrator-workers (R4)_ — non-deterministic multi-agent over a Ralph loop is "a red-hot mess." |
| **R2 Spec-Driven / EPCC** | A1 oracle · A2 sequence · brownfield · team-reviewed | Explore (read-only) → Plan (written, human-gated) → Code (verify-driven) → Commit (`spec-driven.md`) | **L4** machine gate (test/build/lint/screenshot-diff) **+** human plan-approval gate. **L5** spec persisted to disk (survives compaction); fresh session for CODE; commit-per-task durability. **Dispatch** foreground or async-with-PR. | _Ralph (R1)_ — no respect for existing invariants; _jump-straight-to-code_ — solves the wrong problem with no explore/plan stage. |
| **R3 Auto-Research** | A2 + A3 independent breadth · exceeds one window · A8 high-value | Orchestrator → N parallel researchers (isolated contexts) → compress → **cite/verify** → single writer (`auto-research.md`) | **L4** separate citation/verify pass (**add** a source-authority/corroboration check — shipped systems attribute, they don't fact-check). **L5** context isolation + per-subagent compression + plan→external memory; bound fan-out width, depth, per-subagent tool-calls, outer iterations. **Dispatch** async/batch. | _Single-agent ReAct research (R8/R3-lite)_ — too slow/sequential for breadth, right only for depth-first/low-value; _parallel writers_ — disjointed report, so writing stays single-threaded. |
| **R4 Orchestrator-workers** | A2 runtime-discovered · specialists · A7 open | Supervisor routes subtasks; **handoff** (control-transfer, full ctx) **or** **delegation** (agent-as-tool, isolated) (`orchestrator-workers.md`) | **L4** validator/citation/guardrail/HITL stage independent of supervisor self-judgment + system-level LLM-as-jury eval. **L5** shared-vs-isolated context chosen _deliberately_; effort scaled to complexity; checkpointed durable state for long runs. **Dispatch** often async fleet. | _Single-threaded agent (R8)_ — correct when decisions must agree / parallel writes exist (Flappy-Bird); _over-decomposition_ — 50 subagents for a simple query. |
| **R5 Plan-Execute** | A2 fixed sequence · N>3 · foreseeable deps | Strong planner (once) → cheap executors (per step, no replan) → replanner (respond \| revise) (`plan-execute.md`) | **L4** replanner is a coarse gate — **add** a separate critic/tests between execute and respond. **L5** plan = durable scratchpad; executor context isolated; max-replan cap + no-progress guard; DAG scheduling if steps independent. **Dispatch** foreground. | _ReAct (R8)_ — cheaper to first action for N≤3 but re-feeds everything (pricier at scale); _pure ReWOO (no replan)_ — brittle when intermediate results reshape the path. |
| **R6 Evaluator-optimizer** | A1 (any gate) · clear criteria · refinement helps | Generator ⇄ Evaluator/judge loop until PASS or cap (`evaluator-optimizer.md`) | **L4** this **IS** the gate — order by trust (oracle > reference > judge > self); use a separate generator/judge model. **L5** accumulating attempt+feedback memory; **max-iter cap + return-best-not-last + anti-oscillation**; budget ≈ 2N calls. **Dispatch** foreground. | _Self-judge on pure reasoning_ — degrades accuracy (DeepMind); _oracle-label illusion_ — if the stop secretly needs ground truth, the loop won't reproduce in deployment. |
| **R7 Ensemble** | A4 wide + diverse · A1 aggregatable · A8 ok | self-consistency (vote) → debate / MoA / jury, escalating (`debate-ensemble.md`) | **L4** the ensemble **is** the verification (consensus / majority-refute). **L5** fork-and-aggregate (isolated per agent); width N + rounds R near sweet spot (~3 agents / 2 rounds; ~6 proposers / 3 layers; ~3 jurors); fallback-to-single on easy/agreeing items. **Dispatch** foreground/batch. | _Single strong pass (R0)_ — loses only on genuinely diverse+verifiable problems; _debate over self-consistency_ — at equal budget often no better (the ensemble/voting effect does the work). |
| **R8 Autonomous agent** | A7 open-ended · A6 sandboxed · A8 premium ok | ReAct loop (Thought→Action→Observation); + Reflexion cross-attempt retry if a per-attempt reward exists (`react-reflexion.md`) | **L4** environment/tool feedback = ground truth; add HITL checkpoints for stakes. **L5** accumulating trajectory (+ ToT/backtrack if a value heuristic exists); **hard max-iteration + budget cap**; no-progress detector. **Dispatch** foreground or async-in-sandbox. | _Workflow (R5 / anthropic-workflow-patterns)_ — cheaper & safer when step count is predictable; _Reflexion w/o a real evaluator_ — retries chase a bad signal. |
| **R9 Self-improving** | task class repeats · cheap held-out utility · recurring failure class | Outer meta-loop: inner body → reflect → mutate durable artifact (skill/prompt/tool/lesson) → **measure on held-out** → persist-if-better (`self-improving.md`) | **L4** held-out utility gate (gaming-resistant, ≥ generator strength) + functional/regression gate + safety overseer. **L5** artifact = external memory; archive (not greedy) for stepping-stones; bounded iterations + plateau stop; curation/dedup. **Dispatch** usually batch/offline. | _Greedy retention_ — one bad self-mod degrades all descendants (DGM); _self-improve with no held-out utility_ — optimizes vibes, reward-hacks. |

**Routes with no own rubric.** `anthropic-workflow-patterns` (plain chaining / routing / parallelization — score with `rubric-loop-selection` + the sub-pattern's family rubric, e.g. parallelization → `rubric-debate-ensemble`) and `async-oversight` (score with `rubric-loop-control`; hand UX to the sibling).

---

## §4 — The A1 × A4 gate-selection matrix

After the body is chosen, pick the **verification/ensemble sub-step** from the two axes that determine which gate is _trustworthy_: A1 (what oracle exists) and A4 (how wide the solution space is).

```text
            A4 narrow (one likely path)            A4 wide (diverse paths/answers)
          ┌──────────────────────────────────────┬──────────────────────────────────────┐
A1 oracle │ gate on the ORACLE (tests/schema/lint)│ sample-K + vote, oracle-checked       │
          │ — strongest, least gameable           │ (self-consistency on a verifiable task)│
          ├──────────────────────────────────────┼──────────────────────────────────────┤
A1 judge  │ Evaluator-optimizer with a SEPARATE   │ Debate / MoA / jury of DIVERSE         │
          │ judge model; mitigate self-preference │ families; consensus = the gate         │
          ├──────────────────────────────────────┼──────────────────────────────────────┤
A1 none   │ adversarial-verify panel (N skeptics, │ ensemble for robustness only; treat    │
          │ majority-refute) as best proxy gate   │ consensus as NECESSARY-NOT-SUFFICIENT  │
          │                                       │ (correlated error across same-model)   │
          └──────────────────────────────────────┴──────────────────────────────────────┘
```

**Rules (the gate trust ladder):**

1. Prefer the **highest rung** the success criterion affords: **executable oracle > ground-truth comparison > LLM-judge/panel > self-grade.**
2. **Verifier ≥ generator** in strength. A weak verifier on a strong generator _hurts_ — it rejects good outputs and rubber-stamps bad ones.
3. **Never** let an **unaudited LLM-judge or same-model self-grade** be the sole gate on correctness-critical work (self-preference bias + reasoning degradation are documented). If only self-grade is available, say so, add mitigations (separate judge, return-best-not-last, anti-oscillation, iteration cap), and lower the confidence.
4. The **adversarial-verify panel** (N skeptics each told to refute; majority-refute kills the claim) is a **droppable sub-step** after _any_ body's generation — it is a gate, not a topology.
5. Beware the **oracle-label illusion**: the _stop_ decision must not secretly depend on a ground-truth oracle that won't exist in deployment, or the loop won't reproduce.

---

## §5 — L5 instantiation table (mandatory for every route)

Every route instantiates all five control-plane sub-systems. Omitting any one makes the blueprint incomplete (`rubric-loop-control` gates C1/C2/C3/C7). Full treatment in `control-plane.md`.

| Sub-system | Decision for this goal | Defaults by route |
| --- | --- | --- |
| **Termination** `[gate]` | Layer it: **goal-gate** (oracle passes / explicit COMPLETE marker) → **no-progress-K** (flat rounds / tool-call repetition / >~85% state-similarity) → **hard caps** (max-iter + budget). Enforce **outside the model**. Add a STUCK/abort path so impossible tasks escalate instead of iterating into damage. | R1: ledger-empty + `--max-iterations`. R5: respond-marker + max-replan. R6: PASS + cap + best-of-N. R8: env-success + hard cap. R9: plateau + bounded iters. **Never** "the model decides it's done" alone. |
| **Context** `[review]` | Pick a point on **fresh ↔ accumulating ↔ compaction-bridged**; name the external-memory substrate + the cross-iteration handoff schema. | R1/R3: **fresh/isolated** + external files (git/plan/progress). R6/R8: **accumulating** (+ compaction near limit). R4: shared-vs-isolated chosen _deliberately_ — share full traces when decisions must agree. R9: artifact is the memory. |
| **Verification** `[gate]` | The L4 gate from §4, ordered by trust. Tie it to termination (the goal-gate). | (see §4 matrix) |
| **Budget** `[gate]` | **Advisory pace budget** (countdown) **+ hard `max_tokens`/cost ceiling**; size against p99 task length, not a framework default. Concrete numbers, not "tune as needed." | Ensemble/research/fan-out/self-improving: explicitly weigh the **3–15× premium** vs value; gate spend to high-stakes / high-disagreement items; runaway-cost circuit-breaker mandatory on any `while :;`. |
| **Durability** `[gate]` | Checkpoint at step boundaries with a resume key; require **idempotent** tool calls (at-least-once replay safe). | Long/unattended (R1, R3, R4-fleet, async): **mandatory**. Short foreground (R0, R5, R6): skip (YAGNI). |

---

## §6 — Emitted blueprint skeleton

The router emits this per goal. (The full 14-field PLAN/COMPOSE `ORCHESTRATION BLUEPRINT` lives in `SKILL.md` §Output Contract and is checked by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`; this is the router's compact form that feeds it.)

```text
Goal: {feature/task} → {desired outcome}
Axis read: A1 {oracle?} · A2 {decomp} · A3 {independence} · A4 {width}
           · A5 {horizon} · A6 {stakes} · A7 {open-ended?} · A8 {budget}

ROUTE  : {R# + name} via Q{n}  →  reference: references/{topology}.md
BODY   : {loop topology in one line}
L4 GATE: {oracle | evaluator-optimizer | adversarial panel | ensemble} — {why this rung; verifier ≥ generator?}
L5     : termination={layered stop} · context={posture + external store} · verification={→ §4}
         · budget={pace + hard ceiling, as numbers} · durability={checkpoint + idempotency, or N/A}
DISPATCH: {foreground | async+PR | scheduled | fleet} · oversight={in-loop gate | on-loop PR}
PARAMS : {concrete knobs — fan-out width, max-iter, budget ceiling, vote threshold, N×R, model-per-role}

REJECTED:
  1. {alt} — {why it loses on THIS goal's axes}
  2. {alt} — {why}      (MUST include why a single call / minimal Ralph loop was/wasn't enough)

TRUST  : {untrusted content ingested? credentials/privilege in transit; blast radius of one poisoned input; containment if trifecta-exposed (content/action split) — field 14 (A9)}
RUBRICS: rubric-loop-selection + rubric-loop-control + rubric-plan-quality + {family rubric for R#}
HANDOFF: run the sibling agentic-ux skill on this if autonomy / async / high-stakes.

VERDICT: BLUEPRINT — UNVERIFIED  (until dry-run/sanity-checked against the success criterion)
```

---

## §7 — Two worked router traces

Proof the procedure executes end-to-end on real goals.

### Trace A — _"create the best plan to add OAuth login to our existing Rails app, all tests green."_

- **STEP 0 axis read:** A1 **oracle** (test suite) · A2 fixed-ish sequence · A3 mostly serial (shared codebase) · A4 narrow · A5 medium · A6 **brownfield, medium stakes** · A7 predictable · A8 cost-ok.
- **STEP 1 gates:** Q1 no (multi-file, several turns) → Q2 **yes** (oracle + checklist) → Q2a no (brownfield, must respect existing auth/session invariants) → **Q2b → R2 Spec-Driven / EPCC.** Reference: `spec-driven.md`; family rubric `rubric-plan-execute`.
- **STEP 2 L4 gate (§4, A1=oracle × A4=narrow):** gate on the oracle — RSpec green + lint — **plus** a human plan-approval gate (stakes + brownfield).
- **STEP 3 L5:** termination = all planned tasks committed + RSpec green; context = spec persisted to `PLAN.md` on disk (survives compaction), fresh session for CODE; verification per §4; budget = bounded task count, foreground (no large premium); durability = commit-per-task.
- **STEP 4 dispatch:** foreground or async-with-PR; **on-the-loop** review at the diff boundary.
- **STEP 5 REJECTED:** **R1 Ralph** — would trample existing auth/session invariants (greenfield-only); **R8 autonomous** — step count is predictable, so a workflow is cheaper and safer. _Single call ruled out:_ multi-file change across several turns with an oracle worth iterating against.
- **RUBRICS:** loop-selection + loop-control + plan-quality + `rubric-plan-execute`. **VERDICT:** BLUEPRINT — UNVERIFIED until dry-run against "all tests green."

### Trace B — _"create the best plan to produce a cited competitive landscape of the top 8 vector databases."_

- **STEP 0 axis read:** A1 judge/citation (**no executable oracle**) · A2 **independent** sub-topics · A3 **independent** (per-vendor) · A4 breadth · A5 long, exceeds one window · A6 low-stakes/reversible · A7 semi-open · A8 **high-value, premium ok.**
- **STEP 1 gates:** Q1 no → Q2 no (no executable oracle) → **Q3 yes** (independent breadth-first research exceeding one window, high-value) → **R3 Auto-Research fan-out.** Reference: `auto-research.md`; family rubric `rubric-auto-research`.
- **STEP 2 L4 gate (§4, A1=none/judge × A4=wide):** separate citation/verify pass + **add** a source-authority/corroboration check (shipped systems attribute, they don't fact-check); treat consensus as necessary-not-sufficient.
- **STEP 3 L5:** termination = all 8 vendor tracks returned + report assembled + outer-iter cap; context = isolation per researcher + per-subagent compression on return + plan→external memory; budget = explicit ~15× premium accepted, hard ceiling set; durability = checkpoint per returned track.
- **STEP 4 dispatch:** async/batch; **on-the-loop** review of the assembled report.
- **STEP 5 PARAMS:** fan-out = 8 (one vendor each), depth ≈ 2, per-subagent tool-calls ≈ 10, outer-iters ≈ 6, single writer. **REJECTED:** **R3-lite single-agent ReAct research (R8)** — too slow/sequential for 8 independent tracks, and breadth exceeds one window; **parallel writers** — disjointed report, so writing stays single-threaded after all research completes. _Single call ruled out:_ breadth exceeds one context window.
- **RUBRICS:** loop-selection + loop-control + plan-quality + `rubric-auto-research`. **HANDOFF:** async + multi-agent → run the sibling `agentic-ux` skill for the operator-UX pass. **VERDICT:** BLUEPRINT — UNVERIFIED until the fan-out is sanity-checked against "cited landscape of 8."

### Trace C — Naive pick: orchestrator-workers. Router selects: Ralph (R1). _"Create the best plan to generate 50 GDPR-compliant email templates from our brand voice guide."_

**Why the naive pick fails here:** "50 tasks → orchestrator-workers" is the instinctive guess. But the router's ordered gates reveal a cheaper, safer shape.

- **STEP 0 axis read:** A1 **LLM-judge** (brand-voice rubric — no executable oracle) · A2 **fixed checklist** (50 known templates) · A3 **fully independent** (each template is self-contained; no shared mutable state) · A4 narrow (one voice, one brand) · A5 short-to-medium · A6 **low-stakes, reversible** (templates are text) · A7 **predictable** count and step structure · A8 **cost-sensitive** (50 templates × multi-agent premium = significant spend).
- **STEP 1 gates:** Q1 **yes** — independent items + predictable count + automated quality gate (judge per template) → **R1 Ralph / brute-force loop.** Reference: `ralph.md`; family rubric `rubric-ralph-loop`.
- **STEP 2 L4 gate:** LLM-judge per template (brand-voice rubric), separate judge model; A4=narrow so self-consistency adds nothing.
- **STEP 3 L5:** termination = ledger-of-50 empty + judge-pass per item; context = fresh per template (each is independent; accumulating context buys nothing); budget = concrete per-template ceiling; durability = commit per batch of 10.
- **REJECTED — the naive pick:** **R4 Orchestrator-workers** — would add supervisor overhead, inter-agent coordination cost, and a synthesis step where none is needed. Templates are fully independent; there is no runtime decomposition decision to make. Orchestrator-workers is the right shape when subtask selection is _uncertain at dispatch time_; here the 50 are fully known. **~4–10× token premium** vs Ralph with zero quality benefit. Single call ruled out: 50 templates exceed one session.
- **RUBRICS:** loop-selection + loop-control + plan-quality + `rubric-ralph-loop`. **VERDICT:** BLUEPRINT — UNVERIFIED until 3–5 sample templates pass the brand-voice judge.

---

### Trace D — Naive pick: single call. Router selects: evaluator-optimizer (R6). _"Create the best plan to produce a compelling 200-word executive summary of this 40-page technical report."_

**Why the naive pick fails here:** "Just ask Claude to write it" is correct for low-stakes summaries. The quality bar changes the calculus.

- **STEP 0 axis read:** A1 **LLM-judge** (executive clarity rubric — no executable oracle) · A2 monolithic (one output) · A3 N/A (single output) · A4 **narrow** (one best summary, not diversity of approaches) · A5 short (≤3 turns) · A6 **low stakes / reversible** (text) · A7 predictable · A8 **quality premium accepted** (the summary is the deliverable).
- **STEP 1 gates:** Q1 no (no executable oracle) → Q2 no (not a checklist) → Q3 no (not breadth-first) → Q4 no (not runtime-decomposed) → Q5 no (not a fixed sequence) → Q6 **yes** — explicit quality bar + iterative refinement demonstrably adds value on a constrained, single-output writing task → **R6 Evaluator-optimizer.** Reference: `evaluator-optimizer.md`; family rubric `rubric-evaluator-optimizer`.
- **STEP 2 L4 gate (§4, A1=judge × A4=narrow):** evaluator-optimizer with a **separate judge model** (executive-clarity rubric) rating structure, brevity, and decision-orientation; A4=narrow means sample-and-vote would just average toward mediocrity.
- **STEP 3 L5:** termination = judge score ≥ 4/5 or max 3 revisions (return best-not-last); context = accumulating within the session (short enough; generator sees the report + prior drafts + judge feedback); budget = 3 generation passes ceiling; durability = N/A (short foreground).
- **REJECTED — the naive pick:** **Single call** — empirically produces "good" output; evaluator-optimizer produces "publication-ready" on a verifiable quality bar. _When to collapse back:_ if the judge consistently scores the first draft ≥ 4/5 across 5 trials, collapse to a single call with the judge as a spot-check only. **R3 Auto-Research** — irrelevant; the source material is already provided. Single call ruled out: the explicit quality bar with a judge rubric is the trigger condition for R6 (Q6 was the discriminating gate).
- **RUBRICS:** loop-selection + loop-control + plan-quality + `rubric-evaluator-optimizer`. **VERDICT:** BLUEPRINT — UNVERIFIED until first generate→critique→revise cycle confirms judge scores improve across iterations.
