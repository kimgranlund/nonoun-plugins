# Rubric — Self-Improving

Score a **self-improving / self-evolving** plan: a loop that runs a task class many times and, after each run, **persists a durable, reused artifact** (a skill, tool, prompt, lesson, or whole agent) so capability **compounds across runs**. The shapes this covers: skill-library accretion (Voyager-style), `learnings.md` / lessons accumulation, prompt evolution (Promptbreeder), self-taught optimizers, and archive-of-agents search (Darwin Gödel Machine). Selectors: `self-improving`, `self-evolving`, `skill library`, `voyager`, `darwin godel machine`, `promptbreeder`, `learnings.md`, `self-taught optimizer`, `archive of agents`.

**Key question:** _Does capability compound across runs without drift or reward hacking?_

This is a **per-family** rubric — load it only when the plan composes a self-improving loop. Its dimensions are grounded 1:1 in the self-improving entry of the rubric library (mirrored in `rubric-manifest.json`).

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate **blocks SHIP**; it is not a matter of opinion. Cross-cutting gates are backed by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`; per-family gates (SI1/SI4/SI5/SI7) are **[mech-partial]** — the criterion is structural but no automated script enforces it; agent judgment applies.
- **[mech-partial]** — mechanically checkable criterion, no automated script — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment. Score **1–5**; the plan ships at **≥ 3**.

**Ship rule (this rubric):** every **[gate]** passes **AND** no **[review]** is below **3**. A self-improving plan is part of a larger blueprint, so the _plan_ ships only when this rubric's bar is met **and** the union of every other loaded rubric's gates clears (see Dependency note).

**Record evidence for every finding** — the blueprint field, the parameter value, or the artifact line the dimension passes or fails against. A finding without a citation is an opinion.

**Builder-seat boundary.** This rubric scores the _mechanism_ of compounding — the eval, the artifact, the safeguards, the economics. It does **not** score whether a human can comfortably oversee the loop running for days, trust its self-modifications, or steer it; that operator-UX judgment is the sibling `agentic-ux` skill. Where a self-improving loop needs human oversight (SI5's kill switch is a _mechanism_; whether the operator can actually wield it is _UX_), record the mechanism here and **hand off** the experience question — do not duplicate the sibling's rubric.

**Calibration caveat.** Status **draft**, **0 calibration samples**. Treat every score as **directional, not authoritative**, until the ROADMAP v0.2 calibration bar is met. The **[gate]** dimensions are the only mechanically verifiable layer; **[review]** scores carry author judgment and will move under calibration.

---

## The backbone gate (run this first)

A self-improving loop with no real measurement gate is not a self-improving loop — it is unmeasured mutation that will accumulate noise and drift. **SI1 is the load-bearing check; most failures surface here.** Run it before the rest.

### SI1 [gate / mech-partial] — Measurement-gate quality

A **cheap, automatic, held-out** utility decides **keep-vs-revert** for every persisted change. It must be (a) **resistant to gaming** — the loop cannot trivially satisfy it by editing the metric, the test, or the harness rather than the capability; and (b) **aligned with true capability**, not a proxy that the loop will overfit. _A self-improving plan with no real eval scores near zero_ — the whole compounding claim rests on this signal.

**Test (binary + threshold):** find the keep-vs-revert decision in the blueprint.

- Is there an **automatic, runnable** utility (not a human read, not a vibe) that gates each persisted artifact? If **no** → **FAIL** (the loop accretes unmeasured changes).
- Is the utility computed on **held-out / unseen** instances, not the same instances the change was tuned on? If the loop both _tunes against_ and _is scored by_ the same cases → **FAIL** (the gains will not generalize; this is the SI-flavored oracle-label illusion).
- Is the metric **the capability**, or a proxy (token count, self-report, judge sentiment, citation density) the loop can inflate without getting better? A proxy-only gate with no stated anti-gaming guard → **FAIL**.
- Can the loop satisfy the gate by **mutating the gate itself** (editing the test file, the eval prompt, the harness)? If the gate is in the loop's write-perimeter with no protection → **FAIL** (cross-check SI5).

A blueprint that says "the agent keeps what helps" with no automatic held-out utility behind "helps" fails this gate.

---

## Gate dimensions

### SI4 [gate / mech-partial] — Regression & functional gating

The loop carries **hard invariants** that a persisted change must not break — must still **compile / typecheck / pass the core suite**, must **retain the core ability** the artifact was supposed to add — plus a **revert floor** (any change that drops below the floor is rolled back, not kept), preventing **catastrophic capability loss** across the run.

**Test (presence + binary):**

- Is there a named set of **hard invariants** (build passes, core tests green, prior capability preserved) checked on every persisted change? Absent → **FAIL**.
- Is there an explicit **revert/rollback action** when a change regresses below the floor (not just "score logged and continue")? If a regressing change can be _kept_ → **FAIL**.
- Is there protection against **monotone degradation** — the run cannot silently walk the artifact set downhill over many iterations (best-so-far retained, or per-change regression block)? If nothing stops cumulative erosion → **FAIL**.

This is distinct from SI1: SI1 asks _is there a trustworthy signal_; SI4 asks _does a bad signal-failure actually get reverted, and is the core protected_.

### SI5 [gate / mech-partial] — Reward-hacking & safety perimeter

Because the loop **modifies itself** (its skills, prompts, tools, or own code), the plan must contain the blast radius: **sandboxing** of self-modification, an **overseer / human kill switch**, and **explicit written reasoning** about how the utility could be **gamed** or the **constraints stripped**.

**Test (presence + binary):**

- Is self-modification **sandboxed** — executed where a malformed or adversarial artifact cannot escape into production, the host, or the gate itself? No containment → **FAIL**.
- Is there an **overseer or kill switch** (a mechanism to halt and inspect the loop mid-run; the _mechanism_ — its operator UX is the sibling's concern)? Absent for an unattended self-modifying loop → **FAIL**.
- Does the plan **explicitly reason** about the reward-hacking surface — how this specific utility could be inflated without real improvement, and how a self-edit could **strip its own constraints / disable its own gate**? A self-improving plan with **no** stated reward-hacking analysis → **FAIL** (silence here is the failure; reward hacking is the defining risk of the family).
- Is the **gate outside the loop's write-perimeter** (the loop cannot edit what judges it)? If the loop can rewrite its own evaluator → **FAIL** (this is the structural form of SI1's anti-gaming check).

### SI7 [gate / mech-partial] — Termination & budget economics

The loop is **bounded** and the compounding is **economically positive**: bounded **iterations/cost**, a **plateau** stop (improvement flattens → stop) and a **stuck-detection** stop (no admissible improvement found → stop, don't grind), a **sane inner-loop retry cap** (per-attempt generation does not spin), and a stated **positive amortization argument** — the cost of running the loop is repaid by **reuse** of the artifacts it produces.

**Test (presence + threshold):**

- Are there **hard caps** on outer iterations and total cost/tokens (concrete numbers, not "until done")? Unbounded self-improvement loop → **FAIL** (cost runaway is the predictable result; cross-check `rubric-loop-control` C1/C2).
- Is there a **plateau/diminishing-returns stop** (stop when held-out utility stops improving by ≥ ε over K iterations)? If the only stop is max-iterations → weak; if there is **no** stop beyond "model decides" → **FAIL**.
- Is there a **stuck/no-admissible-improvement** abort (when no candidate clears the gate, escalate/stop rather than loop) and a **bounded inner retry** so a single failing step can't burn the budget? Absent → **FAIL**.
- Is there a **stated amortization argument** — why per-iteration cost is justified by future reuse of the persisted artifact? A self-improving loop whose artifacts are used **once** (no reuse) has **no economic basis** and should not have been chosen → **FAIL** (this is a selection error; route back to `rubric-loop-selection`).

---

## Review dimensions

### SI2 [review] — Durable-artifact design

The persisted unit — the **skill / tool / prompt / lesson** — is the product of the loop. It must be **reusable** (consumed by future runs, not write-only), **composable** (combines with other artifacts), **right-grained** (not one giant blob, not a thousand fragments), and **generalized** (captures the class, not the one instance) — and there must be a concrete **retrieval path** so future runs actually find and load it.

**Evidence to cite:** the artifact's schema/shape, where it is stored, the grain (one lesson per what?), and the **retrieval mechanism** (index, embedding search, filename convention, `learnings.md` section) that wires it back into the next run.

**1–5 anchor:**

- **1** — Artifacts are write-only (appended to a log nothing re-reads), or instance-specific (memorizes "fix bug #4123" not the pattern), or grain is pathological (one monolithic file / unbounded fragment spam). No retrieval path → the loop _records_ but does not _compound_.
- **3** — Artifacts are reusable and reasonably grained with a working retrieval path, but generalization is shaky (some lessons are instance-bound) or composition is untested.
- **5** — Artifacts are generalized to the failure class, right-grained, composable, and a concrete retrieval path is specified and demonstrably feeds the next iteration; the substrate is a genuine compounding library, not a log.

### SI3 [review] — Compounding-vs-drift safeguards

Compounding is not guaranteed by accretion — a **greedy** loop can climb into a dead end and a noisy loop can drift. This dimension scores the **search-quality safeguards**: **archive / stepping-stone retention** (keep useful intermediate artifacts even if not currently best, à la open-ended search and the Darwin Gödel Machine archive — do not greedily discard), **diversity / novelty selection pressure** (avoid mode-collapse onto one lineage), and **evidence the loop recovers from temporary regressions** (a dip is survived, not fatal).

**Evidence to cite:** the retention policy (greedy-best vs archive), any novelty/diversity term in selection, and whether the plan shows a recovery path from a transient down-run.

**1–5 anchor:**

- **1** — Pure greedy hill-climb: only the current best is kept, no archive, no diversity pressure; a single bad run or a local optimum permanently caps the loop. No recovery story.
- **3** — Some retention beyond greedy (keeps a small history or best-of-N) and an implicit recovery path, but no explicit diversity/stepping-stone pressure — vulnerable to mode-collapse on long runs.
- **5** — Explicit archive of stepping-stones, diversity/novelty selection pressure preventing collapse, and a demonstrated recovery-from-regression mechanism; the search compounds rather than stalling at the first plateau.

### SI6 [review] — Curation & staleness discipline

An accumulating substrate **rots without curation**: duplicates pile up, stale lessons mislead, low-confidence entries dilute signal. This scores the **maintenance policy**: **dedup**, **pruning thresholds** (entries below a usefulness/age bar are removed), **confidence-tagging** (entries carry how-sure / how-validated), and a **retirement policy** (superseded or contradicted artifacts are retired, not left to poison retrieval).

**Evidence to cite:** the dedup rule, the prune/retire trigger, the confidence tag schema, and whether stale-entry handling is specified — or whether the substrate is append-only-forever.

**1–5 anchor:**

- **1** — Append-only, no curation: duplicates and stale/contradicted lessons accumulate indefinitely; over time the substrate's signal-to-noise collapses and retrieval surfaces garbage.
- **3** — Basic dedup and some pruning exist, but no confidence-tagging or explicit retirement of superseded entries — the substrate degrades slowly.
- **5** — Dedup + threshold-based pruning + confidence-tagging + a retirement/supersession policy keep the substrate high-signal as it grows; staleness is actively managed, not deferred.

### SI8 [review] — Improvement-locus correctness

The loop must improve the **right thing**. A correct self-improving loop targets the **recurring failure CLASS at the artifact/harness level** — _"fix the harness, not the bug"_ — so the fix prevents the whole class next time, rather than patching one instance. It must also **acknowledge the base-model ceiling**: scaffolding and accumulated lessons have a limit set by the underlying model, and piling on more artifacts where the model is the bottleneck can **hurt** (context bloat, conflicting lessons) rather than help.

**Evidence to cite:** what the persisted change _modifies_ (a single output vs the prompt/tool/skill that produced it), whether the trigger is a _class_ or an _instance_, and whether the plan states a base-model-ceiling stop (when to stop scaffolding because the model, not the harness, is the limit).

**1–5 anchor:**

- **1** — The loop patches instances, not classes (records "fixed this specific failure" with no generalization to the harness), and/or assumes unbounded gains from scaffolding with no ceiling acknowledgment — it will add noise where the base model is the real limit.
- **3** — The loop mostly targets classes at the artifact level, but some fixes are instance-bound, or the base-model ceiling is unstated (no rule for when more scaffolding stops helping).
- **5** — The loop systematically fixes failure classes at the harness/artifact layer, generalizes each lesson to the class, and explicitly bounds where scaffolding helps vs where the base-model ceiling dominates — applying compounding only where it pays.

---

## Scoring summary template

```text
Self-improving plan: {goal short name}    Artifact unit: {skill | tool | prompt | lesson | agent}
Selectors matched: {self-improving | skill library | voyager | learnings.md | ...}

