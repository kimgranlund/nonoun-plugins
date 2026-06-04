# Example A — Migrate 200 React class components to hooks

A complete **PLAN-mode** run on a goal that is **large but mechanical**: decomposable, automatically verifiable, closed-target, reversible, and brownfield. The router lands on a **per-file iterative loop wrapping an inner evaluator-optimizer**, driven by an external durable ledger. The companion run (`example-b-auth-vendor.md`) takes the _opposite_ router branch — open-ended research fan-out — to show the router discriminates by goal shape rather than by the skill that ran it.

> **Goal (as stated by the user):** "use agent-loops to create the best plan to migrate a 200-file React class-component codebase to hooks, achieving zero behavior regressions."

> **Seat discipline.** This run stays in the **builder seat**: pick the mechanism, wire the runnable plan. It does **not** score the human experience of operating that plan (trust, observability, steerability, cognitive load). The run ends by handing the emitted blueprint to the sibling `agentic-ux` skill (operator seat) for that evaluation. Shared vocabulary, different job, different output.

---

## A.1 — Ingestion

**Restated goal.** Convert ~200 React class components to function components + hooks, across an _existing_ codebase, with **zero observable behavior change**.

**Success criterion (made concrete — load-bearing; a fuzzy criterion produces a fuzzy loop).**

- **Primary, machine-checkable:** for every migrated file, the existing test suite passes **AND** `tsc --noEmit` is clean **AND** the component's render output / committed snapshots are byte-identical pre/post. "Zero behavior regression" = **the existing automated gate stays green on a per-file basis**, with snapshot diffs as the regression oracle.
- **Coverage-gap flag:** files with **no** test/snapshot coverage cannot be verified by the gate. These are quarantined to a manual-review lane, not silently passed. Naming this gap _now_ is what stops the loop from converging to _green-but-wrong_ on unverifiable files.

**Task-shape classification** (the eight-axis read the router keys on; the discriminating axes are starred):

| Axis | Reading | Signal |
| --- | --- | --- |
| Verifiability / oracle ★ | **Strong, automated, pre-existing** (tests + typecheck + snapshots) | unlocks a real gate → real termination |
| Decomposability ★ | High — ~200 **independent** units; one file ≈ one work item | favors per-item iteration |
| Parallelizability / independence | Mostly independent; shared-util edits are the exception | serialize the shared-write minority |
| Solution-space width ★ | **Closed** — target state (hooks) is specified, not discovered | not a research / decision problem |
| Horizon | Long (200 items) but each item is short | favors many small iterations over one mega-session |
| Reversibility / stakes ★ | High — git-per-file; a bad file is `git revert` | favors brute-force "re-try is cheap" |
| Determinism / open-endedness | Closed + mechanical | rules out replanning / discovery loops |
| Budget posture | Re-running one file ≪ hand-resolving a 200-file mega-diff | favors many cheap disposable attempts |
| Codebase posture ★ | **Brownfield** — must respect existing invariants | constrains which loop is _safe_ |

→ **Shape = decomposable + automatically verifiable + closed-target + reversible + brownfield.** This is the canonical fit for an **iterative per-item loop with a hard verification gate** — _not_ a research, debate, or fan-out problem.

---

## A.2 — Decomposition

### Goal→loop router (showing the discriminating ANSWERS)

The router is an ordered decision table over the classification, read top-to-bottom, stop at the first row that fits (`router.md`). The _answers_ — not the questions — select the topology.

| Router question | Answer for this goal | What it rules in / out |
| --- | --- | --- |
| Does a single strong pass suffice (errors not worth iterating)? | **No** — 200 files, each independently fallible | rules **OUT** the single-augmented-LLM null option |
| Is the solution space open (must discover the approach) or closed (target known)? | **Closed** | rules **OUT** Auto-Research, debate/council, plan-execute-with-replanner |
| Does it decompose into independent verifiable items? | **Yes — ~200** | rules **IN** per-item iteration; rules **OUT** one monolithic agent session |
| Is there a cheap, automated, trustworthy verification gate? | **Yes** (tests + `tsc` + snapshot) | rules **IN** a gated loop; this precondition is what makes brute-force _converge_ rather than _slop_ |
| Do items share mutable state / must decisions agree across items? | **Mostly no** (per-file; shared-util edits are the exception → serialize those) | rules **OUT** naive parallel fan-out with conflicting writes |
| Greenfield or brownfield? | **Brownfield** | **rules OUT a pure Ralph `while:;` loop** (Huntley: _"no way in heck would I use Ralph in an existing code base"_) — must respect existing invariants |
| Does each item need human judgment / is it irreversible? | **No** (mechanical + reversible) | rules **IN** unattended batch; **OUT** mandatory per-item human gate |

