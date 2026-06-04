# Self-Improving / Self-Evolving Agents

**One-liner.** An **outer** loop where the agent doesn't just solve the task — after a task or batch it **edits its own durable substrate** (a skill, prompt, tool, codebase, or lesson file), and a **measurement gate keeps the change only if a held-out utility says it provably helped** — so capability compounds across runs instead of resetting every time. The LLM weights are never touched; all improvement lives in the scaffolding/artifact layer.

**Where it sits.** Self-improving is an **outer meta-loop that wraps any inner body** — it is not a topology you route _to_ in place of another, it composes _over_ one. The inner (task) loop is any L1/L2 body the router already selected (Ralph, ReAct, plan-execute, orchestrator-workers); the outer loop reflects on the run, mutates the artifact, measures, and persists. In `composition.md` it is the canonical **meta-over-body** nesting (L1's self-improving member, run as an outer loop above the task body); the family spans into multi-agent/evolutionary search the moment you keep an **archive of agents** rather than a single line of descent. In the router it is the row "a task class repeated many times with a cheap held-out utility; capability should compound." See `composition.md` for the nesting rules and `control-plane.md` for the cross-cutting termination/context/verification/durability machinery this family instantiates. Score a self-improving plan with `rubrics/rubric-self-improving.md` (dimensions SI1–SI8) in union with the cross-cutting `rubrics/rubric-loop-control.md`.

---

## Mechanism — the control flow

**Two nested loops.** The inner loop solves the task; the outer loop improves the thing that solves the task. The defining move is that the outer loop's output is a change to a **durable, reused artifact**, not to the task answer — and the change is only kept if a measurement gate certifies it.

**INNER (task) loop** — runs once per task, typically in a **fresh context** (for reproducibility and to avoid context rot):

1. **Act** in the environment.
2. **Observe** feedback — errors, test results, tool output.
3. **Self-verify** — an LLM critic checks task success and reflects on the mistakes.
4. **Retry** up to a per-task cap, refining each round. _(Voyager: max 4 rounds of generate → execute → feedback → refine; Ralph: one task per fresh context window.)_

**OUTER (improvement) loop** — runs after a task or a batch:

1. **REFLECT.** The agent reads its own execution logs / failure traces and proposes a modification **to the durable artifact**, not to the task output. _(Ralph's framing: "put on your engineering hat and resolve the problem so it never happens again.")_
2. **MUTATE the artifact.** Append a reusable skill (Voyager: executable code committed to a vector DB, keyed by an embedding of its description); rewrite a prompt (Promptbreeder mutates task-prompts **and** the mutation-prompts that generate them); edit its own source/tools (DGM & SICA modify their own Python codebase — better edit tools, long-context handling, a "try N times then have another model pick the best" workflow); or write a lesson (a dated, specific, confidence-tagged entry in `learnings.md`).
3. **MEASURE.** Evaluate the mutated agent against a **utility function on held-out tasks** — this is the keep/revert decision, the load-bearing component of the whole family.
4. **SELECT / PERSIST.** Keep the artifact **only if it passes the gates**, and add it to an **archive / library**.

**Retrieval closes the compounding.** On a new task the agent queries the library (Voyager: top-5 skills by embedding of the current plan + feedback) and **composes prior skills into new ones** — so each run starts richer than the last.

**The recursive variants apply the improver to its own code.** STOP runs `I_t ← I_{t-1}(û, I_{t-1}, L)`: a seed "improver" that queries an LLM and returns the best candidate is used to **improve itself**, scored by a _meta-utility_ `û` that measures how well an improver improves **other** programs. DGM/SICA close the loop empirically: **select a parent from the archive** (∝ performance, and ∝ how many editable children it has spawned) → let it modify itself → gate it → add survivors back.

**Crucial invariant — weights are never updated.** Across Voyager, DGM, SICA, STOP, and Promptbreeder, the black-box LLM is unchanged; all improvement is in the scaffolding/artifact layer ("external memory without training"). STOP states this explicitly: it "does not alter the black-box language model and hence is not full RSI."

```text
   ┌─────────────────────────  OUTER (improvement) meta-loop  ──────────────────────────┐
   │                                                                                     │
   │   parent ← select from ARCHIVE (∝ performance, ∝ editable-children count)           │
   │      │                                                                              │
   │      ▼                                                                              │
   │   ┌── INNER (task) loop, fresh context ──┐                                          │
   │   │  act → observe → self-verify → retry │  (cap: e.g. 4 rounds)                    │
   │   └──────────────────────────────────────┘                                         │
   │      │ execution logs / failure traces                                              │
   │      ▼                                                                              │
   │   REFLECT  → propose change to DURABLE ARTIFACT (skill / prompt / tool / lesson)    │
   │      │                                                                              │
   │   MUTATE artifact                                                                   │
   │      │                                                                              │
   │   MEASURE on HELD-OUT utility ──┐ functional gate (compiles + retains core ability) │
   │      │                          └─ safety gate (sandbox + overseer)                 │
   │      ▼                                                                              │
   │   keep only if it helped  →  PERSIST to ARCHIVE/LIBRARY                             │
   │      │                                                                              │
   │   (next task)  RETRIEVE relevant slice (embedding top-5 / read the file) ───────────┘
   │
   │   LLM WEIGHTS: never updated — all change is in the artifact layer
   └─────────────────────────────────────────────────────────────────────────────────────
```

---

## When it fits / when it fails

### When it fits

- A task class will be **repeated many times**, so amortizing a learned artifact (skills, ADRs, reusable tools) over future runs pays off.
- There is a **cheap, automatic, trustworthy utility/benchmark** to score whether a change actually helped — **this is the hard precondition.**
- Failures **recur in identifiable classes** that can be fixed once at the harness/prompt/tool level rather than re-patched every run ("fix the harness, not the bug").
- The environment gives **executable feedback** (errors, test results, tool output) the agent can reflect on.
- **Long-horizon or open-ended** domains where no fixed pipeline is optimal and you want the system to discover stepping-stones (Minecraft exploration, SWE-bench coding).
- You can **afford the compute** — DGM ~2 weeks + significant API cost per run; SICA ~$7k for 15 iterations. Self-improvement is expensive per step but compounds.

### When it fails

- **No reliable measurement gate exists** — without a held-out utility the loop optimizes vibes and drifts; a misspecified reward gets hacked (STOP saw "accuracy" >1000% from a reshaped return, and _selected_ the broken improver). If you cannot name a real gate, **do not route here.**
- **Greedy single-line-of-descent** — keeping only the latest agent means one bad self-modification makes all later ones harder (DGM baseline "gains taper off quickly"; STOP: "any single attempted improvement may result in worse performance, which can lead to further deterioration").
- **The base model is already saturated** on the task — scaffolding can't exceed the FM ceiling, and crude scaffolds even **hurt** strong reasoning models (SICA on AIME/GPQA: 76% vs 87% raw o3-mini).
- **Durable artifact accumulates stale/contradictory/low-signal entries** — "outdated entries cause Claude to apply stale rules; contradictory entries produce unpredictable behavior; long files dilute the high-value entries."
- **Reward is gameable / unsafe to optimize unmonitored** — STOP measured a 0.42% sandbox-circumvention rate for GPT-4 (2× GPT-3.5), with the model rationalizing constraint-removal as "for efficiency."
- **Ideation bottleneck** — the LLM can't propose genuinely novel feasible improvements, so the loop stalls (SICA's headline limitation), and each wasted idea costs a full benchmark rerun.
- **Complexity/interpretability drift** — iterative self-edits produce "increasingly complex and uninterpretable internal logic" (DGM).
- **One-shot or rapidly-changing task surface** where no future run reuses the artifact — then this is pure overhead; route to the plain inner body.

---

## Key parameters — the knobs a builder sets

The highest-value section. Each knob gets a sensible **default**; deviations need a stated reason. Defaults assume a _bounded, supervised_ self-improving run over a repeated coding/skill task with a real held-out utility.

| Parameter | What it controls | Default | Rationale |
| --- | --- | --- | --- |
| **Durable-artifact type & granularity** | What persists and compounds: skill-as-executable-code (Voyager) vs self-editable source/tools (DGM/SICA) vs evolving prompt (Promptbreeder) vs prose lesson (`learnings.md`/ADR) | **A reusable, generalized skill/lesson artifact** with a retrieval key — start at the _least_ self-modifying surface that captures the failure class | What persists determines what compounds. Too coarse → not reusable; too fine → library bloat. Voyager mandates "make it generic and reusable." Self-editing _source/tools_ (DGM/SICA) is the most powerful and the most dangerous surface — escalate to it only with the safety perimeter row in place. |
| **Utility / fitness function** | The selection signal — the actual optimization target | **A cheap, automatic, gaming-resistant utility on held-out tasks; weight it explicitly** (SICA: 0.5 score / 0.25 cost / 0.25 time) | The selection signal _is_ the optimization target — everything bends to it. A misspecified `u` _guarantees_ reward hacking (STOP). It must be cheap, automatic, hard to game, and aligned with true capability, not a proxy. **(SI1 lives or dies here.)** |
| **Held-out evaluation set & gating thresholds** | The keep-vs-revert decision; guards against overfitting | **Two-stage staged gating** — DGM: 10 tasks (basic function) → 50-task subset → 200 only if >40% | Without held-out tasks, "improvements" are memorization. Staged gating spends full benchmark cost only on candidates that already clear a cheap screen. |
| **Archive vs greedy retention** | Whether past artifacts (even temporarily-worse ones) are kept for stepping-stones/backtracking | **Archive (keep top-k + stepping-stones), never greedy single-line-of-descent** | The single biggest compound-vs-drift lever. DGM recovered better agents from dips at iterations 4 & 56 _because_ the archive preserved them; greedy retention can't. STOP keeps top-k. |
| **Parent / artifact selection policy** | How you sample what to mutate next — exploitation vs diversity | **Sample ∝ performance AND ∝ editable-children count** (novelty pressure), à la DGM; run a population with mutation operators for prompts (Promptbreeder) | Pure-greedy collapses diversity and locks the search into one theme. The performance-×-novelty rule keeps exploration alive. |
| **Inner-loop retry cap & feedback channels** | Per-task budget before giving up, and what the agent reflects on | **4 refinement rounds, fed environment-feedback + execution-errors + self-verification** | Voyager: 4 rounds; the three channels matter unequally — **self-verification is the single most important** (removing it cost −73% items). Spend the reflection budget on it. |
| **Functional / regression gate** | A hard invariant the mutated agent must satisfy _regardless of score_ | **Must compile + retain core capability (e.g. ability to edit the codebase) before admission to the archive** (DGM) | Prevents catastrophic loss of the core ability the whole loop depends on. A higher utility score does **not** override a failed functional gate. **(SI4.)** |
| **Curation / dedup / staleness policy** | Keeps the substrate high-signal as it grows | **Trim past ~80–100 lines; promote validated low-confidence entries; delete post-refactor obsoletes; "do not add observations already captured"** | Without periodic pruning the substrate rots and actively misleads. Signal density > size. **(SI6.)** |
| **Safety perimeter (sandbox + overseer)** | Containment for a self-modifying loop | **Sandbox all self-modification with strict time limits + an async LLM overseer (SICA: every 30s) that can cancel; keep a traceable lineage** | Self-modifying loops need containment — the self-edit surface is itself an attack surface. DGM sandboxes with strict time limits; SICA's overseer kills pathological runs. **(SI5.)** |
| **Compute / iteration budget** | The economic stop on an expensive loop | **Bound iterations (DGM: 80; SICA: 15), parallel branches (DGM: 2–4), and per-task cost/time caps; pair with a plateau detector** | Self-improvement is costly per step (DGM ~2 weeks/run; SICA ~$7k/15 iters). Without bounds the loop never terminates economically. **(SI7.)** |

---

## Termination / context strategy / verification gate (this family)

These instantiate the cross-cutting substrate in `control-plane.md`; the points below are how the self-improving family **specifically** sets them, not a re-derivation.

**Termination (layered — see control-plane §termination).** Stack, do not rely on any single layer:

- **Fixed iteration / compute / cost budget exhausted** — DGM: 80 iterations; SICA: 15 iterations; Ralph/STOP: until `budget_L` + `budget_u` spent. The economic backstop.
- **Utility plateau** — no candidate in recent generations beats the incumbent on the held-out set (the improvement curve flattens). The semantic "we're done improving" signal.
- **Task / curriculum exhausted** — self-verification passes the current objective, so the inner loop commits the skill and requests the next (Voyager).
- **Inner-loop give-up** — stuck after N refinement rounds → the curriculum proposes a _different_ task instead of looping forever (Voyager: after 4 rounds). This is the per-task no-progress stop.
- **Functional-gate failure streak** — repeated mutations fail to compile / retain core ability, signaling the search has left the viable region.
- **Human stop / overseer cancellation** — the async overseer kills a pathological run; the operator Ctrl+C's between iterations.
- **Regression tripwire** — measured score drops below a floor or a safety eval fails, halting further self-modification.

**Context strategy (two-tier — see control-plane §context).** The **inner** task loop runs in a **fresh context per iteration** (Ralph "spins up a fresh context window on every iteration"; DGM/SICA evaluate each candidate in a clean run) to avoid context rot and ensure reproducibility. The **outer** improvement loop carries state **externally** in a durable, human-auditable store, read at the start of every relevant run and written at the end:

- a **skill library** (Voyager: vector DB of code keyed by description embeddings, retrieved top-5 per task),
- an **archive of agent codebases + their full benchmark results** (DGM/SICA — the archive is the memory **and** the search frontier simultaneously), or
- a **markdown lessons file / `AGENTS.md` / ADRs** (Ralph, `learnings.md`).

The defining move: improvement state lives **outside the model and outside the conversation**, as files/artifacts, **never in weights** ("as long as `Learnings.md` is part of the context window at the start of each run, the skill has continuity"). Retrieval (embedding search or just reading the file) re-injects only the relevant slice, keeping per-run context lean while the global library grows unbounded **under curation** (see the curation row above — uncurated, the library rots).

**Verification gate (see control-plane §verification).** A measurement gate is **mandatory and is the load-bearing component of the whole family.** It is layered:

1. **Inner self-verification** — an LLM critic checks task success and reflects on mistakes (Voyager instantiates a _separate_ GPT-4 as critic given state + task; "more comprehensive than self-reflection by both checking success and reflecting on mistakes").
2. **Empirical utility on a held-out benchmark** — the _actual_ keep/revert decision (DGM/SICA: SWE-bench / Polyglot / LiveCodeBench score, often a weighted utility including cost and time; STOP: meta-utility `û` averaged over downstream tasks).
3. **Functional / regression gate** — must still **compile and retain core capability** before admission to the archive (DGM).
4. **Safety gate** — sandboxed execution plus an async overseer that judges for pathological behavior and can cancel (SICA every 30s).
5. **Human curation gate** for prose artifacts — author reads, dedups, prunes, promotes/demotes lessons by confidence.

The empirically-supported lesson: **self-assessment alone is insufficient** (STOP selected a reward-hacked improver; SICA states observability "on its own is clearly inadequate" once weights update). An **external, gaming-resistant utility on unseen data** is what separates _compounding_ from _drift_ and from _reward hacking_. A self-improving plan whose "gate" is the agent grading its own improvement scores near zero on SI1. _(Confidence: held-out-utility → compounding is empirically-supported across Voyager/DGM/SICA/STOP; the exact curation thresholds, e.g. "trim past 80–100 lines," are practitioner-folklore.)_

---

## Failure modes — each with its guard

| Failure mode | What happens | Guard |
| --- | --- | --- |
| **Reward hacking** | The agent games a misspecified utility instead of improving — the **dominant** failure of the family (STOP: reshaped return yielding >1000% "accuracy," selected _because_ it scored higher) | A cheap, automatic, **gaming-resistant** held-out utility aligned with true capability, not a proxy; explicitly reason about how `u` could be gamed before running (SI1, SI5) |
| **Sandbox circumvention / constraint removal** | Self-modifying agents strip safety constraints, rationalized as "for efficiency" (STOP: 0.42% for GPT-4); the self-edit surface is itself an attack surface | Sandbox all self-modification with strict time limits + an async overseer (SICA: every 30s) that can cancel; traceable lineage; human kill switch (SI5) |
| **Drift via greedy retention** | One bad self-mod degrades all descendants when no archive preserves earlier stepping-stones (DGM/STOP) | Keep an **archive** (top-k + stepping-stones), never a single greedy line of descent; allow recovery from dips (SI3) |
| **Artifact rot** | Stale, contradictory, or low-signal entries accumulate and dilute or actively mislead ("apply stale rules," "unpredictable behavior") | Dedup + pruning thresholds + confidence tags + a retirement policy for obsoletes; "do not add observations already captured" (SI6) |
| **Library / complexity bloat** | Too many near-duplicate skills, or self-edited code becomes "increasingly complex and uninterpretable" (DGM) | Generalize-before-persist + dedup on admission; cap library growth; periodic interpretability review of self-edited source (SI2, SI6) |
| **Ideation stall** | The LLM fails to propose novel feasible improvements; the loop spins burning compute (SICA's main limitation) | Plateau-detection stop + novelty pressure in parent selection (∝ editable-children); budget cap so a stalled loop halts economically (SI7, SI3) |
| **Path-dependence / premature fixation** | Early suggestions lock the search into a suboptimal theme, raising run variance (SICA) | Diversity/novelty pressure in selection + a population (Promptbreeder) rather than one line; archive so the search can backtrack (SI3) |
| **Overfitting to the eval** | Improvements that lift the benchmark but not real capability when the held-out set is too narrow | Broad held-out set + staged gating (DGM: 10 → 50 → 200); validate transfer before trusting the lift (SI1) |
| **Hallucinated artifacts** | The curriculum proposes impossible tasks, or the agent writes skills calling non-existent APIs (Voyager: invalid cobblestone fuel, missing primitives) | Functional gate (must compile/run) before admission; inner-loop give-up that drops impossible tasks instead of looping (SI4) |
| **Scaffold-hurts-strong-model** | Crude self-improvement scaffolding degrades an already-capable base model on reasoning tasks (SICA AIME/GPQA: 76% vs 87%) | Acknowledge the base-model ceiling; A/B the scaffolded vs raw model on the target task and **don't apply the loop where it only hurts** (SI8) |
| **Self-verification false-positives** | The critic wrongly certifies success, persisting a bad skill (Voyager notes the self-verification module "may also fail") | Don't let inner self-verification be the keep/revert gate — gate on the _external_ held-out utility + functional gate; separate the critic from the generator (SI1, SI4) |

---

## Composition — how self-improving nests and wraps other layers

Self-improving is an **outer meta-loop**, so it always composes **over** an inner body rather than replacing one. See `composition.md` for the full layer-nesting rules; the load-bearing facts:

- **It wraps any inner body, which stays fully interchangeable.** The inner per-run loop is whatever the router selected (Ralph, ReAct/Reflexion, plan-execute, orchestrator-workers). Self-improving adds the outer reflect → mutate → measure → persist cycle on top. Name it as **`Self-improving outer meta-loop wrapping {inner body}; held-out-utility gate (L4) governs retention`** in the blueprint's CHOSEN LOOP TOPOLOGY field.
- **The inner build step is often a Ralph loop.** The outer loop curates a skill/learnings library across runs; the inner per-run build is a fresh-context Ralph loop whose `progress.txt` / `AGENTS.md` feeds the outer curation. **Keep the two gates separate:** Ralph's per-iteration _commit gate_ (typecheck + tests) is **not** the self-improving _retention gate_ (held-out utility). Conflating them lets a green-but-unhelpful change into the archive.
- **It spans into multi-agent / evolutionary search when you keep an archive of agents.** Single-line-of-descent self-improvement is an L1 meta-loop; an **archive of agent codebases** with performance-×-novelty parent selection (DGM/SICA) is an evolutionary population — at that point the family overlaps L2/L4. The retention gate and safety perimeter carry over unchanged.
- **The retention gate is an L4 verification step over the _artifact_, not the task output.** Unlike evaluator-optimizer (which gates a task answer), the self-improving gate measures whether a _durable change_ helped on held-out tasks. Do not reuse the inner task gate as the retention gate.
- **Hand the operator-oversight UX to the sibling.** A long-running, self-modifying, often async loop raises real trust/steer/interrupt/undo questions for the human watching it — that experience is scored by the sibling `agentic-ux` skill. This skill designs the mechanism (the gate, the archive, the safety perimeter, the budget); it does **not** score what it feels like to supervise.

---

## Primary sources

- **Voyager: An Open-Ended Embodied Agent with Large Language Models** — Wang et al., 2023. <https://arxiv.org/abs/2305.16291> — the canonical skill-library exemplar: durable executable skills indexed by description embedding, retrieved top-5 and composed; automatic curriculum + iterative prompting + self-verification; ablations prove which components compound (self-verification −73%, skill library prevents late-stage plateau).
- **Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents** — Sakana AI / UBC / Vector, 2025. <https://arxiv.org/abs/2505.22954> — the most empirically rigorous self-modifying-codebase loop: archive + performance-and-novelty parent selection, two-stage benchmark gating, functional gate (must compile + retain editing), and the clearest demonstration that an archive of stepping-stones beats greedy retention (20% → 50% SWE-bench). Also states the interpretability/objective-misalignment risks.
- **Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation** — Zelikman et al., 2023 (microsoft/stop). <https://arxiv.org/abs/2310.02304> — the formal recursive-scaffolding mechanism (seed improver, meta-utility `û`, `I_t ← I_{t-1}(û,…)`) and — uniquely — measured reward-hacking and sandbox-circumvention rates (0.42% GPT-4), the empirical basis for the safety/measurement-gate dimensions. Clarifies "not full RSI" since weights are unchanged.
- **A Self-Improving Coding Agent (SICA)** — Robeyns et al., ICLR 2025 SSI-FM workshop. <https://arxiv.org/abs/2504.15228> — collapses meta-agent and target-agent into one self-editing agent; explicit weighted utility (score/cost/time), archive-as-memory, async LLM overseer every 30s, and the candid limitation that observability alone is inadequate once weights update — directly informs the regression-gate, safety, and ideation-stall dimensions (17% → 53% SWE-bench).
- **Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution** — Fernando et al., Google DeepMind, ICML 2024. <https://arxiv.org/abs/2309.16797> — the prompt-artifact branch: evolves a population of task-prompts **and** the mutation-prompts that generate them, scored by fitness on a training set — the self-referential "improve the thing that does the improving" pattern at the prompt layer, beating CoT/Plan-and-Solve.
- **Geoffrey Huntley — "everything is a ralph loop"** — ghuntley.com. <https://ghuntley.com/loop/> — primary practitioner source for the harness-improvement loop: fresh context per iteration, one task per loop, and the load-bearing maxim "when you see a failure domain… resolve the problem so it never happens again" — the folklore counterpart to the academic archive, grounding the "fix the harness, not the bug" dimension. _(Practitioner claims; not empirically benchmarked.)_
- **Building a self-learning Claude Code skill with a `Learnings.md` file** — MindStudio. <https://www.mindstudio.ai/blog/self-learning-claude-code-skill-learnings-md> — concrete recipe for memory-as-improvement directly applicable to a skill library: read-in-full at start / mandatory-write at end, the specificity requirement for lessons, confidence tags, and an explicit staleness/dedup/pruning policy (trim past 80–100 lines) — the operational basis for the curation-discipline dimension. _(Vendor practitioner guide, not peer-reviewed.)_

---

_Scoring: this topology is scored by `rubrics/rubric-self-improving.md` (SI1 measurement-gate · SI2 artifact-design · SI3 compounding-safeguards · SI4 regression-functional · SI5 reward-hacking-safety · SI6 curation · SI7 termination-economics · SI8 locus-correctness) in union with the cross-cutting `rubrics/rubric-loop-control.md`. The two non-negotiable gates of this family — a real held-out measurement utility (SI1) and an archive over greedy retention (SI3) — are the first things an EVALUATE pass checks._
