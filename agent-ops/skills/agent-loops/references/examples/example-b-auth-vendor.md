# Worked Example B — Research & recommend an auth vendor

A full **PLAN-mode** run on an **open-ended research/decision** goal. Its job in the skill is to prove that the router lands on a **different topology than Example A**: where `example-a-react-to-hooks.md` selected a per-file iterative loop with a borrowed automated oracle, this goal has **no automated oracle and an open solution space**, so the router selects an **orchestrator-worker research fan-out → adversarial-verify/citation stage → single-threaded synthesis**.

Read this alongside `example-a-react-to-hooks.md`: the two share one skill and one invocation contract, and diverge purely on **goal shape**. The closing section states what the pair jointly proves.

This run follows the skill's contract end to end: **Ingestion** (parse goal + success criterion, classify task shape) → **Decomposition** (run `router.md` on the discriminating axes, SELECT + JUSTIFY against rejected alternatives, parameterize the control plane via `control-plane.md`) → **Execution** (emit the runnable blueprint per the Output Contract, self-score against the rubrics, end on an honest verdict).

> **Seat discipline.** This skill is the **builder**: it selects the mechanism and wires the runnable plan. It does **not** score the human experience of operating that plan — trust, observability, steerability, cognitive load. The run ends by handing the blueprint to the sibling `agentic-ux` skill (operator seat) for that evaluation. Shared vocabulary, different job, different output.

---

> **Goal:** "use agent-loops to create the best plan to research and recommend an authentication vendor for our B2B SaaS."

## B.1 — Ingestion

**Restated goal.** Survey the auth-vendor landscape, evaluate candidates against B2B-SaaS-specific needs, and produce a **cited, defensible recommendation** — a decision plus rationale, not a vendor list.

**Success criterion (made concrete — load-bearing; a fuzzy criterion produces a fuzzy gate).** A recommendation report where:

1. the candidate set is **breadth-complete** for the B2B-SaaS auth category (no obvious omission);
2. **every load-bearing claim** (pricing tier, SAML/SCIM support, SOC 2 status, data residency) is **attributed to a specific source**, and every _decisive_ claim is corroborated by **≥2 independent sources**;
3. the recommendation states the decision criteria, the trade-offs, and an explicit **confidence / uncertainty** note.

"Best plan" = a research orchestration whose output a buyer can **act on and audit**. Note what is absent versus Example A: there is **no executable oracle** — no `tests`, no `tsc`, no snapshot to diff. Correctness here means _true and well-sourced_, which the loop must **construct** a gate for rather than borrow one.

**Task-shape classification** (the discriminator `router.md` keys on):

| Axis | Reading | Signal |
| --- | --- | --- |
| Decomposability | High but **breadth-first** — independent _sub-topics_ (vendors × dimensions), not a sequential pipeline | favors fan-out, not a linear chain or item-wise loop |
| Verifiability / oracle | **No automated oracle** — correctness = "is this claim true & well-sourced" | needs a _constructed_ verification stage (citation + adversarial), not tests |
| Solution-space openness | **Open** — the right sub-questions and the answer both emerge during exploration | rules out closed-target iteration |
| Reversibility / stakes | The loop produces a _recommendation_; it takes no irreversible action | low blast radius; the risk is a _wrong conclusion_, not damage |
| Horizon / info volume | Exceeds one context window (many vendors × many dimensions × many sources) | favors isolated per-subagent contexts |
| Budget posture | High-value decision; the fan-out token premium is affordable | favors multi-agent over a single cheap pass |

→ **Shape = open-ended + breadth-first + no-automated-oracle + high-value.** This is the canonical fit for an **orchestrator-worker research fan-out with a separate adversarial-verify/citation stage and a single-threaded synthesis pass** — a _different_ topology from Example A, selected by _different_ router answers.

## B.2 — Decomposition

### Goal→loop router (the answers visibly diverge from Example A)

The router (`router.md`) is a small ordered decision over the classification. The _answers_ — not the questions — select the topology. The right-hand columns put Example A's answers next to this run's so the divergence is explicit.

