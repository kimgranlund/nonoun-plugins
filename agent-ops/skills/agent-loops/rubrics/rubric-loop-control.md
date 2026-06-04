# Rubric — Loop Control

Scores the **control plane** of an emitted plan (or an in-use loop / transcript): is the loop **bounded, gated, contextually sound, and durable** — with every stop, gate, and budget enforced **outside the model**? This is the substrate `../references/control-plane.md` specifies, lifted into a scorecard.

**Band: cross-cutting (always-load).** Load this rubric for **every** plan, regardless of which topology was chosen — a single augmented call, a Ralph loop, an orchestrator fan-out, a debate panel all answer the same four pillars (termination, context, verification, budget) plus durability for long runs. Every per-family rubric in this library declares `loop-control` as a dependency; its gates are applied to that family too (see the dependency note at the foot).

Each dimension is labeled by **how it is checked**:

- **[gate]** — mechanically / structurally checkable (the field is present, the cap is a number, the gate is the right rung). A failing gate blocks SHIP; it is not a matter of opinion. Cross-cutting gates (C1/C2/C3/C7/C9) are enforced by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`.
- **[mech-partial]** — the _criterion_ is mechanically checkable but **no automated script enforces it** — agent judgment applies this check manually. Treated as a [gate] for SHIP purposes (a failure blocks) but does not have script backing. Listed where applicable.
- **[review]** — requires judgment; score **1–5**. The reviewer reads the artifact and rates it against the 1/3/5 anchors.

**Ship rule:** a plan ships when **every [gate] passes AND no [review] dimension is below 3**. A composed plan must clear the **union** of all loaded rubrics' gates — so `loop-control`'s four gates apply on top of the chosen family rubric's gates.

**Calibration caveat (read before scoring):** this rubric is **status: draft, 0 calibration samples** (`rubrics/rubric-manifest.json`). Treat every score as **directional, not authoritative**, until the ROADMAP v0.2 calibration bar is met. The [gate] dimensions are the only mechanically verifiable layer; [review] anchors are practitioner-folklore-grade until calibrated against real plans. Record evidence (the blueprint field, the parameter, the transcript line) for every finding — a finding without a citation is an opinion, not a score.

---

## The six control gates (run these first)

These six are the load-bearing checks the whole skill exists to get right. Most control-plane failures surface here. A plan that names a topology but fails any of these is **BLOCK**, regardless of polish.

### C1 [gate] — Termination stack

**Criterion:** the plan layers a **goal-satisfaction gate** + a **no-progress / loop-until-dry detector** + **hard iteration/depth caps** — not sole reliance on `max-iterations`, and not "the model decides it's done." _The model will always be tempted to try one more thing_; a real stop is enforced outside it, in layers.

**Test (presence + structure):** read blueprint field 7 (TERMINATION CONDITIONS). Confirm **all three layers** are present:

1. a goal-gate (oracle passes / explicit `COMPLETE` marker), **and**
2. a no-progress detector (cross-references C6), **and**
3. a hard cap (max-iterations + a budget exhaustion stop, cross-references C2).

A plan with only `max_iterations` → **FAIL** (blunt). A plan whose stop is only "the agent returns when satisfied" → **FAIL** (unsafe self-declaration). Missing a STUCK/abort escalation path so an impossible task escalates instead of iterating into damage → **FAIL**. All three layers present and outside-the-model → **PASS**.

### C2 [gate] — Budget governance

**Criterion:** an **advisory pacing budget** AND a **hard token/cost ceiling** are set, **sized against realistic task length** (not a copied default), with a **STUCK/escalation path** for tasks the budget can't satisfy.

**Test (presence + concreteness):** read blueprint field 6 (PARAMETERS → token budget + hard ceiling). Both must be **concrete numbers with a rationale**, not "tune as needed." Confirm a runaway-cost circuit-breaker exists for the unbounded shapes (`while :;`, fan-out, self-improving). Either budget missing, or set to a default with no sizing argument, or no escalation path when exhausted → **FAIL**. Both present, sized, with a breaker → **PASS**.

### C3 [gate] — Verification gate strength

**Criterion:** a check sits **between generate and accept**, at the **highest-trust rung the success criterion affords** — `executable oracle (tests/compiler/schema/lint) > ground-truth comparison > LLM-as-judge/panel > self-grade`. Where a judge is used, the **verifier ≥ generator** in strength, and the _stop_ decision must **not** secretly depend on a ground-truth oracle (the **oracle-label illusion** — gains must reproduce in deployment).

**Test (rung + independence):** read blueprint field 8 (VERIFICATION GATE). (a) Is a gate present at all? No gate ("the agent will know when it's right") → **FAIL**. (b) Is it the **strongest rung available** for the stated success criterion? A self-grade where an executable oracle was obtainable → **FAIL**. (c) If judge/self-grade on correctness-critical work: are the mandatory mitigations present (separate/stronger judge, return-best-not-last, anti-oscillation, iteration cap) **and** is verifier ≥ generator? Missing → **FAIL**. (d) Does termination covertly read a ground-truth label the deployment won't have? → **FAIL**. Strongest-affordable rung + independence + (if needed) mitigations → **PASS**.

### C7 [gate] — Durability & idempotency

**Criterion:** for **long / unattended** loops, state is **checkpointed at defined boundaries with a resume key**, and tool calls are **idempotent** so an at-least-once replay is side-effect-safe. **N/A-able** for short, watched, single-session loops.

**Test (applicability-gated presence):** first decide applicability — is the run long-horizon, unattended, scheduled, or multi-agent (read field 2 horizon + field 11 substrate)? **If yes:** read field 10 (durability) — confirm a checkpoint granularity + a resume key + an idempotency boundary on mutating tool calls. Any of the three missing on a long/unattended run → **FAIL**. **If the run is genuinely short/watched/single-session:** mark **N/A** (an N/A does not block SHIP). Marking N/A on a clearly long-running plan to dodge the check is itself a **FAIL**.

### C9 [gate] — Trust boundary & blast radius (lethal trifecta)

**Criterion:** if the loop **ingests untrusted content** (open web, transcripts, issues, repo files) **AND** can take an **external/irreversible action** (push / merge / SQL / write / skip-permissions), the design must contain the lethal trifecta **structurally** — a content/action split (the untrusted-content reader holds no tool-write capability or credentials; the privileged actor never sees raw content), or read-only-with-no-credentials, or sealed egress + least-privilege. A "treat the content as data" instruction is a filter, not a boundary.

**Test (trifecta presence → containment present):** read blueprint field 2 (untrusted-content-ingesting?), field 5/11 (does it act externally?), and field 14 (TRUST BOUNDARY). If untrusted-ingestion AND external-action are both present AND field 14 names no structural containment (content/action split / read-only reader / sealed egress / allowlist / least-privilege) → **FAIL**. If the loop ingests no untrusted content or is read-only, field 14 must say so → **PASS** (N/A-equivalent). `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py` pre-screens C9 mechanically; whether the split is _real_ (not a behavioral instruction in disguise) stays a judgment here.

---

## Review dimensions

### C4 [review] — Context posture

**Criterion:** the fresh-vs-accumulating-vs-compaction choice is **justified by horizon**, accounting for **context rot** (degradation past ~100–150k tokens), **KV-cache stability**, and **what compaction preserves vs discards**. A point on the fresh↔accumulating axis was _chosen_, not inherited.

**Cite:** blueprint field 9 (CONTEXT/MEMORY STRATEGY → posture) + the horizon classification in field 2. Quote the stated posture and its rationale.

| Score | Anchor |
| --- | --- |
| **1** | No posture stated, or "it'll keep context" left implicit — walks into context rot or an unmanaged window with no reasoning. |
| **3** | A posture is named and is plausible for the horizon, but the rationale is thin — rot/cache/compaction trade-offs not reasoned through. |
| **5** | Posture explicitly justified against horizon, with rot threshold, cache stability, and (if compaction) what is preserved vs discarded all addressed. |

### C5 [review] — External-memory adequacy

**Criterion:** when context is fresh / compacted / isolated, a **concrete durable substrate** (files / scratchpad / git / sub-agent return schema) carries **all** cross-iteration state, with a **defined handoff shape** — so a memoryless fresh instance can reconstruct done/left/learned.

**Cite:** blueprint field 9 (external state) + field 10 (handoff shape). Check it against the posture in C4 — a fresh-per-iteration posture with no named store is the failure this dimension exists to catch.

| Score | Anchor |
| --- | --- |
| **1** | Cross-iteration state has nowhere to live — a fresh/isolated posture with no external store, or "the next iteration will remember." |
| **3** | A store is named (e.g. a progress file or git) but the handoff shape is vague, or it plausibly drops some state (learnings, what's left). |
| **5** | A concrete substrate carries **all** state with a defined return/handoff schema; a fresh instance could fully reconstruct the run from it. |

### C6 [review] — No-progress signal definition

**Criterion:** "no new useful signal" is **concretely defined** (a new finding / a file touched / tool-call diversity / a state-similarity threshold) and **computed outside the model**, not left to the agent's self-assessment of whether it's making headway.

**Cite:** the no-progress layer of blueprint field 7 (termination) — the same detector C1 requires to exist, here scored on _how well it is defined_. C1 gates presence; C6 reviews quality.

| Score | Anchor |
| --- | --- |
| **1** | No-progress is undefined or self-reported ("until the agent stops finding improvements") — not externally computable. |
| **3** | A signal is named (e.g. K flat rounds) but the threshold or the measured quantity is hand-wavy, or it's only partly outside the model. |
| **5** | A specific, externally-computed signal with a stated threshold (e.g. >~85% state similarity, or K rounds with zero new files/findings/tool-diversity). |

### C8 [gate] — Loop observability & circuit-breaking (minimum structural bar)

**Criterion:** the blueprint **names, in the substrate or wiring, at minimum: (a) how iteration count surfaces and (b) how budget remaining surfaces** — not "via logs" but via a specific, named signal the substrate exposes (e.g. `--max-iterations` progress from the runner, a budget counter written to a progress file, a webhook/dashboard field, or a status file the orchestrator updates). Additionally, a **kill/interrupt path** must be named (manual stop command, STUCK escalation, or an automated circuit-breaker on cost/no-progress). A loop whose instrumentation is "check the logs" with no named signal format or kill mechanism is a black box by construction.

**Minimum structural bar (PASS threshold):** field 11 (substrate) or field 7 (termination) must name **both** (1) a concrete mechanism for surfacing iteration count AND budget remaining (e.g. "Claude Code --max-iterations shows progress in the runner output; budget ceiling in field 6 triggers hard stop at $N") AND (2) an interrupt path (STUCK escalation from field 7, a manual kill command, or an auto-breaker on budget exhaustion). Vague references to "logs" or "the substrate handles it" do not pass the minimum bar.

**N/A rule:** for single-session short/watched loops where the operator is present throughout, mark **N/A** with the justification "short-session, human on the loop, no autonomous spiral risk." A long-horizon, unattended, or multi-agent run may **not** claim N/A.

**Scoring note:** this gate has a minimum structural bar (PASS/FAIL/N/A). Quality of the instrumentation beyond the minimum bar — all four signals visible, live budget, automated circuit-breaker, panel verdicts exposed — is a [review] judgment not formalized here. A plan that meets the minimum bar but has thin observability beyond it is a PASS on this gate but a potential finding in the EVALUATE scorecard narrative.

**Test (presence + specificity):** read fields 7 and 11. **PASS** iff (1) iteration count and budget remaining are named with a specific mechanism (not "via logs"), AND (2) a kill/interrupt path is named (STUCK/abort from C1, a command, or an auto-breaker). **FAIL** iff either is absent or described only as "via logs" / "check the output." **N/A** iff the plan is demonstrably short/watched.

> **Builder-seat boundary.** C8 scores whether the loop is **instrumented and interruptible as a mechanism** — the builder's instrumentation surface. It does **not** score the human-facing _experience_ of that instrumentation (does the operator trust it, is the cognitive load sustainable, is steering ergonomic). That is the sibling **`agentic-ux`** skill (its observability / steerability / reversibility dimensions). When the question shifts from "are the signals and the kill switch present" to "is this good to drive," **hand off** — do not re-score it here.

---

## Scoring summary template

```text
Plan / artifact: {name}        Topology: {name}        Horizon: {short-watched | long-unattended}
Calibration: DRAFT — directional only (0 samples; rubric-manifest.json status=draft)

