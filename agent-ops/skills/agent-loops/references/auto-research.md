# Auto-Research / Multi-Agent Research Fan-Out

**One-liner.** A lead/orchestrator agent decomposes an open-ended question into **independent** sub-tasks, fans them out to **parallel subagents that each search and read in their own isolated context window**, then a **separate citation/verification pass** attributes every claim before a **single writer** synthesizes one cited report — buying quality with a **~15× token premium** that only pays off on high-value, breadth-first research.

**Where it sits.** Auto-Research is an **L3 research/synthesis super-loop** — a breadth-first specialization of L2 orchestrator-workers, **not a new primitive**. Per `composition.md`: **Auto-Research = orchestrator-workers (L2) + a citation/verify pass (L4)**, with two non-negotiable additions the generic L2 shape does not require — **mandatory per-researcher context isolation** (so parallel agents don't poison each other's context) and **single-threaded writing** (one writer synthesizes after _all_ research returns). Drop either and you get the disjointed-report failure. In the router it is the breadth-first row: selected when the goal is _breadth-first research exceeding one context window where a cited report is the deliverable_. It is **distinct** from single-agent ReAct iteration (OpenAI Deep Research is actually a single RL-trained agent — see the fork below) and from generic map-reduce. The cross-cutting termination/context/verification/budget/durability machinery this family instantiates lives in `control-plane.md`; this file sets those slots **specifically for research fan-out**, it does not re-derive them. Score an Auto-Research plan with `rubrics/rubric-auto-research.md` (AR1–AR8) in union with `rubrics/rubric-loop-control.md`.

---

## Mechanism — the control flow

