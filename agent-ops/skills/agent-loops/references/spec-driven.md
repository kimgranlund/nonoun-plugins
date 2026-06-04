# Spec-Driven Development & Explore-Plan-Code-Commit (plan-as-contract coding loops)

> Mechanism reference for the **spec-driven / Explore-Plan-Code-Commit (EPCC)** loop family. PLAN mode loads this to parameterize the topology after `router.md` selects it. This family is the **coding specialization of plan-execute** and shares its rubric — score the result with `rubrics/rubric-plan-execute.md`.

## 1. One-liner & where it sits

Write the plan/spec **first** as a durable, reviewable artifact; gate it with a **human checkpoint**; then implement **against** it — so coding becomes _verification against a target_ (the documented LLM strength) rather than open-ended generation, with frequent commits making the loop self-correcting and resumable.

In the taxonomy (`composition.md`) this is an **L1 single-agent iteration body** grounded in a durable written artifact — the "plan-first" branch of agentic coding loops. It is **plan-execute (`plan-execute.md`) applied to long-horizon coding**: the written spec _is_ the up-front plan, `CODE` is execution, and the human approval before `code` is plan-execute's `respond|revise` gate made an explicit, blocking human edit. The two share `rubrics/rubric-plan-execute.md`. Per the composition map: its **CODE stage is itself a verification-driven inner loop** on an L4 oracle (test/build/lint/screenshot), and its **EXPLORE stage is frequently delegated to subagents** in isolated context — so a real spec-driven plan straddles L1 (the outer four-stage flow) with an L4 gate nested inside CODE and an optional L2 fan-out for exploration. When you name it in the blueprint's **CHOSEN LOOP TOPOLOGY** field, use the composition grammar: `Spec-Driven / Explore-Plan-Code-Commit (L1); CODE stage is a verification-driven inner loop on the test/build oracle (L4)`.

It diverges from base plan-execute on three points that this reference exists to pin down: (1) the **plan is persisted to a known file on disk** (PLAN.md / SPEC.md / `specs/<feature>/{requirements,design,tasks}.md`) so it survives compaction, `/clear`, and session restart — the conversation is disposable, the artifact is not; (2) the `respond|revise` gate is split into a **human plan-approval gate** _before_ code and a **machine verification gate** _during/after_ code; (3) the spec is treated as the **source of truth that generates code** — changes flow spec→regenerate, not edit-code-directly.

Aliases you may see: Explore-Plan-Code-Commit (EPCC), Spec-Driven Development (SDD), Plan-then-execute, Plan-mode workflow, Specs-as-source-of-truth, Plan-as-contract, Plan-as-verification, Red-Green-Commit (TDD agent loop), spec-kit / Spec Kit, Kiro spec workflow.

## 2. Mechanism — the control flow

Four-stage outer flow, with the **spec/plan as the load-bearing artifact between stages**. Each stage transition is a deliberate mode switch (read-only → no-edit-planning → edit → commit), and the two pipeline arrows that bracket CODE are gates.

**1. EXPLORE — read-only, build context before committing to an approach.** The agent reads code, traces dependencies, studies existing patterns — in a mode that **forbids edits** (Claude Code "plan mode"). The point is to avoid solving the wrong problem in an unfamiliar codebase. Exploration is often **delegated to subagents** in separate context windows that read many files and report back compact summaries, so exploration tokens don't pollute the implementation context.

**2. PLAN — emit a detailed written plan/spec, then HUMAN GATE.** The agent emits a plan naming the **files to change, the order, the interfaces, what's out of scope, and an end-to-end verification step.** This is where extended-thinking budget is spent (`think` < `think hard` < `think harder` < `ultrathink` escalate the reasoning compute — concentrate it here). **HUMAN GATE:** the plan is opened for **direct human edit** (Claude Code: `Ctrl+G` into editor; spec-kit/Kiro: edit the `.md`) and approved before any code is written. The plan is **saved to a file** so it survives context compaction and session restarts and the run becomes resumable.