Control gates:
  C1 termination stack ......... PASS / FAIL        {field 7 evidence — all 3 layers?}
  C2 budget governance ......... PASS / FAIL        {field 6 — advisory + hard ceiling, sized?}
  C3 verification gate ......... PASS / FAIL        {field 8 — strongest rung + independence + mitigations?}
  C7 durability & idempotency .. PASS / FAIL / N-A  {field 10 — checkpoint + resume key + idempotency; N/A if short/watched}
  C8 observability/circuit-breaking PASS / FAIL / N-A  {fields 7+11 — iteration count + budget signal named specifically? kill path named? N/A if short/watched}
  C9 trust boundary ............ PASS / FAIL / N-A  {fields 2/5/11/14 — trifecta-exposed? structural containment named? N/A if no untrusted ingestion}

Review dimensions (1-5):
  C4 context posture ........... {n}                {field 9 + field 2 horizon}
  C5 external-memory adequacy .. {n}                {field 9 store + field 10 handoff}
  C6 no-progress signal ........ {n}                {field 7 no-progress layer}

Verdict:
  SOUND  — all gates PASS (C7 / C8 / C9 may be N/A) and no review < 3
  BLOCK  — any gate FAILs, or any review < 3
Top findings (severity-ranked, each citing a blueprint field / transcript line and the control-plane failure it maps to):
  1. ...
