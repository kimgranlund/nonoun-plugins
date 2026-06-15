# Execution Strategy — How a Dispatched Unit Actually Runs

`Cell: methodology.fleet.execution-strategy · Status: defined · Register: established lineage (frontier-lab workflow patterns, Ralph, autoresearch/hill-climb, context engineering); the dispatch-plan synthesis is house`

## Why This Cell Exists

The coordination spec answers *who acts and under what control*; it underspecifies *how
each unit of work executes*. That "how" is methodology-layer knowledge. Without it, the
`DispatchAdapter` passes a budget and a skill surface and the execution plan is a black
box — the dispatcher decides *that* a worker runs, nothing decides *how*. This cell is
that missing playbook. The kernel defines the strategy vocabulary here; a kit binds which
strategy to which cell type (`dispatch-policy.schema.json`); the compass assembles the plan
deterministically. Selection is policy, never vibes.

## The Execution Plan

Every dispatch carries a typed plan with five fields. The `DispatchAdapter` execution-plan
extends the contract in the coordination spec:

| Field | What it sets |
|---|---|
| `orchestration_shape` | the topology of model calls inside the unit |
| `loop_strategy` | the iteration discipline driving the engine |
| `context_plan` | the working-set / retrieval / compaction policy |
| `effort` | model tier × reasoning effort × iteration budget × parallelism |
| `delegation` | sub-agent vs team, and the depth limit |

## Orchestration Shapes

The published frontier-lab pattern set, ascending in structure.

**Default posture: maximal decomposition along real seams.** The factory is
decomposition-first and parallel-first. The selection rule inverts the usual burden of
proof: **decompose by default — prefer teams, sub-agents, and parallel/orchestrated shapes
wherever the work admits them — and justify *collapsing* to a simpler shape, rather than
justifying escalation.** A `workflow`/`system` unit defaults to orchestrator–workers or a
team; a unit with independent sub-parts defaults to parallelization.

This is not a licence for orchestration maximalism, which the methodology layer still
forbids — it is a directive to exploit *genuine* structure aggressively. Three floors keep
"maximal" effective rather than wasteful, and they are floors, not preferences:

1. **Maximal width, bounded depth.** Fan out as wide as the work admits; `delegation.max_depth`
   still caps nesting, because handoff fidelity is multiplicative (*fⁿ*) and past a few hops
   the loss exceeds the parallelism gain. Maximal means breadth, not infinite recursion.
2. **Seams must be real.** Parallelize only where sub-units are genuinely independent — the
   join must exist. Sectioning a sequential unit into "parallel" parts that secretly depend
   on each other is corruption, not concurrency (the conflict at merge is the proof the split
   was unsound).
3. **An irreducible unit runs single-pass.** A unit with no internal seams — one atomic edit,
   a single-criterion check — collapses to `single-pass`, because there is nothing to
   decompose; forcing a team onto an atom is the waste the floors prevent. Budget and the
   cost ceiling always bind.

Collapsing to a simpler shape is therefore justified by *absence of real structure* (an
irreducible unit, no independent seams, depth past the fidelity limit), never by timidity.

| Shape | When | Maps to |
|---|---|---|
| **single-pass** | deterministic-ish, low-risk cells; one call suffices | `call`/`task` scope, low risk |
| **prompt-chain** | a fixed sequential decomposition within one context | `task` with known sub-steps |
| **routing** | classify the input, dispatch to a specialized handler | heterogeneous ticket intake |
| **parallelization** | independent sub-units fanned out, then reconciled | wide `workflow` slices |
| **orchestrator–workers** | a lead decomposes dynamically and dispatches sub-agents | `workflow`/`system` decomposition |
| **evaluator–optimizer** | generate → critique → revise against a rubric | any cell with a graded quality bar |

**Parallelization reconciles by join.** The combination of parallel results is the least
artifact consistent with all of them — every fact each established, nothing invented to
force agreement (see `lattice-theory-agentic-systems.md`). When results conflict, no upper
bound exists: the parallelization was unsound and the conflict is the signal, not a merge
to paper over. Consensus across workers is the meet; synthesis is the join.

**Evaluator–optimizer is the engine's default** for definitional cells, and it is the same
generator/critic split the safety model requires — the optimizer never writes its own
signal.

## Loop Strategies

The iteration discipline inside the engine, keyed to **ticket type × target layer**.

**Ralph / fresh-context iteration.** Every iteration starts with a clean context window;
all state survives on disk, not in conversation history. The default for long-horizon work
and the mitigation for context rot. Trigger: multi-hour units, or any unit where compaction
would otherwise accumulate. One cell per dispatch already gives this property by
construction; Ralph extends it across iterations within a unit.

**Auto-research / hill-climb.** Generate → score against the bound rubric → improve the
*weakest* dimension → re-score; repeat until the score stabilizes or clears threshold. The
right strategy for **quality-maximizing** cells with a graded rubric: specs, rubrics, prose,
design, documents. Stop condition: score plateau or threshold, within budget. This is the
autoresearch technique applied as a dispatch strategy.

