# Control Plane — termination · context · verification · budgets · durability

The cross-cutting machinery **every** loop instantiates, regardless of body shape. A plan that names a topology (Ralph, ReAct, orchestrator-workers, debate…) but does not set its five control-plane choices is **not a plan** — it is a label. This is the most rigorous reference in the skill because it is the part that actually closes the loop.

> **One thesis.** The loop body is the easy part. The control plane is the design. A "ralph loop" is not a distinct primitive — it is a _specific set of control-plane choices_ (fresh context + goal-gate termination + git durability + commit-gate verification). Change those choices and the same `while`-loop becomes a different loop. So: pick the body, then **deliberately set all five sub-systems below**, with concrete values.

The five sub-systems and what each one prevents:

| # | Sub-system | The failure it exists to prevent | Mandatory when |
| --- | --- | --- | --- |
| 1 | **Termination** | Non-termination / runaway cost; or premature-stop with a silent partial result | Always (every loop) |
| 2 | **Context** | Context rot, goal-drift, KV-cache thrash, memoryless resume | Always (even "do nothing" is a choice) |
| 3 | **Verification** | Convergence-to-slop; an unverified self-grade passing garbage | Always (the gate is the engine) |
| 4 | **Budgets** | Cost blowout; or refusal-from-too-small-a-budget masquerading as a guardrail | Always (a number, not "as needed") |
| 5 | **Durability** | Hours of work lost to a crash; double-fired side effects on replay | Long / unattended / multi-agent only (N/A for short foreground — YAGNI) |

These four–five choices map 1:1 to the `rubric-loop-control` dimensions: C1 termination-stack, C2 budget, C3 verification-gate, C4 context-posture, C5 external-memory, C6 no-progress-signal, C7 durability-idempotency, C8 observability. Filling this reference's five sections **is** clearing that rubric.

---

## 1 — TERMINATION (layered; enforced outside the model)

**The load-bearing rule** _(empirically-supported across Ralph, Manus, agent-harness practice)_: **progress detection and stop rules must be enforced OUTSIDE the model, because the model will always be tempted to try one more thing.** A stop condition that lives in the prompt ("stop when you think you're done") is not a stop condition. The controller that decides continue/halt runs in the harness, after the model call returns, reading objective signals.

Stop signals compose in **priority order** — each catches a failure the others miss. A real termination stack has all three layers plus an escape hatch:

```text
  after each loop-body iteration, the stop-controller (OUTSIDE the model) checks, in order:

  (a) GOAL-SATISFACTION GATE  ──► halt: SUCCESS
        objective oracle passes  (tests green / build succeeds / schema validates)
        OR an explicit COMPLETE marker is emitted by the agent
              │ not satisfied
              ▼
  (b) STUCK / ABORT MARKER  ──► halt: ESCALATE (do NOT iterate into damage)
        agent emits explicit STUCK (task impossible / ambiguous / blocked)
              │ not stuck
              ▼
  (c) NO-PROGRESS / LOOP-UNTIL-DRY DETECTOR  ──► halt: CONVERGED (or STALLED)
        K consecutive flat rounds with no new useful signal (max_flat_steps)
        OR tool-call repetition (same tool + near-same args 2–3×)
        OR >~85% semantic similarity between consecutive (thought, action, observation) states
              │ still progressing
              ▼
  (d) HARD CAPS  ──► halt: BUDGET/ITERATION EXHAUSTED  (circuit breaker of last resort)
        max-iterations · max-recursion-depth · token/cost budget exhausted
              │ under all caps
              ▼
  continue → run next iteration
```

### 1.1 Layer (a) — goal-satisfaction gate

The **objective** stop. Halt when the success criterion is _provably_ met, not when the model asserts it. Two acceptable forms:

- **Oracle passes** — the same signal that is the verification gate (§3) doubles as the termination goal-gate: tests green, compiler clean, schema validates, lint passes. _This is the strongest possible stop because it is the success criterion itself._
- **Explicit COMPLETE marker** — when no oracle exists, the agent emits a structured `COMPLETE` sentinel. **Caution:** a self-reported sentinel is _not trustworthy alone_ (it is the "model decides it's done" failure wearing a token). Pair it with the no-progress detector (c) and the hard cap (d); never let `COMPLETE` be the _sole_ layer.