| Router question | Answer here | vs Example A | What it selects / rules out |
| --- | --- | --- | --- |
| Solution space open or closed? | **Open** | A was **closed** (target = hooks, known) | rules **IN** research orchestration; rules **OUT** per-item iteration |
| Automated trustworthy gate exists? | **No** — must construct verification (citation + adversarial cross-check) | A had a **strong automated** gate (`tsc`+`jest`+snapshot) | the gate becomes a **built stage**, not `tests` |
| Decomposes how? | **Breadth-first** into independent sub-topics explored simultaneously | A was **item-wise sequential** (one file ≈ one work item) | rules **IN** parallel subagent fan-out |
| Does the information fit one context window? | **No** | A: each per-file unit **did** fit a window | rules **IN** isolated per-subagent contexts (each gets a fresh window) |
| Is writing/synthesis parallelizable? | **No** — parallel writers produce disjointed reports | (n/a in A — output was a code diff) | synthesis is **single-threaded after** research |
| Worth the fan-out token premium (~4×–15×)? | **Yes** — high-value, genuinely-parallel decision | A optimized for **cheap re-runs** of disposable attempts | justifies multi-agent over a single-agent ReAct pass |

→ Same skill, **opposite branch of the router**: where A landed on per-file iteration with a borrowed oracle, B lands on fan-out → verify → synthesize with a constructed oracle. **The router discriminates by goal shape.**

### SELECTED topology

**Orchestrator-worker research fan-out → adversarial-verify/citation stage → single-threaded synthesis** (the Auto-Research pattern in its true multi-agent form; rubric `rubrics/rubric-auto-research.md`, reference `auto-research.md`).

Concretely: a lead/orchestrator scopes the brief and decomposes it into independent research sub-topics; **parallel subagents** each research one sub-topic in an **isolated** context (running an inner ReAct loop) and return a **compressed** findings+sources summary; a dedicated **verification pass** attributes and adversarially cross-checks every load-bearing claim; a **single** writer synthesizes the cited recommendation. The fan-out earns its premium on the breadth dimension; the verify stage is the constructed analogue of Example A's per-file gate; the single synthesis avoids the disjointed-report failure of parallel writers.

### JUSTIFICATION vs ≥2 rejected alternatives

Per First Principle 2, escalation to _any_ multi-agent topology requires ruling out the cheaper options in writing. Three were considered and rejected; each contributed a sub-component rather than the whole shape.

- **Rejected: single-agent ReAct / Reflexion (one agent, search→read→reflect loop).** Cheaper (~4× vs ~15× tokens) and the correct call for a _narrow, depth-first_ question — but here the information volume exceeds one context window and the sub-topics are **embarrassingly parallel**, so one sequential agent is **too slow for the breadth** and under-covers the category. **Kept** ReAct as the **inner loop each subagent runs** (search → reflect "is this sufficient / what's the gap" → refine query → repeat), not as the whole topology.

- **Rejected: Example A's per-file iterative + automated-gate loop.** It depends on a cheap automated oracle (`tests`) and a closed target — **neither exists here**. There is no `tests` for "is Auth0's SCIM support real," and the candidate set is not enumerable up front. Forcing A's shape onto this goal would leave the loop with **no real termination gate** (no oracle to go green) and **no way to verify claims** — the "no oracle exists here" failure. This is the single sharpest contrast with Example A and the reason the router branches.

- **Rejected: debate / council / ensemble (N agents argue the recommendation; rubric `rubrics/rubric-debate-ensemble.md`).** Diversity-via-ensemble helps _judgment_ calls, but the **bottleneck here is grounding, not opinion** — getting claims true and cited, not aggregating viewpoints. Debate can talk a correct finding into a wrong consensus and adds cost without adding ground truth. **Borrowed** only the **adversarial-skeptic** idea, and only for the _verification_ stage (skeptics each told to refute a decisive claim or demand a second corroborating source; majority-refute kills it), never as the generator.

### PARAMETERIZE the control plane

Per `control-plane.md`, every emitted loop must pin termination, context, verification, and budget to concrete values. For a research fan-out that means fan-out width, per-subagent caps, the re-dispatch cap, the **constructed** verification gate, and an isolation+compression context posture.

