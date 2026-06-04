# Rubric — Orchestrator-Workers

Scores an **orchestrator-workers** plan: a central agent that decomposes a goal at runtime and routes sub-tasks to workers via **handoff** (control-transfer, full context) or **delegation** (agent-as-tool, isolated context). Use when the plan composes a supervisor / manager-worker / hierarchical-agent-team / routines-and-handoffs topology (`../references/orchestrator-workers.md`). This is the family rubric the router selects when _decomposition is unpredictable, decided at runtime, with heterogeneous specialists_ — distinct from `rubric-auto-research` (fixed breadth-first research fan-out) and `rubric-debate-ensemble` (quality-via-diversity on one answer).

**Band:** per-family (load-on-match). Loaded only when the plan composes this family; composed plans (e.g. an orchestrator whose workers run plan-execute loops) also load the matched families' rubrics, and `rubric-loop-selection` S7 then scores the nesting.

**Key question:** Is delegation independent, correctly-dispatched, gated, and halting?

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate blocks SHIP; it is not a matter of opinion. Cross-cutting gates are backed by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`; per-family gates (OW1/OW2/OW6) are **[mech-partial]** — the criterion is structural but no automated script enforces it; agent judgment applies.
- **[mech-partial]** — mechanically checkable criterion, no automated script — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment; score **1–5** against the cited evidence.

**Ship rule:** this family passes when **every [gate] passes AND no [review] dimension < 3**. A composed plan must clear the **union** of all loaded rubrics' gates. Record evidence for every finding — the plan section, the parameter value, the wiring step it fails. A finding without a citation is an opinion.

**Dependency:** this rubric **depends on `rubric-loop-control`** (declared in `rubrics/rubric-manifest.json`). Its four control-plane gates — **C1 termination-stack, C2 budget, C3 verification-gate, C7 durability-idempotency** — **also apply** to every orchestrator-workers plan and are scored there. The dimensions below are the _orchestration-specific_ checks that `rubric-loop-control` does not cover; do not re-litigate the cross-cutting gates here, but do not skip them either.

> **Calibration caveat.** Library status **draft**, **0 calibration samples**. Treat every score as **directional, not authoritative**, until ROADMAP v0.2 calibration is met. The [gate] dimensions are the only mechanically verifiable layer; [review] anchors are first-pass and subject to recalibration.

> **Builder seat.** This rubric scores the _mechanism_ — whether delegation is independent, dispatched correctly, gated, and bounded. It does **not** score the operator's experience of supervising the orchestration (trust, steerability, interruptibility, cognitive load); that is the sibling `agentic-ux` skill. Where a plan touches the human, the check here is that it **hands off** cleanly (see OW7's HITL note and `rubric-plan-quality` Q6), not that the UX is good.

---

## Backbone gates (orchestration soundness)

These three are the load-bearing checks for this family. Run them first; most orchestrator-workers failures surface here. They sit _on top of_ the inherited `rubric-loop-control` gates, not instead of them.

### OW1 [gate / mech-partial] — Decomposition independence

Sub-tasks are parallelizable with **minimal shared mutable state**; parallel writes to a shared artifact are flagged and avoided. This is the dominant orchestrator-workers failure: isolated workers making conflicting implicit decisions a coordinator cannot reconcile (the Cognition "Flappy-Bird" failure — parallel sub-agents each invent an incompatible interpretation of an under-specified shared interface).

**Test (binary):** enumerate the worker sub-tasks. For each pair that runs in parallel, ask: do they **write** to the same file / interface / shared state? If any parallel pair shares a write target with no reconciliation step, **fail**. Read-heavy / independent sub-tasks pass; shared-write / depth-coupled work must be re-shaped (single-thread it, or serialize the conflicting writers, or split the shared artifact) before this gate passes. A plan that fans out onto work the brief itself calls interdependent fails regardless of polish.

### OW2 [gate / mech-partial] — Dispatch-mode fit

The plan chooses **deliberately** between **handoff** (control transfers to the worker, full conversation context travels with it) and **delegation / agent-as-tool** (the orchestrator calls the worker like a function, worker runs in an isolated window and returns a result), and the choice matches the read-vs-write nature of the work. The two are not interchangeable: handoff suits a coherent continuation that needs the full trace; delegation suits an independent, compressible sub-task whose raw transcript should not pollute the orchestrator's context.

**Test (presence + fit):** the plan must **name** the dispatch mode per worker class (not leave it implicit). Then check fit: an isolated, independently-verifiable sub-task using full-context **handoff** (leaking the whole trace into a worker that needed only a brief) → fail; a continuation that genuinely needs the prior reasoning forced through a stateless **agent-as-tool** call (so the worker re-derives lost context) → fail. A plan that says "route to workers" without naming handoff vs delegation fails on presence.

### OW6 [gate / mech-partial] — Termination & guards

Concrete stop conditions exist so the orchestration **provably halts**: sufficiency criteria for "the goal is met," a max-iterations / max-delegation-depth cap, budget ceilings, and guardrails against a worker spawning workers without bound. Sole reliance on "the orchestrator decides it's done" is unsafe; an unbounded supervisor that can re-dispatch indefinitely is the orchestration-level overbake.

**Test (presence):** point at each of — (a) the sufficiency/goal-satisfaction criterion the orchestrator checks before stopping, (b) a hard cap on orchestrator outer-loop iterations **and** delegation recursion depth, (c) a spawn-budget cap (total workers, or workers-per-level). If any of the three is absent, **fail**. ("The orchestrator stops when the task is complete" with no cap and no spawn budget is not a stop condition.) This gate is the orchestration-layer complement to `rubric-loop-control` C1; both must hold.

---

## Review dimensions

### OW3 [review] — Context-passing adequacy

Workers receive **enough** context (objective, required output format, boundaries) to avoid duplicating each other's work or leaving gaps, and the orchestrator↔worker return channel — **full trace** vs **final result only** vs **filtered/structured summary** — is tuned for reliability against cost. Large worker outputs are passed **by reference** (a handle / file path / resource link), not inlined into the orchestrator's window where they cause context bloat.

**Evidence to cite:** the per-worker briefing (what each worker is told) and the declared return-channel shape. **1** = workers get a bare task string with no format/boundary and dump raw transcripts back into the orchestrator (duplication + context bloot inevitable); **3** = workers are briefed with objective + format, return final results, but the channel is one-size-fits-all and large outputs are inlined; **5** = each worker class has objective + format + explicit boundary, the return channel is matched to need (final-result for independent sub-tasks, filtered summary for large ones), and oversized outputs are passed by reference.

### OW4 [review] — Routing determinism & testability

The supervisor's **routing policy** — LLM-chosen, a deterministic dispatch function, or round-robin — is appropriate to the task and is **observable and testable**, not opaque emergent behavior. A routing decision that cannot be inspected or replayed cannot be debugged when it sends the wrong sub-task to the wrong worker.

**Evidence to cite:** how the plan says the orchestrator decides which worker handles what, and whether that decision is logged/testable. **1** = routing is "the orchestrator figures it out," no logging, no way to test which worker fires for a given input; **3** = routing rationale is stated and logged, but mixing LLM-choice where a deterministic function would be cheaper and more testable, or vice-versa; **5** = routing policy is matched to the work (deterministic where the mapping is fixed, LLM-chosen only where genuinely ambiguous), each decision is logged with its rationale, and a representative input set can be replayed to test routing correctness.

### OW5 [review] — Effort scaling

Fan-out **width** and per-worker **tool-call budget** are scaled to task complexity by **explicit rules**, preventing both over-decomposition (a worker per trivial step, paying the coordination tax for nothing) and under-investigation (one overloaded worker where the task needed several).

**Evidence to cite:** the worker-count / budget parameters and the rule that sets them. **1** = a fixed worker count regardless of input, or no stated rule (e.g. always-spawn-N, the 50-workers-for-a-simple-goal anti-pattern); **3** = budgets are concrete but flat — reasonable for the typical case, no scaling rule for simple vs complex inputs; **5** = an explicit rule ties worker count and tool-call budget to a complexity signal, with named floors/ceilings, so trivial goals stay cheap and hard goals get the investigation they need.

### OW7 [review] — Verification gate

An **explicit validator** independent of the orchestrator's self-judgment sits between worker output and acceptance — a citation/attribution check, a guardrail, an executable check, or a human-in-the-loop stage — **plus** a system-level eval on a representative query set proving the orchestration as a whole works. The orchestrator grading its own workers' output is the same self-preference failure `rubric-loop-control` C3 warns against, one level up.

**Evidence to cite:** the acceptance check applied to worker results and the system-level eval. **1** = the orchestrator accepts worker output on its own say-so, no independent check, no eval; **3** = an independent per-worker check exists (validator / guardrail / HITL) but there is no system-level eval on a representative set; **5** = independent per-worker verification AND a system-level eval on a representative query set, with the verifier at least as strong as the workers it judges. **Builder-seat note:** where the gate is **human-in-the-loop**, this dimension checks only that the HITL stage is _wired in and independent_ — it does **not** score what that review feels like for the operator. The quality of the human oversight UX is the sibling `agentic-ux` skill's; hand off, per `rubric-plan-quality` Q6.

### OW8 [review] — Durability & cost-justification

Long / stateful orchestrations are **checkpointed and resumable** with safe in-flight redeploys (a mid-run code change does not corrupt in-flight workers), and the multi-agent **compute premium (~4×–15× tokens)** is explicitly weighed against task value, with **model tiering** considered (a strong orchestrator over cheaper workers, not top-tier everywhere). This dimension extends the inherited `rubric-loop-control` C7 with the orchestration-specific cost argument.

**Evidence to cite:** the checkpoint/resume design (if the run is long) and the cost/value rationale. **1** = a long stateful orchestration with no checkpointing (a crash loses all worker progress) and no cost justification for going multi-agent; **3** = either durability or the cost argument is handled but not both, or model tiering is ignored (every role on the top tier); **5** = checkpoint boundaries + resume key + idempotent re-dispatch for long runs, AND an explicit argument that the ~4×–15× premium is justified by task value, with models tiered per role. _N/A-able on the durability half for short, single-shot orchestrations — score the cost-justification half only and note N/A._

---

## Scoring summary template

```text
ORCHESTRATOR-WORKERS — {plan / goal short name}
Inherited (scored in rubric-loop-control): C1 termination · C2 budget · C3 verification · C7 durability

