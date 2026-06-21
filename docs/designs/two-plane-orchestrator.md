# Design: the two-plane orchestrator (working name: `plane-forge`)

A `nonoun-plugins` orchestrator that plans and reviews any system on the **two planes** — **OUTSIDE-IN**
(the goals: what we're trying to do and how we'll know it's good) and **INSIDE-OUT** (the foundations:
the technical structure that honors the physics and constraints) — while **preventing the two analyses
from polluting each other**, producing **two durable documents** that persist as guidance, and
**maintaining them over time** as either plane changes.

> Status: **DESIGN FOR REVIEW.** Nothing built. This doc exists so we can review and recalibrate before
> the symmetric skill work (the OUTSIDE-IN `goals-decomposer`) and the staged-isolation technique note.

## 1. What we're carrying forward (and what we're not)

**Carrying forward** (compose, don't invent):

- The **two-plane convention** just established in `nonoun-skills/HOWTO.md` §1 — OUTSIDE-IN = the intent
  axis (goals), INSIDE-OUT = the mechanism axis (foundations); orthogonal to intent/mechanism; the 2×2
  whose mechanizable cells route to a `bin/`.
- The decomposer **doctrine of fresh-context adversarial verification** — *"a verifier sharing the
  author's context inherits its blind spots."* The orchestrator generalizes this from *one* isolated
  step to *every* plane analysis.
- The `nonoun-skills` per-plane **skills as the method+rubric+bin**: `architecture-decomposer`
  (INSIDE-OUT, exists) and the planned `goals-decomposer` (OUTSIDE-IN, item #1). The agents *consume*
  these skills; they don't re-encode them.
- The `.agents/harness` **durable-state pattern**: `lattice.json` + an append-only `ledger/` +
  `rubric/` + `policy/` + staleness-propagation + regeneration. The two docs are a **2-cell lattice**.

**Not** carrying forward: this is **not** a code-generation loop (that's `dev-kernel`). It produces and
maintains two **planning/spec documents** and a verdict — the artifacts that *precede* and *govern*
implementation.

## 1a. Relationship to the decomposers — consumer, not duplicate

The orchestrator owns **isolation, the two living docs, the cross-check, and maintenance over time**.
It does **not** own how a single plane is graded — it calls the decomposer skills for that:
`goals-decomposer` grades the Charter, `architecture-decomposer` grades the Blueprint. If those skills
get sharper, the orchestrator gets sharper for free. (Same parallel-not-dependency stance as
`brand-guidelines-system.md` ↔ `brand-decomposer`.)

## 2. Core concepts

### 2.1 The two living documents

| Doc | Plane | Holds | Graded by |
|---|---|---|---|
| **The Charter** | OUTSIDE-IN | the problem, the ranked architecture-characteristics (*-ilities*), principles, KPIs/SLOs, falsifiable acceptance criteria, the rubric the work is held to | `goals-decomposer` (item #1) / `product-forge` |
| **The Blueprint** | INSIDE-OUT | bounded contexts + ownership, module/container graph, contracts, the dependency graph + ordered layers, the fitness functions | `architecture-decomposer` + `dependency-check.py` |

Both are **terse, versioned, evidence-linked** (every claim cites the request, a Charter goal, or a
constraint) — the same discipline as a decomposer **card**. They are the orchestrator's durable state;
everything else (agent transcripts) is disposable.

### 2.2 Staged isolation — the pollution guarantee

The heart of the answer to *"do we prevent context pollution?"* — **three isolated agent contexts**,
sequenced so the dependency between planes is honored without cross-contamination:

1. **Charter agent** (Stage A) — fresh context. Input: the request only. **No architecture in context**,
   so the goals can't be bent to fit a structure that doesn't exist yet. Output: the Charter.
2. **Blueprint agent** (Stage B) — fresh context. Input: the Charter as a **read-only contract**. It
   reasons on structure independently; it **cannot edit the Charter** — if a goal is infeasible or two
   goals contradict, it raises a **tension signal** back to the orchestrator (an explicit finding, never
   a silent rewrite). Output: the Blueprint.
3. **Cross-check agent** (Stage C) — fresh context. Input: **both** docs. Asks the one question neither
   author can ask itself — *does the Blueprint actually serve the ranked goals in the Charter?* — and
   emits the **2×2 verdict** + misfit findings. This is the "elegant solution to the wrong problem"
   detector.

The orchestrator's own context holds **only the two docs + the ledger**, never the agents' reasoning —
so the *orchestrator* doesn't accumulate pollution either. Three guarantees, stated plainly:
**(a)** Charter precedes any architecture (no anchoring); **(b)** the Blueprint can honor but not
relitigate goals (no goal-drift); **(c)** the seam is graded by a third party (no author grading itself).

### 2.3 The cross-check — the seam rubric

The cross-check is where the two planes meet (the 2×2's SHIPPABLE cell). It is **gated, not optional**
— skipping it is how the two docs silently diverge. It checks:

- **Coverage:** every *ranked* -ility in the Charter has a **named structural mechanism** in the
  Blueprint (a scalability goal → a stated bottleneck + an independent scale path; a security goal → a
  trust boundary). An unserved high-rank goal is a gate finding.
- **Contradiction:** no Blueprint choice violates a Charter **principle** (e.g. "stay vendor-neutral"
  vs. a hard dependency on one vendor's primitive).
- **Fit quadrant:** OUTSIDE-IN score × INSIDE-OUT score → *right-goals/won't-hold* vs.
  *holds/wrong-goals* (the elegant-solution-to-the-wrong-problem cell) vs. SHIPPABLE.

A misfit is routed to the **right** doc's owner (a coverage gap → the Blueprint; an unrankable or
contradictory goal → the Charter), never patched at the seam.

### 2.4 Maintenance over time — staleness + regeneration

The 2-cell lattice has one edge: **Charter → Blueprint** (`derived-against`). Each doc carries a content
hash + provenance.

- When the **Charter** changes, the Blueprint is marked **STALE** (it was derived against the old goals)
  and the orchestrator schedules a Stage-B regeneration + a fresh cross-check. Not a silent edit — a
  deliberate `STALE → REGENERATING → VALIDATED` transition, with a **ledger entry naming the Charter
  delta** that triggered it.
- When the **Blueprint** changes (a refactor), the cross-check alone re-runs (the Charter is upstream,
  unaffected).
- **Section-level staleness** (not whole-doc): a Charter edit to one goal stales only the Blueprint
  sections that cite it — so a typo fix doesn't regenerate the world.

This is `harness-forge`'s staleness-propagation, scoped to two cells. The ledger makes the *why* of
every regeneration inspectable.

## 3. The loop (the heart)

```
INTAKE      request → orchestrator
  ↓
CHARTER     Stage A (isolated) → produce → goals-decomposer grades → < bar? iterate
  ↓
BLUEPRINT   Stage B (isolated, Charter read-only) → produce → architecture-decomposer grades
  ↓             ↖ raises a TENSION signal if a goal is infeasible/contradictory → back to CHARTER
CROSS-CHECK Stage C (isolated, both docs) → 2×2 verdict + misfit findings
  ↓             ↘ misfit → routed to the owning doc, re-enter its stage
COMMIT      both docs + ledger entry persisted (durable state)
  ↓
MAINTAIN    on any doc change: section-level staleness → schedule regeneration → re-cross-check
```

Bounded and attended by design (the `harness-builder` stance): explicit caps, a no-progress detector
(if Charter↔Blueprint ping-pong N times without converging, halt and surface the irreducible tension to
a human — that *is* the finding).

## 4. Skill / agent / MCP split (respecting the repo boundary)

- **Skills** (`nonoun-skills`, method+rubric+bin, reused as-is): `architecture-decomposer` (have),
  `goals-decomposer` (item #1, to build). `nonoun-skills` is **skills-only** — none of the orchestration
  below can live there.
- **Agents** (`nonoun-plugins`, this plugin): the **orchestrator** + the three stage agents (Charter,
  Blueprint, Cross-check) + the **maintainer**. Each stage agent is a thin role that loads the matching
  skill and runs it in isolation.
- **MCP** (optional, later): a read-only **query surface** over the two docs + ledger (mirroring the
  existing `*-query` MCP servers) so *other* agents can read the current Charter/Blueprint without
  re-deriving them — the docs become shared, citable context.

## 5. Data model

- `charter.json` / `blueprint.json` — the two docs (terse, evidence-linked; schemas TBD, modeled on the
  decomposer cards).
- `lattice.json` — two cells + the `derived-against` edge + per-cell maturity (`draft / validated /
  stale / regenerating`) + content hashes.
- `ledger/*.jsonl` — append-only: every produce / grade / cross-check / regeneration, each with its
  trigger and verdict. The audit trail.
- `bin/` — a deterministic **lattice/staleness checker** (which cell is stale, which edge is violated)
  and the **cross-check coverage gate** (every ranked -ility has a Blueprint mechanism) — the
  mechanizable half of the seam, routed to code per the doctrine.

## 6. Build increments (proposed, post-review)

1. **Durable state** — the two doc schemas + `lattice.json` + the ledger + the staleness `bin/`.
2. **The three stage agents** + the orchestrator loop (isolated contexts; consume the skills).
3. **The maintainer** — staleness → regeneration, section-level, ledgered.
4. **The MCP query surface** over the doc pair.

(#1 of *this* design is independent of `goals-decomposer`; it can use `product-forge` for the Charter
until the symmetric skill exists.)

## 7. Decisions — RESOLVED (2026-06-21)

1. **Doc names → Charter / Blueprint.** Evocative and distinct from the decomposer cards they project from.
2. **Blueprint agent input → a distilled constraints extract.** The orchestrator extracts the *binding*
   subset of the Charter — the **ranked characteristics + principles + non-goals** (not the prose/
   narrative) — and hands *that* to the Blueprint agent. Least anchoring; the extraction is its own small
   isolated step. The full Charter is *not* in the Blueprint agent's context. (The central pollution
   guarantee.)
3. **Staleness → section-level.** A Charter edit stales only the Blueprint sections that cite the changed
   characteristic/principle. Requires stable IDs: each Charter characteristic/principle has an `id`, and
   each Blueprint mechanism cites the `id`(s) it serves (`serves: [char.scalability, …]`).
4. **OUTSIDE-IN home → `goals-decomposer`** (built, `nonoun-skills/code-skills`). The Charter agent loads
   it; `product-forge` remains the broader-bet taste judgment, not the charter grader.
5. **Home → extend `.agents/harness` directly** (no new plugin). Realize the two planes as a small
   lattice using the existing conventions: **Charter = a `spec` cell**, **Blueprint = a `capability`
   cell** (`depends_on` the spec cell), **cross-check = a `rubric` cell** bound to the Blueprint, with the
   **`ledger`** for maintenance. Names validate against `naming.schema.json`; maturity walks
   `defined → instantiated → validated → … → stale → regenerating`.
6. **Agents → single agent per plane; a council at the cross-check.** One Charter agent (loads
   `goals-decomposer`), one Blueprint agent (loads `architecture-decomposer`); the cross-check fans out a
   small critic set (coverage · contradiction · feasibility) where independent perspectives earn their cost.

### How the two planes map onto the harness lattice

```
spec.workflow.charter        (Charter)   maturity: validated when goals-decomposer grades it GOVERNABLE
  └─ capability.workflow.blueprint  (Blueprint, depends_on the charter)  validated when architecture-decomposer passes
       └─ rubric.workflow.cross-check  (the seam; bound to the blueprint)  the gated coverage check
ledger.workflow.events       (every produce / grade / extract / cross-check / regeneration, with its trigger)
```

A Charter change → the `spec` cell re-validates → the `capability` (Blueprint) cell flips to **`stale`**
(section-level) → regenerate → re-run the `rubric` cross-check. The deterministic half (coverage gate +
which cells are stale) is `bin/`; the judgment half is the agents.

## 8. Risks

- **Over-isolation → the wrong problem.** If the Charter is thin, the Blueprint solves it elegantly but
  pointlessly. *Mitigation:* the gated cross-check + the Blueprint's tension-raising back-channel.
- **Maintainer churn.** Whole-doc staleness regenerates the Blueprint on every typo. *Mitigation:*
  section-level staleness (open decision #3).
- **Skipped cross-check → silent drift.** The two docs diverge if the seam isn't a gate. *Mitigation:*
  the cross-check is a gate; a stale lattice edge blocks "done."
- **Context growth.** The orchestrator holding both docs + a long ledger bloats. *Mitigation:* docs stay
  terse; the ledger is summarized; the MCP surface offloads reads.
- **Irreducible tension read as failure.** Sometimes the goals genuinely can't all be met. The
  no-progress detector must surface that to a human as a *decision*, not loop forever.