> **Oracle-label illusion (do not commit this):** never let the _stop_ decision secretly depend on a ground-truth oracle that won't exist at deployment. If your termination logic reads a golden label to decide "done," the loop will not reproduce in production where that label is absent. The goal-gate must use a signal that is actually available at run time.

### 1.2 Layer (b) — STUCK / abort escalation path

The escape hatch that prevents **destructive iteration ("overbaking")**: on an ambiguous or impossible task, a loop with only a goal-gate and a hard cap will iterate _into damage_ by iteration two — rewriting working code, deleting state, thrashing — until the cap finally fires. The fix is an explicit **STUCK signal**: the agent is instructed that emitting `STUCK` (impossible / ambiguous / blocked on a missing dependency) is a **valid, rewarded outcome** that routes to **human escalation** rather than continued iteration. Without it, "the loop iterates into damage instead of emitting STUCK" is a named failure mode.

### 1.3 Layer (c) — no-progress / loop-until-dry detector

The **convergence** stop, for loops with no clean oracle or that legitimately run "until there's nothing left to do." The single hardest parameter is _what counts as "no new signal."_ Concrete signal definitions (use one or combine):

| Signal | Definition | Fires when |
| --- | --- | --- |
| **K flat rounds** (`max_flat_steps`) | "did a new _useful_ signal appear this round?" — a new finding, a new file touched, a new test passing | K consecutive rounds answer **no** |
| **Tool-call repetition** | same tool invoked with near-identical args | 2–3× in a row → stuck |
| **State similarity** | semantic similarity of consecutive (thought, action, observation) states | **>~85%** similar → spinning |

Two cautions, both empirically grounded:

- **K too low stops mid-work.** A naive counter wrongly kills a research agent legitimately summarizing 20 documents at iteration 8. Size K to the task's real cadence.
- **A surface-signal detector is gameable by busywork.** If "progress = a new file touched," the model touches files without advancing the goal ("false progress"). Prefer a signal tied to the _objective_ (a new test passing) over an _activity_ signal (a file changed).

### 1.4 Layer (d) — hard caps

The **financial circuit breaker of last resort**: `max-iterations`, `max-recursion-depth`, and a token/cost ceiling. These are blunt by design — they exist so that when (a)–(c) all fail, the loop still halts before a runaway. **Sole reliance on `max-iterations` is "a blunt instrument"**: it has no idea whether iteration 8 is wasted spin or essential work, so it cannot be the _only_ stop. It is the backstop, not the strategy.

### 1.5 Per-route termination defaults

| Route | Goal-gate (a) | No-progress (c) | Hard cap (d) | Notes |
| --- | --- | --- | --- | --- |
| **R0 Single call** | n/a (no loop) | n/a | n/a | Termination is trivial; there is no iteration. |
| **R1 Ralph** | plan-ledger empty **AND** commit-gate (tests/typecheck) green | tool-repeat / >85% similarity | **`--max-iterations` is the PRIMARY backstop** + budget cap | `COMPLETE`/`STUCK` markers; the iteration cap is load-bearing, not optional, because `while :;` is unbounded by construction. |
| **R2 Spec-Driven / EPCC** | machine gate green (test/build/lint/screenshot-diff) | per-task | max-tasks + budget | Human plan-gate happens _before_ the loop, not as a stop. |
| **R3 Auto-Research** | research plan exhausted + citation pass complete | new-source-rate flat | fan-out width · depth · per-subagent tool-calls · outer iterations | All four caps bound separately; the no-progress signal is "no new useful source." |
| **R4 Orchestrator-workers** | all dispatched subtasks returned + validated | supervisor sees no new actionable subtask | max-depth + max-subagents + budget | Guard against runaway re-dispatch and over-decomposition (50 subagents for a simple query). |
| **R5 Plan-Execute** | plan steps complete + final critic passes | replanner produces no new step | **max-replan cap** + budget | No-progress guard prevents replan ping-pong. |
| **R6 Evaluator-optimizer** | judge returns **PASS** | score stops improving (anti-oscillation) | **max-iter cap; return-best-not-last** | Budget ≈ 2N calls. Never loop forever chasing a marginal judge delta. |
| **R7 Ensemble** | aggregation complete (vote / consensus) | n/a (fixed N×R, not iterative-to-convergence) | width N + rounds R + budget | Fallback-to-single on easy/agreeing items saves the premium. |
| **R8 Autonomous (ReAct)** | environment success signal | tool-repeat / >85% similarity | **hard max-iteration + budget** | The most failure-prone termination; the hard cap is doing real work here. |
| **R9 Self-improving** | held-out utility plateaus | no candidate beats incumbent for K generations | bounded generations + plateau stop | Outer-loop termination; inner loop has its own stack. |