Backbone gate:
  SI1 measurement-gate quality ....... PASS / FAIL   {the held-out utility + anti-gaming evidence}

Gate dimensions:
  SI4 regression & functional gating . PASS / FAIL   {invariants + revert floor evidence}
  SI5 reward-hacking & safety ........ PASS / FAIL   {sandbox + kill switch + hacking analysis}
  SI7 termination & budget economics . PASS / FAIL   {caps + plateau/stuck stop + amortization}

Review dimensions (1-5):
  SI2 durable-artifact design ........ {n}   {grain + reuse + retrieval-path evidence}
  SI3 compounding-vs-drift safeguards  {n}   {archive + diversity + recovery evidence}
  SI6 curation & staleness ........... {n}   {dedup + prune + confidence + retire evidence}
  SI8 improvement-locus correctness .. {n}   {class-vs-instance + base-model-ceiling evidence}

Operator-UX handoff:
  Oversight/kill-switch UX, trust in self-edits ... → the sibling agentic-ux skill (not scored here)

Verdict (this rubric):
  SHIP   — SI1 + SI4 + SI5 + SI7 all PASS and no review < 3
           (and the union of all other loaded rubrics' gates also clears)
  BLOCK  — any gate FAILs, or any review < 3
Top findings (severity-ranked, with citations):
  1. ...
```

Map every finding back to the self-improving failure modes for root cause: **unmeasured mutation** (SI1), **silent capability regression** (SI4), **reward hacking / constraint-stripping** (SI5), **cost runaway / non-amortizing reuse** (SI7), **write-only memory** (SI2), **greedy local-optimum stall** (SI3), **substrate rot** (SI6), and **instance-patching / over-scaffolding past the model ceiling** (SI8). See `../references/self-improving.md` for the family's failure taxonomy.

---

## Dependency note

Every per-family rubric **depends on `rubric-loop-control`** — its gates also apply to this plan, in addition to the dimensions above. A self-improving loop is still a loop: it must clear **C1 termination-stack**, **C2 budget**, **C3 verification-gate**, and **C7 durability-idempotency** as well as SI1/SI4/SI5/SI7. The overlap is intentional and the checks compound, not cancel:

- **SI1 ↔ C3** — C3 demands a verification gate between generate and accept at the highest available trust rung; SI1 is that gate _specialized_ to the self-improving keep-vs-revert decision (held-out, anti-gaming, capability-aligned). Pass both.
- **SI7 ↔ C1/C2** — C1/C2 demand a layered termination stack and a hard budget ceiling for _any_ loop; SI7 adds the self-improving-specific plateau/stuck stops and the amortization argument. Pass both.
- **SI5 ↔ C7/C8** — durability (C7) and observability/circuit-breaking (C8) are where the kill switch and sandbox boundary become real; SI5 names them, C7/C8 wire them.

When scoring a composed plan, take the **union** of this rubric's gates and `rubric-loop-control`'s gates (plus the always-loaded `rubric-loop-selection` and `rubric-plan-quality`). A self-improving plan ships only when **all** of those gates pass and **no** review across the loaded set is below 3.
