# Rubric — Ralph / Brute-Force Loop

Scores a **Ralph / brute-force-until-done** plan: a single agent iterating a fixed prompt against a fresh-context-per-pass loop, converging to working code via an automated gate rather than slop. The canonical shape is `while :; do cat PROMPT.md | <agent>; done` (or `--max-iterations N`) over a greenfield checklist, with all state externalized to spec + plan/ledger + git + progress file. Use in **EVALUATE** to audit a Ralph plan or transcript, and as the acceptance bar in **PLAN / COMPOSE** before a Ralph loop ships.

**Band:** per-family. Loaded only when the plan composes the Ralph / brute-force family (manifest `selectors`: `ralph`, `brute-force-until-done`, `while-true loop`, `fresh-context loop`, `overnight batch`, `prompt.md loop`).

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate blocks SHIP; it is not a matter of opinion. Cross-cutting gates are backed by `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`; per-family gates (R2/R3/R4/R7) are **[mech-partial]** — the criterion is structural but no automated script enforces it; agent judgment applies.
- **[mech-partial]** — mechanically checkable criterion, no automated script — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment; score **1–5**, cite the evidence.

**Ship rule:** a Ralph plan ships when **every [gate] passes AND no [review] dimension < 3** — _and_ it additionally clears the dependency: `rubric-loop-control`'s gates (see the dependency note below). Record evidence for every finding — the plan field, the parameter value, the missing bound. A finding without a citation is an opinion.

> **Calibration caveat.** This rubric is **draft** (`rubric-manifest.json` status `draft`, 0 calibration samples). Treat every score as **directional, not authoritative**, until ROADMAP v0.2 calibration is met. The [gate] dimensions are the only mechanically verifiable layer; [review] anchors are best-effort until calibrated against real Ralph runs.

> **Builder-seat boundary.** This rubric scores the _mechanism_ — whether the brute-force loop converges to working code without overbaking or destroying the tree. It does **not** score the operator's experience of watching an overnight Ralph run (trust, interruptibility, the dread of an unattended `--dangerously-skip-permissions` loop). That is the sibling `agentic-ux` skill; hand off rather than scoring UX here.

---

## The backbone: the four gates that decide convergence-vs-slop

Run these first. A Ralph loop that fails any one of them does not converge to working code — it either ships placeholders (R2), poisons itself with stale context (R3), overbakes/runs forever (R4), or corrupts the tree past recovery (R7). The two-axis Ralph thesis is: **a fresh agent, pointed at a declarative spec, gated by a real check, bounded outside the model, contained in its blast radius.** R2/R3/R4/R7 are those four load-bearing structural conditions; R1/R5/R6/R8 are the quality of the spec and the economics around them.

### R2 [gate / mech-partial] — Verification gate rigor

**Criterion:** An automated commit-gating check (typecheck + tests + build + lint, as the task affords) sits between each iteration and acceptance, and it tests **real behavior** such that placeholder / stub / TODO code **fails** the gate. The gate is the loop's engine; a gate that green-lights stubs converges the loop to slop, not to working code.

**Test (binary):** Point at the exact gate command(s) the loop runs each pass (e.g. `npm test && tsc --noEmit && npm run build && npm run lint`). **PASS** iff (a) the command exists and is named concretely (not "the agent checks its work"), AND (b) the gate would reject a stub — i.e. it runs the code / asserts behavior, not merely "file exists" or "it compiled." A loop whose only gate is the agent's self-declaration of done **FAILS**. A gate that a `return null` / `throw new Error("TODO")` placeholder would pass **FAILS** (the placeholder-passes-the-gate failure).

### R3 [gate / mech-partial] — Context-reset discipline

**Criterion:** Each iteration starts **fresh**, loading only the spec + plan/ledger (not the accumulated transcript of prior iterations), so context rot cannot compound across passes; OR, for the Stop-hook session-internal variant where context genuinely accumulates, that divergence from canonical Ralph is **explicitly acknowledged** and the rot risk is named. All cross-iteration state lives on disk (git + plan + progress file), not in the model's window.

**Test (binary):** **PASS** iff the plan states the per-iteration context is fresh (new process / new session per pass — the `while :; do cat PROMPT.md | <agent>; done` shape resets by construction) and names what the fresh instance loads at the top of each pass. For the session-internal Stop-hook variant: **PASS** iff the plan explicitly flags that context accumulates (this is not canonical Ralph) and names the rot mitigation. **FAIL** if the plan assumes the loop "keeps context" across iterations with no acknowledgment that this reintroduces context rot, or never says where per-iteration state comes from.

### R4 [gate / mech-partial] — Stop-condition safety