---

## 2 — CONTEXT (a deliberate point on the fresh↔accumulating axis, backed by external memory)

Context is a **finite resource** _(empirically-supported, Anthropic "Effective context engineering")_: transformer n² attention gives the model a finite **"attention budget,"** and recall degrades as the token count grows — **context rot**. The model "remains highly capable" while late-iteration recall and long-range reasoning **silently** degrade. So the question is never "will it remember?" but "**where on the fresh↔accumulating axis do I sit, and where does state live when it falls off the window?**"

### 2.1 The fresh↔accumulating axis

```text
  FRESH per iteration ◄─────────────── COMPACTION bridge ───────────────► ACCUMULATING / append-only
  (Ralph)                              (summarize near the limit)         (full trace, never mutate)

  + immune to context rot              + extends a long accumulating       + best trace fidelity
  + clean window every loop              loop past the window               + maximal KV-cache reuse
  − ALL state must live on disk        − over-aggression drops latently-    − accrues context rot
    (git + plan/ledger + codebase)       critical context                  − unbounded growth
```

| Posture | What it is | Buys | Costs | Best for |
| --- | --- | --- | --- | --- |
| **Accumulating / append-only** | Keep the full trace; **never mutate prior turns** | Best trace fidelity; **maximal KV-cache reuse** (see §2.4) | Context rot past ~100–150k tokens; unbounded growth | Short-to-medium loops (R6, R8) where the trajectory IS the reasoning |
| **Fresh per iteration** | Each iteration is a clean window; nothing carries in-context | **Immune to context rot**; trivially parallel | Forces **all** durable state to external memory | Ralph (R1), isolated fan-out (R3) |
| **Compaction-bridged** | Summarize when near the window limit, then continue | Extends a long accumulating loop without a hard wall | Over-aggression silently drops context whose importance "only becomes apparent later" | Long single-agent runs that outgrow the window |

### 2.2 Compaction — what it preserves vs discards

Compaction is the bridge that lets an accumulating loop run long. The discipline _(Anthropic; Cognition uses a dedicated compression LLM for context that outgrows the window)_:

- **PRESERVE:** architectural decisions, unresolved bugs, implementation details, the active goal.
- **DISCARD:** redundant tool outputs, superseded intermediate results.
- **CONTINUE WITH:** the summary **+ the five most-recently-accessed files**.
- **TUNE recall first, then precision** — it is safer to keep a little too much than to drop the one subtle fact that matters 30 iterations later. **Over-compaction is a failure mode**: it "corrupts the very long loops it was meant to save."
- **Carry the budget across the boundary** — re-inject `task_budget.remaining` so the countdown (§4) doesn't reset to full on the other side of a compaction.

### 2.3 External-memory substrates (where state lives when it leaves the window)

When context is fresh, compacted, or isolated, **every** piece of durable state must live in an external store. Pick the substrate and define its **schema and size budget** — that handoff _is_ what survives across iterations.

| Substrate | Holds | Notes |
| --- | --- | --- |
| **Spec / contract** (`SPEC.md`, `PLAN.md`) | The immutable success criterion + the plan | Persists across compaction; the thing the gate checks against. Spec-Driven's whole premise. |
| **Plan / ledger** (`TODO.md`, `PROGRESS.md`) | Remaining work + done work | The Ralph loop's worklist; "plan-ledger empty" is its goal-gate. |
| **Git** | The codebase + per-iteration commits | Unlimited, restorable, **the fallback path** (`git reset --hard` to last green). Durability and memory in one. |
| **Scratchpad / NOTES** (`NOTES.md`, `learnings.md`) | Findings, lessons, dead-ends to avoid | Reloaded on demand; just-in-time retrieval keeps lightweight identifiers (paths, queries) and loads the body only when needed. |
| **File system** | Anything; the unlimited persistent context | Compression that keeps **URLs/paths** is _loss-free_ (the identifier round-trips to the full content). |
| **Sub-agent return schema** | A distilled summary back to the parent | Size-budgeted — typically a **1,000–2,000 token** summary per sub-agent. The schema is load-bearing (see §2.5). |