The structured-pipeline variants (spec-kit, Kiro) formalize this single stage into a multi-arrow pipeline, each arrow a human review/refine point:

```text
constitution ─▶ specify ─▶ clarify/analyze ─▶ plan ─▶ tasks ─▶ implement
(immutable      (reqs +     (resolve            (design,  (small,    (execute
 principles,     acceptance  [NEEDS              data       indep.,    sequentially,
 9 articles)     criteria)   CLARIFICATION];     models,    reviewable each = small
                             flag ambiguous      contracts) [P] units)  reviewable diff)
                             criteria)
```

**3. CODE — switch to edit mode, implement _against the plan_.** The agent treats the plan as the spec to satisfy. The **inner loop is verification-driven**: run the check (tests / build / lint / screenshot-diff) → read the pass/fail signal **in-context** → fix → repeat until green. **TDD variant** (the crispest form): write failing tests → **confirm they FAIL (Red)** → commit the tests → write code until all tests pass (Green) → commit.

**4. COMMIT — commit (often per-task, incrementally) and open a PR.** Per-task / red-green commits create rollback points so either party can revert a bad step. The spec-as-source-of-truth stance means subsequent changes flow **spec→regenerate** rather than editing code directly ("code serves specifications").

The outer loop:

```text
EXPLORE ──▶ PLAN ──[HUMAN GATE: edit + approve]──▶ CODE ──[MACHINE GATE: run check]──▶ COMMIT
(read-only)  (write spec    ▲                       │ (inner: run→read→fix→green)   │
 subagents    to disk)      edit/approve            └──── re-run check until green ──┘
 in isolated                the .md                                                 │
 context                                                       ┌─ per-task / red-green ┘
                                                               ▼
                                                  drift? ──▶ update the SPEC first, then code
```

**Contrast with base plan-execute (`plan-execute.md`):** plan-execute's replanner is a single typed `respond|revise` that _self-judges_ `past_steps`; spec-driven splits that into a **human** gate on the plan (before code) and a **machine** gate on the result (after code), and persists the plan to disk so the loop is resumable across sessions. The structured-pipeline variants add **compile-time architectural gates** (spec-kit's constitution: "the LLM cannot proceed without either passing the gates or documenting justified exceptions").

## 3. When it fits / when it fails

**Fits (empirically-supported where noted):**

- **Non-trivial change spanning multiple files where the approach is uncertain** — "if you could describe the diff in one sentence, skip the plan" (Anthropic).
- **Unfamiliar codebase:** explore-first prevents solving the wrong problem.
- **Multi-step features** where the agent would otherwise drift across turns — a written plan converts generation into verification, the documented LLM strength. _(Empirically-supported: shinpr cites ADaPT, Prasad et al. NAACL 2024 — up to 33% higher success from separating planning and execution.)_
- **Work that must outlive a single context window:** the on-disk spec survives compaction, `/clear`, and session restart, making the run resumable.
- **Team settings** needing a reviewable contract before code lands, and living documentation that stays in sync because it generates the code.
- **Bug fixes with a reproducible failure:** "write a failing test that reproduces the issue, then fix it" gives an unambiguous red→green target.
- **Large mechanical migrations:** a `tasks.md` with `[P]` markers fans out cleanly to parallel agents.
- **When you want to walk away from the run:** a written plan plus a runnable check is what lets an unattended session finish correctly ("the difference between a session you watch and one you walk away from" — Anthropic).

**Fails (route elsewhere or drop the ceremony):**