Canonical orchestrator-worker flow (Anthropic's, mirrored by LangChain Open Deep Research and GPT-Researcher). Each numbered step is a real stage a builder wires; the bracketed note is the load-bearing property.

1. **SCOPE / CLARIFY** _(optional gate)._ Optionally ask the user 1–3 clarifying questions, then **compress the chat into one dense "research brief"** so downstream agents reason over intent, not raw transcript. LangChain gates this with `allow_clarification` (default true) and a `write_research_brief` node. [The brief is the single artifact every subagent reads — bad brief, bad fan-out.]

2. **PLAN** _(orchestrator / lead / supervisor)._ The lead reads the brief, uses extended/interleaved thinking as a "controllable scratchpad," **decides whether the brief decomposes into INDEPENDENT sub-topics**, and sizes the effort. It **writes the plan to external memory** (Anthropic) so it survives context truncation. Critical: it must explicitly tell each subagent its **objective, output format, tool/source guidance, and task boundary** — Anthropic found terse delegation causes subagents to duplicate work or misread scope. [Decomposition quality is what makes the fan-out coherent — see AR1, AR4.]

3. **FAN-OUT** _(parallel subagent spawn)._ The orchestrator spawns N subagents (Anthropic: 3–5 typical; LangChain `max_concurrent_research_units` default 5, range 1–20), **each given ONE sub-topic and its OWN isolated context window**. This is the load-bearing move: parallel contexts let the system process far more than a single ~200k-token window and explore directions simultaneously. Anthropic uses **two layers of parallelism** — (a) multiple subagents at once, and (b) each subagent issuing 3+ tool calls in parallel — cutting wall-clock research time by up to ~90%. [Isolation + parallelism is the entire reason this topology exists — see AR5, the context strategy below.]

4. **INNER RESEARCH LOOP** _(each subagent, concurrent)._ A ReAct-style iteration: issue search → read/fetch results → use interleaved / `think_tool` reflection to judge _"are these results sufficient, or do I have a gap?"_ → refine the next query (**start broad, then narrow**). Bounded per-subagent by a tool-call cap (LangChain `max_react_tool_calls` default 10, range 1–30; Anthropic's embedded scaling rules: simple = 1 agent / 3–10 calls, comparison = 2–4 agents / 10–15 calls each, complex = 10+ agents). [Each inner loop is itself an L1 ReAct body — Auto-Research is _ReAct per-researcher_.]

5. **COMPRESS / PRUNE** _(each subagent before returning)._ A final LLM call strips raw dumps and irrelevant tokens, returning a **clean summary + sources — NOT the full transcript.** This prevents token-bloat in the orchestrator's context. [Compression-on-return is mandatory, not optional — see AR5.]

6. **ORCHESTRATOR REFLECTION + RE-DISPATCH** _(outer loop)._ The lead reflects (`think_tool` / the `ResearchComplete`-vs-`ConductResearch` decision in LangChain): _do findings cover the brief?_ If gaps remain, spawn additional subagents or refine. Bounded by `max_researcher_iterations` (LangChain default 6, range 1–10). [This is the outer convergence loop; its cap is one of the four mandatory bounds.]

7. **VERIFY / CITE** _(separate agent / stage, AFTER synthesis or just before it)._ Anthropic runs a dedicated **CitationAgent** that walks the report + all gathered documents and **pins each claim to a specific source location**. OpenAI Deep Research uses inline clickable citations to exact source lines plus a _second_ custom-prompted o3-mini model to summarize chains of thought. This is the closest thing to a verification gate in shipped systems — see the gate caveat below. [The cited, auditable report is a first-class deliverable, not a side effect — see AR6.]

8. **SYNTHESIZE** _(single writer)._ A final single LLM call composes the report from the **compressed findings**. LangChain deliberately keeps writing **single-agent after all research completes** because parallel writers produce disjointed reports: _"multi-agent helps gathering, hurts coherent prose."_ [Single-threaded synthesis is non-negotiable — see AR7.]

**The fork a builder MUST resolve first.** "Deep research" names two different shapes:

| Shape | What it actually is | Examples |
| --- | --- | --- |
| **True orchestrator-worker fan-out** | Lead agent + parallel isolated subagents + separate citation pass (this topology) | Anthropic multi-agent research system · GPT-Researcher · LangChain Open Deep Research |
| **Single-agent RL-trained loop** | ONE o3-based agent trained end-to-end to run a long plan-act-observe loop (30–60 searches, 120–150 fetches, 150–200 reasoning iterations, ~20–30 min) — **not multi-agent at all** | OpenAI Deep Research |

If the budget or task can't justify the ~15× fan-out premium and the work is depth-first, the **single-agent variant is the cheaper correct choice** — route it as ReAct (`react-reflexion.md`) with the hard caps from the termination section, not as this fan-out.

---

## When it fits / when it fails

### When it fits

- **Breadth-first questions that decompose into INDEPENDENT directions explored simultaneously** — Anthropic's canonical example: _"find all board members of the S&P 500 IT companies"_ (embarrassingly parallel; single-agent fails on slow sequential search).
- **The total information to gather exceeds a single context window** — parallel subagents each get a fresh window, multiplying effective context. Simon W.: _"The key benefit is all about managing that 200,000 token context limit."_
- **High economic value per task that justifies a 15× token spend** — legal due diligence, competitive intelligence, biomedical/scientific literature review, market landscapes.
- **Open-ended research where the right sub-questions emerge during exploration** (start-wide-then-narrow), not fully known up front.
- **Tasks needing many heterogeneous tools/sources** where a subagent can specialize on a slice.
- **When a cited, auditable report — not just an answer — is the deliverable**; the citation/verification stage is a first-class output.

### When it fails

- **Depth-first / tightly-coupled tasks** where every step depends on the previous one. **Coding is the cited counterexample:** _"LLM agents are not yet great at coordinating and delegating to other agents in real time,"_ and parallel coders produce conflicting/disjointed output.
- **Low-value or simple queries** where the 15× premium is pure waste — early Anthropic systems pathologically _"spawned 50 subagents for simple queries"_ and _"scoured the web endlessly for nonexistent sources."_
- **When sub-tasks actually share context or have heavy interdependencies** (the decomposition assumption is false) — subagents duplicate work (one explored the 2021 chip crisis while two others redid it).
- **Synthesis/writing done in parallel** — yields incoherent reports; writing must be single-threaded after research.
- **When source quality matters and no verification gate exists** — agents prefer SEO content farms over authoritative-but-lower-ranked sources, and models _"may struggle to distinguish authoritative information from rumors"_ with poor confidence calibration (OpenAI's own stated limitation).
- **Latency- or cost-sensitive interactive use** — these run minutes and burn tokens; they are batch/async tools, not chat.
- **Reproducibility-critical contexts** — non-deterministic between runs even with identical prompts; _"minor changes cascade into large behavioral changes,"_ and errors compound across stateful multi-turn execution.

---

## Key parameters — the knobs a builder sets

The highest-value section. Each knob gets a sensible **default** with a rationale; deviations need a stated reason. Defaults assume the canonical mid-complexity research task; the effort-scaling policy (last-but-one row) is what _adjusts_ width/depth/budget away from these per query.

| Parameter | What it controls | Default | Rationale |
| --- | --- | --- | --- |
| **Fan-out width** (number of subagents / breadth) | The core breadth knob and the main cost driver | **5 subagents** (`max_concurrent_research_units`; GPT-Researcher `deep_research_breadth=4`) | Anthropic's 3–5 typical band; scale to complexity (1 / 2–4 / 10+). Too many = the 50-subagents-for-a-simple-query pathology + runaway tokens; too few = under-parallelized, slow, missed coverage. **This is the dominant cost lever.** |
| **Recursion depth** | How many levels deep a promising lead is followed before stopping | **2** (`deep_research_depth=2`), with breadth decaying per level `new_breadth = max(2, breadth // 2)` | Bounds the depth axis of the breadth/depth tradeoff; prevents infinite rabbit-holing. Depth-decay keeps total work from exploding as `breadth^depth`. |
| **Per-subagent tool-call budget** | Caps searches/fetches a single subagent may issue | **10 calls** (`max_react_tool_calls`, range 1–30); Anthropic embeds 3–10 / 10–15 / more by complexity | Stops a subagent from _"searching endlessly for nonexistent sources."_ The inner-loop backstop. |
| **Orchestrator outer-loop iteration cap** | How many rounds of gap-fill re-dispatch the supervisor runs before it MUST synthesize | **6** (`max_researcher_iterations`, range 1–10) | Bounds the never-finish failure. The lead always gets at least one reflection-and-refill round, but cannot loop forever. |
| **Concurrency limit** (parallel execution cap) | Simultaneous in-flight subagents/tool calls — distinct from logical breadth | **4** (`deep_research_concurrency`, an `asyncio.Semaphore`) | Respects provider rate limits and memory independently of how many logical subagents the plan calls for. Keep ≤ width. |
| **Effort-scaling policy** (complexity → budget mapping) | The explicit rule mapping query complexity to subagent count + tool budget | **Anthropic's rule, embedded in the lead prompt:** simple fact-find = 1 agent / 3–10 calls; comparison = 2–4 agents / 10–15 calls each; complex = 10+ agents, clearly divided | _The single highest-leverage prompt-engineering decision._ Without it the orchestrator mis-sizes effort in **both** directions. _"Scale effort to query complexity."_ |
| **Delegation contract** (per-subagent task spec) | What each subagent prompt carries | **objective + output format + source/tool guidance + explicit boundary**, per subagent | Terse delegation causes duplicated/vague work (the chip-crisis collision). Quality of the contract is what makes the fan-out coherent — see AR4. |
| **Context / compression strategy** | Whether subagents return compressed summaries vs raw transcripts; whether the plan is persisted | **Compressed summary + sources on return** (not transcript); **plan written to external memory** | Determines whether the orchestrator's context survives long runs. The central mechanism, not a tweak — see the context strategy section + AR5. |
| **Model assignment per role** | Lead vs subagent vs compressor vs writer model tier | **Strong lead** (e.g. Opus-tier) **+ capable subagents** (e.g. Sonnet-tier) + cheaper compressor | Anthropic: _"upgrading to Claude Sonnet 4 is a larger performance gain than doubling the token budget on Sonnet 3.7"_ — model choice is a **top-3 variance driver** alongside token count and tool-call count. |
| **Verification / citation stage** (on/off + strictness) | Whether a separate citation/verify agent runs after synthesis | **ON** — a dedicated post-synthesis CitationAgent attributing every claim | The only real guard against fabricated/rumor-sourced claims and the auditability of the report. Off is acceptable **only** for throwaway/low-stakes runs, and that downgrade is itself the headline risk. |

(Confidence: the LangChain/GPT-Researcher numeric defaults are lifted from inspectable reference implementations — empirically grounded. The "scale effort to complexity" thresholds and the model-choice-beats-token-budget claim are Anthropic's reported findings on their internal eval, not independently reproduced — strong practitioner evidence, treat as directional.)

---

## Termination / context strategy / verification gate (this family)

These instantiate the cross-cutting substrate in `control-plane.md`; below is how Auto-Research **specifically** sets each slot, not a re-derivation.

**Termination (layered — see control-plane §termination).** Stack these; never rely on a single layer:

- **Goal-gate:** the orchestrator's reflection (`think_tool` / `ResearchComplete`) concludes the findings sufficiently address the **research brief** with no remaining gaps. The semantic "done."
- **Outer-loop cap (hard):** `max_researcher_iterations` (e.g. 6) — force synthesis even if imperfect.
- **Per-subagent tool-call cap (hard):** `max_react_tool_calls` (e.g. 10) — a subagent returns what it has when exhausted.
- **Recursion-depth exhaustion:** `deep_research_depth` decremented to 0.
- **Single-agent variant ceilings (OpenAI DR):** hard caps on searches (30–60), fetches (120–150), reasoning iterations (150–200), + a wall-clock budget (~20–30 min).
- **No-progress / diminishing returns:** successive searches stop surfacing novel sources (the L3 analogue of the control-plane no-progress detector).
- **Economic ceiling:** a hard token/cost cap for the whole run — the circuit-breaker against the 15×-premium runaway.

This family's defining termination risk is that **all four bounds (width, depth, per-subagent calls, outer-loop iterations) must be set explicitly** — AR3 gates exactly this. A plan that names only `max_iterations` is under-bounded.

**Context strategy (the central mechanism — see control-plane §context).** **Isolation, not accumulation.** Each subagent runs in its **own fresh context window**, so the system processes far more than one ~200k window and avoids "context clash" between unrelated sub-topics (LangChain: a single window _"needs to store and reason about tool feedback across all of the sub-topics,"_ degrading quality). **Compression is mandatory at the boundaries:** (a) the user chat is compressed into one dense **research brief** before fan-out; (b) each subagent prunes its findings with a final LLM call, returning a **clean summary + sources** rather than its raw transcript, so the orchestrator's context doesn't bloat. The orchestrator **persists its plan to external memory** so the plan survives context truncation across long runs. Net pattern: **fan-out to isolated contexts → compress on the way back → orchestrator holds only summaries → single writer composes from summaries.** This is fundamentally different from single-threaded L1 loops that accumulate everything in one growing window — and it is the property AR5 scores.

**Verification gate (see control-plane §verification).** The canonical gate is a **separate, post-synthesis citation/verification agent.** Anthropic's CitationAgent walks the synthesized report plus all gathered documents and pins each claim to a specific source location, ensuring attribution. OpenAI Deep Research emits inline clickable citations to exact source lines and runs a second custom-prompted o3-mini model to inspect chains of thought (PersonQA: **0.86 accuracy, 0.13 hallucination rate** — better than o1 at 0.55/0.20 — though OpenAI still states it _"may struggle to distinguish authoritative information from rumors"_ with weak confidence calibration). A weaker/lighter gate is the **per-subagent interleaved reflection** ("evaluate quality, identify gaps, refine next query") in the inner loop, which catches thin or off-target results before they reach the orchestrator.

> **The gate caveat a builder must internalize.** In shipped systems the "verification" is mostly **citation-attribution** (_did a source say this?_) — **not adversarial fact-checking** (_is the source authoritative? are claims cross-corroborated?_). On the control-plane trust ladder, citation-attribution sits **below** an executable oracle and below true ground-truth comparison; it is a _provenance_ check, not a _correctness_ check. A builder wanting real adversarial verification must add a **cross-checking / red-team pass explicitly** (compose an L4 adversarial-verify panel after synthesis — see `composition.md` and `debate-ensemble.md`); it is **not** standard in shipped systems. A citation stage that attributes claims to untrustworthy sources is **verification theater** (see failure modes).

---

## Failure modes — each with its guard

| Failure mode | What happens | Guard |
| --- | --- | --- |
| **Over-spawning on simple queries** | _"Spawning 50 subagents for simple queries"_ — token blowout; the inverse of correct effort-scaling | Embed the **effort-scaling policy** in the lead prompt (1 / 2–4 / 10+); cap fan-out width; route trivial/depth-first queries to single-agent ReAct |
| **Endless search for nonexistent sources** | Subagents don't know when to stop | **Per-subagent tool-call budget** (`max_react_tool_calls`); start-broad-then-narrow inner-loop discipline |
| **Duplicated work across subagents** | Vague/terse delegation → multiple subagents investigate the same sub-topic (the 2021 chip-crisis collision) | **Delegation contract** per subagent (objective + format + source guidance + **boundary**); enforce decomposition independence (AR1) |
| **Source-quality failure** | Preference for SEO-optimized content farms over authoritative-but-lower-ranked sources (caught only by human testers) | Explicit **source-authority guidance** in subagent prompts; add a corroboration/cross-check pass; surface source provenance in the report |
| **Compounding errors across the stateful pipeline** | _"One step failing can cause agents to explore entirely different trajectories"_; _"the last mile often becomes most of the journey"_ | Plan persisted to external memory; checkpoint per stage; bounded outer-loop with explicit gap-detection rather than open-ended re-dispatch |
| **Non-determinism / unreproducibility** | Different results between runs with identical prompts; _"minor changes cascade into large behavioral changes"_ | Log full agent trajectories ("think like your agents"); persist plan + briefs + seeds where supported; acknowledge non-determinism in the report's confidence note |
| **Coordination overhead** | Orchestrator and subagents _"distracting each other with excessive updates"_; LLMs are poor at real-time inter-agent coordination | Asynchronous fan-out (no live chatter); subagents return **once**, compressed; keep the orchestrator's job to dispatch + reflect + synthesize, not micromanage |
| **Disjointed synthesis** | Parallelized writing yields incoherent reports | **Single-threaded writing** after _all_ research completes (AR7) — never fan out the writer |
| **Hallucination + poor confidence calibration** | Final report presents rumors as fact, fails to convey uncertainty (OpenAI's stated limitation) | Citation gate ON; require explicit uncertainty/confidence statements; add adversarial cross-check for high-stakes claims |
| **Pure cost waste** | The 15× premium applied to a task whose value doesn't justify it | **Economic-viability check up front** (AR8): reserve fan-out for high-value, genuinely-parallel, breadth-first tasks; cheaper single-agent fallback otherwise |
| **Verification theater** | A citation stage attributes claims to sources without checking whether the sources are trustworthy or corroborated | Go **beyond attribution**: add source-authority + corroboration checks; an explicit adversarial-verify pass for claims that matter |

The **dominant** failure for this family is **mis-sized effort in both directions** (over-spawn on the simple, under-bound on the complex). Its single best guard is the explicit effort-scaling policy plus the four hard bounds.

---

## Composition — how Auto-Research nests and wraps other layers

Auto-Research is **itself a composite** — that is the point. Per `composition.md` it is **not a body you drop in whole**; it is L2 orchestrator-workers, specialized for breadth-first research, with an L4 gate appended.

- **It IS orchestrator-workers (L2) + a citation/verify pass (L4).** Name it that way in the blueprint's **CHOSEN LOOP TOPOLOGY** field; do not write "an auto-research loop" as if it were atomic. The composition file's canonical naming: `Orchestrator-workers (L2) fan-out, ReAct per-researcher, isolated context + compression-on-return, then a single-writer synthesis + a citation/verify pass (L4)`.
- **Each researcher's inner loop is an L1 ReAct body** (`react-reflexion.md`) — _ReAct per-researcher_, each with its **own** tool-call budget. When you name the fan-out, you inherit the full L5 control plane **per nested body**: every researcher gets its own cap; the orchestrator gets its own outer-loop cap.
- **The two non-negotiable specializations over plain L2** are **per-researcher context isolation** and **single-threaded writing after all research returns.** A plain orchestrator-workers plan does not require either; an Auto-Research plan that drops either is mis-composed and produces the disjointed-report failure.
- **An evaluator-optimizer (L4) may nest inside a researcher** (R6-in-R4-in-L2) when a single sub-topic's findings need iterative refinement against a judge before returning. Name the inner loop explicitly; it has its own iteration cap.
- **Upgrade the verification gate by adding an adversarial-verify panel (L4) after synthesis** when correctness — not just provenance — matters: `… then an adversarial-verify panel (N skeptics, majority-refute) as the L4 gate` (see `debate-ensemble.md`). This is how a builder turns the shipped citation-attribution gate into something closer to real fact-checking.
- **Dispatch wrapper:** these runs take minutes and burn tokens — they are **batch/async tools, not chat.** Wrap the whole topology in an async/background/scheduled dispatcher (`async-oversight.md`) and hand the **operator-oversight UX** of that unattended run to the sibling `agentic-ux` skill — this skill designs the fan-out mechanism; that one scores the human's trust/steer/interrupt experience.
- **Worked example:** `examples/example-b-auth-vendor.md` instantiates this end-to-end — open-ended research + a constructed verify gate → orchestrator-worker fan-out + adversarial-verify + single synthesis.

**Cross-check against L5.** After naming the nesting, confirm blueprint fields 6–10 set termination, parameters, gate, context, and durability **for each named body**: the orchestrator's outer-loop cap, each researcher's tool-call budget, the isolated-context strategy, the compression-on-return, the citation gate, and the external plan store. Naming the composition is step one; instantiating L5 per nested body is what makes it executable.

---

## Primary sources

- **How we built our multi-agent research system** — Anthropic. <https://www.anthropic.com/engineering/multi-agent-research-system> — THE primary source for the orchestrator-worker research pattern: the `LeadResearcher → parallel subagents → CitationAgent` flow, the explicit effort-scaling rules (1 / 2–4 / 10+ agents), the token economics (~15× vs chat, ~4× for single-agent; token use explains ~80% of BrowseComp variance, token + tool-calls + model ~95%), the 90.2% eval lift, the 8 prompt-engineering principles, and the failure-mode catalogue. The author explicitly named "Auto Research" — this is the spec.
- **Deep Research System Card (PDF)** — OpenAI. <https://cdn.openai.com/deep-research-system-card.pdf> — primary source for the **single-agent RL-trained variant** and its verification surface: a second custom-prompted o3-mini model summarizing chains of thought; PersonQA accuracy 0.86 / hallucination rate 0.13 (vs o1 0.55/0.20). Grounds the failure-mode and confidence-calibration claims in measured numbers, and forces the single-agent-vs-fan-out distinction.
- **Introducing deep research** — OpenAI. <https://openai.com/index/introducing-deep-research/> — source of the canonical stated limitations every research-loop builder designs against: _"can sometimes hallucinate facts," "may struggle to distinguish authoritative information from rumors,"_ weak confidence calibration. Also the benchmark framing (Humanity's Last Exam / GAIA) and the plan-act-observe browsing loop.
- **Open Deep Research** (blog + repo `configuration.py`) — LangChain. <https://www.langchain.com/blog/open-deep-research> — open-source, inspectable reference with **exact default parameters** a builder can lift: `max_concurrent_research_units=5` (1–20), `max_researcher_iterations=6` (1–10), `max_react_tool_calls=10` (1–30), `allow_clarification=true`, per-role model assignment. Documents supervisor↔subagent isolation, `think_tool` reflection, per-subagent compression, single-threaded writing, and the explicit rationale for multi-agent in research **but not in coding** (context clash).
- **Deep Research** (docs) — GPT-Researcher. <https://docs.gptr.dev/blog/2025/02/26/deep-research> — concrete tree-exploration mechanism with named breadth/depth/concurrency parameters (`deep_research_breadth=4`, `deep_research_depth=2`, `deep_research_concurrency=4`) and the depth-decay rule `new_breadth = max(2, breadth // 2)`. Supplies the cost/time data point (~\$0.40, ~5 min) and the planner→executor→publisher framing — the clearest open-source illustration of bounding breadth × depth.
- **Notes on Anthropic's multi-agent research system** — Simon W. <https://simonwillison.net/2025/Jun/14/multi-agent-research-system/> — independent practitioner read isolating the load-bearing insight (_"The key benefit is all about managing that 200,000 token context limit — each sub-task has its own separate context"_) and the economic caveat (only worth it _"where the value of the task is high enough"_). A calibration check separating mechanism from hype.

---

_Scoring: this topology is scored by `rubrics/rubric-auto-research.md` (AR1 independence · AR2 effort-sizing · AR3 bounding · AR4 delegation-contract · AR5 isolation-compression · AR6 citation-rigor · AR7 synthesis-coherence · AR8 economics) in union with the cross-cutting `rubrics/rubric-loop-control.md`._