### SELECTED topology

**Per-file iterative loop (one item per iteration, fresh-ish context) wrapping an evaluator-optimizer inner micro-loop, driven by an external durable ledger — orchestrated as a pipeline over the 200 files.**

Concretely: a Ralph-_style_ fresh-context-per-file outer loop (borrowing the externalized-state + one-task-per-loop discipline) but **bounded and brownfield-safe** — file allowlist, per-file branch, mandatory pre-existing gate, no autonomous scope expansion. Within each file, an evaluator-optimizer micro-loop: convert → run gate → if fail, feed the failure back and revise (cap 3) → commit only if green.

### REJECTED alternatives (≥2, with why)

- **Rejected: pure Ralph loop (`while :; do cat PROMPT.md | <agent>; done`).** Right _iteration_ primitive, wrong _autonomy posture_ for brownfield. Pure Ralph is greenfield-only and prone to "overbaking" (inventing out-of-scope work) and **trampling existing invariants**. **Kept** its load-bearing ideas — externalize state to a ledger + git, one task per loop, fresh context to dodge context rot — but **added** the brownfield guards (allowlist, per-file branch, snapshot oracle, max-iterations, no scope expansion) that pure Ralph lacks. _(See `ralph.md` for the suitability boundary.)_
- **Rejected: orchestrator-workers parallel fan-out (N files at once).** Tempting for 200 files, but files that touch **shared** utilities/contexts make _conflicting implicit decisions_ across isolated worker contexts — the Cognition **"Flappy-Bird" failure**: two workers, incompatible choices, coordinator can't reconcile. Independence is _mostly_ true but not _uniformly_ true, and the cost of one cross-file collision corrupting a shared module outweighs the wall-clock win. Adopted instead as a **bounded read-only sub-step** (search-before-write, to avoid duplication) and a **serial** write path; shared-module edits are explicitly serialized.
- **Rejected: evaluator-optimizer alone (single session, whole codebase).** It's the right _inner_ gate but the wrong _outer_ shape: a single accumulating context across 200 files hits **context rot** well before completion (quality degrades past ~150k tokens) and gives no per-file revert granularity. So evaluator-optimizer is **demoted to the inner micro-loop** (per file), where its accumulating-feedback memory is an asset, and the **outer** loop carries state externally.

### PARAMETERIZE the control plane

Every loop in this skill pins these knobs to concrete values (`control-plane.md`):

| Knob | Value | Rationale |
| --- | --- | --- |
| **Iteration unit** | one file per outer iteration | fits a clean context; produces a small, reviewable, revertible diff |
| **Inner refine cap** | max **3** generate→gate→revise rounds per file | evaluator-optimizer returns saturate in 1–2 rounds; 3 prevents oscillation / cost blow-up |
| **Outer bound** | `--max-files` = 200 + a per-file **budget** (~40k tokens, hard ceiling 60k) | financial circuit breaker; refusal-resistant sizing |
| **Termination (layered, enforced OUTSIDE the model)** | (1) **goal gate** — ledger has 0 files with `status != passed`; (2) **no-progress** — a file fails the gate 3× → mark `BLOCKED`, do not loop further on it; (3) **hard cap** — file budget / file count exhausted | naive max-iterations alone is a blunt instrument; the ledger's all-passed state is the real "done" |
| **Verification gate** | per file: `tsc --noEmit` clean **AND** `jest <file>` green **AND** snapshot diff empty. Commit **only if green**. Files with no coverage → `status = NEEDS_MANUAL` (never auto-`passed`) | the gate must test **real** behavior or the loop converges to stubs that merely compile; snapshot diff is the regression oracle |
| **Context strategy** | **fresh context per file**; durable state externalized to `migration_ledger.json` + git history + `AGENTS.md` (learned hooks-migration gotchas appended). Within a file, accumulate (output + failure + feedback) for the 3 refine rounds | dodges context rot across 200 files; a memoryless fresh worker fully reconstructs "what's left / what's done / what was learned" from the ledger |

