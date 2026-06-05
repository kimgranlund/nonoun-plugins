---
date: 2026-05-28
status: draft
version: "0.1.0"
type: reference
key_question: >
  For the technique in play (ralph, subagents, async, YOLO, self-improving), can you name the
  property that makes it safe here — reversible, verifiable, greenfield, sandboxed, independent —
  or is it being run on luck?
companion_documents:
  - rubric-agentic-ux.md
  - rubric-agentic-architecture.md
  - workflow-lifecycles.md
  - pev-superworkflows.md
---

# Techniques Catalog — Cutting-Edge Patterns and Their Fit Envelopes

Each technique below is a powerful tool with a **narrow fit envelope**. The defining agentic-UX failure is running a technique outside its envelope — a ralph loop on a brownfield codebase, YOLO mode without a sandbox, subagent fan-out on work whose decisions must agree. The meta-rule for every technique:

> **Name the property that makes it safe here — reversible, verifiable, greenfield, sandboxed, or independent. If you can't name one, you're running on luck.** (`rubric-agentic-ux.md` Hard Test 7.)

> **Seat & ownership (drift control).** This catalog is the **operator-lens projection** — a fit / hard-limit / safe-property row per technique, framed around "can the operator name the property that makes this safe here?" The **builder-grade mechanism catalog** (full control flow, key parameters, termination conditions, context strategy, verification gate, and failure modes per loop family) is owned by the sibling skill **`agent-loops`** (its `references/` + the goal→loop router). One-directional dependency: a new technique or parameter lands in `agent-loops` first; this table adds at most a fit/safe-property row and defers to it for mechanism detail. This file never grows a key-parameters / termination column; `agent-loops` never grows a trust / cognitive-load column. **Mechanism → `agent-loops`; operator experience → here.**

## Fit/risk table

| Technique | Fits | Hard limit | Property that makes it safe |
| --- | --- | --- | --- |
| **Ralph loop** | Greenfield bootstrap, low-stakes MVP | Not brownfield, not high-stakes | Greenfield + sandboxed + backpressure |
| **Subagents / multi-agent** | Analysis fan-out; decomposable builds | Work whose implicit decisions must agree | Genuinely independent subtasks (esp. read-only) |
| **Background / async agents** | Well-specified, verifiable, parallel tasks | Unverifiable or ambiguous tasks | Spec + verifiability + sandbox + PR review |
| **YOLO mode** | Sandboxed, reversible, tight iteration | Anything with real-world blast radius | Containment granted _with_ autonomy |
| **Self-improving loops** | The Improving lifecycle; harness evolution | Unsupervised self-edits to live behavior | Human-curated, inspectable, reversible graduations |

---

## Ralph loop (Geoffrey Huntley)

**What.** An unbounded loop that feeds a prompt file to a coding agent over and over with **fresh context each iteration**: `while :; do cat PROMPT.md | claude-code ; done`. Each loop reads a prioritized task list (`@fix_plan.md`), the specs (`@specs/*`), and a learning doc (`@AGENT.md`), does **one task**, and validates through a single build/test path. The agent spawns subagents for expensive parallel work.

**How to run.** Keep one task per loop to conserve the context window. Guard it with **signs** (prompt guidance), **specs** (explicit requirements), and **backpressure** (compilation, tests, static analysis that fail loudly). The operator's real job is the senior-engineer judgment of **reset vs. rescue** when a loop goes sideways.

**Fits.** Greenfield bootstrapping and low-stakes/MVP work — it gets a fresh codebase ~90% of the way. Proof point: Huntley built CURSED (a working programming language) this way over ~3 months.

**Risks & limits.** "Ralph is deterministically bad in a non-deterministic world" — its failures are predictable and guardable, but it _will_ fail without guards: it can wrongly conclude the work is done, and it can run up cost. The explicit boundary, in Huntley's own words: "no way in heck would I use Ralph in an existing code base." It needs a senior engineer to tune.

