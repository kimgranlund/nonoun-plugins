# Improve — the governed evolution loop

IMPROVE runs **only on a real, observed failure of a loop already in use** — never speculatively. A loop overbaked, produced slop, never stopped, burned the budget, the subagents fought, the context rotted, the gate certified a wrong answer. The job is to evolve the loop _durably and compoundingly_ so that specific failure cannot recur, and to do it as a **governed change** rather than an ad-hoc patch. This is the builder-seat counterpart to EVALUATE: EVALUATE _finds_ where a loop breaks; IMPROVE _fixes the loop so it stays fixed._

The thesis is one line, drawn from practitioner folklore (Huntley, _everything is a ralph loop_, <https://ghuntley.com/loop/>) and the self-improving literature (DGM, SICA, STOP):

> **Fix the harness, not the bug.** When a loop fails, the cheap reflex is to re-patch this run's output. The compounding move is to change the _control plane or topology_ — the gate, the no-progress detector, the fan-out width, the context posture, the prompt/spec contract — so the whole **failure class** disappears for every future run. Most IMPROVE changes are control-plane changes, not loop-body changes.

The discipline that makes it compound (the same one EVALUATE → IMPROVE inherits): **every observed failure adds a repro/eval case _first_, then the fix.** Improving without a new case is just editing; the case is the regression that proves the fix and prevents the class from re-emerging. This mirrors the agentic-UX feedback-graduation discipline owned by the sibling — but here we change the _mechanism_, not the operator experience.

> **Boundary.** If the "failure" is really _the operator couldn't trust / steer / interrupt / undo the run_ — that is a UX defect, scored and fixed by the sibling `agentic-ux` skill, not here. IMPROVE changes the loop's control plane; the sibling changes how it feels to drive. Hand off when the trigger is an experience complaint, not a mechanism failure.

## When to run IMPROVE

| Run it when… | Do **not** run it when… |
| --- | --- |
| A loop in use produced a named, observed failure (overbaking, slop, non-termination, runaway cost, conflicting subagents, context rot, wrong gate verdict). | Nothing was observed — "this loop might break someday" is not a trigger. Speculative hardening adds gate/branch complexity for no evidence. |
| A near-miss is worth promoting to a permanent guardrail (the budget ceiling was hit but caught; harden it before it isn't caught). | The complaint is about the _human experience_ of the run (trust, control, observability-as-UX) → hand off to the sibling `agentic-ux` skill. |
| The same failure class recurred across runs and should be fixed once at the harness level, not re-patched each run. | The fix belongs to the _tool perimeter_ the loop reaches (a tool is wrong/missing/over-scoped) → MCP / tool-perimeter design (out of scope for this plugin). |

If nothing was observed, **stop** — escalating a loop's control complexity without evidence is the same over-engineering this skill warns against in PLAN.

## The loop (governed, compounding)

Six steps, in order. The order is the point: name before mapping, **case before change**, change before re-score, re-score before claiming anything.

1. **Name the trigger.** State the observed failure concretely — what was seen, on which run, against which success criterion. "Burned 1.2M tokens and never emitted COMPLETE on the 40-item refactor" is a trigger; "feels slow" is not.

2. **Map it to the in-use topology's named failure mode.** Load the in-use topology's reference and find the matching entry in its failure taxonomy (e.g. Ralph → overbaking / blast-radius; orchestrator-workers → conflicting-implicit-decisions / non-halting dispatch; evaluator-optimizer → oscillation / oracle-label illusion; auto-research → unbounded fan-out / synthesis incoherence; self-improving → reward hacking / drift). The named mode tells you _which control-plane lever_ is the candidate fix and stops you guessing. A trigger that maps to no known failure mode is itself a finding — the topology may be the wrong one (re-open PLAN), not just mis-tuned.

3. **Add the repro/eval case FIRST.** Before changing anything, write down the **failing condition that must now pass** — the smallest reproducible check that currently fails and that the fix must make green. Make it executable where possible (a deterministic oracle: a transcript that must now terminate by step N; a budget assertion `tokens < ceiling`; a no-progress trip after K flat rounds; a held-out task the changed loop must still solve). For non-verifiable failures, the case is a documented scenario + the expected gated outcome. **This case is the regression.** It is what later separates "fixed" from "hoped." It is added _before_ the change so it can be seen to fail first.

4. **Make the MINIMAL control-plane or topology change.** Prefer, in order: (a) **tune the control plane** — tighten the gate, add/strengthen a no-progress detector, lower a cap, change the context posture, add a STUCK/abort path, add a durability checkpoint; (b) **re-parameterize the topology** — narrow fan-out, change model-per-role so the verifier ≥ the generator, change replan cadence, return-best-not-last; (c) **swap the topology** only when the trigger maps to "wrong loop for the task," and only by re-running PLAN. Resist rewriting the loop body. The smallest change that makes the step-3 case pass is the correct change — anything larger is unjustified scope and re-opens its own verification debt. **Treat any topology swap or tool add/remove as a governance event:** it shifts behavior for the whole loop, so the _whole_ relevant rubric set must be re-scored, not just the touched dimension.

5. **Re-score the rubric.** Re-run the cross-cutting `rubrics/rubric-loop-control.md` (a termination/gate/budget change must re-clear C1–C3, C6) plus the in-use topology's family rubric. Score each touched dimension `[gate]` (mechanically — present/absent/count) or `[review]` (judgment, with cited evidence). A description- or prompt-level change is still a behavior change — re-check the gate it touches. The verdict obeys the honesty rule below.

6. **State the residual risk + record.** Name what could still recur (the class this change does _not_ cover; the new failure surface the change introduces — e.g. a tighter gate that now risks false-reject and oscillation). Append the change record (template below) so the evolution is legible without the transcript.

## The honesty rule

**The verdict stays `UNVERIFIED` until the step-3 repro case has actually been executed against the changed loop.** A control-plane edit with every field filled and the rubric re-scored is still `UNVERIFIED` — it is a _proposed_ fix until the failing case is run and observed to pass. This is the same discipline PLAN uses for `BLUEPRINT — UNVERIFIED`: a fix that reads correct but was never exercised is not a fix. Never report `READY` / `FIXED` / `SHIP` on an unrun case. The only path to a non-UNVERIFIED verdict is: case failed before → change applied → case passes now → and, ideally, the original full failure no longer reproduces.

A second honesty trap specific to gate fixes: do not let the _new_ gate or the _new_ stop decision secretly depend on a ground-truth oracle the deployed loop won't have (the **oracle-label illusion**). A fix that only passes the repro case because the test harness happened to know the right answer has not fixed the deployed loop.

## Common observed failure → typical control-plane fix

The default lever for each common failure class. The fix lives in the control plane or in topology parameters — almost never in the loop body. Confidence is marked: most gate/cap fixes are **empirically-supported** (Anthropic, ReAct/Reflexion, Voyager/DGM/STOP ablations); the prompt-and-lesson fixes are **practitioner-folklore** (Huntley, learnings.md) unless noted.

| Observed failure | Maps to (typical topology mode) | Typical control-plane / topology fix | Confidence |
| --- | --- | --- | --- |
| **Overbaking** — keeps "improving" a good-enough output, drifting it worse | Ralph / evaluator-optimizer: no-progress blindness; oscillation | Add a no-progress detector (K flat rounds / >~85% state similarity); **return-best-not-last** instead of last; lower the iteration cap; add an explicit COMPLETE sentinel the gate honors. | empirically-supported |
| **Slop** — converges to plausible-but-wrong; gate passes garbage | evaluator-optimizer / debate: weak gate; self-preference bias; oracle-label illusion | Raise gate trust: swap self-grade → executable oracle / ground-truth where it exists; if judge-only, use a **separate/stronger** judge (verifier ≥ generator) + add an adversarial/negative case to the gate; label correctness UNVERIFIED if no oracle exists. | empirically-supported |
| **Non-termination** — loop never emits done / spins on the same step | orchestrator-workers / ReAct: non-halting dispatch; tool-call repetition | Layer the stop **outside the model**: goal-gate + no-progress (tool-repetition / state-similarity) + hard max-iterations; add a STUCK→escalate path so impossible tasks abort instead of looping. Never rely on the model self-declaring done. | empirically-supported |
| **Runaway cost** — budget exhausted, especially fan-out / `while :;` | auto-research / self-improving / Ralph: unbounded width or iterations | Set a hard token/cost ceiling as a circuit-breaker (not advisory pace alone); cap fan-out width and scale effort to task complexity; for self-improving, bound iterations + per-task cost and add a plateau-stop. | empirically-supported |
| **Conflicting subagents** — parallel agents make irreconcilable implicit decisions (the Flappy-Bird failure) | orchestrator-workers / auto-research: shared-write fan-out; isolation collision | Stop fanning out onto interdependent/shared-write work: serialize the dependent slice, **single-thread synthesis** after parallel research, pass a shared decisions contract in each worker's brief; drop to single-agent depth-first if the work isn't genuinely independent. | empirically-supported |
| **Context rot** — quality decays as the accumulating window passes ~100–150k tokens | any accumulating loop: context-posture mismatch | Switch posture: fresh-per-iteration with all state externalized (spec + plan/ledger + git + progress file), or compaction-bridged with a written summary at the boundary; shrink the per-iteration working set; move long-lived state out of the conversation into a durable store. | empirically-supported |
| **Oracle-label illusion** — the _stop_ secretly depended on ground truth the deployed loop won't have | evaluator-optimizer / self-improving: gate–termination leak | Decouple the stop from any ground-truth signal: terminate on the _deployable_ gate (oracle the loop actually runs, or judge + caps), and verify the repro case passes without the test harness feeding the answer. | empirically-supported |
| **Reward hacking / drift** (self-improving only) — the loop games a misspecified utility or one bad self-edit degrades all descendants | self-improving: gameable utility; greedy retention | Harden the utility (cheap, automatic, held-out, hard-to-game) + a functional/regression gate (must still compile / retain core ability); keep an **archive** of prior artifacts (stepping-stones) instead of greedy retention; add a sandbox + overseer/kill-switch. | empirically-supported |

When a trigger doesn't fit any row, it usually means **wrong topology, not wrong tuning** — re-open PLAN rather than bolting another guard onto a loop the task never matched.

## Output — the IMPROVE change record

Emit exactly this artifact (from the SKILL.md Output Contract). Reviewable and handoff-ready without reading the session transcript. Lead with the run-header line.

Run-header (first line): `agent-loops · improve · topology {name} · verdict {UNVERIFIED | SOUND} · {trigger short name}`

```text
Trigger: {observed failure} → maps to {topology failure mode}
Repro/eval case added (first): {the failing condition that must now pass}
Change: {minimal control-plane or topology edit}
Re-score: {gates + review deltas}
Residual risk: {what could still recur}
Verdict: UNVERIFIED until the repro case is executed against the changed loop
```

Field notes:

- **Trigger** names the observed failure _and_ the named topology mode it maps to (step 1 + 2). No bare symptom.
- **Repro/eval case** is written in the present tense as the condition that must _now_ pass, and it was added **before** the change. State whether it is an executable oracle or a documented scenario.
- **Change** is the _minimal_ edit and says which lever it pulls (gate / no-progress / cap / context posture / fan-out / model-per-role / topology swap). A topology swap or tool add/remove is flagged as a governance event with the full re-score.
- **Re-score** lists the touched `rubric-loop-control` gates (PASS/FAIL) and any `[review]` deltas in the family rubric, with one-line cited evidence.
- **Residual risk** names the class still uncovered _and_ the new surface the change introduced (e.g. tighter gate → false-reject/oscillation risk).
- **Verdict** is `UNVERIFIED` until the repro case is run; only then may it become `SOUND`.

## §SelfAudit for IMPROVE

Before emitting the change record:

- **Real trigger?** Was this run on an _observed, named_ failure — not speculative hardening? If speculative, stop.
- **Mapped, not guessed?** Did the trigger map to a _named_ failure mode of the in-use topology (or, if it mapped to none, did I re-open PLAN instead of bolting on a guard)?
- **Case before change?** Was the repro/eval case written _and seen to fail_ **before** the fix? It is the regression; no case = editing, not improving.
- **Minimal lever?** Is this the _smallest_ control-plane/parameter change that makes the case pass — not a loop-body rewrite or unrelated scope creep? Did I fix the **harness**, not this run's bug?
- **Governance event handled?** If I swapped a topology or added/removed a tool, did I re-score the _whole_ relevant rubric set, not just the touched dimension?
- **No new oracle-label leak?** Does the fixed stop/gate depend only on signals the _deployed_ loop will have — not a test-harness answer key?
- **Verdict honest?** Is the verdict `UNVERIFIED` because the case hasn't actually been run against the changed loop — and only `SOUND` if it has and passes?
- **Right seat?** Was the trigger a _mechanism_ failure (mine to fix) and not an operator-experience complaint (hand off to the sibling `agentic-ux` skill)?
