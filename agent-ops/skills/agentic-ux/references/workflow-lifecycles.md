---
date: 2026-05-28
status: draft
version: "0.1.0"
type: reference
key_question: >
  Which workflow lifecycle is the operator actually in — and is the loop shape, technique,
  and autonomy level fitted to that lifecycle, or is everything being treated as a generative
  build?
companion_documents:
  - rubric-agentic-ux.md
  - pev-superworkflows.md
  - techniques-catalog.md
---

# Workflow Lifecycles — The Five Modes of Working With an Agent

The single most common agentic-UX design error is **treating every task as a generative build**. Generative work is the photogenic case — the greenfield demo where the agent writes a thousand lines and it runs. But most real work with an agent is one of five distinct lifecycles, each with a different operator job, a different loop shape that fits, a different set of techniques, and a different dominant failure mode.

This reference is taxonomy, not a rubric — it is the map the `design` mode uses to locate a task and the `evaluate` mode uses at Stage 1 to scope the lifecycles a workflow must support. `rubric-agentic-ux.md` Dimension 8 (lifecycle coverage) scores whether a workflow supports all five or only the happy path; this file is what that dimension points to.

## Quick-pick map

| Lifecycle | Operator's job | Loop shape that fits | Techniques that fit | Dominant failure mode | Load-bearing rubric dims |
| --- | --- | --- | --- | --- | --- |
| **Cold-start** | Onboard the tool/codebase to the agent | Author-and-verify the context | CLAUDE.md/AGENTS.md authoring; compaction | Bloated/stale context | UX D2, D7 · Arch A4 |
| **Orientation** | Understand unfamiliar code before touching it | Explore (read-only) → Plan | Plan-mode; subagent fan-out for survey | Editing before understanding | UX D3, D6 · Arch A3 |
| **Generative** | Build something new | Explore→Plan→Code→Commit; ralph (greenfield) | Autonomous loops; spec-driven | Vibe-coding past where it degrades | UX D1, D5 · Arch A2, A4 |
| **Analysis** | Answer a question about a system | Fan-out → summarize → synthesize | Subagents in isolated context | Context fragmentation / wrong merge | UX D3 · Arch A3 |
| **Improving** | Make the agent better at _this_ project | Observe → correct → graduate | Memory→skill→hook ladder; self-improving loops | Corrections that evaporate | UX D7, D2 · Arch A4 |

The point of the map: **pick the loop and technique from the lifecycle, not from habit.** A ralph loop is excellent for generative greenfield and catastrophic for orientation in a brownfield codebase. Subagent fan-out is right for analysis and a context-fragmentation trap for a coherent generative build.

---

## 1. Cold-start — onboarding the tool and the codebase

**What it is.** The agent arrives at zero mileage every session; cold-start is the work of giving it the context it needs to be useful here. The artifact is the onboarding guide — CLAUDE.md / AGENTS.md / rules / memory — that the agent reads before it does anything.

**Operator's job.** Author the context the way you'd onboard a sharp new hire who forgets everything overnight: what the project is, the conventions, the verify commands, the landmines. Then verify the agent actually absorbed it.

**Loop that fits.** Author → run a representative task → watch where the agent goes wrong → encode the correction → repeat. This is Mitchell H.'s "each line is based on a bad behavior" loop applied to the context file.

**Failure modes.** Context bloat is the silent killer of reliability — a CLAUDE.md that only grows becomes stale and contradictory, and the agent's reliability degrades invisibly. The opposite failure: a thin context file that makes the agent re-discover the same constraints every session.

**Load-bearing dimensions.** UX D2 (context & memory curation — editable, prunable), D7 (feedback compounding — corrections graduate into the context). Arch A4 (the context file _is_ part of the harness).

---

## 2. Orientation — understanding unfamiliar code before touching it

**What it is.** Dropping the agent into a codebase neither it nor (often) the operator fully understands, and building a correct mental model _before_ making changes.

**Operator's job.** Keep the agent read-only until it understands. Use a plan/exploration mode; require a written understanding (what's here, how it fits) before any edit is permitted.

**Loop that fits.** Explore (read-only) → Plan → (only then) act. The plan is the gate; editing before the plan is the failure.

