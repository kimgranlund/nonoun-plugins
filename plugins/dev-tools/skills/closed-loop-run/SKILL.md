---
name: closed-loop-run
description: Run bounded, evidence-driven verification, diagnosis, repair, and learning cycles for any agentic task without collapsing into an unbounded recursive solver. Use when an agent must test or inspect work, identify failures, improvise locally through limited trial-and-error, progressively verify fixes, stop or escalate predictably, and produce a durable report that improves future runs. Also use to run a series of cycles against a live, nondeterministic or paid system (model evaluations, live rounds), where cycles must stay comparable and spend stays capped.
---

# Closed Loop Run

Use this skill to execute **bounded closed-loop improvement** across software, data, content, workflows, infrastructure, research, design systems, generated artifacts, automation, or other agentic work.

The governing principle is:

> **Explore locally. Verify progressively. Commit at checkpoints. Learn globally.**

Do not restart the full verification cycle after every defect. Do not turn the run into a single recursively expanding problem-solving loop. Instead, separate global governance from bounded local improvisation.

For screenshot feedback, composition defects or user corrections after a passing UI check, read [Close a UI feedback loop](references/ui-feedback.md). It specializes diagnosis and discriminating verification; component and recipe rules remain in the project.

## 1. Core model

Operate across five control horizons:

- **H0 Action:** one command, edit, probe, measurement, or experiment.
- **H1 Repair Window:** a bounded set of H0 actions used to resolve or understand one local issue.
- **H2 Episode:** one failure or tightly coupled failure cluster with a focused objective.
- **H3 Verification Cycle:** the full run: establish intent, verify broadly, resolve episodes, regress, synthesize, report.
- **H4 Learning Cycle:** patterns accumulated across H3 cycles that improve tests, contracts, knowledge, architecture, prompts, tools, or process.

Lower horizons have narrower context, smaller authority, lower cost, and tighter stopping criteria. Higher horizons own broader intent, acceptance criteria, systemic changes, and durable learning. Above them all is the **owner**: the person or governing caller who holds the budget, approves every paid cycle, and settles rulings; this skill uses that one term for that role. The control flow, the run protocol, checkpoints, concurrency, cost strategy and domain adaptation: [references/control-model.md](references/control-model.md).

## 2. Non-negotiable invariants

1. **Intent precedes evaluation.** Define expected outcomes, invariants, and acceptance criteria before interpreting results.
2. **Evidence precedes diagnosis.** Record what happened before explaining why.
3. **Diagnosis precedes repair.** Form and test causal hypotheses instead of immediately editing.
4. **Local loops are bounded.** Every H1 repair window has explicit limits on attempts, time/cost, scope, authority, and verification radius.
5. **Success criteria are immutable inside a repair window.** Local solvers may not redefine the target to make a failure pass.
6. **Verification expands progressively.** Start with the cheapest discriminating check and widen only after local success.
7. **No-progress is a first-class stop condition.** Repetition without material information gain or outcome improvement must terminate the local loop.
8. **Global learning happens after local work.** Do not rewrite architecture, policy, or shared knowledge opportunistically inside a narrowly scoped repair unless escalation authorizes it.
9. **Passing is not enough.** Capture why the failure was possible and what durable change reduces recurrence.
10. **Every run terminates in a reportable state.** Never continue indefinitely.

## 3. H3 verification cycle

Run the outer cycle in this order:

1. **Frame:** establish intent, scope, constraints, expected outcomes, invariants, budgets, and exit conditions.
2. **Baseline:** establish or restore a known-good checkpoint and capture the initial state.
3. **Verify:** run the broadest economically justified verification pass and collect evidence.
4. **Triage:** classify, deduplicate, and cluster failures into episodes.
5. **Resolve episodes:** give each episode an H1 repair window for bounded exploration and repair.
6. **Integrate:** combine validated episode changes at a checkpoint.
7. **Regress progressively:** widen verification from local to system-level.
8. **Evaluate outside-in and inside-out:** confirm both structural correctness and actual outcome correctness.
9. **Synthesize:** identify root causes, recurring patterns, residual risk, and confidence.
10. **Learn and harden:** create regression coverage and update durable knowledge or structures when justified.
11. **Report:** emit the cycle record with resolved, improved, blocked, escalated, exhausted, and newly discovered issues.

Only begin another H3 cycle when the report or governing caller explicitly authorizes continuation. A cycle that spends money needs the owner's explicit approval first (section 17); a report's `next_cycle.required` is a recommendation, never that approval.

## 4. H2 episode contract

