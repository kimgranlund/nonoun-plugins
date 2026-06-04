# Rubric — Plan-Execute

Score a **plan-first coding loop** — Plan-and-Execute (+Replanner: ReWOO, LLMCompiler) and/or Spec-Driven / Explore-Plan-Code-Commit (spec-kit, plan-as-contract, red-green-commit) — where a **durable written plan/spec is the contract** and coding-against-the-plan becomes the verification. Use in **EVALUATE mode** to audit an existing plan-execute loop, plan, or transcript, and as the acceptance bar in **PLAN / COMPOSE mode** before a blueprint that composes this family is declared READY-TO-RUN.

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate blocks SHIP; it is not a matter of opinion. Cross-cutting gates are backed by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`; per-family gates (PE1/PE4/PE5/PE7) are **[mech-partial]** — the criterion is structural but no automated script enforces it; agent judgment applies.
- **[mech-partial]** — mechanically checkable criterion, no automated script — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment. Read the artifact, cite evidence, score **1–5** against the anchors.

**Band:** per-family. Load this rubric **only when the plan composes the plan-execute / spec-driven family** (selectors: `plan-and-execute`, `planner-executor`, `replanner`, `rewoo`, `llmcompiler`, `spec-driven development`, `explore-plan-code-commit`, `spec-kit`, `plan-as-contract`, `red-green-commit`).

**Ship rule.** A plan ships against this rubric when **every [gate] passes AND no [review] dimension < 3** — evaluated as part of the global ship rule (the union of all loaded rubrics' gates must clear; see `rubric-manifest.json`).

**Dependency.** This rubric **depends on `rubric-loop-control`** (manifest `dependencies: ["loop-control"]`). Its gates are **also** in force here: C1 termination-stack, C2 budget, C3 verification-gate, C7 durability-idempotency must pass, and C4–C8 reviews apply, for any plan-execute loop. Score `rubric-loop-control` alongside this one; a plan-execute loop that passes every PE gate but fails a loop-control gate does **not** ship.

**Calibration caveat.** Status: **draft**, **0 calibration samples**. Treat every score here as **directional, not authoritative**, until the ROADMAP v0.2 calibration bar is met. The [gate] dimensions are the only mechanically verifiable layer; [review] scores are uncalibrated judgment. Record evidence (the plan section, the spec line, the gate command, the transcript step) for **every** finding — a finding without a citation is an opinion.

---

## The backbone gates

These four are the load-bearing checks for this family. Run them first; most failures surface here. The plan-first family lives or dies on three things — **the plan is warranted, the human can actually edit the plan before code runs, and the plan and code do not silently decohere** — plus a real verification target. A plan-execute loop missing any one is a structured way to ship the wrong thing confidently.

### PE1 [gate / mech-partial] — Plan-trigger appropriateness

The plan correctly decides **whether to plan at all**. Planning is not free — it spends a turn and a model call. The loop skips planning for one-sentence / single-file diffs and plans for multi-file, uncertain, unfamiliar, or high-blast-radius work. Reflexive always-plan (ceremony on a typo fix) and reflexive never-plan (diving straight into a 12-file refactor) both fail.

**Test (binary):** locate the trigger rule. Pass requires a stated condition that gates planning on task complexity/uncertainty (e.g. "plan when >1 file or unfamiliar subsystem or unclear approach; skip for trivial localized edits"). Fail if planning is unconditional, absent, or undefined — i.e. the loop plans everything or nothing regardless of task size.

### PE4 [gate / mech-partial] — Human plan-gate design

An **explicit, appropriately-strong, editable plan-approval checkpoint precedes code**. The human can read AND amend the plan before a single line is written, and the gate has a **rubber-stamp-resistant** mechanism so approval is not a reflex click — clarification markers, ambiguity flags the human must resolve, or EARS-style acceptance criteria the human signs off on.

**Test (presence + structural):** confirm (a) a checkpoint exists between plan and code; (b) the plan artifact is editable by the human at that checkpoint (not read-only or post-hoc); (c) at least one rubber-stamp-resistance mechanism is present (explicit `[CLARIFY]`/ambiguity markers, open questions block, or EARS/"the system shall…" testable criteria). Fail if code can begin before human sign-off, if the plan cannot be edited at the gate, or if approval is a bare yes/no with no surfaced ambiguities. For high-autonomy/unattended variants where no human is in the loop, this gate **fails by construction** unless an equivalent automated acceptance contract gates execution — note that and route the human-experience question to the sibling `agentic-ux` skill.

### PE5 [gate / mech-partial] — Verification-target hardness

A **runnable, machine-readable pass/fail gate** exists (test / build / lint / diff / screenshot-diff), its **hardness is matched to the autonomy level**, and the agent **shows evidence, not assertions** ("tests pass" must be a pasted runner result, not a claim). This is the plan-execute instance of `rubric-loop-control` C3; score both.

**Test (presence + threshold):** name the gate command and the artifact it emits. Pass requires (a) a concrete runnable check, not "the agent reviews its work"; (b) the agent surfaces the actual output (exit code / test summary / diff / image), not a prose assertion of success; (c) hardness scales with autonomy — the more unattended the run, the stronger the gate (full test+build+lint for unattended; lighter for watched). Fail if the only gate is the model's self-assertion, or if hardness is flat-weak under high autonomy.

### PE7 [gate / mech-partial] — Drift & freshness control

**"Update the plan before diverging"** is enforced, **plus** a regeneration/sync path so the spec and the code do not decohere into a lying source of truth. A spec that no longer matches the code is worse than no spec — it actively misleads the next agent and the human. The loop names the mechanism that keeps plan and code in sync as execution reveals reality.

**Test (presence):** locate the drift rule. Pass requires both (a) a divergence protocol — when the executor must deviate from the plan, it updates the plan first (or records the deviation against it), not silently; and (b) a sync/regeneration path — a defined way the spec is reconciled to the shipped code (re-derive plan from diff, plan-vs-code diff check, or an explicit "spec is regenerated at end of milestone" step). Fail if the plan is write-once and never reconciled, or if divergence is permitted silently with no plan update.

---

## Design dimensions

### PE2 [review] — Plan/spec representation & self-containment

The **plan form fits the structure of the work**, and the plan is **self-contained enough to execute against**. Form options: a flat ordered list (linear dependent steps), a blueprint with placeholders (ReWOO-style variable-passing), a DAG (LLMCompiler-style parallelizable steps), or a spec markdown (spec-driven). Whatever the form, the plan names the **files and interfaces** it touches, states **what is out of scope**, and **ends with a verification step**.

**Evidence to cite:** the plan/spec artifact itself — its shape, whether it names files+interfaces, its out-of-scope section, its final step.

**Score:**

- **1** — form mismatched to the work (a flat list for heavily-parallel independent steps, or a vague prose paragraph standing in for a plan); no files/interfaces named; no scope boundary; no verification step. The "plan" is a wish.
- **3** — form is reasonable for the dependency structure; names most files/interfaces; verification step present; but scope boundaries are loose or some steps are under-specified ("update the auth logic").
- **5** — form precisely fits the dependency/parallelism structure (DAG where steps parallelize, list where they chain); every step names its files+interfaces; out-of-scope is explicit; the plan ends with a concrete verification step; a fresh executor could implement it without re-deriving intent.

### PE3 [review] — Replanning policy calibration

The **replan trigger/cadence suits the task's uncertainty**, with a **respond-vs-revise decision** and a **stall guard**. Options on the spectrum: never replan (pure ReWOO — plan once, execute blind, cheapest, brittle to surprises); replan on plan-exhaustion; replan on step failure; replan every step (most adaptive, most expensive). The loop also decides, per observation, whether to **respond** (finish) or **revise** (update the remaining plan), and it has a **no-progress / stall** guard so replanning cannot loop forever.

**Evidence to cite:** the replan rule, the respond-vs-revise branch, the stall guard.

**Score:**

- **1** — replan cadence mismatched to uncertainty (plan-once-blind on an exploratory unfamiliar task, or replan-every-step on a fully-foreseeable sequence burning tokens); no respond-vs-revise logic; no stall guard — replanning can spin indefinitely.
- **3** — cadence is broadly appropriate; a respond-vs-revise union exists; but the stall guard is weak or the trigger is coarse (replans on any failure, including trivially-retriable ones).
- **5** — cadence is tuned to the task's actual uncertainty (cheap plan-once for foreseeable work; failure-triggered or per-step replanning where the next step genuinely depends on observations); explicit respond-vs-revise branch; a concrete no-progress/stall guard caps replanning. (Ties to `rubric-loop-control` C6.)

### PE6 [review] — Planner/executor split & cost

A **strong planner pairs with cheaper executors**, and the resulting **cost profile beats the ReAct alternative** for the expected step count. The point of plan-execute over ReAct is to spend reasoning once (the plan) and let cheap executors carry out foreseeable steps, rather than invoking a strong reasoner every step. The split should be deliberate — model-per-role assigned — and the economics should hold for the task's horizon.

**Evidence to cite:** the model-per-role assignment (planner vs executor tiers), the step-count estimate, the cost comparison against a ReAct baseline.

**Score:**

- **1** — no split (same strong model plans and executes every step, i.e. ReAct wearing a plan's clothes with none of the cost benefit), or a split with no cost rationale; the plan-execute shape buys nothing over ReAct here.
- **3** — a planner/executor split exists with sensible model tiers, but the cost advantage over ReAct is asserted rather than reasoned, or the step count is short enough that the split barely pays.
- **5** — strong planner + cheap executors with an explicit cost profile; the expected step count is named and the plan-execute economics demonstrably beat the per-step-strong-reasoner ReAct alternative; model tiers are assigned per role. (Model-per-role concreteness also feeds `rubric-plan-quality` Q1.)

### PE8 [review] — Context durability & stage isolation

The **plan is persisted to disk**, and the **explore / plan / code / review stages are isolated** so the run survives compaction and is not polluted by exploration tokens. Exploration is read-only and its tokens do not bleed into the implementation context; the plan is the durable hand-off artifact; implementation is handed to a **fresh or sub-agent context** that reads the plan rather than carrying the whole exploration transcript.

**Evidence to cite:** where the plan is stored, the stage separation, the handoff to the implementing context. (Ties to `rubric-loop-control` C5 external-memory and C4 context-posture.)

**Score:**

- **1** — plan lives only in the conversation (lost on compaction / new session); explore/plan/code/review run in one accumulating context so exploration tokens pollute implementation and the run rots past the context window.
- **3** — plan is persisted to disk; some stage separation exists; but exploration and implementation share a context, or the handoff to a fresh implementing context is informal.
- **5** — plan persisted to disk as the durable contract; explore (read-only) / plan / code / review cleanly separated; implementation handed to a fresh or sub-agent context that reads the plan, so the run survives compaction and carries no exploration-token pollution.

---

## Scoring summary template

```text
Plan-execute loop: {name / goal short-name}
Variant: {plan-and-execute | replanner (ReWOO/LLMCompiler) | spec-driven | explore-plan-code-commit}
Autonomy level: {watched | semi-autonomous | unattended}   Expected step count: {n}