---

## A.3 — Execution: the runnable orchestration blueprint

Emitted against the 14-field Orchestration Blueprint (`SKILL.md` → Output Contract). Fields condensed where A.1/A.2 already established them; the runnable sketch and gate command are given in full.

```text
ORCHESTRATION BLUEPRINT — react-class-to-hooks

1.  GOAL & SUCCESS CRITERION
    - Goal: migrate ~200 React class components to function components + hooks.
    - Success criterion: per file, tests pass AND `tsc --noEmit` clean AND snapshot diff empty;
      uncovered files quarantined to a manual lane, never auto-passed.

2.  TASK CLASSIFICATION
    - brownfield · decomposable · depth-shallow-per-item · verifiable (automated oracle) ·
      reversible (git-per-file) · one-shot-per-file (re-tryable).

3.  CHOSEN LOOP TOPOLOGY + WHY
    - Primary: per-file iterative loop (Ralph-style fresh-context, one item/iteration) —
      because the work is decomposable, closed-target, reversible, and automatically verifiable.
    - Nested: an evaluator-optimizer micro-loop INSIDE each file (convert → gate → revise, cap 3),
      where accumulating failure-feedback is an asset.

4.  REJECTED ALTERNATIVES
    - Single strong pass — rejected: 200 independently-fallible files; one pass cannot self-verify
      each and gives no revert granularity.
    - Pure Ralph `while:;` — rejected: greenfield-only; overbakes and tramples brownfield invariants
      (Huntley). Kept its externalized-state + one-task-per-loop ideas; added brownfield guards.
    - Orchestrator-workers parallel fan-out — rejected: shared-util edits cause conflicting implicit
      decisions across isolated contexts (Cognition Flappy-Bird). Demoted to a read-only grounding
      sub-step + serialized shared-module writes.
    - Evaluator-optimizer alone (whole codebase, one session) — rejected: context rot past ~150k
      tokens, no per-file revert. Demoted to the inner micro-loop.

5.  WIRING / CONTROL FLOW
    setup → seed ledger, quarantine uncovered files
    outer loop (fresh context/iteration): pick next pending file → branch → read-only dep grounding
      → inner evaluator-optimizer (cap 3): convert → gate → green? commit+passed : keep feedback
      → not green after 3 → BLOCKED → append learnings → discard context → next file
    The gate sits INSIDE the inner loop; the ledger's all-passed state sits OUTSIDE the model as
    the goal gate.

6.  PARAMETERS
    - iteration unit: 1 file/outer-iteration ; inner refine cap: 3 ; dep-grounding fan-out: ≤5 (read-only)
    - per-file token budget (advisory): 40k ; hard ceiling: 60k ; outer cap: --max-files=200
    - model-per-role: converter+reviser = capable coding model ; gate = deterministic shell (no model)
    - plan representation: migration_ledger.json (pending|passed|BLOCKED|NEEDS_MANUAL, attempts, last_error)
    - learned-memory: AGENTS.md append-only ; replan cadence: none (closed target, no replanning)

7.  TERMINATION CONDITIONS (layered, enforced outside the model)
    - goal-gate: ledger.none(status == pending)
    - no-progress: a file fails the gate 3× → status = BLOCKED (stop looping it; do not iterate into damage)
    - hard caps: per-file budget exhausted OR --max-files reached
    - stuck/abort path: BLOCKED + NEEDS_MANUAL tails escalate to a human, never auto-pass.

8.  VERIFICATION GATE
    - type: executable oracle (deterministic shell; no model in the gate).
    - what it checks: `tsc --noEmit` clean AND `jest --findRelatedTests` green AND snapshot diff empty.
    - trust note: a green build alone is gameable (a stub compiles) → the snapshot diff is the
      real-behavior oracle; uncovered files cannot be gated → routed to NEEDS_MANUAL, not faked green.
    - verifier ≥ generator? yes — the verifier is ground-truth tooling, stronger than any model self-grade.

9.  CONTEXT / MEMORY STRATEGY
    - posture: fresh-per-iteration (outer) ; accumulating within the 3 inner refine rounds.
    - external state: migration_ledger.json (resume point) + git (one branch+commit/file) + AGENTS.md (learnings).
    - survives an iteration: the ledger, git history, AGENTS.md. Discarded: the per-file working context.

10. FAILURE / FALLBACK HANDLING
    - dominant failure mode of this topology: converge-to-green-but-wrong (gate too weak) and
      cross-file collision on shared modules.
    - fallback path: a bad file is `git revert` on its own branch — no mega-diff to untangle; a file
      that won't go green in 3 rounds drops to BLOCKED for human pickup.
    - durability: ledger is the checkpoint; a crash resumes at the failed file, not file 1; each
      commit is the idempotency boundary (re-running a passed file is a no-op).

11. EXECUTION SUBSTRATE + RUNNABLE SKETCH
    - substrate: a bash/Stop-hook `--max-iterations` driver (or `TaskCreate` per file for monitored,
      serialized dispatch). The per-file branch + commit is the revert path; migration_ledger.json
      is the resumable checkpoint.
    - sketch: see the pipeline outline and the per-file gate command below.

12. SCORING
    - rubrics: rubric-ralph-loop + rubric-evaluator-optimizer + rubric-loop-selection +
      rubric-loop-control + rubric-plan-quality (see A.4).
    - self-score: gates PASS; review dims ≥ 3; verdict BLUEPRINT-COMPLETE — UNVERIFIED.

13. CONFIDENCE / UNVERIFIED NOTE
    - Unvalidated: the gate has not been run against the repo; the uncovered-file count is unknown
      until the setup scan runs; the token budget is an estimate, not a guarantee.
    - Verdict: BLUEPRINT-COMPLETE — UNVERIFIED.

14. TRUST BOUNDARY & BLAST RADIUS
    - ingested content: a first-party codebase the operator owns — NOT attacker-controlled external
      content; no open-web / transcript / issue ingestion. (Were the repo untrusted, the converter
      would need a content/action split before any write.)
    - privilege / blast radius: writes are confined to a file allowlist + a per-file branch; the loop
      holds no production credentials and takes no external/irreversible action; the blast radius of a
      single bad iteration is one revertible file (`git revert` on its branch).
    - containment: file-allowlist + per-file branch + clean `git reset --hard` to last green.
```