| Knob | Value | Rationale |
| --- | --- | --- |
| **Fan-out width** | scale to complexity: ~**5–7** subagents, one per dimension-cluster — identity protocols (SAML/OIDC/SCIM), pricing/packaging, compliance/security (SOC 2, data residency), DX/SDKs, scalability/SLAs, B2B specifics (org management, provisioning) | avoids both the "50 subagents for a simple query" over-spawn and breadth under-coverage; effort scaled to task complexity |
| **Per-subagent tool-call cap** | **10** searches/fetches each (sane range 1–30) | stops a subagent searching endlessly for sources that do not exist; bounds per-worker cost |
| **Orchestrator re-dispatch cap** | **2–3** gap-fill rounds max, then force synthesis | bounds the never-finish failure; the coverage judgement (below) is the weakest link, so it is backstopped by a hard round cap |
| **Termination (layered, enforced OUTSIDE the model)** | (1) **coverage gate** — orchestrator's reflection judges the brief's dimensions covered with no gaps; (2) **iteration cap** — 3 re-dispatch rounds; (3) **hard ceiling** — token/cost budget exhausted | a coverage _judgement_ alone is a soft stop, so it is layered with the round cap + budget; no single signal is trusted to halt the loop |
| **Verification gate (CONSTRUCTED — this replaces "tests")** | a **separate post-research stage**: (a) **citation attribution** — every load-bearing claim pinned to a source location; (b) **adversarial corroboration** — for each top-3-vendor decisive claim, an independent **skeptic** subagent tries to refute it or demands a ≥2nd corroborating independent source; uncorroborated claims are **flagged LOW-confidence**, never silently dropped or silently passed | shipped research systems do citation-attribution but rarely an adversarial fact-check; this goal's stakes require the explicit refute pass, or the gate is verification theater. The verifier is a _separate_ agent from the researcher (no self-grading the finding it produced) |
| **Context strategy** | **isolation, not accumulation**: each subagent runs in its own fresh window; the orchestrator persists the plan + brief externally; subagents return **compressed** summaries (~1–2k tokens) — **never** raw transcripts; the orchestrator holds only summaries | one window cannot reason over all sub-topics without context clash/rot; compression keeps the orchestrator lean and the run resumable |
| **Synthesis** | **single writer**, runs **after** all research + verification complete | parallel writers produce a disjointed report; one writer yields a coherent recommendation |
| **Model tiering** | strong orchestrator + capable researcher subagents + cheap compressor for the summarization step | model-per-role is a top-tier variance driver, not just a token-count knob |

## B.3 — Execution: the executable orchestration blueprint

The full run header and 14-field blueprint per the Output Contract. Header first (the operator inbox line):

```text
agent-loops · PLAN · topology orchestrator-worker-research+adversarial-verify+single-synthesis · verdict BLUEPRINT-UNVERIFIED · gates 4/4 control-plane · key risk: candidate-set completeness & source quality unknown until fan-out runs
```

### Blueprint (the full 14-field Output Contract — passes `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`)

```text
1. GOAL & SUCCESS CRITERION
   Goal: survey the B2B-SaaS auth-vendor landscape and produce a cited, defensible recommendation (see B.1).
   Success criterion: a breadth-complete candidate set; every load-bearing claim attributed to a source and ≥2-source corroborated on decisive claims; an explicit confidence/uncertainty note. No executable oracle — the gate is CONSTRUCTED, not borrowed.
2. TASK CLASSIFICATION
   open-ended · breadth-first decomposable · no automated oracle (source-graded) · reversible / low-stakes (produces a recommendation; takes no irreversible action) · one-shot research · high-value budget posture.
3. CHOSEN LOOP TOPOLOGY + WHY
   Primary: orchestrator-worker research fan-out (references/auto-research.md) — breadth exceeds one context window and the sub-topics are independent. Nested: a ReAct inner loop per researcher; an adversarial-skeptic verify stage (borrowed from debate-ensemble) between research and synthesis.
4. REJECTED ALTERNATIVES
   single-agent ReAct — too slow for breadth, under-covers; Example A's per-file loop — no executable oracle exists and the candidate set isn't enumerable up front; debate/council as the generator — the bottleneck is factual grounding, not opinion. Single strong pass ruled out: information volume exceeds one window and sub-topics are genuinely parallel.
5. WIRING / CONTROL FLOW
   orchestrator scopes a dense brief → fan out 5–7 isolated researcher subagents (one sub-topic each, ReAct inner loop) → collect compressed findings → a SEPARATE adversarial-verify/citation stage → a SINGLE writer synthesizes. The gate sits between research and synthesis; the orchestrator's coverage judgement over the external findings/ set is the goal gate. Runnable sketch below (field 11).
```

