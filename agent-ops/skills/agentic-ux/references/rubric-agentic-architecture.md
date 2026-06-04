---
date: 2026-05-28
status: active
version: "0.1.0"
type: rubric
lens: operator   # architecture in service of the human's utility, not elegance for its own sake
council: architecture-utility
dimension_critics:
  A1: critic-mcp
  A2: critic-harrison-c
  A3: critic-walden-y
  A4: critic-mitchell-h
  A5: critic-mitchell-h
  A6: critic-harrison-c
key_question: >
  Does this agentic workflow's architecture compound into real utility for the operator —
  composing with the ecosystem, keeping context coherent, coordinating without conflict,
  persisting its state, and engineered to be right the first time — or is it sophistication
  that demos well and fragments under use?
companion_documents:
  - rubric-agentic-ux.md                         # the human-facing UX spine (peer rubric)
  - council/agentic-ux-council-eval-prompts.md   # the critic council orchestrator
---

# Agentic Workflow Architecture & Utility — Best Practices Rubric

**An agentic workflow's architecture is judged by the utility it delivers to the operator, not by its sophistication.** The unit of evaluation is what's _underneath_ the experience: how the workflow composes with tools and agents, how it keeps context coherent, how it coordinates work, how durable its state is, and whether it's engineered to produce the right result. This is the peer of `rubric-agentic-ux.md` (which scores the human-facing experience); together they ask "is the experience good?" and "is the thing under it well-built and actually useful?"

The central failure mode is **architecture that demos well but doesn't compound into utility**: it fragments context across agents that can't see each other, reinvents every integration as bespoke glue, hides its state so an interruption loses everything, and tolerates recurring errors instead of engineering them out. Complexity gets mistaken for capability. A workflow can be architecturally impressive and still cost the operator more than it saves.

This rubric is owned by the **Architecture & Utility sub-council** — Walden Y., Harrison C., Mitchell H., and the MCP/interoperability seat. It deliberately carries an unresolved tension: **Yan's single-threaded continuous context vs. Chase's durable multi-agent orchestration.** Dimensions A2 and A3 surface that tension rather than pretending it has one answer; the right resolution is workflow-specific, and the rubric's job is to force the choice into the open.

**Companion docs:**

- `rubric-agentic-ux.md` — the human-facing experience spine (peer rubric; the UX & Quality sub-council owns it)
- `council/agentic-ux-council-eval-prompts.md` — the critic council, engagement routing, and synthesis prompts
- The **builder-side** rubrics (multi-agent coordination as isolation-by-structure; context as a precision instrument) are the engineering-side peers of A2/A4 — this rubric scores the same territory from the operator's utility standpoint.

> **Format-fitness note.** The 1–5 matrix fits bounded evaluation of parallel dimensions. The six dimensions below are evaluable. The _choice_ between single-threaded and multi-agent architectures is a judgment, not a score — A2/A3 score how well whichever choice was made is executed, not which choice is "correct."

---

## §The Problem

An agentic workflow whose architecture is never examined for utility will fail in these ways:

1. **Context fragmentation.** Work is split across agents or sessions that cannot see each other's full traces. Each makes locally-sensible decisions; the merge produces something incoherent that still looks like progress.

2. **Integration sprawl.** Every tool, data source, and agent connection is bespoke glue. Adding the next one is hand-wiring, not composition — an M×N tax the workflow keeps paying — and nothing interoperates with the broader ecosystem.

3. **Orchestration without coordination.** Multiple agents fan out with no shared state and no human checkpoints. Conflicting implicit decisions collide; the failure is noticed late, if at all.

4. **Ephemeral state.** There is no durable, inspectable, resumable state. An interruption — crash, timeout, or human — loses the work, and oversight is all-or-nothing: watch the whole run or get only the end.

5. **Un-engineered harness.** The model is treated as the system. The agent can't verify its own work, and recurring errors are tolerated as inevitable instead of encoded as guardrails.

6. **Sophistication without utility.** The workflow is complex and impressive but does not reliably produce the right result faster than not using it. The novelty hides negative ROI.

---

## §First Principles

### 1. Architecture is justified by utility, not elegance

Every added agent, layer, or coordination mechanism is a cost — in context, in failure surface, in operator attention. It must be justified by utility it produces, not by how sophisticated it looks. The first question of any added component is "what would break if we deleted it?" If the answer is "nothing the operator would miss," delete it.

### 2. Context continuity is the default; fragmentation must be earned

Per Walden Y.: continuous context is the baseline, and every split into separate agents or sessions introduces conflicting implicit decisions. Fragmentation is sometimes worth it — but it is a deviation to be justified, not a feature to be celebrated. Handoffs should pass full traces, not summaries, because the summary drops the reasoning the next step needs to stay coherent.