### (a) Pipeline over files — runnable script outline

```text
# === agent-loops blueprint: react-class-to-hooks ===
# Durable state (survives every context reset):
#   migration_ledger.json : [ { file, status: pending|passed|BLOCKED|NEEDS_MANUAL,
#                               attempts:int, last_error:str } ]
#   AGENTS.md             : append-only learned migration gotchas
#   git                   : one branch + commit per file (the verified-state chain)

setup:
  ledger = scan("src/**/*.{jsx,tsx}") |> detect_class_components()   # seed pending
  for f in ledger: f.has_coverage = test_or_snapshot_exists(f)
  ledger.where(!has_coverage).status = NEEDS_MANUAL                  # quarantine the gap NOW

outer_loop:                          # one FRESH agent context per iteration
  while ledger.any(status == pending):
    f = ledger.next(status == pending, order_by=priority)           # pick highest-priority pending
    branch("migrate/" + f)

    # read-only grounding (bounded sub-step, NOT a writing fan-out):
    deps = search_codebase(f, max_subagents=5)   # find shared utils/contexts it touches
    if deps.touches_shared_module: serialize_lock(deps.shared)      # avoid cross-file collision

    # inner evaluator-optimizer micro-loop (cap 3):
    for attempt in 1..3:
      patch = convert_to_hooks(f, deps, learned=read("AGENTS.md"))
      gate  = run("tsc --noEmit") && run("jest " + f) && snapshot_diff(f).empty
      if gate.green:
        commit(f); ledger[f].status = passed; break
      else:
        feedback = gate.failure_detail        # KEEP the error in context for the next round
    if not gate.green:
      ledger[f].status = BLOCKED; ledger[f].last_error = feedback   # no further looping on it
    append_learnings("AGENTS.md", from=this_iteration)              # fix the harness, not just the file
    # context discarded; outer loop respawns fresh on the next file

terminate_when:
  ledger.none(status == pending)        # goal gate
  OR file_budget_exhausted              # hard cap
report:
  passed=N, BLOCKED=[...with last_error], NEEDS_MANUAL=[...]        # humans handle the two tails
```

Mapped to harness primitives: the outer loop is a Ralph-style `Stop`-hook / `--max-iterations` driver (or `TaskCreate` per file for monitored, serialized dispatch); the per-file branch + commit is the revert path; `migration_ledger.json` is the resumable checkpoint, so a crash resumes at the failed file, not file 1.