**Safe property.** Greenfield + sandboxed + strong backpressure + low stakes. **Rubric/critic**: Arch A2 (it _is_ an orchestration choice), A4 (backpressure is harness — Mitchell H.); UX D1 (high autonomy), D5 (reversibility — Karri S.'s banks). For brownfield, use bounded Spec-Driven Development instead (`pev-superworkflows.md`).

---

## Subagents / multi-agent orchestration

**What.** Spawning subagents into isolated context windows — a Planner → Worker → Judge hierarchy, or a flat fan-out for parallel search and summarization — with an orchestrator synthesizing the returns.

**How to run.** Decompose into subtasks; isolate each subagent's context; have each return a summary; synthesize. For **analysis** this is ideal — the subtasks are read-only and independent, so there are no conflicting _write_ decisions to reconcile.

**Fits.** Analysis/exploration (the clear win), and large decomposable generative builds with hard file boundaries.

**Risks & limits.** This is the heart of the **Walden Y.↔Harrison C. tension**. Walden Y.: parallel subagents make conflicting implicit decisions, and a summary-only handoff drops the reasoning the next step needs — "actions carry implicit decisions, and conflicting decisions carry bad results." Harrison C.: multi-agent is fine _if_ backed by durable shared state and human-in-the-loop checkpoints. Both are right within their envelope.

**Safe property.** Subtasks genuinely independent (read-only analysis is the safest case); full-trace synthesis, not summary-only; or durable shared state + checkpoints when subagents write. **Rubric/critic**: Arch A2 (Harrison C.), A3 (Walden Y.).

---

## Background / async agents

**What.** Assign a ticket; the agent works for minutes to hours in a sandbox and returns a PR. Devin, Cursor Background Agents, OpenAI Codex Cloud, Google Jules, Claude Code Remote Tasks. The human stays **on-the-loop** (reviewing at the PR boundary), not **in-the-loop** (approving each step).

**How to run.** Give a well-specified, verifiable task → let it run async in a sandbox → review the returned PR → merge or send back. One human can keep several in flight.

**Fits.** Parallelizable, well-specified, verifiable tasks — the path to scaling one operator across many agents.

**Risks & limits.** Unverifiable tasks are the trap: if the operator can't verify the PR, the async run just relocates the uncertainty. Spec ambiguity → confidently wrong PR. And many PRs → a review bottleneck that quietly re-bounds the human.

**Safe property.** Well-specified + verifiable + sandboxed + reviewed at the PR boundary. **Rubric/critic**: Arch A6 (durable state, oversight-at-scale — Harrison C.); UX D3 (observability of what the run did), D6 (the PR review _is_ the verify step).

---

## YOLO mode (no per-step approval)

**What.** Auto-accept every agent action with no per-step approval. In Simon W.'s words, "so dangerous, but it's also key to getting the most productive results."

**How to run.** Only inside containment: a container without internet, scoped (non-production) credentials, budget and step limits, and a strong test suite as backpressure. "If a credential can spend money, set a tight budget limit."

**Fits.** Sandboxed, reversible, greenfield, tight-iteration work where per-step approvals would destroy flow without adding safety.

**Risks & limits.** Without containment, YOLO is unbounded blast radius — the agent can take wide, irreversible, real-world actions before anyone notices. Autonomy and containment must be granted **together or not at all**.

**Safe property.** Structural containment (sandbox / no-network / scoped creds / budget) + reversibility. **Rubric/critic**: UX D5 (reversibility & blast-radius — Karri S.), D1 (autonomy calibration — Amelia W.).

---

## Self-improving loops (Reflexion, SICA, MemSkill)

**What.** The research frontier of the **Improving** lifecycle. Reflexion (verbal self-reflection stored in persistent memory); SICA (a self-improving coding agent that edits its own scaffolding, ICLR 2025); MemSkill (an agent that evolves its own skill set). The shape: the agent reflects on failures, writes durable lessons, and applies them next time.

**How to run.** Let the agent surface candidate lessons; the **operator curates** which graduate into durable memory, skills, or guardrails (the memory→skill→hook ladder). Keep self-edits inspectable and reversible.

**Fits.** The Improving lifecycle and long-horizon harness/skill evolution.

**Risks & limits.** Drift (the agent reinforces its own mistakes), unverified self-edits to live behavior, and over-trusting the agent's self-assessment of what's worth keeping.

**Safe property.** Human-curated graduations; inspectable, reversible self-edits; lessons that earn their place against evidence. **Rubric/critic**: UX D7 (feedback compounding — Geoffrey L.), Arch A4 (harness — Mitchell H.).

---

## Supporting: context-engineering techniques

**What.** The disciplines that keep context a precision instrument across long tasks: **compaction** (summarize/trim without losing load-bearing detail), **structured note-taking** (a durable scratchpad the agent maintains), and **sub-agent context isolation**. Cognition calls context engineering "effectively the #1 job of engineers building AI agents."

**Fits.** Any long-horizon task in any lifecycle where context grows toward the window limit.

**Risks & limits.** Compaction that drops the decisions/traces the work depends on; notes that go stale; isolation that fragments coherence (Walden Y. again).

**Safe property.** Compaction preserves decisions and traces; notes are curated, not just appended; isolation reserved for genuinely independent subtasks. **Rubric/critic**: UX D2 (context & memory curation — Geoffrey L.), Arch A3 (context architecture & integrity — Walden Y.).

---

## Using this catalog

- **design mode**: pick the technique from the lifecycle and stakes (`workflow-lifecycles.md`), then name the property that makes it safe _before_ committing to it.
- **evaluate mode**: when a workflow uses one of these, apply the meta-rule — can the operator name the safety property? If not, that's a Major finding on UX D1/D5 or Arch A2/A4.
- **council mode**: route ralph/orchestration questions to Walden Y. + Harrison C. + Mitchell H.; YOLO/blast-radius questions to Karri S. + Amelia W.; self-improving questions to Geoffrey L. + Mitchell H.