### 3. Compose with the ecosystem; don't reinvent integrations

Per the MCP position: standard interfaces turn an M×N integration explosion into an M+N problem. A workflow that rides MCP/A2A gets the ecosystem's tools and agents for free; one that hand-wires everything carries every integration on its own back, forever. Composability and discoverability are architecture commitments, not later features.

### 4. Orchestration needs coordination, or it shouldn't parallelize

Per Harrison C., answering Yan: multi-agent work is defensible _if_ it is backed by durable shared state and explicit human-in-the-loop checkpoints that prevent and catch conflicting decisions. Fire-and-forget fan-out scales agent count but not reliability. If you can't name what reconciles parallel decisions, don't run them in parallel.

### 5. State should be durable, inspectable, and resumable

Long-horizon agent work is a process, not a chat turn. The state must survive interruption, be inspectable mid-run, and be resumable from a checkpoint with a correction applied. Without this, every interruption costs the operator the whole run, and oversight collapses to all-or-nothing.

### 6. The harness is the product; engineer the environment

Per Mitchell H.: Agent = Model + Harness. The model is fixed; the harness — tools, self-check loops, context files, guardrails — is where reliability is engineered. The agent should be able to verify its own work, and the workflow should be built so the agent is right the first time, because "agents are much more efficient when they produce the right result the first time."

### 7. Every recurring error is an un-built guardrail

Also Mitchell H.: "anytime you find an agent makes a mistake, you engineer a solution such that the agent never makes that mistake again." An error that is merely noticed will recur. An error that is encoded into the harness is gone. The boundary of the harness is the set of errors the team has given up on preventing.

### 8. The architecture must scale the human, not just the agent count

Utility at scale is measured in operator leverage. An architecture that lets one human stay on-the-loop over many durable, resumable, ambiently-surfaced runs scales the human. One that demands synchronous attention per agent scales the agent count while leaving the human as the bottleneck.

---

## §The Rubric

### Dimension A1 [gate] — Ecosystem interoperability & composability

_primary: MCP/interoperability seat (`critic-mcp`)_

Does the workflow connect to tools, data, and other agents through standard, discoverable, composable interfaces — or bespoke glue?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Integrations go through standard interfaces (MCP or equivalent). Tools are discoverable and reusable across workflows; agent-to-agent handoff uses a standard (A2A). Adding a tool or source is M+N. No lock-in at the core seams. |
| **4 — Good** | Mostly standard interfaces; a few bespoke. Most tools reusable. Some lock-in, but components are swappable with effort. |
| **3 — Adequate** | Mix of standard and bespoke. Tools work within this workflow but aren't easily discoverable or reusable elsewhere. Adding integrations is moderate hand-work. |
| **2 — Poor** | Mostly bespoke glue, hand-wired and workflow-specific. Adding a tool means writing glue. Notable vendor lock-in. |
| **1 — Failing** | All integrations bespoke and closed. Nothing discoverable or reusable. M×N tax on every addition. Hard lock-in. |

**Test (gate):** count the integrations and classify each as standard-interface vs. bespoke glue. Then pick a hypothetical new tool — is the cost to add it M+N (it speaks the standard) or M×N (hand-wire it to everything)?

---

### Dimension A2 [review] — Orchestration & coordination model

_primary: Harrison C. (`critic-harrison-c`) · tension: Walden Y._

If the workflow coordinates multiple agents or steps, is coordination backed by shared state and human checkpoints — or fire-and-forget fan-out?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Topology is explicit. Multi-agent is used only where justified, and each branch's decisions are reconciled through durable shared state; human-in-the-loop checkpoints sit at meaningful points; the conflicting-decision failure mode is structurally prevented. **Or:** the workflow is deliberately single-threaded with continuous context (Yan's baseline) and says so explicitly. |
| **4 — Good** | Coordination is mostly sound; shared state exists; checkpoints present with a few gaps. |
| **3 — Adequate** | Coordination by convention; some shared state; checkpoints ad hoc. Holds at small scale. |
| **2 — Poor** | Fan-out with weak coordination; branches can make conflicting decisions; few or no checkpoints. |
| **1 — Failing** | Fire-and-forget parallelism. No shared state, no checkpoints; incoherent merges ship as results. |

**Test:** draw the orchestration topology. For each parallel branch, name what reconciles conflicting decisions and where the human checkpoints are. If neither exists, the workflow is running the multi-agent reliability trap.

---

### Dimension A3 [review] — Context architecture & integrity

_primary: Walden Y. (`critic-walden-y`)_