**Criterion:** The loop has explicit bounds it **cannot** exceed: a hard `--max-iterations` (or token/cost ceiling) as the **primary** backstop, PLUS a completion ledger/sentinel (an explicit COMPLETE marker or an empty remaining-items list) as the goal-gate. Neither alone suffices — the sentinel is self-reported and not trustworthy as the sole stop; the iteration cap is blunt and overbakes if it is the only stop.

**Test (binary / threshold):** **PASS** iff BOTH are present with concrete values: (1) a hard cap — `--max-iterations {n}` or a token/cost ceiling — that bounds an unbounded `while :;`, AND (2) a completion signal the loop reads to halt early (ledger empty / explicit sentinel). **FAIL** if the plan specifies a bare `while :; do … done` with **no** `--max-iterations` and no cost ceiling (the cost-runaway / overbake failure), OR if the **only** stop is the model self-declaring done (the self-reported-sentinel-alone failure). A STUCK/abort path (impossible item escalates instead of iterating into damage) is required at score ≥ pass when the checklist is non-trivial.

### R7 [gate / mech-partial] — Blast-radius containment

**Criterion:** The damage a single bad iteration can do is bounded by structure: a **file allowlist** (the loop may only write within named paths), **git-commit-per-iteration** (every pass is a restore point), a clean **`git reset --hard` to last green** fallback path, AND a **subagent spawn-budget cap** if the Ralph body is allowed to fan out. Brute force without containment corrupts the tree; the recovery path is what makes "throw away the bad pass" cheap.

**Test (binary):** **PASS** iff all four are present: (1) write scope is restricted (allowlist / working-dir boundary — the loop is not free to touch the whole repo), (2) the loop commits per iteration so each pass is individually revertible, (3) the fallback is named as `git reset --hard {last-green}` (or equivalent), AND (4) if the body spawns subagents, a spawn cap is set. **FAIL** if any iteration can write anywhere with no per-pass commit and no reset path (an unrecoverable tree), or if uncapped subagent spawning is permitted.

---

## Quality & economics dimensions

### R1 [review] — Spec / source-of-truth quality

**Criterion:** A concrete, **declarative end-state spec** (a PRD / standard / acceptance list describing _what done looks like_) exists and is **decomposed into independent, verifiable items** — not a vague one-shot imperative ("build the app"). This is the **#1 leverage point** of a Ralph loop: the fresh agent is only as good as the spec it reloads each pass; an ambiguous spec produces a loop that brute-forces toward the wrong target.

**Evidence to cite:** the spec artifact named in the plan (its path, e.g. `spec.md` / `PRD.md`), its decomposition into items, and whether each item is independently checkable by the R2 gate.

**1–5 anchor:**

- **1** — No real spec; the loop is driven by a vague imperative prompt. Done is undefined, so the gate has nothing objective to test against.
- **3** — A spec exists and describes the end state, but items are coarse or partially coupled / partially verifiable; the loop will mostly aim correctly but some items are ambiguous.
- **5** — A concrete declarative spec decomposed into independent, individually-verifiable items, each tied to a check the R2 gate can run. The fresh agent can pick any item and know exactly what "done" means.

### R5 [review] — Scope-per-iteration

**Criterion:** Each pass is constrained to **one item** (or one small coherent unit) producing **small, reversible, reviewable changesets**, with the agent trusted/instructed to pick the **highest-priority** remaining item from the ledger. Wide per-iteration scope defeats the fresh-context model (too much to hold) and produces large unreviewable diffs that the R7 reset can only discard wholesale.

**Evidence to cite:** the per-iteration scope instruction in the prompt (e.g. "implement the single highest-priority unchecked item"), and the expected changeset size.

**1–5 anchor:**

- **1** — The prompt asks the agent to "do as much as it can" per pass; unbounded scope, large diffs, no prioritization signal.
- **3** — Scope is loosely bounded (a few items, or "a feature") and there is some prioritization, but changesets may grow large or the agent may sprawl.
- **5** — Exactly one prioritized item per pass, small reversible reviewable changeset, explicit "pick the highest-priority unchecked item" instruction. Each pass is independently reviewable and discardable.

### R6 [review] — Durable-memory design

**Criterion:** The external state — **plan / progress / PRD ledger + git history + AGENTS.md** — is sufficient to **fully reconstruct** "what is done / what is left / what was learned" for a **memoryless fresh instance** at the start of any iteration. Because R3 throws away the in-window trace each pass, the disk _is_ the agent's only memory; a gap here means the fresh agent re-does or forgets work.

**Evidence to cite:** the named state files (progress file, ledger, git, AGENTS.md / learnings file) and what each carries; whether together they answer done/left/learned with no in-context dependency.

**1–5 anchor:**

