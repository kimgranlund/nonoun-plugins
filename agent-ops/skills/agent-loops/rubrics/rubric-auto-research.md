# Rubric — Auto-Research Fan-Out

Score an **auto-research / multi-agent research fan-out** plan (proposed or in-flight): a lead agent plans a query, dispatches parallel **isolated** subagents to search, compresses their findings, verifies/cites, and a **single writer** synthesizes the report. Use in **EVALUATE mode** to audit an existing research-fleet plan or transcript, and as the acceptance bar in **PLAN / COMPOSE mode** before a fan-out is declared READY-TO-RUN.

**Backbone question:** _Is the research fan-out independent, bounded, compressed, and cited?_ The four [gate] dimensions below are that question, decomposed. Most fan-out failures surface there: a hidden cross-subtask dependency that breaks parallelism, an unbounded width/depth/tool spiral, raw transcripts dumped back into the lead's window, or parallel writers producing an incoherent report. The reviews catch the quality and economics calls a builder makes repeatedly.

**Band:** per-family. Load this rubric **only when the plan composes the auto-research family** (selectors: `auto-research`, `deep research`, `lead agent + subagents`, `supervisor-subagent research`, `fan-out search`, `planner/executor/publisher`). It is **not** loaded for every plan.

**Dependency (mandatory):** this rubric **depends on `rubrics/rubric-loop-control.md`** — its gates (C1 termination-stack, C2 budget, C3 verification-gate, C7 durability-idempotency) **also apply** to every auto-research plan and must be loaded and scored alongside this one. A fan-out plan ships only when the **union** of loop-control's gates and this rubric's gates passes. The cross-cutting `rubrics/rubric-loop-selection.md` and `rubrics/rubric-plan-quality.md` apply as well (always-load band).

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate blocks SHIP; it is not a matter of opinion. Cross-cutting gates are backed by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`; per-family gates (AR1/AR3/AR5/AR7) are **[mech-partial]** — the criterion is structural but no automated script enforces it; agent judgment applies.
- **[mech-partial]** — mechanically checkable criterion, no automated script — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment. Read the artifact, cite evidence, score **1–5**.

**Ship rule:** an auto-research plan ships when **every [gate] passes AND no [review] dimension < 3** — across this rubric _and_ every other loaded rubric (loop-control, loop-selection, plan-quality). Record evidence for every finding (the plan field, the parameter, the missing stage). A finding without a citation is an opinion.

**Calibration caveat:** this rubric is **draft (v0.1.0), 0 calibration samples.** Treat every score as **directional, not authoritative**, until the ROADMAP v0.2 calibration bar is met. The [gate] dimensions are the only mechanically verifiable layer; [review] anchors are first-draft and will move. Confidence on the underlying criteria is mixed: bounding/isolation/single-writer-synthesis are **empirically-supported** (Anthropic multi-agent research engineering report); specific effort-sizing thresholds and the ~15× premium figure are **practitioner-folklore-to-directional** and should be read as order-of-magnitude, not exact.

Map findings to the topology's named failure modes via `../references/auto-research.md`.

---

## Dimensions

The four backbone gates (AR1, AR3, AR5, AR7) come first — run them first, most failures surface there — then the four reviews (AR2, AR4, AR6, AR8).

### AR1 [gate / mech-partial] — Decomposition independence

**Criterion:** Sub-tasks are genuinely independent — no hidden dependency that breaks parallelism (subtask B needs subtask A's output), and no overlap that duplicates work (two subagents researching the same sub-question).

**Test (binary):** enumerate the subtasks the lead dispatches. For each ordered pair, ask: _does one consume the other's output?_ If yes → the fan-out is secretly sequential → **FAIL** (it should be staged or single-threaded, not parallel). Then check for overlap: do two subtask briefs cover the same ground? If yes → wasted spend → **FAIL**. A pass requires a written subtask list whose items are mutually independent and non-overlapping. (Failure mode: false-parallel decomposition / duplicated fan-out — `../references/auto-research.md`.)

### AR3 [gate / mech-partial] — Bounding & termination

**Criterion:** All four fan-out bounds are set with defaults, plus a cost ceiling: (1) **fan-out width** (max subagents per wave), (2) **recursion depth** (can a subagent spawn subagents, and how deep), (3) **per-subagent tool-call cap**, (4) **orchestrator outer-loop cap** (max research waves before forced synthesis) — and a **token/cost ceiling** over the whole run.

**Test (presence × 5):** grep the plan's PARAMETERS / TERMINATION fields for all five values. Each must be a concrete number (or an explicit "operator decides + default"), not absent and not "as needed." Missing **any** of the five → **FAIL**. (This is the family-specific instantiation of loop-control C1/C2 — both must pass; loop-control checks that _a_ termination stack and budget exist, AR3 checks the _four fan-out-specific bounds_ exist.) (Failure mode: width/depth/tool-call runaway — `../references/auto-research.md`.)

### AR5 [gate / mech-partial] — Context isolation & compression

**Criterion:** Subagents run in **isolated context windows** and return **COMPRESSED findings** — a structured summary / answer schema, not raw transcripts or full page dumps — back to the lead. Additionally, the research brief itself is compressed and the plan is **persisted to external memory** (so the lead survives its own context limits across waves).

**Test (presence/structural):** confirm two things in the wiring/context fields. (1) Each subagent is dispatched into its own context (Task-tool subagent / isolated session), **not** sharing the lead's window. (2) The subagent **return contract** is a compressed shape (defined output schema / bounded summary), **not** "return everything you found." If subagents dump raw transcripts back into the lead's window → context bloat → **FAIL**. Then confirm the brief/plan is written to an external store (file / scratchpad) rather than held only in the lead's context. Missing isolation OR missing compression → **FAIL**. (Failure mode: lead-context flooding / transcript dump — `../references/auto-research.md`.)

### AR7 [gate / mech-partial] — Synthesis coherence

**Criterion:** Writing is **single-threaded after research completes** — one writer composes the final report from the collected compressed findings. The report is **not** produced by parallel writers each owning a section.

**Test (binary):** locate the synthesis stage in the wiring. Is there exactly **one** writer that runs **after** the fan-out returns? If the plan parallelizes the _writing_ (N subagents each draft a section, concatenated) → incoherent / contradictory report → **FAIL**. Parallelism belongs in **research**; synthesis is serial. A pass requires a named single-writer synthesis step downstream of the research fan-out. (Failure mode: parallel-writer incoherence — `../references/auto-research.md`.)

### AR2 [review] — Effort right-sizing

**Criterion:** Subagent count, depth, and tool budget **scale to query complexity** — no 50-subagents-for-a-trivial-query (over-spawn), no under-parallelized single-thread for a genuinely broad query (under-investigation). Concrete budgets are specified per the query's breadth.

**Evidence to cite:** the subtask count vs the query's actual breadth; the per-subagent tool budget vs the depth each sub-question needs; any stated sizing rule ("simple fact → 1 subagent / few calls; broad survey → N subagents / deeper budget").

**Score (1–5):**

- **1** — effort is fixed/reflexive regardless of query (e.g. always-spawn-N), or grossly mismatched (a large fleet for a one-fact lookup, or a single thread for a 20-source survey).
- **3** — effort is roughly proportional to breadth and budgets are stated, but the sizing is a single static number with no rule tying it to complexity.
- **5** — an explicit sizing rule maps query breadth/depth to subagent count + tool budget, with named simple/broad cases, and the chosen values sit at a defensible point (not inflated past diminishing returns).

### AR4 [review] — Delegation contract

**Criterion:** Each subagent gets a complete brief: **objective** (the exact sub-question), **output format** (the compressed return shape), **source/tool guidance** (where to look, which tools), and an **explicit boundary** (what is out of scope / belongs to a sibling subagent).

**Evidence to cite:** the dispatch template / subagent prompt spec; whether all four elements are present per subagent or whether subagents are launched with a bare task string.

**Score (1–5):**

- **1** — subagents dispatched with a one-line task and no format, no source guidance, no boundary → duplication and gaps are predictable.
- **3** — objective + output format are specified, but source/tool guidance or the scope boundary is missing or implicit.
- **5** — every subagent brief carries all four (objective, output format, source/tool guidance, explicit boundary), so subtasks compose without overlap or holes.

### AR6 [review] — Verification & citation rigor

**Criterion:** A **separate post-synthesis stage** attributes **every claim to a source location**, and goes **beyond bare attribution** toward source-authority/corroboration (is the source credible, is the claim corroborated) and **uncertainty surfacing** (contested or thin claims are flagged, not laundered into confident prose).

**Evidence to cite:** the presence and placement of a citation/verification stage (is it a distinct stage, independent of the writer?); whether it only checks that citations exist or also weighs source quality and surfaces uncertainty.

**Score (1–5):**

- **1** — no citation/verification stage; claims asserted without sources, or sources attached by the same pass that wrote the claims with no independent check.
- **3** — a separate stage attributes each claim to a source, but does nothing about source authority, corroboration, or uncertainty (attribution-only).
- **5** — a separate verification stage attributes every claim, weighs source authority/corroboration, and explicitly surfaces contested or low-confidence claims. (This dimension scores the _research-quality_ gate; the cross-cutting loop-control C3 still applies to the run's overall verification gate.)

### AR8 [review] — Economic justification

**Criterion:** The plan **acknowledges the ~15× token premium** of multi-agent research, **reserves the fan-out for high-value, breadth-first tasks**, and **names a single-agent fallback** for the simple / depth-first case. (The ~15× figure is directional, from the Anthropic multi-agent report — read as order-of-magnitude, not exact.)

**Evidence to cite:** any cost-vs-value reasoning in the rejected-alternatives / confidence fields; whether a cheaper single-agent path is named for the low-value or depth-first variant; whether the task is genuinely breadth-first (parallel search wins) vs depth-first (a single thread would match the fleet at a fraction of the cost).

**Score (1–5):**

- **1** — multi-agent chosen reflexively with no cost acknowledgment and no fallback; the task is not even clearly breadth-first.
- **3** — the premium is acknowledged and the task is plausibly breadth-first, but no single-agent fallback is named for the cheap case.
- **5** — the premium is acknowledged with an order-of-magnitude figure, the fan-out is explicitly justified by task value + genuine breadth, and a concrete single-agent fallback is named for the simple/depth-first variant. (Pairs with loop-selection S5 cost/value — both must hold.)

---

## Scoring summary template

```text
Plan / artifact: {name}        Mode: {PLAN | COMPOSE | EVALUATE}
Family: auto-research          Fan-out width: {n}   Depth: {n}   Writer: {single | parallel}
Loaded alongside: rubric-loop-control (dep) + rubric-loop-selection + rubric-plan-quality

