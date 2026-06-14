# Composition — how the layers nest and wrap

Loaded when a route is **composite** (a body that nests a sub-loop, or a gate dropped after a generation): R3 Auto-Research, R4 Orchestrator-workers with an inner evaluator, R6-inside-R4, R9 Self-improving, or any plan that adds an adversarial-verify gate. The router (`router.md`) names the primary body; this file tells you what legally nests inside it, what merely wraps it, and how to name the nesting in the blueprint's **CHOSEN LOOP TOPOLOGY** field.

> **One rule above all:** layers **compose**, they are not exclusive. A real plan is almost never "a topology" — it is one L1/L2 **body** + L4 **gates** + the full L5 **control plane** + (optionally) the dispatch **wrapper**. If your blueprint names a single topology and nothing nested, either the task was genuinely simple (fine — say so) or you under-specified (not fine).

---

## 1. The five-layer model

Every technique sorts into exactly one of five layers. **L1–L4 are loop bodies** (they define what happens inside an iteration and how iterations relate). **L5 is cross-cutting** — it wraps any body and is mandatory. A sixth construct, the **dispatch wrapper**, is _orthogonal_: it governs when/where/how-supervised a body runs, never the body itself.

| Layer | What it is | Members | Defining property |
| --- | --- | --- | --- |
| **L1 — Single-agent iteration** | One agent improves a task across iterations; members differ only in _what carries forward_ and _what closes the loop_ | Ralph (`ralph.md`) · ReAct + Reflexion + Self-Refine (`react-reflexion.md`) · Plan-Execute as one agent (`plan-execute.md`) · Spec-Driven / Explore-Plan-Code-Commit (`spec-driven.md`) · Self-improving as a meta-loop (`self-improving.md`) | No second _agent_. Redundancy/verification, if present, is sequential. |
| **L2 — Multi-agent orchestration** | A supervisor decomposes a goal and routes subtasks to worker agents | Orchestrator-workers / supervisor (`orchestrator-workers.md`) · Plan-Execute-as-roles (planner/executor/replanner as distinct agents, `plan-execute.md`) | A control plane _between_ agents: routing, shared-vs-isolated state, dispatch mode (handoff vs delegation). |
| **L3 — Research / synthesis super-loops** | A breadth-first information-gathering **specialization of L2**: plan → fan out parallel researchers in isolated contexts → compress → cite/verify → single-writer synthesis | Auto-Research / deep-research fan-out (`auto-research.md`) | Per-researcher context **isolation** + compression on return + a separate citation gate; writing is single-threaded. |
| **L4 — Verification & ensemble** | Quality/robustness via **redundancy** (run N, aggregate) or via an **explicit gate** (a check between "generated" and "accepted") | Evaluator-optimizer (`evaluator-optimizer.md`) · Self-consistency, Debate/Council, Mixture-of-Agents, LLM-as-jury / adversarial-verify panel (`debate-ensemble.md`) | Either aggregates diverse outputs, or sits _between_ generated and accepted as a check. **Not a standalone body** — it always wraps or follows a generation. |
| **L5 — Control plane** | The orthogonal sub-systems every loop needs regardless of shape | Termination · Context · Verification · Budgets · Durability (`control-plane.md`) | **Mandatory and shared.** Wraps every body. A plan missing any of the five is incomplete by definition. |

### The orthogonal dispatch wrapper

Not a layer — a wrapper. It governs **when / where / how-supervised** any L1–L4 body runs, and never alters the body.

| Wrapper | What it is | Members | Defining property |
| --- | --- | --- | --- |
| **Dispatch & oversight** | Detached execution + the oversight plane around it | Async / Background / Scheduled agents · human-in-loop interrupt + agent inbox · fleet orchestration (`async-oversight.md`) | Relocates _who waits_ and _how it's reviewed_; the loop body is unchanged. Hand the **UX** of this wrapper to the sibling `agentic-ux` skill — design the dispatch mechanism here, score the operator experience there. |

---

## 2. Composition diagram

How the layers nest and wrap. Read top-down for "what contains what."