### Runnable sketch (fields 5 & 11) — fan-out → verify → synthesize

```text
# === agent-loops blueprint: auth-vendor-recommendation ===
# Durable state (survives context truncation; makes the run resumable + auditable):
#   research_brief.md          : orchestrator-persisted dense brief
#   findings/<subtopic>.json   : compressed summary + sources per subagent

scope:
  brief = compress(user_goal + clarifications)          # dense research brief, not raw chat
  persist("research_brief.md", brief)

plan:                                                    # orchestrator (strong model)
  subtopics = decompose(brief, target=5..7, independent=true)
  # e.g. [identity-protocols, pricing, compliance, DX/SDK, scalability, b2b-org-mgmt]

fan_out:                                                 # PARALLEL, ISOLATED contexts
  parallel for st in subtopics (max_concurrent=6):
     agent(st):                                          # ReAct inner loop, fresh window
       for call in 1..10:                                # per-subagent tool-call cap
         hits = web_search(st.query); read(hits)
         if reflect("sufficient? gaps?").done: break
         st.query = refine(st.query)                     # broad -> narrow
       return compress(findings + sources)               # ~1-2k tokens, NOT raw transcript
  collect -> findings/

reflect_redispatch:                                      # orchestrator outer loop, cap 3
  gaps = orchestrator.reflect(findings vs brief)
  if gaps and round < 3: fan_out(gaps); goto reflect_redispatch

verify:                                                  # SEPARATE stage = the CONSTRUCTED gate
  for claim in load_bearing_claims(findings):
     attribute(claim -> source_location)                 # (a) citation pass
     if claim in top3_vendor_decisive:                   # (b) adversarial corroboration
        skeptic = agent("refute this claim, or find a 2nd independent corroborating source")
        claim.confidence = corroborated ? HIGH : LOW     # FLAG low, never silently drop
  source_quality_check: prefer authoritative > SEO/content-farm

synthesize:                                              # SINGLE writer, AFTER verify
  report = write_recommendation(
     decision_criteria, per_vendor_scored_table,
     trade_offs, RECOMMENDATION, confidence_note,
     inline_citations)                                   # every load-bearing claim cited

terminate_when:
  orchestrator.coverage_complete(brief)   # (1) coverage gate
  OR redispatch_round == 3                 # (2) iteration cap
  OR token_budget_exhausted                # (3) hard ceiling
```

The blueprint continues (fields 6–14):

```text
6. PARAMETERS
   fan-out width 5–7; per-subagent tool-call cap 10; orchestrator re-dispatch cap 3; hard token-budget ceiling ~800k as a cost circuit-breaker (≈ 6 researchers × ~100k + synthesis); model tiering: strong orchestrator / capable researchers / cheap compressor; subagent return budget ~1–2k tokens.
7. TERMINATION CONDITIONS (layered, enforced outside the model)
   goal-gate: the orchestrator's coverage-reflection, computed over the external findings/ set, finds every brief dimension covered (NOT a researcher self-asserting done). no-progress: a re-dispatch round that adds no new sub-topic finding. hard caps: 3 re-dispatch rounds + the token-budget ceiling. stuck/abort: at round 3 with residual gaps, force synthesis and surface gaps as explicit LOW-confidence sections rather than looping into cost.
8. VERIFICATION GATE
   type: a CONSTRUCTED citation + adversarial-corroboration stage (not an executable oracle, not a self-grade). what it checks: every load-bearing claim attributed to a source location; every decisive (top-3 vendor) claim corroborated by ≥2 independent sources or marked LOW-confidence. trust note + mitigations: the skeptic/verifier is a SEPARATE agent from the researcher (not same-model self-grade); consensus is necessary-not-sufficient; a source-authority check prefers authoritative over SEO/content-farm. verifier ≥ generator? yes (the skeptic runs at ≥ the researcher tier).
9. CONTEXT / MEMORY STRATEGY
   posture: isolation (per-researcher fresh windows) + compression (1–2k-token returns), not accumulation. external state: research_brief.md + findings/<subtopic>.json; the orchestrator holds only summaries. survives an iteration: the brief + findings. discarded: each researcher's raw transcript.
10. FAILURE / FALLBACK HANDLING
    dominant failure mode: the coordinator drowning in raw worker output, or breadth gaps masquerading as coverage. fallback: drop to single-agent ReAct on a narrowed question if fan-out cost runs away; force synthesis at the cap. durability: research_brief.md + findings/<subtopic>.json are the resumable checkpoint (a crash resumes at the missing sub-topic, not from scratch); a researcher dispatch is idempotent — re-running a sub-topic overwrites its findings file.
11. EXECUTION SUBSTRATE + RUNNABLE SKETCH
    substrate: parallel TaskCreate subagents in isolated contexts (or a deep-research-style harness); the verify stage is distinct skeptic subagents. sketch: the fan-out → verify → synthesize outline above.
12. SCORING
    rubrics (per rubric-manifest.json): rubric-loop-selection + rubric-loop-control + rubric-plan-quality (cross-cutting) + rubric-auto-research (per-family) + rubric-debate-ensemble (partial, skeptic stage). self-score in B.4.
13. CONFIDENCE / UNVERIFIED NOTE
    Unvalidated: candidate-set completeness and source quality are unknown until the fan-out + verify stages run; the token budget is an estimate. The plan is runnable and the verification stage is concrete, but "the recommendation is correct/complete" is not established until it is exercised. Verdict: BLUEPRINT — UNVERIFIED (READY-TO-RUN is reserved for a dry-run/executed plan).
14. TRUST BOUNDARY & BLAST RADIUS
    ingested content IS attacker-controllable: researchers fetch arbitrary open-web pages, which can carry prompt-injection. containment (content/action + content/privilege split — the Dual-LLM-analogue): the researcher subagents read untrusted content but have NO external-action / tool-write capability and NO credentials (read-only web fetch + return-compressed-text only); the privileged orchestrator and the single writer never ingest raw page text, only the compressed, source-attributed findings. blast radius of one poisoned source: at most a LOW-confidence claim the adversarial-verify stage flags or drops — no credential transit, no irreversible action; egress limited to fetch.
```