### (b) Per-file verification gate (the concrete back-pressure)

```bash
# gate(file) — exit 0 ⇒ commit; non-zero ⇒ feed stderr back into the refine round
tsc --noEmit \
  && jest --findRelatedTests "$FILE" --ci \
  && git diff --exit-code -- "$(snapshot_path "$FILE")"   # empty snapshot diff = no behavior change
```

This gate is what converts brute force into **convergence-to-working-code** instead of convergence-to-slop: a green build alone is gameable (a stub compiles), so the **snapshot diff** is added as the real-behavior oracle, and uncovered files are routed to humans rather than allowed to fake-pass.

---

## A.4 — Rubrics that would score this plan

Loaded via `rubrics/rubric-manifest.json`: the three cross-cutting rubrics always, plus the per-family rubrics for the chosen outer (Ralph-style) and inner (evaluator-optimizer) topologies.

- **`rubric-loop-control`** (cross-cutting, applies to _every_ emitted plan):
  - `C1-termination-stack` `[gate]` — goal gate + no-progress→BLOCKED + hard cap, all enforced outside the model. **PASS.**
  - `C2-budget` `[gate]` — per-file 40k advisory / 60k ceiling + `--max-files` circuit breaker. **PASS.**
  - `C3-verification-gate` `[gate]` — snapshot diff defeats green-but-wrong; uncovered→manual. **PASS.**
  - `C7-durability-idempotency` `[gate]` — ledger resume + per-commit idempotency boundary. **PASS.**
  - `C4-context-posture` / `C5-external-memory` / `C6-no-progress-signal` / `C8-observability` `[review]` — fresh-per-file justified by rot; ledger+git+AGENTS.md carry state; 3-fail→BLOCKED is the no-progress signal; the report surfaces both tails. **≥3.**
- **`rubric-ralph-loop`** (the outer loop borrows Ralph):
  - `R2-gate-rigor` `[gate]` — snapshot oracle, not bare typecheck. **PASS.**
  - `R3-context-reset` `[gate]` — fresh context per file, state on disk. **PASS.**
  - `R4-stop-safety` `[gate]` — BLOCKED lane + uncovered→manual + hard caps. **PASS.**
  - `R7-blast-radius` `[gate]` — file allowlist + per-file branch + clean revert. **PASS.**
  - `R1-spec-quality` / `R5-scope-per-iteration` / `R6-durable-memory` / `R8-economics` `[review]` — one file/iteration, ledger + AGENTS.md, cheap disposable retries; **`R5` explicitly flags the brownfield risk and confirms the guards that make Ralph-style safe here.** **≥3.**
- **`rubric-evaluator-optimizer`** (the inner micro-loop):
  - `EO1-gate-soundness` `[gate]` — executable oracle, verifier ≥ generator. **PASS.**
  - `EO2-oracle-independence` `[gate]` — gate is deterministic tooling, independent of the generator. **PASS.**
  - `EO5-termination-budget` `[gate]` — cap 3 rounds. **PASS.**
  - `EO6-regression` `[review]` — snapshot diff is the regression protector; commit-only-if-green returns best-not-last. **≥3.**

---

## A.5 — Verdict

**Output Contract run header:**

```text
agent-loops · PLAN · topology per-file-iterative+inner-evaluator-optimizer ·
verdict BLUEPRINT-UNVERIFIED · gates {all PASS at design time} ·
gate not yet executed against the repo; uncovered-file count unknown until the setup scan runs
```

**`PLAN react-class-to-hooks · loop = per-file-iterative + inner-evaluator-optimizer · termination = ledger-all-passed ∥ no-progress→BLOCKED ∥ file/budget cap · gate = tsc + jest + snapshot-diff · BLUEPRINT-COMPLETE — UNVERIFIED`** (the gate has not yet run against the repository; the uncovered-file tail is unmeasured until the setup scan executes).

> **Honest-verification note.** The plan is _runnable_, but per the skill's own rule it is **not** "verified" until the gate has actually run against the codebase and the uncovered-file tail is measured. `READY-TO-RUN` is reserved for an executed, passing run — not a built plan. Per-seat discipline, the blueprint now hands off to the sibling `agentic-ux` skill to score the operator experience of running it (trust, observability, steerability) — that judgment is outside this skill's builder seat.