Create one episode per failure or tightly coupled failure cluster. An episode MUST declare its objective, the observed deviation, the expected result, its scope (allowed and forbidden areas), its invariants, its verification (direct and local checks), its budget (attempts, wall time, cost, change radius, whether architecture changes are allowed), and its stop rule (no-progress window, confidence floor). The full shape is in [references/records.md](references/records.md); the scaffold is `templates/episode.yaml`.

Adjust budgets to the task. If wall time or monetary cost cannot be measured, use attempts plus scope and verification limits.

## 5. H1 repair window

Within an episode, run a bounded micro-loop:

```text
Observe local evidence
  → form/update hypothesis
  → choose smallest discriminating experiment
  → execute one action
  → run targeted verification
  → update evidence + confidence
  → decide: continue | resolve | stop | escalate
```

The repair window may improvise. It may try alternate implementations, probes, configurations, or hypotheses, but it MUST remain inside the episode contract.

Prefer experiments that maximize information per unit cost. Choose actions that either materially improve the local objective, or materially reduce uncertainty between competing causes. Do not spend attempts on changes that cannot distinguish hypotheses or be measured against the objective.

Track every attempt: hypothesis, action, expected and observed signal, outcome delta, information delta, decision ([references/records.md](references/records.md), `templates/attempt.yaml`). Do not require numeric confidence unless the domain supports it. Ordinal confidence is acceptable.

## 6. Diagnosis protocol

Before repair, decompose failure into:

- **Symptom:** visible or measured deviation.
- **Boundary:** where expected and observed behavior diverge.
- **Candidate causes:** plausible mechanisms, not vague labels.
- **Discriminating evidence:** cheapest evidence that separates candidates.
- **Root cause:** causal explanation supported by evidence.

Then classify, localize, generate hypotheses, rank them by evidence and cost to test, run the discriminating test, confirm or refute, and repair only the confirmed cause (the sequence: [references/diagnosis.md](references/diagnosis.md)). Avoid symptom patching unless the episode explicitly permits a temporary containment fix.

Two root-cause steps come before any hypothesis about the system under test:

- **Rule out lost context first.** Confirm that what should have reached the system under test did: every retrieved item was submitted, every tool result reached the next step, nothing was truncated or stopped at a token or size cap. A failure on lost context is a transport defect, and no change to guidance or behavior can fix it.
- **Uniform errors point at your own pipeline until proven otherwise.** When every run, model, or case fails the same way (one error code, one stop reason, one shape), suspect your harness, checks, scenario, credentials, or transport first, and test that with discriminating evidence before opening episodes against the system. This is a diagnosis step, not a repair.

## 7. Universal root-cause taxonomy