Backbone gates:
  PE1 plan-trigger appropriateness ... PASS / FAIL   {the trigger rule}
  PE4 human plan-gate design ......... PASS / FAIL   {checkpoint + editable + anti-rubber-stamp mechanism}
  PE5 verification-target hardness ... PASS / FAIL   {gate command + evidence-not-assertion}
  PE7 drift & freshness control ...... PASS / FAIL   {divergence protocol + sync/regen path}

Review dimensions (1-5):
  PE2 representation & self-containment ... {n}   {form fit · files/interfaces · scope · verify step}
  PE3 replanning policy calibration ...... {n}   {cadence · respond-vs-revise · stall guard}
  PE6 planner/executor split & cost ...... {n}   {model tiers · step count · vs-ReAct economics}
  PE8 context durability & stage isolation {n}   {persisted plan · stage isolation · fresh-context handoff}

Inherited from rubric-loop-control (MUST also pass — score there):
  C1 termination-stack ........ PASS / FAIL
  C2 budget ................... PASS / FAIL
  C3 verification-gate ........ PASS / FAIL   (PE5 is its plan-execute instance)
  C7 durability-idempotency ... PASS / FAIL
  C4–C8 reviews ............... {scored in rubric-loop-control}

Verdict:
  SOUND  — every PE gate PASS, every loop-control gate PASS, and no review < 3
  BLOCK  — any gate fails (PE or inherited loop-control), or any review < 3
Top findings (severity-ranked, with citations):
  1. ...
```

Map each finding to the family's dominant failure modes for root cause: **plan/code drift into a lying source of truth** (PE7), **rubber-stamped plan gate** (PE4), **plan-once-blind on an exploratory task** (PE3), **ReAct-in-disguise with no cost benefit** (PE6), and **exploration-token pollution / lost plan on compaction** (PE8). Plan-execute failures are usually a sound topology undone by a missing contract discipline, not a wrong topology choice — confirm the topology fit in `rubric-loop-selection` (S3 decomposition-shape) before attributing a failure to this family.