- **Trivial / well-scoped changes** (typo, log line, rename): plan overhead exceeds value — Anthropic explicitly says do it directly. → single augmented pass.
- **No runnable verification target exists:** without a check the agent can run, "looks done" is the only signal and the human _becomes_ the verification loop (the **trust-then-verify gap**). Construct an oracle or downgrade the autonomy claim.
- **Plan drift:** implementation diverges from the plan without updating it, which "kills the verification benefit" (shinpr). Update the plan first, then code.
- **Over-detailed plans:** lose flexibility, waste planning budget, and lock in wrong assumptions before contact with the code.
- **Stale spec under deadline:** the durability claim depends on regeneration discipline that's easy to skip; spec and code silently diverge so the "source of truth" lies.
- **Approval-gate theater:** informal "confirm when ready" gates get rubber-stamped — the human skims a long plan and approves without catching omissions.
- **Pipeline overhead for small work:** full `constitution→specify→clarify→plan→tasks→implement` is overkill for a one-line fix.

## 4. Key parameters (the knobs you set)

The highest-value section. Set each to a concrete value in the blueprint; deviations from the default need a stated reason.

| Parameter | Default | Rationale |
| --- | --- | --- |
| **Plan-or-not threshold** | **Plan when the change is multi-file, the approach is uncertain, or the code is unfamiliar; SKIP only if the diff fits in one sentence** (Anthropic's heuristic) | Decides whether to pay planning overhead at all. Reflexive always-plan wastes time on typos; reflexive never-plan ships the wrong-problem solution in unfamiliar code. This is the first gate the router checks. Maps to rubric **PE1-plan-trigger**. |
| **Thinking budget per stage** | **Concentrate extended-thinking in PLAN** (`think` → `think hard` → `think harder` → `ultrathink`); cheap thinking in CODE/COMMIT | The approach is chosen in PLAN; reasoning compute spent on a wrong approach in CODE is wasted. Cheap thinking on planning is the highest-leverage spend. |
| **Plan persistence location & format** | **Write to a known path** — `PLAN.md` / `SPEC.md` for single-spec; `specs/<feature>/{requirements,design,tasks}.md` for the pipeline form — and make the spec **self-contained: name files + interfaces, state what is out of scope, end with an end-to-end verification step** | On-disk persistence is what makes the loop resumable and compaction-proof; self-containment is what makes the spec actually _constrain_ the agent rather than read as vague prose. Maps to **PE2-representation** + **PE8-context-durability**. |
| **Human-gate strength** | **Editable-and-blocking** before code by default (`Ctrl+G` / edit the `.md` + explicit approve); escalate to **hard constitutional/phase gates** for high-stakes work; with an anti-rubber-stamp mechanism (`[NEEDS CLARIFICATION]` markers, ambiguity flags) regardless | Too soft → rubber-stamping (no real check); too hard → friction. Choose per stakes, but never ship a purely informal "confirm when ready" gate as the sole control on a multi-file change. Maps to **PE4-human-gate**. |
| **Verification target type & hardness** | **A check returning a machine-readable pass/fail** (tests > build exit code > linter > output-diff > screenshot-vs-design), with **hardness matched to autonomy**: in-prompt "run and iterate" (watched) → `/goal` re-eval each turn → deterministic **Stop-hook** (unattended) → fresh-context **reviewer subagent** (highest); **agent shows evidence, not assertion** | The check is the loop's engine and sets how unattended the run can be. The most common defect is no runnable check at all (see §3, §6). Maps to **PE5-verification-hardness**; tie to `control-plane.md` §verification. |
| **Commit cadence** | **Per-task** (or **red→green** for TDD) — small reviewable diffs, each a rollback point | Frequent commits create the checkpoints that make the loop self-correcting and resumable, and are the precondition for "try something risky, rewind if it fails." Coarse commits produce thousand-line diffs no one reviews. Maps to **PE7-drift-control** (rollback points) + `control-plane.md` §durability. |
| **Requirement formality (EARS)** | **Express acceptance criteria as EARS** — `WHEN [condition] THE SYSTEM SHALL [behavior]` — for anything with non-obvious behavior; plain prose only for trivially-scoped work | Single-interpretation criteria reduce the ambiguity that produces wrong code, and **directly seed the tests**. Fuzzy user stories admit multiple readings the agent picks wrong. Maps to **PE2-representation**. |
| **Task granularity & parallelism** | **Small, independently reviewable units**; mark independent ones `[P]` / by wave so they fan out — coarse enough to avoid coordination overhead, fine enough that each is one reviewable diff | Sets reviewability and how cleanly the migration fans out to parallel agents. Too coarse → un-reviewable diffs; too fine → coordination overhead. Governs the L2 fan-out option for mechanical migrations. |
| **Context handoff boundary** | **`/clear` and execute the spec in a FRESH session** after planning (Anthropic) — clean context anchored only by the written spec | Trades conversational continuity for less context rot; the on-disk spec is what makes this safe. The fresh-context handoff doubles as a quality lever: a reviewer in a fresh session isn't biased toward code it just wrote. Maps to **PE8-context-durability**; see `control-plane.md` §context. |

## 5. Termination / context / verification (this family's instantiation)

These are the cross-cutting `rubrics/rubric-loop-control.md` concerns. **Do not re-derive them** — `control-plane.md` is canonical; below is how this family wires into it.

**Termination** — layered, enforced outside the model (control-plane §termination):

- **Goal-gate (canonical success exit):** the **machine verification target passes** — test suite green, build succeeds, lint clean, or screenshot matches design — and the agent reads the signal and stops. (Pipeline form: **all tasks in `tasks.md` / the plan checked off**, each having produced a reviewed diff.)
- **Stop-hook stops blocking** — the deterministic check it runs finally passes. _Note: Claude Code force-ends after 8 consecutive Stop-hook blocks to avoid infinite loops_ (see §6).
- **`/goal` condition holds** when the separate evaluator re-checks after a turn.
- **Human approves the final diff / merges the PR** — often after an adversarial reviewer subagent reports no correctness gaps.
- **Escape hatch / abort:** human course-corrects or **rewinds to a checkpoint** when the loop is thrashing (`>2` failed corrections → `/clear` and re-plan). This is the STUCK path — escalate, don't iterate into damage.
  > Never let the human's "looks done" approval be the _only_ stop on correctness-critical work — pair it with the machine gate, or the human silently becomes the verification loop.

**Context strategy** — _the spec/plan is the durable memory; this is the family's core durability mechanism_ (control-plane §context):

- The **spec is written to disk** so it survives context compaction, `/clear`, and session restart — the conversation is disposable, the artifact is not.
- **EXPLORE is offloaded to subagents** in separate context windows that read many files and report back compact summaries, keeping the main implementation context clean (the context window is "the most important resource to manage"; performance degrades as it fills).
- **Strong recommendation to execute the spec in a fresh session** after planning, so implementation starts with clean context anchored only by the written spec.
- Across stages: `/clear` between unrelated tasks, `/compact` with focus instructions, and checkpoint-summarize keep the working context lean.
- Pipeline variants (spec-kit/Kiro) persist the **full chain** (`constitution.md` + `requirements/design/tasks.md`) under version control, so context is reconstructable by any agent or human at any later point — "consistency across time" and "across LLMs."

**Verification gate** — _two complementary gates; this family's distinguishing feature_ (control-plane §verification; rubric **PE5-verification-hardness**):

- **(1) HUMAN PLAN-APPROVAL GATE before any code:** the plan/spec is reviewed and **editable** (`Ctrl+G`; edit the `.md`; "confirm when requirements meet your needs"), and in the strict form **blocked** by constitutional/phase gates. Spec-kit forces self-review via `[NEEDS CLARIFICATION]` markers; Kiro's requirements analysis flags acceptance criteria with multiple interpretations _before_ design.
- **(2) MACHINE VERIFICATION GATE during/after code:** a check returning a readable pass/fail — tests, build exit code, linter, output-diff vs fixture, or screenshot-vs-design. **TDD makes this maximally crisp:** tests written → confirmed to **FAIL (Red)** → human-approved → committed → code until green.
- **Hardness is tunable** (matched to autonomy in §4): in-prompt iterate → `/goal` re-evaluation each turn → deterministic Stop-hook → **fresh-context reviewer subagent that tries to refute the result** so "the agent doing the work isn't the one grading it."
- **Best-practice rule:** the agent shows **evidence** (test output, command + return code, screenshot) rather than asserting success. An asserted "tests pass" with no shown output is not a gate.

## 6. Failure modes (each with its guard)

| Failure mode | Guard |
| --- | --- |
| **Trust-then-verify gap** — plausible implementation that silently fails edge cases because no runnable check gated the stop; the human becomes the verification loop | Construct a runnable oracle (tests/build/lint/diff/screenshot) _before_ CODE; if none can exist, drop the autonomy claim and keep a human in the inner loop. Rubric **PE5**. |
| **Plan drift** — code diverges from the plan without updating it, destroying the verification benefit and leaving a lying spec | Mandate **"update the plan first, then code"**; receding re-check of code against the spec. Rubric **PE7-drift-control**. |
| **Spec rot** — `requirements/design/tasks.md` fall out of sync with code; the "source of truth" becomes fiction | A **regeneration/sync path** (spec→regenerate) and a freshness check; treat the spec as authored, not generated-once. Rubric **PE7** + **PE2**. |
| **Rubber-stamped gates** — human approves a long plan without reading it; soft "confirm when ready" gates provide no real check | Anti-rubber-stamp mechanism: `[NEEDS CLARIFICATION]` markers, ambiguity flags forcing explicit resolution; raise gate strength for high-stakes work. Rubric **PE4**. |
| **Test gaming** — agent writes mocks or trivially-passing tests to reach green | **"Confirm tests FAIL first" (Red)**, "avoid mocks," real-environment testing, and **human test approval** before code. Rubric **PE5**. |
| **Over-planning** — excessive plan detail wastes budget and prematurely locks wrong assumptions before contact with the code | Cap planning detail to "files + interfaces + out-of-scope + verification step"; don't over-specify implementation the code should discover. Rubric **PE2**. |
| **Reviewer over-engineering** — a gap-hunting reviewer subagent manufactures findings, inducing needless abstraction and defensive code | **Scope the reviewer to correctness / stated-requirements gaps only** — not style or speculative completeness. (Composition: the adversarial-verify sub-step is droppable and must be scoped — `composition.md` §3.) Rubric **PE5**. |
| **Context pollution during exploration** — an un-scoped "investigate X" reads hundreds of files and fills the main context | Delegate EXPLORE to **subagents in isolated context**; scope the investigation. See §5 + `control-plane.md` §context. |
| **Stop-hook infinite loop / 8-block force-end** — a too-strict deterministic gate can never pass, burning turns until the harness force-ends | Make the Stop-hook check _achievable_; pair it with `max_replans` / a hard iteration cap and a no-progress detector. Rubric **PE7** + loop-control C1. |
| **Pipeline overhead for small work** — full `constitution→specify→clarify→plan→tasks→implement` for a one-line fix | Router gate: skip the spec ceremony when the diff fits in one sentence (single augmented pass). Rubric **PE1-plan-trigger**. |
| **Cost inversion on short tasks** — the up-front PLAN call is pure overhead when the change is tiny | Same gate as above; the planning call must earn its cost on multi-file/uncertain work. Rubric **PE1**. |

## 7. Composition — how it nests / wraps

(`composition.md`)

- **It IS the coding specialization of plan-execute.** `plan-execute.md` §7 lists this family as "the planning skeleton of a coding loop": the written spec is the up-front plan, `code` is execution, the human approval before `code` is the `respond|revise` gate. **Same rubric** (`rubric-plan-execute`). When the roles stay in one agent it is **L1**; when planner/executor/reviewer become distinct agents it borders **L2** (`orchestrator-workers.md`) — the test is whether the decomposition is foreseeable (stay here) or runtime-decided (go there).
- **The CODE stage nests an L4 oracle gate.** Per `composition.md`, "Spec-Driven's CODE stage is a verification-driven inner loop (L4 oracle gate)." The inner run→read→fix→green loop is an evaluator-optimizer-shaped loop (`evaluator-optimizer.md`) whose evaluator is an **executable check**, not an LLM judge — the strongest gate kind. Name its own iteration cap and budget per `composition.md` §4's cross-check-against-L5 rule.
- **EXPLORE is an optional L2 fan-out.** Exploration delegated to subagents in isolated context is an orchestrator-workers / research-style fan-out (`auto-research.md` discipline: isolation + compression-on-return) bolted onto the front of an L1 body. Keep it read-only and single-purpose.
- **Verifier as a wrapped sub-step.** Beyond the executable inner gate, a **fresh-context reviewer subagent** or an adversarial-verify panel (`debate-ensemble.md`) can sit between CODE and the respond branch — the droppable adversarial-verify gate (`composition.md` §3), scoped to correctness only (§6).
- **Mechanical-migration fan-out.** A `tasks.md` with `[P]` markers fans the IMPLEMENT stage out to parallel agents — bounded by the same independence/isolation discipline as `auto-research.md` (no parallel writes to shared state).
- **Async dispatch.** A spec-driven run is a prime candidate for the **dispatch wrapper** (`async-oversight.md`): the on-disk spec + runnable gate is exactly what lets the run go unattended/background. Design the dispatch mechanism here; **hand the operator-experience scoring to the sibling `agentic-ux` skill** (trust/steerability of the running workflow is out of this skill's seat).

## 8. Primary sources

- **Best practices for Claude Code** (Anthropic / Claude Code Docs). Primary source for Explore→Plan→Code→Commit, the TDD red→green→commit loop, "give Claude a way to verify its work" (tests/build/screenshot), the thinking-budget keywords, the plan-mode human gate (`Ctrl+G`), subagent exploration/verification, fresh-context handoff, the writer/reviewer pattern, `/goal` + Stop-hook gate hardness, and the named failure patterns (trust-then-verify, infinite exploration). <https://code.claude.com/docs/en/best-practices>
- **spec-kit/spec-driven.md** (GitHub, official methodology doc). Defines spec-as-source-of-truth ("code serves specifications"), the constitution concept and its 9 articles as compile-time architectural gates, `[NEEDS CLARIFICATION]` self-review markers, test-first/Red approval, and the `specify→plan→tasks` pipeline with phase gates and Complexity-Tracking exceptions. <https://github.com/github/spec-kit/blob/main/spec-driven.md>
- **Spec-driven development with AI: a new open-source toolkit** (The GitHub Blog). Clearest articulation of the vibe-coding problem SDD solves, the four phases (specify/plan/tasks/implement) each with an explicit human checkpoint question, why small reviewable diffs beat thousand-line dumps, and the spec as a regenerable/living artifact (update spec → regenerate). <https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/>
- **Specs — Kiro Docs** (AWS). Primary source for the three durable artifacts (`requirements.md` / `design.md` / `tasks.md`), the Requirements-First vs Design-First vs Quick-Plan variants, approval gates between phases, dependency-based wave execution of tasks, and the EARS acceptance-criteria template (`WHEN … THE SYSTEM SHALL …`). <https://kiro.dev/docs/specs/>
- **Planning Is the Real Superpower of Agentic Coding** (shinpr, DEV). Supplies the mechanism claim "execution becomes verification — and LLMs are better at verification," the empirical anchor (ADaPT, Prasad et al. NAACL 2024: up to 33% higher success from separating planning and execution), and the drift failure mode ("update the plan first; drift kills the verification benefit"). <https://dev.to/shinpr/planning-is-the-real-superpower-of-agentic-coding-1imm>

---

**Score this topology with `rubrics/rubric-plan-execute.md`** (gates: PE1-plan-trigger, PE4-human-gate, PE5-verification-hardness, PE7-drift-control; review: PE2-representation, PE3-replanning, PE6-planner-executor-split, PE8-context-durability), plus the always-on cross-cutting rubrics (`rubric-loop-selection`, `rubric-loop-control`, `rubric-plan-quality`).