Read [references/taxonomy-and-hardening.md](references/taxonomy-and-hardening.md#7-universal-root-cause-taxonomy) before acting on this section.

## 8. Progressive verification ladder

Do not run the full suite after every H0 action. Expand verification only after cheaper checks pass.

Default ladder, each level defined in [references/verification-ladder.md](references/verification-ladder.md): **V0 Direct**, **V1 Local**, **V2 Neighbor**, **V3 Representative integration**, **V4 Full regression**, **V5 Outcome evaluation**.

H1 repair windows normally operate at V0–V2 and may use V3 when inexpensive. H3 owns V4–V5.

Cache and reuse unchanged evidence where validity can be proven. Invalidate cached evidence when its assumptions or dependencies change.

## 9. Inside-out and outside-in evaluation

Always distinguish these perspectives when both apply. Inside-out asks whether the system behaved according to its internal structures and contracts; outside-in asks whether the actual consumer-visible outcome is correct (the checklists: [references/verification-ladder.md](references/verification-ladder.md)).

A run is not fully resolved when only one perspective passes unless the specification explicitly scopes verification to one side.

## 10. Episode terminal states

Every episode MUST stop in exactly one of these states:

- **RESOLVED:** objective satisfied and required local verification passes.
- **IMPROVED:** meaningful measurable progress, but residual issue remains.
- **BLOCKED:** missing dependency, information, access, resource, or external condition prevents progress.
- **ESCALATED:** likely root cause lies outside the episode's permitted scope or authority.
- **EXHAUSTED:** repair budget consumed without sufficient progress or information gain.

Optionally use **INVALIDATED** when the original reported failure is proven not to be a real defect.

Do not collapse these states into generic PASS/FAIL.

## 11. Stopping policy

Stop an H1 window when any condition is true:

- objective is satisfied;
- attempt/time/cost budget is exhausted;
- the same failure signature persists for the configured no-progress window;
- successive attempts produce negligible outcome improvement and negligible information gain;
- required changes exceed allowed scope or authority;
- a prerequisite is unavailable;
- evidence shows the initial diagnosis is structurally wrong and requires H2/H3 reframing;
- continuing would threaten an invariant or create disproportionate regression risk.

Never create a new repair loop inside a repair loop. New discoveries become:

1. a child finding attached to the current episode if they are strictly local and within budget; or
2. a queued episode for H2/H3 triage if they broaden scope.

This is the primary anti-recursion rule.

## 12. Checkpoints and transactional change

Use checkpoints to keep experimentation reversible: preserve at minimum the starting baseline, the episode start state, the last validated state, and the integrated candidate state before full regression ([references/control-model.md](references/control-model.md)). Commit or retain changes only after their required progressive verification passes.

## 13. Failure clustering

Before creating episodes, deduplicate identical failure signatures, group failures sharing a probable causal boundary, separate independent symptoms that only appear related, prefer the smallest cluster that can be causally reasoned about, and order clusters by dependency and expected downstream impact. Assign a failed case to every cluster it fails in, and report how many cases fail in each cluster at all and how many fail in it only.

When one upstream cause plausibly explains many downstream failures, test that hypothesis before opening many separate repair windows. A failure signature shared across unrelated cases, models, or inputs is that hypothesis at its strongest: apply the uniform-errors step of section 6 before splitting it into episodes.

## 14. Evaluator integrity

Read [references/taxonomy-and-hardening.md](references/taxonomy-and-hardening.md#14-evaluator-integrity) before acting on this section.

## 15. Learning and hardening

Read [references/taxonomy-and-hardening.md](references/taxonomy-and-hardening.md#15-learning-and-hardening) before acting on this section.

## 16. Records

Every materially resolved or escalated episode gets a compact learning record, and every H3 cycle ends in a cycle report; the shapes, the series fields and the output behavior during a run are in [references/records.md](references/records.md), with scaffolds in `templates/`. Store only durable lessons.

The report is the handoff boundary between H3 cycles. A new cycle starts from this report rather than from hidden reasoning or an ever-growing recursive context.

During a run, keep raw evidence near the episode that produced it, keep the active context on current hypotheses and decisive evidence, summarize discarded experiments rather than carrying raw reasoning forward, distinguish known facts, supported inference, and unresolved uncertainty, preserve provenance from finding to resolution, and make stopping and escalation visible decisions, not silent failures. At completion, return the H3 cycle report plus any durable learning records and artifacts required by the caller.

## 17. Running a series

A series is H4 in practice: H3 cycles in sequence, each framed by the previous report, against a system whose output varies between runs or costs money per run.

- **Compare only identical runs.** Rerun a fixed comparison set unchanged; a changed set is a new set with a new id.
- **Alternate targeted and full cycles.** A targeted cycle reruns failures cheaply; a full cycle reruns the whole set to catch passes that turned into failures.
- **Count churn, not only the pass rate.** Report every pass to fail and fail to pass transition beside the totals.
- **Measure the mechanism.** Each fix names one metric that shows its mechanism working live, beyond pass or fail.
- **Freeze before fixing.** Turn each useful failure (a real failure a fix will target, not noise or a quarantined provider error) into a keyless replay pinned to today's behavior, then fix it.
- **Spend under a hard cap.** Cheapest first, a dry run and a credential preflight before spend, the owner's approval before each paid cycle, provider errors quarantined from results.
- **The tooling learns with the product.** Gaps the analysis or runner tooling showed in one cycle are fixed under test before the next cycle needs them.

How: [references/experiment-series.md](references/experiment-series.md) (the series loop, comparison sets, churn, mechanism metrics, the approval gate) and [references/live-evaluation.md](references/live-evaluation.md) (noise and sampling, the cap, preflight, quarantine, replays).

## 18. Cost-aware strategy

Optimize for **evidence gained per unit cost**, not for the number of actions completed. Prefer focused, cheap, reversible, upstream and cached work before broad, expensive, structural, downstream and recomputed work (the full list: [references/control-model.md](references/control-model.md)).

Do not optimize cost by weakening acceptance criteria or skipping the final verification required to make a trustworthy claim.

## 19. Concurrency

Episodes may run in parallel only when their causal boundaries are independent, their change scopes do not conflict, shared state can be isolated, integration order is known or unimportant, and each keeps its own evidence and budget ([references/control-model.md](references/control-model.md)). Serialize episodes when one is upstream of another or when they modify shared contracts, architecture, evaluators, or common state.

## 20. Anti-patterns

Read [references/taxonomy-and-hardening.md](references/taxonomy-and-hardening.md#20-anti-patterns) before acting on this section.

## References

Each reference above is linked where its section needs it; [references/diagnosis.md](references/diagnosis.md) also holds the diagnosis sequence and the clustering steps. `updates-log/` holds one folder per change set to this skill, indexed newest first in `updates-log/CHANGELOG.md`.