- **1** — State lives mostly in the agent's context window; a fresh instance cannot tell what is done or left. The loop loses or repeats work across resets.
- **3** — Git + a plan file carry "done/left," but "learned" (gotchas, decisions, dead ends) is not durably captured, so the fresh agent repeats discovered mistakes.
- **5** — Ledger + git + AGENTS.md/learnings fully reconstruct done/left/learned for a fresh, memoryless instance; the loop resumes losslessly from disk after any reset.

### R8 [review] — Cost / convergence economics

**Criterion:** A stated rationale that **throwing tokens at a brute-force loop beats careful orchestration / conflict-resolution for THIS task**, with a **budget expectation** (rough token/cost/iteration estimate). Ralph is the right tool when the task is greenfield, parallel-checklist-shaped, tolerant of redundant attempts, and cheap-to-gate; it is the wrong tool when items are coupled or the gate is expensive, where the per-iteration premium of repeated full passes is not amortized.

**Evidence to cite:** the plan's justification for brute force over a more orchestrated loop, plus the budget line (expected iterations × cost, or a ceiling).

**1–5 anchor:**

- **1** — No economic rationale and no budget; Ralph is chosen reflexively where the task is coupled or expensive-to-gate (brute force is the wrong fit and the premium is wasted).
- **3** — A budget is stated but the brute-force-vs-orchestrate rationale is thin, or the fit is plausible but unargued.
- **5** — Explicit argument that brute force wins for this greenfield/parallel/cheap-to-gate task over orchestration, with a concrete budget expectation and a named fallback if the loop fails to converge (drop to plan-execute / human triage).

---

## Scoring summary template

```text
Ralph loop: {plan / transcript name}     Topology: Ralph / brute-force-until-done
Substrate: {bash while-loop | --max-iterations runner | Stop-hook session-internal | overnight batch}

Backbone gates (convergence-vs-slop):
  R2 verification-gate rigor ..... PASS / FAIL   {gate command; does a stub fail it?}
  R3 context-reset discipline .... PASS / FAIL   {fresh per pass? state on disk?}
  R4 stop-condition safety ....... PASS / FAIL   {--max-iterations + sentinel; not bare while :;}
  R7 blast-radius containment .... PASS / FAIL   {allowlist + commit/pass + reset path + spawn cap}

Quality & economics (1-5):
  R1 spec / source-of-truth ...... {n}   {declarative spec, decomposed, verifiable items}
  R5 scope-per-iteration ......... {n}   {one prioritized item, small reversible diff}
  R6 durable-memory design ....... {n}   {ledger+git+AGENTS.md reconstruct done/left/learned}
  R8 cost / convergence economics  {n}   {brute-force-vs-orchestrate rationale + budget}

Dependency — rubric-loop-control gates (also apply; see note):
  C1 termination-stack ........... PASS / FAIL
  C2 budget ...................... PASS / FAIL
  C3 verification-gate ........... PASS / FAIL
  C7 durability-idempotency ...... PASS / FAIL / N-A (short loop)

Verdict:
  SHIP / READY-TO-RUN  — every gate (R + inherited C) PASS and no review < 3
  BLOCK                — any gate fails, or any review < 3
  (BLUEPRINT-UNVERIFIED if the plan was not dry-run against its success criterion — per SKILL.md)

Top findings (severity-ranked, each mapped to a Ralph failure mode):
  1. ...
```

Map each finding to the Ralph failure taxonomy in `../references/ralph.md` for root cause (placeholder-passes-the-gate, context-rot-across-passes, unbounded-overbake / cost-runaway, unrecoverable-tree, vague-spec-misconvergence).

---

## Dependency note (load-bearing)

**Every per-family rubric depends on `rubric-loop-control`** (manifest `"dependencies": ["loop-control"]`). When this rubric is loaded, `rubric-loop-control` is loaded too, and **its gates also apply** to the Ralph plan. Concretely, the Ralph-specific gates here are the _family specialization_ of the cross-cutting control plane:

| `rubric-loop-control` gate | How Ralph specializes it (this rubric) |
| --- | --- |
| **C1 termination-stack** (goal-gate + no-progress + hard caps) | **R4** — completion ledger/sentinel + `--max-iterations` + STUCK path |
| **C3 verification-gate** (highest-trust gate between generate and accept) | **R2** — the automated commit-gating check that rejects stubs |
| **C7 durability-idempotency** | **R7** (git-commit-per-iteration restore points) + **R6** (disk is the memory) |
| **C2 budget** (advisory pace + hard ceiling) | **R4** cost ceiling + **R8** budget expectation |

A Ralph plan does **not** ship on this rubric alone: it must clear the **union** of `rubric-loop-selection` + `rubric-loop-control` + `rubric-plan-quality` (the three cross-cutting rubrics, always loaded) **and** these Ralph gates. Passing R1–R8 while failing an inherited `rubric-loop-control` gate is still a **BLOCK**.