**Ablation / sweep / bisect.** The **diagnostic** strategies, for `bug` and `spike` tickets
and for no-progress investigations: ablation isolates which component carries an effect;
sweep optimizes a parameter across a range; bisect finds the change that broke a previously
working cell. Stop condition: the responsible factor identified, recorded as a pattern.

**Tracer-bullet / walking-skeleton.** For a new vertical slice: drive the thinnest possible
end-to-end path to a signal before widening. The probe is sized to the assumption, not the
ambition.

| Ticket type / target | Default loop strategy |
|---|---|
| feature/task → spec, rubric, pattern (graded) | auto-research hill-climb |
| feature/task → new vertical slice | tracer-bullet, then hill-climb |
| any long-horizon unit | Ralph fresh-context (wraps the above) |
| bug → operating/validated cell | bisect, then targeted fix |
| spike / no-progress | ablation or sweep |

## Delegation Topology

Two distinct nestings, often confused:

- **Sub-agents** — children a lead *dispatches*, one cell each, isolated context (the
  orchestrator–workers shape, recursively). The reason to spawn one is to keep the parent's
  context clean: the child absorbs the noise of a sub-investigation and returns only the
  structured result.
- **Agent teams** — role-specialized *peers* collaborating on one unit (e.g., advancer +
  domain specialist + critic) with explicit, typed handoffs between them.

**Depth is bounded because handoff fidelity is multiplicative.** Each delegation hop is a
lossy serialization of intent (fidelity *fⁿ* over *n* hops); past a small depth, context-loss
dominates any parallelism gain. The `delegation.max_depth` field is a hard cap. A handoff
between team peers is a typed contract, not text-in/text-out — the same trust-boundary
discipline the protocol layer applies, here inside one instance.

## Context Engineering

The context window is a **budgeted resource**, allocated deliberately — not filled.

- **Disk vs. context.** Durable state lives on disk (lattice, ledger, signals, progress
  log); only the *active working set* occupies the window. The repo remembers; the context
  forgets.
- **Just-in-time retrieval.** Pull the *minimal relevant substrate* — the cell's spec, its
  bound rubric, and the nearest patterns — not the whole corpus. Retrieve on demand over
  preloading; preloading the corpus is context hoarding and degrades the signal.
- **First-pass context quality beats iteration count.** Token economics: a 10-turn loop can
  spend ~50× a single call, so improving what the first iteration sees reduces loop count
  more cheaply than adding iterations. Front-load the right context; do not pad it.
- **Compaction is a last resort, not a strategy.** Prefer fresh-context handoff (Ralph) with
  disk state. When compaction is unavoidable, preserve decisions, rationale, and open
  threads; drop resolved detail.
- **Sub-agent isolation is a context tactic.** Delegating a sub-investigation is how the
  parent keeps its window clean — the child's context rot does not propagate up.

## Effort Ladder & Model Management

Collapse four dials into one, set by **(cell risk × scope × autonomy tier)**:

`effort = (model tier) × (reasoning effort) × (iteration budget) × (parallelism)`

| Unit profile | Effort setting |
|---|---|
| low-risk, `call`/`task`, deterministic-ish | small model, low reasoning, few iterations, no parallel |
| moderate, `workflow` | mid model, moderate reasoning, standard budget |
| high-risk / definitional (spec, rubric, architecture) | large model, high reasoning, generous budget, possibly a team |
| diagnostic (bug/spike) | mid model, high reasoning, bounded iterations |

Three rules govern the dial:

1. **Escalate quality-per-iteration before adding iterations.** On no-progress, raise model
   tier or reasoning effort first; raw iteration count is the last lever, because loop length
   dominates cost.
2. **The critic's model is an independent choice.** The generator/critic split has a *model*
   dimension, not just a prompt dimension — the critic is separately selected and calibrated,
   often differently from the generator. A model grading its own output is the failure the
   split exists to prevent.
3. **Budget tiers tighten with autonomy.** Unattended (Tier 2+) families run under stricter
   caps than attended ones; the loop surfaces a cap, it never burns through it.

## Selection Is Deterministic Policy

The mapping from unit characteristics to execution plan is a **dispatch-policy cell**
(`policy.{scope}.dispatch`), read by the compass — not a model decision at dispatch time.
Kernel defines the strategy vocabulary; the kit supplies the mapping for its family; the
compass assembles the plan as a deterministic lookup. Computation routes to code; only the
work *inside* the assembled plan routes to inference.

## Execution-Strategy Failure Modes

Orchestration maximalism in the *fabricated* sense (inventing seams that are not there;
ceremony with no real boundary). Under-decomposition (running a unit single-threaded when
real independent seams exist — the failure the maximal-decomposition default targets). Wrong
loop for the layer (hill-climbing a deterministic cell; single-passing a graded one). Context
hoarding (preloading the corpus; compaction as a strategy). Effort mismatch (a large model on
a trivial cell wastes budget; a small model on a definitional cell thrashes). Delegation too
deep (handoff loss exceeds parallelism gain — width good, depth bounded). Selection by
inference (the dispatcher "deciding" a plan a policy should compute).