Mapped to harness primitives: `fan_out` is parallel `TaskCreate` subagents in isolated contexts (or a `deep-research`-style harness); `verify` is a distinct stage with its own skeptic subagents; `research_brief.md` + `findings/` are the durable, resumable, auditable artifacts. The **verification stage is non-optional** and runs _before_ synthesis — the analogue of Example A's per-file gate, reconstructed for a domain with no automated oracle.

## B.4 — Scoring: rubrics that would score this plan

Per the manifest (`rubrics/rubric-manifest.json`): the three cross-cutting rubrics always load; the `auto-research` per-family rubric loads on the topology match; the `debate-ensemble` rubric loads partially for the borrowed skeptic stage. Dimension IDs and gate/review labels are taken verbatim from the manifest.

- **`rubrics/rubric-loop-selection.md`** (cross-cutting). `S1-simplest-sufficient [gate]` — single pass / cheaper ReAct ruled out in writing (breadth + volume) ✓. `S2-workflow-vs-agent [gate]` — runtime-decided decomposition → agentic orchestration, correct ✓. `S4-verifiability-driven [review]` — selection driven by the _absence_ of an oracle (constructed gate) ✓. `S5-cost-value [review]` — fan-out premium acknowledged and justified by decision value ✓. `S7-composition-coherence [review]` — ReAct-inner / skeptic-verify / single-synth nesting named ✓.
- **`rubrics/rubric-loop-control.md`** (cross-cutting). `C1-termination-stack [gate]` — coverage gate + cap + budget, layered ✓. `C2-budget [gate]` — per-subagent cap + re-dispatch cap + token ceiling, concrete ✓. `C3-verification-gate [gate]` — citation **+** adversarial corroboration, separate verifier ✓. `C4-context-posture [review]` — isolation justified by context clash ✓. `C5-external-memory [review]` — brief + findings/ externalized ✓. `C6-no-progress-signal [review]` — gap-reflection + round cap ✓.
- **`rubrics/rubric-plan-quality.md`** (cross-cutting, depends on loop-control). `Q1-runnable-concreteness [gate]` — fan-out/verify/synthesize script is executable shape ✓. `Q2-parameter-completeness [gate]` — width/caps/budget/tiering all pinned ✓. `Q3-control-plane-wired [gate]` — termination + gate + context + budget all present ✓. `Q7-verify-target [gate]` — verdict honest about non-execution ✓.
- **`rubrics/rubric-auto-research.md`** (per-family, the load-bearing one). `AR1-independence [gate]` — sub-topics genuinely independent (no shared writes) ✓. `AR3-bounding [gate]` — width + per-subagent cap + re-dispatch cap + budget all set ✓. `AR5-isolation-compression [gate]` — fresh windows + 1–2k compressed returns ✓. `AR7-synthesis-coherence [gate]` — single-threaded writer after verify ✓. `AR2-effort-sizing [review]` — 5–7 not 50 ✓. `AR4-delegation-contract [review]` — each subagent gets one sub-topic + a return schema ✓. `AR6-citation-rigor [review]` — goes beyond attribution to source-authority + ≥2-source corroboration + LOW-confidence surfacing ✓. `AR8-economics [review]` — premium bounded and justified ✓.
- **`rubrics/rubric-debate-ensemble.md`** (per-family, partial — only the skeptic verify stage). `DE8-gate-integrity [review]` — bias-controlled refute pass; consensus treated as necessary-not-sufficient; the skeptic is a separate agent from the claim's author ✓. (`DE1`/`DE2` answer-shape/diversity gates are N/A — debate is _not_ the generator here, only the verifier.)