Is context continuous across the workflow, with full traces shared at handoffs — or fragmented into brains that can't see each other?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Context is continuous by default. Handoffs pass full traces, not summaries. Fragmentation points are few, justified, and reconciled. The whole task shares one brain. |
| **4 — Good** | Mostly continuous; a couple of summary-only handoffs; minor fragmentation. |
| **3 — Adequate** | Some continuity, some fragmentation; handoffs mix traces and summaries; occasional incoherence. |
| **2 — Poor** | Frequent fragmentation; handoffs pass conclusions, not reasoning; coherence is luck. |
| **1 — Failing** | Context shattered across agents/sessions; no trace sharing; incoherent merges are routine. |

**Test:** follow one representative task end to end. Mark every point where the acting agent lacks what the previous step knew. Count the breaks — each is a place the system stopped sharing a brain.

---

### Dimension A4 [gate] — Harness & verification environment

_primary: Mitchell H. (`critic-mitchell-h`)_

Is there a real harness — self-check tooling the agent can run itself — and are recurring mistakes encoded as durable guardrails?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Rich harness: the agent can run linters, type checks, tests, builds, screenshot/diff tools itself, with no human. Recurring errors are encoded as guardrails traceable to real bad behaviors. Quality survives without relying on the model's luck. |
| **4 — Good** | Solid self-check tooling; most recurring errors guarded; a few still tolerated. |
| **3 — Adequate** | Some self-check exists; guardrails inconsistent; several recurring errors merely noticed, not prevented. |
| **2 — Poor** | Minimal harness; the agent can't verify itself; errors are caught only in human review. |
| **1 — Failing** | No harness. The model is the system; recurring errors are tolerated as inevitable. |

**Test (gate):** list the self-check tools the agent can run with no human in the loop. Then take three recent recurring errors — is each now structurally prevented by the harness, or just noticed after the fact?

---

### Dimension A5 [review] — Utility, ROI & first-result quality

_primary: Mitchell H. (`critic-mitchell-h`)_

Does the workflow reliably produce the right result faster than not using it — right the first time — or is it impressive ceremony?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Clear, demonstrable utility: high first-pass success on common tasks; measurable time saved or errors prevented. Every bit of complexity is justified by the utility it produces. |
| **4 — Good** | Good utility; first-pass success is solid; occasional rework; clearly worth it. |
| **3 — Adequate** | Net positive but with meaningful overhead; first-pass success moderate; utility real but unmeasured. |
| **2 — Poor** | Marginal utility; frequent retries and rescues; the human does much of the real work in the cracks. |
| **1 — Failing** | Negative utility: ceremony that feels productive while costing more than it saves. |

**Test:** for the most common task, measure first-pass success rate and end-to-end time vs. not using the workflow. If neither number is known, the utility is asserted, not demonstrated — which is itself the finding.

---

### Dimension A6 [gate] — State durability, resumability & oversight-at-scale

_primary: Harrison C. (`critic-harrison-c`)_

Is agent state durable, inspectable, and resumable — and does that let one human oversee many runs without babysitting?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | State is durable and inspectable mid-run, resumable from checkpoints with corrections applied; an interruption loses nothing. An ambient/inbox model lets one human oversee many runs on-the-loop. |
| **4 — Good** | Durable/resumable state exists; resume is mostly clean; oversight scales with some friction. |
| **3 — Adequate** | Partial persistence; resume is possible but lossy; oversight is mostly synchronous. |
| **2 — Poor** | Little durable state; interruptions lose work; oversight is one-at-a-time, fully attended. |
| **1 — Failing** | Ephemeral runs; any interruption restarts from zero; no inspection; oversight is all-or-nothing. |

**Test (gate):** kill a long run midway. Does it resume from the last checkpoint with state intact, or restart? Then: could one human keep three runs in flight and stay on-the-loop, or does each run demand full attention?

---

## §Anti-patterns

### AP-A1 — Context confetti

**Symptom:** work is shredded across subagents/sessions, then stitched back together at the end. The stitch is where coherence dies. **Root cause:** parallelism treated as free; context fragmentation not counted as a cost. **Correction:** default to continuous context (Principle 2). Fragment only where justified, pass full traces at handoffs, and name what reconciles split decisions.

### AP-A2 — Integration sprawl (not-invented-here glue)

**Symptom:** every tool and data source is hand-wired; adding one is a project; nothing interoperates with the ecosystem. **Root cause:** interoperability treated as a later feature instead of an architecture commitment. **Correction:** ride standard interfaces (MCP/A2A). Make integration M+N, expose capabilities discoverably, and avoid core-seam lock-in (Principle 3).

### AP-A3 — Fire-and-forget fan-out