Two techniques that fight goal-drift over long (Manus reports ~50 tool-calls/task average) loops _(empirically-supported, Manus)_:

- **Recitation** — rewrite the objective/todo to the **end** of context every step, so the goal stays in recent attention and resists lost-in-the-middle drift.
- **Keep the wrong turns in** — _do not_ erase failed actions, errors, and stack traces. "Erasing failure removes evidence; without evidence the model can't adapt." Keeping them lets the model update its priors and avoid repeating the mistake. This is counter-intuitive but load-bearing.

### 2.4 KV-cache stability (the production cost lever)

_(empirically-supported, Manus: cache hit rate is the single most important production metric — ~10× cost delta cached vs uncached.)_ Append-only context exists partly to protect the cache. **What invalidates the KV-cache prefix:**

- a **timestamp** or any dynamic value early in the prompt;
- a **changed prefix token** (even one);
- **mid-loop tool add/remove** (changes the tool-definition prefix) — _mask tool logits to disable a tool instead of removing it_;
- **client-side budget mutation** in the prefix.

Cache thrash is a named failure: a single changed prefix token → "latency + 10× cost spike." The discipline: **stable prefix, append-only suffix, no mid-loop mutation of the front of the window.**

### 2.5 Sub-agent isolation (the spatial version of fresh context)

Fan-out gives each sub-agent its **own clean window** — effective context multiplied, rot avoided per-agent. But isolation has a sharp edge _(empirically-supported, Cognition "Don't Build Multi-Agents")_: **share full agent traces, not just the task message.** Actions carry **implicit decisions**; sub-agents that see only their task (not the full trace) make **conflicting** implicit decisions the coordinator cannot reconcile — the **Flappy-Bird failure** (two sub-agents build mismatched halves of one artifact). Therefore:

- **Read-only / genuinely independent** work (research fan-out) → isolation is fine; return a 1–2k-token summary.
- **Work where decisions must agree** (shared-write, one coherent artifact) → **share full traces** or stay **single-threaded** (Cognition's default). Writing/synthesis is single-threaded _after_ parallel research completes.

### 2.6 Per-route context defaults

| Route | Posture | External store | What survives an iteration | What is discarded |
| --- | --- | --- | --- | --- |
| **R1 Ralph** | **fresh** | git + plan/ledger + codebase | everything on disk | the entire in-context window |
| **R2 Spec-Driven** | fresh session for CODE | spec on disk (survives compaction) | the spec + commits | exploration chatter |
| **R3 Auto-Research** | **isolated** per researcher | plan → external; 1–2k-token return summaries | the distilled summary + citations | each researcher's raw trace |
| **R4 Orchestrator-workers** | shared **or** isolated, **chosen deliberately** | checkpointed durable state | per A3: full traces if decisions must agree | redundant worker chatter |
| **R5 Plan-Execute** | executor context isolated; plan accumulates | plan = durable scratchpad | the plan + step results | per-executor working context |
| **R6 Evaluator-optimizer** | **accumulating** (attempt + feedback) | in-context (+ compaction near limit) | prior attempts + critiques | nothing (feedback history is the value) |
| **R8 Autonomous (ReAct)** | **accumulating** trajectory (+ compaction) | optional scratchpad | the trajectory | redundant tool outputs on compaction |
| **R9 Self-improving** | per-run fresh; artifact persists across runs | the artifact (skill/prompt/lesson) + archive | the durable artifact + the archive | per-run scratch |

---

## 3 — VERIFICATION (the trust ladder; verifier ≥ generator)

Between **"generated"** and **"accepted"** sits a check. The verification gate is the loop's engine and the single biggest determinant of **convergence-to-working vs convergence-to-slop**. It exploits the **generator–verifier asymmetry**: _(empirically-supported)_ checking "is this correct?" is cheaper than producing a correct answer, and models discriminate better than they generate. The gate's verdict feeds **two** consumers: the **accept/reject** decision _and_ the **termination** goal-gate (§1.1).

### 3.1 The trust ladder (order every gate toward the strongest available rung)

```text
  STRONGEST / least gameable
  ▲   (1) DETERMINISTIC ORACLE   tests · compiler · type-checker · schema/JSON-schema · linters
  │       └ cheapest, least gameable; doubles as the termination goal-gate
  │   (2) GROUND-TRUTH COMPARISON   against a known answer / golden set
  │       └ trustworthy but only where a labeled answer exists
  │   (3) LLM-AS-JUDGE / ADVERSARIAL VERIFIER / PANEL   rubric-guided critique; N skeptics
  │       └ flexible but BIASED (see §3.3); needs mitigations
  ▼   (4) SELF-GRADE   the generator grades itself
  WEAKEST / most gameable          └ use only with corroboration; degrades on non-verifiable tasks
```

> **Trust = accuracy AND integrity.** This ladder ranks gates by accuracy _under honest conditions_. A second, orthogonal axis is **integrity under adversarial input**: if the content the loop ingests is attacker-controllable (open web, transcripts, repo files — router axis A9), the gate itself can be the target — an attacker who controls the content can write the very test an "executable oracle" then runs green, turning the strongest rung into the exfiltration trigger. When the loop is trifecta-exposed, picking a high rung is not enough; the **content-reader must be structurally separated from the privileged actor** (router A9 / blueprint field 14). A gate is only as trustworthy as the integrity of its inputs.

**Rule:** pick the **highest rung the success criterion affords.** If only self-grade is available, _say so_, drop the confidence, and add the §3.3 mitigations — do not pretend the loop converges.

### 3.2 The generator/verifier asymmetry (verifier ≥ generator)

The asymmetry only pays off under a **hard constraint** _(empirically-supported)_: **the verifier must be at least as strong as the generator.**

- **small verifier + large generator → measurably HURTS** performance (the weak checker passes the strong generator's subtle errors).
- **large verifier + small generator → large gains.**

Practical consequence: **prefer many cheap generations gated by one strong verifier** over a single expensive generation. This is _why_ ensemble-then-verify (R7) and best-of-N-then-judge work — they put the spend on generation breadth and a single strong gate, not on one costly attempt. Always answer the blueprint's question **"verifier ≥ generator? {yes/no}"** explicitly.

### 3.3 LLM-judge biases and their mitigations

The judge rung is flexible but carries documented biases _(empirically-supported)_ — especially dangerous inside self-improvement loops (R9), where a biased judge **silently corrupts the optimization signal**:

| Bias | What it is | Mitigation |
| --- | --- | --- |
| **Self-preference** | Models over-rate **their own** and **same-vendor** outputs | **Separate the judge** — different model/family, or an executable check; never same-model self-grade as the sole correctness gate |
| **Position bias** | Order-sensitivity (favors the first/last candidate) | **Randomize order**; average over permutations |
| **One-token reward hacking** | A bare "Solution" or even ":" elicits a **false-positive** reward | **Reward-hacking-resistant rubrics**; require the judge to cite the passing evidence |

### 3.4 The oracle-label illusion (the trap that breaks deployment)

A loop that looks gated can secretly be cheating: if the **stop** or **accept** decision quietly reads a **ground-truth label** that exists only in the eval harness, the loop **will not reproduce** in deployment where that label is absent. Stated as a gate question: _does the verification (and the termination goal-gate it feeds) use a signal that is actually available at run time?_ If "the gate needs the golden answer," the gate is an illusion. This is the §1.1 caution restated from the verification side — they are the same trap viewed from both ends.

### 3.5 Self-judge degradation (why self-grade is the floor)

On **non-verifiable** tasks, self-judgment doesn't just add noise — it **degrades** output. Same-model self-grade is subject to self-preference _and_ reasoning-degradation under self-critique. So: self-grade is the **floor** of the ladder, used only with corroboration; on correctness-critical work, route at least to a **separate** judge or an executable check. "Never trust a same-model self-grade as the sole gate on correctness."

### 3.6 Per-route verification defaults

| Route | Gate type (rung) | What it checks | Mitigations / notes |
| --- | --- | --- | --- |
| **R1 Ralph** | (1) oracle | tests/typecheck green — **must test REAL behavior**, not a tautology | The commit-gate is also the termination goal-gate. |
| **R2 Spec-Driven** | (1) oracle + human | test/build/lint/screenshot-diff **+** human plan-approval gate (pre-loop) | Two gates: machine (in-loop) + human (before). |
| **R3 Auto-Research** | (3) separate citation/verify pass | each claim attributed to a source | Shipped systems _attribute_, they don't fact-check — **add** a source-authority/corroboration check yourself. |
| **R4 Orchestrator-workers** | (1–3) validator stage **independent of supervisor self-judgment** | subtask outputs + guardrails; + system-level LLM-as-jury eval | Never let the supervisor be its own judge. |
| **R5 Plan-Execute** | replanner (coarse) **+ add a separate critic/tests** | step outputs against the plan | The replanner alone is a weak gate — add a real check between execute and respond. |
| **R6 Evaluator-optimizer** | **this IS the gate** — order by trust (oracle > reference > judge > self) | the artifact against the criterion | **Separate generator/judge model**; mitigate self-preference; return-best-not-last. |
| **R7 Ensemble** | the ensemble **is** the verification (consensus / majority-refute) | agreement across diverse agents | Diverse **families** (uncorrelated error); treat consensus as _necessary-not-sufficient_. |
| **R8 Autonomous** | (1) environment/tool feedback = ground truth | the world's response to an action | + HITL checkpoints scaled to stakes. |
| **R9 Self-improving** | **held-out utility** gate (gameable-resistant, **≥ generator**) + functional/regression + safety overseer | did the mutation actually improve a held-out metric? | A biased/weak utility gate silently corrupts the whole archive — the highest-stakes gate in the skill. |

---

## 4 — BUDGETS (advisory pacing budget + hard ceiling)

A budget is **two** mechanisms, not one _(empirically-supported, Anthropic task-budgets)_:

| Mechanism | What it is | Behavior |
| --- | --- | --- |
| **Advisory pacing budget** (`task_budget`) | A **soft hint** the model paces against, via a **server-injected countdown** of remaining budget across the full agentic loop | The model wraps up _gracefully_ as the countdown runs down; **advisory, not enforced** |
| **Hard ceiling** (`max_tokens` / cost cap) | The **enforced** wall | The run is cut off; the circuit breaker that backstops termination (§1.4) |

### 4.1 Sizing — against p99, not a default

**Size the budget against the actual task-length distribution (p99), not a fixed default.** The two failure directions:

- **Too small → refusal-like behavior.** A budget too small for the task induces the model to "decline to attempt the task, scope it down aggressively, or stop early with a partial result" — e.g. a 20k-token budget on a multi-hour task. This is **premature-stopping masquerading as a guardrail**: it looks like a safety win and is actually a silent failure. The documented **minimum accepted is ~20k tokens**.
- **Too large → no pacing pressure** and an ineffective circuit breaker; the hard ceiling stops mattering.

So: estimate the p99 task length, set `task_budget` to pace against it, set `max_tokens`/cost above it as the wall, and **carry `task_budget.remaining` across compaction** (§2.2) so the countdown doesn't reset.

### 4.2 The multi-agent premium (~4×–15×)

Multi-agent topologies (fan-out research, debate, orchestrator-workers, MoA) buy quality at a **~4×–15× token premium** over a single agent, **plus** reproducibility loss. The budget section must **explicitly weigh that multiplier against task value** and gate the spend:

- Spend the premium only on **high-value, genuinely-parallel, breadth-first** work.
- **Gate spend to the items that need it** — high-stakes / high-disagreement items get the ensemble; easy/agreeing items **fall back to a single pass** (§3.6 R7).
- Document the multiplier you are accepting in the blueprint (e.g. "~15× premium accepted because the cited landscape is high-value and the 8 tracks are genuinely independent"). An undocumented multi-agent spend is the canonical over-engineering failure — much of debate's apparent lift is just the ensemble effect, so at equal compute single-agent often matches it.

### 4.3 Per-route budget defaults

| Route | Advisory pace | Hard ceiling | Premium note |
| --- | --- | --- | --- |
| **R0 Single call** | n/a | `max_tokens` only | 1× baseline. |
| **R1 Ralph** | per-iteration soft budget | **overall cost cap** + `--max-iterations` | 1× per iter, but unbounded iterations ⇒ the cap is the real spend control. |
| **R3 Auto-Research** | per-subagent budget | total fan-out cost cap | **~15× premium — weigh explicitly**; gate width to value. |
| **R4 Orchestrator-workers** | per-worker budget | total + per-child cap | 4–15× premium; scale effort to complexity (no 50 subagents for a simple query). |
| **R6 Evaluator-optimizer** | budget ≈ **2N calls** | max-iter cap | ~2× per iteration (generate + judge). |
| **R7 Ensemble** | per-agent budget | width N × rounds R cap | N×R premium — **fallback-to-single** on easy items recovers most of it. |
| **R8 Autonomous** | `task_budget` paced to p99 | **hard max-iteration + budget** | 1× but open-ended — the cap is doing real work. |
| **R9 Self-improving** | per-generation budget | bounded generations | Offline/batch; amortized over many future runs. |

---

## 5 — DURABILITY (checkpoint + idempotency; N/A for short foreground)

For loops spanning **minutes to months**, a crash must **not** lose hours of completed work. Durability snapshots state at **step boundaries** so a crash resumes at the **failure point** without re-running completed work.

### 5.1 The two mechanisms

| Mechanism | What it does | Source pattern |
| --- | --- | --- |
| **Event-history replay** | Append-only event log; on restart, **replay** the history to reconstruct in-memory state, then continue at the exact failure point | _Temporal durable execution_ — reconstructs in-memory state from an append-only event history; auto-retries failed activities for hours-to-months loops |
| **Per-node checkpointing** | Snapshot graph/loop state after **every node/step** into a thread; resume by key; **pending-writes recovery** so successful nodes in a _failed_ super-step aren't re-run | _LangGraph persistence_ — `thread_id` is the **resume key**; dev→prod tiers InMemory → SQLite → Postgres |

Both require a **resume key** (the `thread_id` / run-id that identifies which run to resume) and **checkpoint at defined step boundaries** (every node, every activity return, every iteration).

### 5.2 Idempotency is non-negotiable (at-least-once replay)

Both mechanisms **demand idempotent tool calls** because the model is **at-least-once**: replay re-fires side effects. The named failure is **"durability without idempotent tools → at-least-once replay re-fires side effects (double-charges, duplicate writes)."** So:

- Every side-effecting tool call needs an **idempotency boundary** — a key (request-id, natural key) that makes a re-fire a **no-op** rather than a second effect.
- Read-only and pure-compute calls are idempotent by default; the discipline applies to **writes, charges, sends, and external mutations**.
- "Define the idempotency boundary" is a blueprint field for any durable route, not an afterthought.

### 5.3 When durability is N/A

**Short foreground loops: skip it (YAGNI).** The control-plane overhead — checkpointers, resume keys, idempotency wrappers — **costs more than it saves** on a single-shot or 2–3-turn task that a human is watching and can simply re-run. Durability earns its complexity only when **(a)** the loop is long enough that re-running from scratch is expensive, **and/or (b)** it runs **unattended** (no human to notice and restart), **and/or (c)** it is **multi-agent / fleet** (many in-flight units, partial failure likely). If none of those hold, durability is **N/A** — and saying so explicitly is a valid, complete answer to the durability field.

### 5.4 Per-route durability defaults

| Route | Durability | Resume key | Idempotency boundary |
| --- | --- | --- | --- |
| **R0 Single call** | **N/A** (YAGNI) | — | — |
| **R1 Ralph** | **git commit per iteration** (durability + memory + fallback in one) | last green commit | commits are idempotent; external writes need keys |
| **R2 Spec-Driven** | **commit per task** | last task commit | per-task commit boundary |
| **R3 Auto-Research** | checkpoint per completed researcher | run-id + per-subagent id | search/fetch are read-only; report-write needs a key |
| **R4 Orchestrator-workers (fleet)** | **checkpointed durable state** (mandatory) | per-child thread/run id | per-worker write keys; the binding constraint at scale |
| **R5 Plan-Execute** | checkpoint per step result | step index | per-step write boundary |
| **R6 Evaluator-optimizer** | usually foreground → **N/A**; checkpoint per attempt if long | attempt index | — (typically in-context) |
| **R8 Autonomous (async/sandbox)** | checkpoint per step (if detached) | run-id | per-action write keys |
| **R9 Self-improving** | **archive persisted per generation** | generation id | artifact-write boundary; the archive _is_ the durable state |

---

## Observability (C8 — the human's window into the loop)

Distinct from durability but co-located here because both serve "a human can recover": the control plane must **expose** its own state so a human can see a runaway or destructive-iteration spiral _and intervene before it completes_. Surface, at minimum: **iteration count · budget remaining · no-progress state · verifier verdicts**, and provide a **kill/redirect** affordance. A loop whose control-plane state is invisible cannot be circuit-broken in time.

> **Seat boundary.** Observability _as a mechanism the harness emits_ is in scope here (the builder wires the counters, the budget countdown, the verdict log, the kill switch). Whether that telemetry produces **calibrated operator trust and sustainable cognitive load** — the _human experience_ of watching the loop — is the sibling `agentic-ux` skill's job. Build the window; hand off the question of whether the view is good to look through.

---

## Sources (primary)

| # | Pillar(s) | Source | URL |
| --- | --- | --- | --- |
| 1 | Context (rot, attention budget, compaction, sub-agent isolation) | Effective context engineering for AI agents — Anthropic Engineering | <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents> |
| 2 | Context (KV-cache, append-only, recitation, keep-the-wrong-stuff-in, filesystem-as-memory) | Context Engineering for AI Agents: Lessons from Building Manus — Yichao "Peak" Ji / Manus | <https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus> |
| 3 | Context (share full traces; Flappy-Bird; single-threaded default; compression LLM) | Don't Build Multi-Agents — Cognition / Devin | <https://cognition.ai/blog/dont-build-multi-agents> |
| 4 | Budgets / termination (advisory countdown, refusal-when-small, 20k min, p99 sizing, carry-across-compaction) | Task budgets — Anthropic API docs | <https://platform.claude.com/docs/en/build-with-claude/task-budgets> |
| 5 | Durability (event-history replay, resume-at-failure, step-boundary checkpoint, auto-retry) | Durable Execution meets AI: Why Temporal is ideal for AI agents — Temporal | <https://temporal.io/blog/durable-execution-meets-ai-why-temporal-is-the-perfect-foundation-for-ai> |
| 6 | Durability (per-node checkpoint, thread_id resume key, pending-writes recovery, tiers) | Persistence — LangGraph / LangChain docs | <https://docs.langchain.com/oss/javascript/langgraph/persistence> |
| 7 | Termination / context (fresh-context loop, COMPLETE/STUCK markers, iteration limits, overbaking) | The Ralph Wiggum Agent Loop Is Really About Engineering Discipline — alteredcraft | <https://writing.alteredcraft.com/p/the-ralph-wiggum-agent-loop-is-really> |

> **Confidence tags.** Items marked _empirically-supported_ are grounded in the primary sources above. The **K-flat / 85%-similarity** thresholds and the **3-agents/2-rounds** ensemble sweet spots are _practitioner-folklore_ starting points — tune them against your task's real cadence; they are defaults to set deliberately, not constants to trust blindly.

---

## Cross-references

- Router that selects the body these choices wrap: `router.md` (the nine axes A1–A9, incl. the A9 trust-boundary overlay; the L5 instantiation table).
- How L5 nests across composed topologies: `composition.md`.
- The rubric this reference clears: `rubrics/rubric-loop-control.md` (C1–C8); the mechanical gap-check `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py` (verifies every `rubric-loop-control` gate is instantiated).
- Topology references set the _body_; this reference sets the _plane_ every one of them must instantiate: `ralph.md` · `react-reflexion.md` · `evaluator-optimizer.md` · `orchestrator-workers.md` · `auto-research.md` · `debate-ensemble.md` · `self-improving.md` · `plan-execute.md` · `spec-driven.md` · `async-oversight.md`.