Backbone gates:
  OW1 decomposition-independence ... PASS / FAIL   {evidence: parallel-write pairs, if any}
  OW2 dispatch-mode-fit ............ PASS / FAIL   {evidence: handoff vs delegation named + fit}
  OW6 termination-guards ........... PASS / FAIL   {evidence: sufficiency + caps + spawn budget}

Review dimensions (1-5):
  OW3 context-passing-adequacy ..... {n}   {evidence: worker briefing + return channel}
  OW4 routing-determinism .......... {n}   {evidence: routing policy + testability}
  OW5 effort-scaling ............... {n}   {evidence: width/budget rule}
  OW7 verification ................. {n}   {evidence: independent check + system eval}
  OW8 durability-cost .............. {n}   {evidence: checkpoint/resume + premium justification}  (N/A: durability half if short run)

Verdict:
  SHIP   — every [gate] PASS (incl. inherited C1/C2/C3/C7) and no [review] < 3
  BLOCK  — any gate fails, or any review < 3
Top findings (severity-ranked, each mapped to the orchestrator-workers failure mode):
  1. ...
```

Map findings to the topology's named failure mode for root cause: the conflicting-implicit-decision / shared-write failure (OW1 — the Flappy-Bird class), wrong-dispatch-mode context leakage or re-derivation (OW2), unbounded re-dispatch / spawn runaway (OW6), worker-output duplication or context bloat (OW3), and self-judged worker acceptance (OW7). Orchestration-level failures are typically a control-plane gap (inherited C1/C2/C3/C7) amplified by delegation — fix the harness, not the worker.