## B.5 — Verdict

```text
PLAN auth-vendor-recommendation
loop      = orchestrator-worker-research + adversarial-verify + single-synthesis
termination= coverage-gate ∥ 3-redispatch ∥ token-ceiling
gate      = citation + adversarial-corroboration (constructed; separate verifier)
context   = isolated per-subagent windows + compressed returns
verdict   = BLUEPRINT — UNVERIFIED
```

**Honest-verification note.** The plan is _runnable_ and the verification stage is _concrete_, but per the skill's own contract (First Principle 6, Verify Target) "the recommendation is correct/complete" is **not** established until the fan-out + verify stages actually run and the citation/corroboration coverage is measured. **READY-TO-RUN is reserved for a dry-run/executed plan; this is BLUEPRINT — UNVERIFIED** because the candidate-set completeness and source quality are unknown until the fan-out executes. Building a sound plan is not the same as exercising it against its success criterion.

> **Handoff.** With the mechanism designed, the operator-experience question — can a buyer trust, steer, interrupt, and audit this research run; is the LOW-confidence surfacing legible at a glance — belongs to the sibling `agentic-ux` skill. This skill stops at the runnable blueprint.

---

## What the two examples jointly prove

Read against `example-a-react-to-hooks.md`:

|  | **Example A** (migrate to hooks) | **Example B** (auth vendor) |
| --- | --- | --- |
| Goal shape | closed-target, decomposable, **automated** oracle, brownfield, reversible | open-ended, **breadth-first**, **no automated** oracle, high-value |
| Router answers (diverge) | closed · oracle exists (tests) · item-wise sequential | **open** · **no oracle, construct one** · **breadth-first parallel** |
| **Selected topology (different)** | per-file iterative loop + inner evaluator-optimizer | orchestrator-worker research fan-out + adversarial verify + single synthesis |
| Termination (always concrete) | ledger all-`passed` ∥ no-progress→BLOCKED ∥ file/budget cap | coverage gate ∥ 3 re-dispatch rounds ∥ token ceiling |
| Verification (always concrete) | `tsc` + `jest` + **snapshot-diff** per file; uncovered → manual | **citation + adversarial corroboration**; uncorroborated → LOW-confidence |
| Context strategy | fresh-per-file, state in ledger + git (anti-rot) | isolated per-subagent windows, compressed returns (anti-clash) |
| Output | runnable pipeline script + per-file gate command | runnable fan-out/verify/synthesize script |
| Verdict | BLUEPRINT — UNVERIFIED (gate not yet run) | BLUEPRINT — UNVERIFIED (no research run yet) |
| Handoff | → the sibling `agentic-ux` skill (operator UX) | → same sibling, same handoff |

The single point both examples make together: **the router discriminates by goal shape.** Same skill, same six-step decomposition, same honesty contract — but a closed, verifiable, brownfield goal and an open, breadth-first, oracle-less goal route to **opposite branches** and produce **different runnable topologies**. The mechanism is selected, never defaulted to; termination and verification are pinned to concrete signals in both cases — including the hard case (B) where the oracle had to be **constructed** rather than borrowed from `tests`; and both stop at an honest **BLUEPRINT — UNVERIFIED**, reserving "verified" for an executed run.