**Failure modes.** Editing before understanding — the agent pattern-matches a change that's locally plausible and globally wrong. The orientation lifecycle is where read-only plan modes earn their keep; a workflow that has no read-only mode forces orientation and generation into the same dangerous step.

**Load-bearing dimensions.** UX D3 (observability — can the operator see the agent's forming model?), D6 (loop closure — is there a plan gate before execution?). Arch A3 (context architecture — does the agent build a coherent model, or fragment it across reads?).

---

## 3. Generative — building something new

**What it is.** Greenfield or substantially new work, where the agent produces a lot and the surrounding code doesn't constrain it much. The photogenic case — and the one most over-generalized to the other four lifecycles.

**Operator's job.** Set the goal and the verify target, then grant a long leash where the work is reversible and verifiable. This is where higher autonomy pays off.

**Loop that fits.** Explore→Plan→Code→Commit for feature work; spec-driven loops when requirements must be explicit; an unbounded **ralph loop** for low-stakes greenfield bootstrapping (it gets ~90% of the way on a fresh codebase). See `pev-superworkflows.md` and `techniques-catalog.md`.

**Failure modes.** Vibe-coding past the point it degrades — autonomous generation degrades once the agent has to guess too many unstated requirements (empirically, somewhere past a few hundred lines). The fix is to make requirements explicit (spec-driven) before the agent guesses.

**Load-bearing dimensions.** UX D1 (autonomy calibration — long leash, earned by reversibility), D5 (reversibility & blast-radius — generation is safe when undoable). Arch A2 (orchestration if multi-agent), A4 (harness/self-check catches generation errors).

---

## 4. Analysis — answering a question about a system

**What it is.** Using the agent to investigate, search, summarize, or explain an existing system — not to change it. "Where is X handled?" "What would break if we changed Y?" "Summarize how this subsystem works."

**Operator's job.** Decompose the question, fan out the search, and synthesize the returns — without letting the parallel investigation fragment into incoherent conclusions.

**Loop that fits.** Fan out subagents into isolated context windows for parallel search/summarization, each returning a summary; the orchestrator synthesizes. This is the one lifecycle where subagent fan-out is clearly right — the subtasks are read-only and independent, so the context-fragmentation cost Walden Y. warns about is low (no conflicting _write_ decisions to reconcile).

**Failure modes.** Fragmentation with conflicting conclusions when the analysis isn't truly independent; or a synthesis that merges summaries without the traces, losing the reasoning. Keep the question decomposed into genuinely independent sub-questions.

**Load-bearing dimensions.** UX D3 (observability — can the operator see what each branch found?). Arch A3 (context architecture — independent sub-questions, full-trace synthesis).

---

## 5. Improving — making the agent better at _this_ project

**What it is.** The meta-lifecycle: training and improving the agent over time so the relationship compounds. Capturing corrections, routines, and preferences so the same work gets easier and the same mistakes stop recurring.

**Operator's job.** Notice what the agent gets wrong or what you keep re-explaining, and graduate it to the right durable tier: auto-memory → declared memory (CLAUDE.md) → skill → hook/CI gate. Prose for soft guidance; mechanism for must-not-regress.

**Loop that fits.** Observe → classify (soft preference vs hard rule) → place at the right tier → verify it stuck. Self-improving loops (Reflexion, SICA, MemSkill) are the research frontier of automating this; see `techniques-catalog.md`.

**Failure modes.** Evaporating corrections — every fix is verbal and per-session, so the operator re-teaches the same lessons forever. The opposite failure: over-mechanizing a soft preference into a brittle hook, or hoarding everything into context (cold-start failure leaking in).

**Load-bearing dimensions.** UX D7 (feedback compounding — the graduation ladder), D2 (context curation — where soft corrections live). Arch A4 (harness — where hard corrections become guardrails).

---

## Using this map

- **design mode**: name the lifecycle(s) the workflow must serve _before_ choosing a loop or technique. A workflow that only serves generative work will fail its users in the other four.
- **evaluate mode (Stage 1)**: tag the artifact's supported lifecycles. Score UX D8 against the count and quality of supported lifecycles, not against the polish of the generative path.
- **The honest test** (UX D8): list the operator's last ten sessions and tag each by lifecycle. A repeatable workflow for only one or two tags means the rest run on luck.