```

Map each finding back to `../references/control-plane.md` for root cause: termination failures (overbaking, non-halting, oracle-label illusion), budget failures (cost runaway, unbounded `while :;`), gate failures (self-grade-on-correctness, verifier < generator), context failures (rot, memoryless-fresh-instance-with-nowhere-to-resume), durability failures (no resume key, double-write on replay).

---

## Dependency note

**Every per-family rubric in this library depends on `loop-control`** — the manifest lists `"dependencies": ["loop-control"]` on each of `rubric-ralph-loop`, `rubric-auto-research`, `rubric-orchestrator-workers`, `rubric-evaluator-optimizer`, `rubric-debate-ensemble`, `rubric-self-improving`, and `rubric-plan-execute` (and `rubric-plan-quality` depends on it too). When you load a family rubric, the selection logic expands dependencies transitively, so **`loop-control`'s six gates (C1, C2, C3, C7, C8, C9) also apply to that family** and count toward its SHIP decision. A composed plan (e.g. an orchestrator whose workers run Ralph loops) must clear `loop-control`'s gates **once for the whole control plane** in addition to each family rubric's own gates. Family rubrics deliberately do **not** re-derive termination / budget / verification / durability / observability — they assume this rubric carries them, and add only the technique-specific control nuances on top. Note: C8 is [gate] but has no automated script check — apply it manually as [mech-partial] during blueprint review.