**Symptom:** multiple agents launched in parallel with no shared state and no checkpoints; conflicting decisions collide and ship. **Root cause:** orchestration scaled agent count without scaling coordination. **Correction:** back orchestration with durable shared state and human-in-the-loop checkpoints, or don't parallelize (Principle 4).

### AP-A4 — Amnesiac runs

**Symptom:** an interruption — crash, timeout, or human — loses the whole run; the operator can't inspect or resume. **Root cause:** agent runs treated as ephemeral chat turns rather than durable processes. **Correction:** durable, inspectable, resumable state with meaningful checkpoint granularity (Principle 5).

### AP-A5 — Prompt-and-pray harness

**Symptom:** the agent can't verify its own work; recurring errors are tolerated and re-corrected by hand every time. **Root cause:** the model is treated as the system; the harness was never engineered. **Correction:** build the harness — self-check tooling the agent runs itself — and encode every recurring error as a guardrail (Principles 6–7).

### AP-A6 — Demo-ware

**Symptom:** the workflow is sophisticated and impressive but doesn't reliably beat not using it; the novelty hides negative ROI. **Root cause:** architecture judged by sophistication, not utility. **Correction:** measure first-pass success and time-vs-baseline (Dimension A5). Delete complexity that doesn't compound into utility (Principle 1).

---

## §Hard Tests

1. **The continuity-trace test.** Follow one task end to end. Where does it stop sharing a brain? The first break is the architecture's coherence ceiling. _(Yan)_

2. **The M×N test.** Add a hypothetical new tool. Is the integration cost M+N (speaks a standard) or M×N (hand-wired to everything)? _(MCP)_

3. **The conflict test.** Point two parallel branches at the same shared surface. What reconciles their conflicting implicit decisions? If nothing, the merge is incoherent by construction. _(Yan / Chase)_

4. **The interruption test.** Kill a long run halfway. Does it resume from a checkpoint with state intact, or restart from zero? _(Chase)_

5. **The self-check test.** What can the agent run to verify its own work with no human in the loop? If the answer is "nothing," the harness is missing its core. _(Mitchell H.)_

6. **The first-result test.** For the most common task, what fraction of runs are right on the first pass? Every retry is waste the harness should have prevented. _(Mitchell H.)_

7. **The deletion test.** What could you remove from this architecture and lose no utility the operator would miss? Whatever you name should probably go. _(utility / Principle 1)_

8. **The oversight-at-scale test.** Could one human keep N runs in flight and stay on-the-loop, or does supervision cost rise linearly with agent count? _(Chase)_

---

## §Research Corpus and Theoretical Grounding

**Cognition — "Don't Build Multi-Agents" (Walden Y., 2025).** The case for single-threaded continuous context: "share context, and share full agent traces, not just individual messages"; "actions carry implicit decisions, and conflicting decisions carry bad results." Grounds Dimension A3 and the A2 tension, and Principle 2. (cognition.ai/blog/dont-build-multi-agents)

**Anthropic — Building Effective Agents.** The orchestration vocabulary the A2 dimension is scored against: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, and the workflows-vs-agents distinction. (anthropic.com/engineering/building-effective-agents)

**LangChain — Ambient Agents & LangGraph (Harrison C., 2025).** Durable, inspectable, resumable agent state ("time travel"), the "agent inbox," and event-driven (ambient) triggering. Grounds Dimensions A2 and A6 and Principles 4–5, 8. (langchain.com/blog/introducing-ambient-agents)

**Anthropic — Model Context Protocol; A2A / Linux Foundation.** The interoperability standard turning M×N integration into M+N; A2A extends it to cross-vendor agent-to-agent communication. Grounds Dimension A1 and Principle 3. (anthropic.com/news/model-context-protocol, linuxfoundation.org A2A)

**Mitchell H. — Harness Engineering ("My AI Adoption Journey," 2026).** Agent = Model + Harness; "anytime you find an agent makes a mistake, you engineer a solution such that the agent never makes that mistake again"; "agents are much more efficient when they produce the right result the first time." Grounds Dimensions A4–A5 and Principles 6–7. (mitchellh.com/writing/my-ai-adoption-journey, martinfowler.com harness-engineering-memo)

**Anthropic — Effective Context Engineering for AI Agents.** Compaction, structured note-taking, and sub-agent context isolation — the disciplines behind context integrity (A3) and the cost-of-fragmentation argument. (anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Builder-side rubrics.** The engineering-side peers of A2/A4 — multi-agent coordination (isolation as structure, not behavior) and the PEV loop mechanics of agentic coding — score the same territory from the builder's correctness standpoint; this rubric scores it from the operator's utility standpoint.