Backbone gates:
  AR1 decomposition independence .... PASS / FAIL   {evidence: subtask list / dependency or overlap}
  AR3 bounding & termination ........ PASS / FAIL   {evidence: width/depth/tool/outer-loop/ceiling}
  AR5 context isolation & compression PASS / FAIL   {evidence: isolation + compressed return shape + external store}
  AR7 synthesis coherence ........... PASS / FAIL   {evidence: single writer, post-research}

Dependency gates (from rubric-loop-control — must also pass):
  C1 termination-stack .............. PASS / FAIL
  C2 budget ......................... PASS / FAIL
  C3 verification-gate .............. PASS / FAIL
  C7 durability-idempotency ......... PASS / FAIL / N-A (short attended run)

Review dimensions (1-5):
  AR2 effort right-sizing ........... {n}   {evidence}
  AR4 delegation contract ........... {n}   {evidence}
  AR6 verification & citation rigor . {n}   {evidence}
  AR8 economic justification ........ {n}   {evidence}

Verdict:
  SHIP / READY-TO-RUN   — every gate (this rubric + loop-control + loop-selection + plan-quality) PASS, no review < 3
  BLUEPRINT-UNVERIFIED  — gates pass but the plan was not dry-run / sanity-checked against the success criterion
  BLOCK                 — any gate fails, or any review < 3
Top findings (severity-ranked, with citations + mapped failure mode):
  1. ...
```

(Calibration caveat applies to the whole scorecard: draft, directional-not-authoritative until v0.2 calibration.)