```text
DISPATCH WRAPPER  (async / background / scheduled + inbox / HITL)  — ORTHOGONAL
   └─ wraps any body below to run it detached & supervised; never changes the body
      │
      L2  ORCHESTRATOR-WORKERS  (supervisor routes runtime-discovered subtasks)
         ├─ each worker runs an L1 body (ReAct / Plan-Execute / Spec-Driven / Ralph)
         ├─ L3 AUTO-RESEARCH **IS** this L2 shape, specialized for breadth-first research
         │     ( = orchestrator-workers + a citation/verify pass )
         └─ a worker's output may be gated by ↓
            │
            L4  VERIFICATION & ENSEMBLE   (the universal SUB-STEP — never a body)
               ├─ evaluator-optimizer wraps a single generator (L1) OR a parallel one
               ├─ debate / council / MoA  replaces a single generate with N + aggregate
               ├─ self-consistency  is the cheap baseline every costlier L4 must beat
               └─ adversarial-verify panel = a GATE droppable after ANY L1–L3 generation
                  │
      L1  BODIES ─┘
         ├─ Reflexion's Actor can itself be a ReAct / Plan-Execute sub-loop  (L1-in-L1)
         ├─ Self-improving is an OUTER meta-loop; its inner loop is any L1 body
         ├─ Spec-Driven's CODE stage is a verification-driven inner loop (L4 oracle gate)
         └─ Ralph is the DEGENERATE L1 body  (model + tools + stop; fresh ctx; state on disk)

L5  CONTROL PLANE  — instantiated by ALL of the above, NOT OPTIONAL:
      termination · context · verification · budgets · durability
```

---

## 3. Load-bearing composition facts

Each is a hard constraint on what may nest in what. Violating one is a finding in EVALUATE and a §SelfAudit miss in PLAN. Confidence noted where the fact is folklore rather than measured.

