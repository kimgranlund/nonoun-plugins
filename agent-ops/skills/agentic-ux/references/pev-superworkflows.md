---
date: 2026-05-28
status: draft
version: "0.1.0"
type: reference
key_question: >
  Is the loop shape fitted to the lifecycle and stakes — and does it close against reality,
  with the human owning the verify target — or is it Plan→Execute with the operator eyeballing
  the summary?
companion_documents:
  - rubric-agentic-ux.md
  - workflow-lifecycles.md
  - techniques-catalog.md
---

# P-E-V Super-Workflows — Loop Shapes and Their Fit

**Plan → Execute → Validate is the spine of every productive agentic workflow.** But "P-E-V" is a family, not a single loop: its instantiation differs by lifecycle, stakes, and how explicit the requirements must be. This reference catalogs the canonical loop shapes, when each fits, and how each can fail — so the `design` mode can choose the right one and the `evaluate` mode can judge whether the chosen one closes.

The builder-side mirror is the agentic-coding rubric, which scores whether a _system_ implements PEV reliably. This file is the _operator's_ view: which loop to run, and how to keep the human in the three seats only the human can hold.

## The human's three irreducible pillars

Across every loop shape, three responsibilities stay with the operator and cannot be delegated to the agent (Simon Willison):

1. **Goal definition** — what "done" means, stated before the loop starts.
2. **Tool preparation** — giving the agent the tools and access the loop needs.
3. **Verification** — naming the verify target _grounded in reality_, and owning the judgment that it passed.

The agent can _run_ the verification; the human must _define_ it. A loop where the human skipped pillar 3 doesn't close — it stops when the agent says "done," which is not the same thing. This is `rubric-agentic-ux.md` Dimension 6.

## The core loop

```text
        ┌──────────── name the verify target (before starting) ───────────┐
        ▼                                                                   │
   PLAN  ──►  EXECUTE  ──►  VALIDATE (against reality)  ──►  done?  ──�no──►─┘
                                                              │
                                                             yes
                                                              ▼
                                                            COMMIT
```

The loop's integrity comes from naming the verify target _before_ execution. An agent that picks the verify target after executing will choose the easiest available signal (compile, lint) rather than the one that proves the work (the product behaves correctly).

---

## Variant 1 — Explore → Plan → Code → Commit (Anthropic)

**Shape.** Explore the relevant code read-only → produce a plan (files, approach, verify target) → implement → verify → commit. **When.** The default for feature work and most brownfield changes. "Skip the planning step only if the change is so small the diff fits in one sentence." **Lifecycle fit.** Orientation (the Explore phase) and Generative (the Code phase). The highest-leverage single practice across all of it: _give the agent a way to verify its own work_ (tests, a screenshot, a lint pass). **Fails when.** The plan is a vibe ("I'll start with auth") with no file list and no verify target — execution then improvises and the loop never really closes.

## Variant 2 — Spec-Driven Development (Spec → Plan → Tasks → Implement)

**Shape.** Write an explicit, executable spec first; derive a plan; decompose into tasks; implement against the spec. Tools: GitHub Spec-Kit (works across 30+ agents), AWS Kiro (spec → design → tasks → implementation), BMAD-METHOD. **When.** Larger builds, multi-agent work, and **brownfield** changes where requirements must be explicit before the agent guesses. The spec is the coordination surface and the anti-vibe-coding mechanism. **Lifecycle fit.** Generative at scale, and the safe alternative to an unbounded loop on an existing codebase. **Fails when.** The spec is the PRD with technical bullets appended — no decomposition, no acceptance criteria, no file/module map. (See PRD- and spec-authoring rubrics for the bar.)

## Variant 3 — The tight agentic loop (think → code → execute → verify → repeat)

**Shape.** A fast inner loop: the agent thinks, writes code, runs it, reads the result, debugs, repeats — until the verify target passes. **When.** Tight iteration where feedback is cheap and fast (a failing test, a stack trace, a screenshot). This is where autonomy pays off most, because each turn is grounded by a real signal. **Lifecycle fit.** Generative and the inner loop of Improving. **Fails when.** There is no fast real-world signal to close each turn — the agent loops on its own internal consistency, "fixing" things that were never broken, with no backpressure. Pairs with a circuit breaker (stuck-counter) to bound runaway loops.

## Variant 4 — Orchestrated loops (orchestrator-workers, evaluator-optimizer)

**Shape.** Anthropic's multi-agent patterns: an **orchestrator** decomposes work to **workers** and synthesizes; an **evaluator-optimizer** pairs a generator with a critic that loops until quality passes. **When.** Decomposable work with clear sub-boundaries (orchestrator-workers) or work with a clear quality signal a critic can check (evaluator-optimizer). **Lifecycle fit.** Analysis (fan-out) and large Generative builds. **Fails when.** The orchestration has no durable shared state or checkpoints (Chase) — or it parallelizes work whose implicit decisions must agree, producing conflicting merges (Yan). This is exactly the A2/A3 tension; choose the topology deliberately, not by reflex.

---

## Fit table

| Loop shape | Best lifecycle | Stakes/requirements | Primary risk |
| --- | --- | --- | --- |
| Explore→Plan→Code→Commit | Orientation + Generative (feature work) | Medium; requirements discoverable | Plan-as-vibe |
| Spec-Driven Development | Generative at scale; brownfield | High; requirements must be explicit | Spec = PRD-with-bullets |
| Tight agentic loop | Generative; Improving inner loop | Low-medium; fast real signal available | Looping with no backpressure |
| Orchestrated (workers / evaluator) | Analysis; large Generative | High; decomposable or critic-checkable | Conflicting merges / no shared state |
| Ralph loop (see techniques-catalog) | Generative greenfield only | Low stakes; sandboxed | Brownfield disaster; non-determinism |

---

## The one rule under all of them

**The loop closes against reality, or it doesn't close.** Whatever the shape, the validate step must check the real product — npm publish → curl the registry; UI change → render it; API change → integration test against a running server — not the agent's self-report and not a green compile. The shape determines _how_ the agent works; the verify target determines whether the operator can believe the result.

Cross-references: `workflow-lifecycles.md` (which loop fits which lifecycle), `techniques-catalog.md` (ralph, subagents, async, YOLO as ways to run these loops), `rubric-agentic-ux.md` D6 (loop closure) and `rubric-agentic-architecture.md` A2 (orchestration).