- **Auto-Research (L3) = orchestrator-workers (L2) + a citation/verify pass (L4).** It is not a new primitive. It is the L2 fan-out shape specialized for breadth-first research, with two non-negotiable additions: **mandatory context isolation** per researcher (so parallel agents don't poison each other's context) and **single-threaded writing** (one writer synthesizes after _all_ research returns). Drop either and you get the disjointed-report failure. _(Empirically-supported — Anthropic's multi-agent research system.)_

- **Evaluator-optimizer nests inside an orchestrator worker.** A worker can be wrapped in a generate→critique→revise loop before it returns its result to the supervisor — the supervisor sees a vetted artifact, not a first draft. The nesting is L4-inside-L2. This is the canonical R6-in-R4 composition; name it explicitly in the blueprint rather than hiding the inner loop.

- **Adversarial-verify is a droppable SUB-STEP, not a topology.** N skeptics, each instructed to refute the claim; majority-refute kills it. It is a **gate you drop after any L1–L3 generation**, never a loop body in its own right. Do not route to it as a "topology"; attach it as the L4 verification gate when no executable oracle exists (the best available proxy). _(Practitioner-folklore on exact panel size; the diversity-of-error principle behind it is supported.)_

- **Ralph is the degenerate L1 body.** Reduce L1 to its minimum and you get Ralph: **model + tools + stop-condition**, with **fresh context per iteration** and **all state externalized** (git + plan/ledger + progress file). The claim "everything is a Ralph loop" is that this is the _universal substrate_ — every other L1 body is Ralph with richer **in-context** memory instead of externalized memory. Use this as the lens: when a fancier body isn't earning its in-context memory, collapse it toward Ralph. _(Practitioner-folklore — Geoffrey Huntley; useful framing, not a measured claim.)_

- **Self-improving is an OUTER meta-loop wrapping any inner body.** The inner loop solves the task (any L1/L2 body Q1–Q8 selected); the **outer** loop reflects on the run, mutates a _durable substrate_ (skill / prompt / tool / lesson file), and **keeps the change only if a held-out utility says it helped**. The nesting is meta-over-body. The inner body is fully interchangeable — self-improving composes _over_ a route, it does not replace one.

- **Plan-Execute straddles L1↔L2.** Same mechanism, different seating. **One agent** doing plan-then-execute-then-replan is **L1**. **Planner / executor / replanner as distinct agents** is **L2**. Choose the seating by whether the roles need genuine isolation (distinct context windows, distinct models) — if not, keep it L1 (cheaper, no inter-agent coordination cost). Name which seating you chose in the topology field.

- **Self-consistency is the BAR any costlier ensemble must beat.** Sample-K-and-vote is the cheap L4 baseline. Debate, Mixture-of-Agents, and jury panels cost more and **must be justified against** self-consistency on _this_ task — because at equal compute, much of debate's apparent lift is just the ensemble/voting effect, not the debate. If you can't say why the costlier mechanism beats sample-and-vote here, route to self-consistency. _(Empirically-supported — equal-compute comparisons repeatedly show the ensemble effect dominates.)_

- **L5 is mandatory and shared by every body.** Termination · context · verification · budgets · durability are instantiated by _every_ loop, L1 through L4. A "Ralph loop" is just a specific set of L5 choices (fresh context + goal-gate/ledger-empty termination + git-per-iteration durability + commit-gate verification). When you name a body, you are committing to fill all five L5 slots — `control-plane.md` is where you set them.

---

## 4. How to name a nested plan (the CHOSEN LOOP TOPOLOGY field)

Field 3 of the Orchestration Blueprint is **CHOSEN LOOP TOPOLOGY + WHY** with a **Primary** line and a **Nested (if composite)** line. A topology name that hides the nesting is incomplete. Use this grammar.

**Grammar:** `{primary body} {± nested bodies, with where each sits} {+ L4 gate} {+ dispatch wrapper if detached}`

State **the seating relationship** with these connectors:

- **`wraps`** / **`inside`** — an outer construct contains an inner one (self-improving _wraps_ a body; evaluator-optimizer _inside_ a worker).
- **`per-{role}`** — a body runs once per worker/branch (`ReAct per-worker`).
- **`then`** — a sequential gate after generation (`… then adversarial-verify panel`).
- **`as roles`** — Plan-Execute split into distinct agents (vs. `as one agent`).

| Composite shape | How to name it in the field |
| --- | --- |
| Auto-Research | `Orchestrator-workers (L2) fan-out, ReAct per-researcher, isolated context + compression-on-return, then a single-writer synthesis + a citation/verify pass (L4)` |
| Evaluator inside a worker (R6-in-R4) | `Orchestrator-workers (L2); each worker wraps an evaluator-optimizer loop (L4) before returning` |
| Self-improving over a body (R9) | `Self-improving outer meta-loop wrapping {inner body, e.g. Ralph}; held-out-utility gate (L4) governs retention` |
| Plan-Execute, one agent | `Plan-Execute as one agent (L1): plan → execute → replan, plan persisted to disk` |
| Plan-Execute, split roles | `Plan-Execute as roles (L2): planner / executor / replanner as distinct agents` |
| Spec-Driven coding | `Spec-Driven / Explore-Plan-Code-Commit (L1); CODE stage is a verification-driven inner loop on the test/build oracle (L4)` |
| Any body + skeptic gate | `{body} then adversarial-verify panel (N skeptics, majority-refute) as the L4 gate` |
| Async-dispatched body | `{full body name} — dispatched async/background, on-the-loop PR review (dispatch wrapper)` |

**Anti-pattern (do not write):** "use an orchestrator-workers pattern" or "a debate loop." Those name a layer, not a plan — they omit the inner body, the gate, and the seating. The reviewer (and the operator) must be able to read the topology line and know exactly what contains what, without opening the transcript.

**Cross-check against L5.** Every body you name in the topology field inherits the full L5 control plane. After naming the nesting, confirm fields 6–10 of the blueprint actually set termination, parameters, gate, context, and durability _for each named body_ — a nested evaluator-optimizer has its own iteration cap; a per-researcher ReAct has its own tool-call budget. Naming the nesting is step one; instantiating L5 per nested body is what makes it executable.

---

## 5. Worked composition examples

Three compositions that appear frequently in real plans. Each shows the abbreviated blueprint field 3 (topology) and the critical L5 choices that make the nesting executable — not pseudocode, but the decisions required before a runnable sketch can be written.

---

### 5a — Orchestrator-of-evaluator-loops (R6-inside-R4)

**When to use:** Runtime-discovered subtasks where each subtask has an assessable quality criterion (e.g., code that can be compiled; answers that can be verified against a source; analyses that can be scored by an LLM judge). The supervisor routes; each worker refines before returning.

**Topology field 3:**

```text
Primary: Orchestrator-workers (L2) — supervisor routes runtime-discovered subtasks to specialist workers.
Nested: each worker wraps an evaluator-optimizer loop (L4/R6) before returning:
  generator → critique (separate judge, ≠ generator model) → revise → PASS or cap-and-return-best.
L4 gate: per-worker evaluator-optimizer is the gate; supervisor receives only vetted artifacts.
L5 outer (supervisor): termination = all workers returned; context = isolation per worker; budget = supervisor-level token budget.
L5 inner (evaluator-optimizer): termination = oracle PASS or max_iter=3; context = accumulating generator+feedback within the worker; budget = per-worker token ceiling.
```

**Critical L5 choices:**

- Inner loop's max_iter cap (default: 3 revisions before return-best) — prevents runaway refinement within a single worker.
- Judge model ≠ generator model for each worker's critique step (prevents self-preference bias; the Anthropic finding that evaluator-optimizer degrades when generator grades itself).
- Isolation: each worker's context is isolated from other workers (prevents cross-contamination of intermediate drafts).
- Outer durability: checkpoint after each worker returns (long fan-outs can resume from the last completed worker).

**Rejected-alternatives note required:** Single-pass orchestrator (R4 without R6 inside) — rejected when first-draft quality is below bar and revision demonstrably helps. Auto-Research (R3) — rejected if subtasks are not independent research threads (shared state, or one task's result gates another).

---

### 5b — Self-improving outer loop wrapping a Ralph loop (R9 over R1)

**When to use:** A coding or document-generation task class that repeats many times (e.g., test-driven feature generation, recurring doc audits), where you want the skill/prompt to compound across runs, and you have a cheap held-out utility (test pass rate, link-check pass rate, scoring rubric).

**Topology field 3:**

```text
Primary: Self-improving outer meta-loop (R9) — reflects on the run, mutates the durable skill/prompt,
  measures on a held-out set, and keeps the change only if utility improves.
Inner body: Ralph (R1 / L1) — fresh-context-per-iteration, state in git + ledger + plan, greenfield checklist.
L4 gate on outer: held-out utility (test pass rate on a held-out batch) — mutations are kept iff utility ≥ best-so-far.
L5 outer: termination = plateau stop (no improvement for K consecutive mutations) or outer budget; context = durable skill/prompt/lesson file (externalized).
L5 inner (Ralph): termination = ledger-empty + max_iterations; context = fresh per iteration; durability = git-commit per completed item.
```

**Critical L5 choices:**

- Held-out set must be separate from the training items Ralph is running against (contamination makes the outer loop reward-hack).
- Archive-not-greedy: preserve stepping-stone mutations even if they don't immediately pass — the outer loop may need to pass through a local minimum. `self-improving.md` §3.
- Inner Ralph uses git for durability; the outer loop must not mutate the skill mid-Ralph-run (race condition — outer loop updates complete only between Ralph sessions).
- Outer iteration cap: self-improving can spiral; a hard cap (e.g., 10 outer iterations) plus a plateau detector prevents indefinite execution.

**Rejected-alternatives note required:** Evaluator-optimizer (R6) — rejected when the task class repeats across many sessions (R6 operates within one session; R9 compounds across sessions). Single-pass Ralph (R1) — rejected when the recurring failure class is systematic and a skill/prompt mutation can fix it across future runs.

---

### 5c — Auto-Research fan-out with a debate-based verify stage (R3 + L4 debate)

**When to use:** Breadth-first research where the synthesized report will be used to make a high-stakes decision (e.g., competitive landscape informing a product pivot, security analysis), and the synthesis step benefits from adversarial challenge before the final report is written.

**Topology field 3:**

```text
Primary: Auto-Research fan-out (R3 = L2 + citation/verify L4):
  orchestrator → N parallel researchers (isolated contexts) → compress + cite/verify → single writer.
Additional L4 gate: after the single writer produces a draft, a debate panel (3 agents, majority-refute)
  challenges each major claim. Claims that survive challenge are retained; challenged claims are flagged
  for the single writer to revise or disclaim.
Final output: revised report with explicit confidence flags on challenged claims.
L5 researchers: context isolation + compression-on-return + per-researcher tool-call budget.
L5 writer: accumulating draft + challenge annotations; termination = all challenges addressed.
L5 debate panel: 3 agents, independent contexts; aggregation = majority-refute (2/3 refute = flagged).
```

**Critical L5 choices:**

- Citation/verify pass (L4, standard Auto-Research) comes _before_ the debate panel — the debate challenges the synthesized draft, not raw researcher output.
- Debate panel agents use separate model families or at least separate contexts (prevents correlated errors — a shared-context debate is not adversarial).
- Challenged claims are _flagged_, not deleted — the writer decides how to address each flag (disclaimer, revision, or additional evidence). The debate panel is not the final arbiter.
- Fan-out budget: set per-researcher token ceiling explicitly; the added debate step requires a separate budget allocation beyond standard R3.

**Rejected-alternatives note required:** Single-writer synthesis only (standard R3) — rejected when claim quality variance is high and a single expert reader can't catch all error types. Self-consistency vote on each researcher's output — rejected because the synthesis step already resolves researcher disagreements; the debate gate is for the _synthesized_ narrative, not the raw inputs.

---

## 6. Substrate adapters — runnable sketch by carrier

Field 11 (EXECUTION SUBSTRATE + RUNNABLE SKETCH) must compile to a real carrier. The blueprint names a substrate and a sketch specific enough to execute. This section gives the minimal required elements per substrate so the sketch is complete.

| Substrate | Minimal required elements in field 11 |
| --- | --- |
| **Claude Code subagents** (`Task` tool) | Agent count and isolation model (parallel Task calls vs sequential); the task prompt passed to each subagent (or a template); the output schema subagents return to the orchestrator. Example sketch: `Task(prompt=PLAN.md §{step}, tools=[...])` repeated per step, results collected. |
| **Workflow tool** (durable, resumable, scheduled) | `agent()` or `parallel()` / `pipeline()` call structure; the schema for structured output; concurrency cap if fan-out; any `phase()` labels. Example sketch: `const results = await parallel(items.map(x => () => agent(prompt(x), {schema: SCHEMA})))`. |
| **Bash `while` loop** (fresh-context-per-iter, a.k.a. Ralph) | The loop command with `--max-iterations` flag; the prompt file path (`cat PROMPT.md \| claude`); the state files (PLAN.md, progress.md, git commit). Example: `while :; do cat PLAN.md \| claude --max-iterations 50; done`. Must include a hard cap enforced externally. |
| **Stop-hook** (session-internal loop, same context) | The hook trigger condition; the loop body the hook runs; the termination signal the model emits to escape. Example: `on_stop → if !plan_complete: re-invoke with plan remainder`. Appropriate only for short loops (accumulating context); use Workflow for long/unattended. |
| **Cron / scheduled agents** | The cron expression or trigger; the entrypoint command; the durable state path the agent reads on resume and writes before exit. Example: `0 6 * * * python3 agent.py --state .agents/brain/audit-state.json`. Requires external durability; the agent must be idempotent. |
| **Single session** (no substrate wrapper) | State the turn count, the tool set, and how the loop closes (explicit COMPLETE marker or oracle PASS). Example: "single session, ≤10 turns, ReAct over Bash + Read + Write, terminates on `test` passing". |
